import os

import click
from utilities import CardSize, PaperSize, generate_pdf

front_directory = os.path.join('game', 'front')
back_directory = os.path.join('game', 'back')
double_sided_directory = os.path.join('game', 'double_sided')
output_directory = os.path.join('game', 'output')

default_output_pdf_path = os.path.join(output_directory, 'game.pdf')

@click.command()
@click.option("--front_dir_path", default=front_directory, show_default=True, help="The path to the directory containing the card fronts.")
@click.option("--back_dir_path", default=back_directory, show_default=True, help="The path to the directory containing one or no card backs.")
@click.option("--double_sided_dir_path", default=double_sided_directory, show_default=True, help="The path to the directory containing card backs for double-sided cards.")
@click.option("--output_pdf_path", default=default_output_pdf_path, show_default=True, help="The desired path to the output PDF.")
@click.option("--card_size", default=CardSize.STANDARD.value, type=click.Choice([t.value for t in CardSize], case_sensitive=False), show_default=True, help="The desired card size.")
@click.option("--paper_size", default=PaperSize.LETTER.value, type=click.Choice([t.value for t in PaperSize], case_sensitive=False), show_default=True, help="The desired paper size.")
@click.option("--front_registration", default=False, is_flag=True, help="Enable the front pages to have Print & Play (registration marks).")
@click.option("--only_fronts", default=False, is_flag=True, help="Only use the card fronts, exclude the card backs.")
@click.option("--extend_corners", default=0, type=click.IntRange(min=0), show_default=True, help="Reduce artifacts produced by rounded corners in card images.")
@click.option("--load_offset", default=False, is_flag=True, help="Apply saved offsets. See `offset_pdf.py` for more information.")

def cli(front_dir_path, back_dir_path, double_sided_dir_path, output_pdf_path, card_size, paper_size, front_registration, only_fronts, extend_corners, load_offset):
    generate_pdf(front_dir_path, back_dir_path, double_sided_dir_path, output_pdf_path, card_size, paper_size, front_registration, only_fronts, extend_corners, load_offset)

if __name__ == '__main__':
    cli()