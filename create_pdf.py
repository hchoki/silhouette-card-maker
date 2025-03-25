import os

import click
from generate_pdf import generate_pdf

front_directory = os.path.join('game', 'front')
back_directory = os.path.join('game', 'back')
output_directory = os.path.join('game', 'output')

back_path = os.path.join(back_directory, 'back.jpg')
pdf_path = os.path.join(output_directory, 'card_game.pdf')

@click.command()
@click.option("--front_dir_path", default=front_directory, show_default=True, help="The path to the directory containing the card front images.")
@click.option("--back_img_path", default=back_path, show_default=True, help="The path to the card back image.")
@click.option("--pdf_path", default=pdf_path, show_default=True, help="The desired path to the output PDF.")
@click.option("--front_registration", default=False, is_flag=True, help="Enable the front pages of the PDF to have registration marks.")

def cli(front_dir_path, back_img_path, pdf_path, front_registration):
    generate_pdf(front_dir_path, back_img_path, pdf_path, front_registration)

if __name__ == '__main__':
    cli()