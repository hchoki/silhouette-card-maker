import os

import click
from deck_formats import DeckFormat, parse_deck
from scryfall import get_handle_card

from typing import List

front_directory = os.path.join('game', 'front')
double_sided_directory = os.path.join('game', 'double_sided')

@click.command()
@click.argument('deck_dir_path')
@click.argument('format', type=click.Choice([t.value for t in DeckFormat], case_sensitive=False))

def cli(deck_dir_path, format):
    if not os.path.isfile(deck_dir_path):
        print(f'{deck_dir_path} is not a valid file.')
        return

    with open(deck_dir_path, 'r') as deck_file:
        parse_deck(deck_file.read(), format, get_handle_card(True, [], False, False, front_directory, double_sided_directory))

if __name__ == '__main__':
    cli()