from os import path
import sys
from click import command, argument, Choice

from deck_formats import DeckFormat, parse_deck
from one_piece import get_handle_card

# Add the plugins directory to the path
sys.path.append(path.join(path.dirname(__file__), '..'))
from shared_upscaling import add_upscale_options

front_directory = path.join('game', 'front')

@add_upscale_options
@command()
@argument('deck_path')
@argument('format', type=Choice([t.value for t in DeckFormat], case_sensitive=False))

def cli(deck_path: str, format: DeckFormat, upscale: bool, upscale_factor: int, noise_level: int):
    if not path.isfile(deck_path):
        print(f'{deck_path} is not a valid file.')
        return

    with open(deck_path, 'r') as deck_file:
        deck_text = deck_file.read()

        parse_deck(deck_text, format, get_handle_card(front_directory, upscale, upscale_factor, noise_level))

if __name__ == '__main__':
    cli()