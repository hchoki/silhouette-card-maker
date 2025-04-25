import os

import click
from deck_formats import DeckFormat, parse_deck
from scryfall import get_handle_card

from typing import List, Set

front_directory = os.path.join('game', 'front')
double_sided_directory = os.path.join('game', 'double_sided')

@click.command()
@click.argument('deck_path')
@click.argument('format', type=click.Choice([t.value for t in DeckFormat], case_sensitive=False))
@click.option('-i', '--ignore_set_and_collector_number', default=False, is_flag=True, show_default=True, help="Ignore provided sets and collector numbers when fetching cards.")
@click.option('--prefer_older_sets', default=False, is_flag=True, show_default=True, help="Prefer fetching cards from older sets if sets are not provided.")
@click.option('-s', '--preferred_set', multiple=True, help="Specify preferred set(s) when fetching cards if sets are not provided. Use this option multiple times to specify multiple preferred sets.")
@click.option('--prefer_showcase', default=False, is_flag=True, show_default=True, help="Prefer fetching cards from showcase treatment")
@click.option('--prefer_full_art', default=False, is_flag=True, show_default=True, help="Prefer fetching cards with full art, borderless, or extended art.")

def cli(
    deck_path: str,
    format,
    ignore_set_and_collector_number: bool,
    prefer_older_sets: bool,
    preferred_set: Set,

    prefer_showcase: bool,
    prefer_full_art: bool
):
    if not os.path.isfile(deck_path):
        print(f'{deck_path} is not a valid file.')
        return

    with open(deck_path, 'r') as deck_file:
        deck_text = deck_file.read()

        parse_deck(
            deck_text,
            format,
            get_handle_card(
                ignore_set_and_collector_number,

                prefer_older_sets,
                preferred_set,
                
                prefer_showcase,
                prefer_full_art,

                front_directory,
                double_sided_directory
            )
        )

if __name__ == '__main__':
    cli()