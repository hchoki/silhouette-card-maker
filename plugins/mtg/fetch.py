import os

import click
from deck_formats import DeckFormat, parse_deck
from scryfall import get_handle_card as scryfall_get_handle_card
from mpcfill import get_handle_card as mpc_get_handle_card

from typing import Set

front_directory = os.path.join('game', 'front')
double_sided_directory = os.path.join('game', 'double_sided')

def fetch_cards(
    deck_path: str,
    format: DeckFormat,
    front_directory: str,
    double_sided_directory: str,
    ignore_set_and_collector_number: bool = False,
    prefer_older_sets: bool = False,
    prefer_set: Set[str] = None,
    prefer_showcase: bool = False,
    prefer_extra_art: bool = False,
    tokens: bool = False,
    art_crop: bool = False,
    parallel: bool = True,
    max_workers: int = 6,
    api_delay: float = 0.05,
    cancel_check = None
):
    """
    Shared function for fetching MTG cards from a deck list.
    Used by both CLI and GUI to ensure consistent behavior.
    
    Args:
        deck_path: Path to deck list file
        format: DeckFormat enum value
        front_directory: Directory for front images
        double_sided_directory: Directory for double-sided back images
        ignore_set_and_collector_number: Ignore provided sets/collector numbers
        prefer_older_sets: Prefer cards from older sets
        prefer_set: Set of preferred set codes
        prefer_showcase: Prefer showcase treatment
        prefer_extra_art: Prefer full art/borderless/extended art
        tokens: Fetch related tokens
        art_crop: Download cropped artwork
        parallel: Enable parallel downloads
        max_workers: Number of parallel download threads
        api_delay: Delay between API requests
        cancel_check: Optional function that returns True if operation should be canceled
    """
    if not os.path.isfile(deck_path):
        raise FileNotFoundError(f'{deck_path} is not a valid file.')
    
    if prefer_set is None:
        prefer_set = set()
    
    # Choose handler based on format
    if format == DeckFormat.MPCFILL_XML:
        get_handle_card = mpc_get_handle_card(
            front_directory,
            double_sided_directory,
            parallel,
            max_workers
        )
    else:
        get_handle_card = scryfall_get_handle_card(
            ignore_set_and_collector_number,
            prefer_older_sets,
            prefer_set,
            prefer_showcase,
            prefer_extra_art,
            tokens,
            art_crop,
            parallel,
            max_workers,
            api_delay,
            front_directory,
            double_sided_directory,
            cancel_check=cancel_check
        )

    with open(deck_path, 'r') as deck_file:
        deck_text = deck_file.read()
        parse_deck(deck_text, format, get_handle_card)
    
    # If parallel mode is enabled and we have queued downloads, process them now
    if parallel and hasattr(get_handle_card, 'download_queue'):
        queue = get_handle_card.download_queue
        if queue.size() > 0:
            print(f"\n📋 Processing {queue.size()} queued downloads in parallel...")
            downloader = get_handle_card.downloader
            
            # Use the appropriate fetch function based on format
            if format == DeckFormat.MPCFILL_XML:
                fetch_func = get_handle_card.fetch_card
            else:
                fetch_func = get_handle_card.fetch_card_art
            
            downloader.download_cards_parallel(
                tasks=queue.get_all_tasks(),
                fetch_function=fetch_func,
                front_dir=get_handle_card.front_img_dir,
                double_sided_dir=get_handle_card.double_sided_dir,
                art_crop=get_handle_card.art_crop if hasattr(get_handle_card, 'art_crop') else False,
                cancel_check=cancel_check
            )

@click.command()
@click.argument('deck_path')
@click.argument('format', type=click.Choice([t.value for t in DeckFormat], case_sensitive=False))
@click.option('-i', '--ignore_set_and_collector_number', default=False, is_flag=True, show_default=True, help="Ignore provided sets and collector numbers when fetching cards.")
@click.option('--prefer_older_sets', default=False, is_flag=True, show_default=True, help="Prefer fetching cards from older sets if sets are not provided.")
@click.option('-s', '--prefer_set', multiple=True, help="Prefer fetching cards from a particular set(s) if sets are not provided. Use this option multiple times to specify multiple preferred sets.")
@click.option('--prefer_showcase', default=False, is_flag=True, show_default=True, help="Prefer fetching cards with showcase treatment")
@click.option('--prefer_extra_art', default=False, is_flag=True, show_default=True, help="Prefer fetching cards with full art, borderless, or extended art.")
@click.option('--tokens', default=False, is_flag=True, show_default=True, help="Fetch related tokens when fetching cards")
@click.option('--art_crop', default=False, is_flag=True, show_default=True, help="Download cropped card artwork instead of full card images")
@click.option('--parallel/--no-parallel', default=True, show_default=True, help="Enable/disable parallel downloads")
@click.option('--max_workers', default=6, type=int, show_default=True, help="Maximum number of parallel download threads (1-20)")
@click.option('--api_delay', default=0.05, type=float, show_default=True, help="Delay between API requests in seconds (default: 0.05 = ~20 req/s, Scryfall limit: ~10 req/s)")

def cli(
    deck_path: str,
    format: DeckFormat,
    ignore_set_and_collector_number: bool,

    prefer_older_sets: bool,
    prefer_set: Set[str],

    prefer_showcase: bool,
    prefer_extra_art: bool,
    tokens: bool,
    art_crop: bool,
    parallel: bool,
    max_workers: int,
    api_delay: float
):
    if not os.path.isfile(deck_path):
        print(f'{deck_path} is not a valid file.')
        return
    
    if format == DeckFormat.MPCFILL_XML:
        get_handle_card = mpc_get_handle_card(
            front_directory,
            double_sided_directory,
            parallel,
            max_workers
        )
    else:
        get_handle_card = scryfall_get_handle_card(
            ignore_set_and_collector_number,

            prefer_older_sets,
            prefer_set,
            
            prefer_showcase,
            prefer_extra_art,
            tokens,
            art_crop,
            parallel,
            max_workers,
            api_delay,

            front_directory,
            double_sided_directory
        )

    with open(deck_path, 'r') as deck_file:
        deck_text = deck_file.read()

        parse_deck(
            deck_text,
            format,
            get_handle_card,
        )
    
    # If parallel mode is enabled and we have queued downloads, process them now
    if parallel and hasattr(get_handle_card, 'download_queue'):
        queue = get_handle_card.download_queue
        if queue.size() > 0:
            print(f"\n📋 Processing {queue.size()} queued downloads in parallel...")
            downloader = get_handle_card.downloader
            
            # Use the appropriate fetch function based on format
            if format == DeckFormat.MPCFILL_XML:
                fetch_func = get_handle_card.fetch_card
            else:
                fetch_func = get_handle_card.fetch_card_art
            
            downloader.download_cards_parallel(
                tasks=queue.get_all_tasks(),
                fetch_function=fetch_func,
                front_dir=get_handle_card.front_img_dir,
                double_sided_dir=get_handle_card.double_sided_dir,
                art_crop=get_handle_card.art_crop if hasattr(get_handle_card, 'art_crop') else False
            )

if __name__ == '__main__':
    cli()