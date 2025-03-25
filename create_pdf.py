import os

import click
from generate_pdf import TemplateType, generate_pdf

front_directory = os.path.join('game', 'front')
back_directory = os.path.join('game', 'back')
output_directory = os.path.join('game', 'output')

back_path = os.path.join(back_directory, 'back.jpg')
pdf_path = os.path.join(output_directory, 'card_game.pdf')

@click.command()
@click.option("--front_dir_path", default=front_directory, show_default=True, help="The path to the directory containing the card front images.")
@click.option("--back_img_path", default=back_path, show_default=True, help="The path to the card back image.")
@click.option("--pdf_path", default=pdf_path, show_default=True, help="The desired path to the output PDF.")
@click.option("--template_type", default=TemplateType.STANDARD.value, type=click.Choice([t.value for t in TemplateType], case_sensitive=False), show_default=True, help="The desired card size.")
@click.option("--front_registration", default=False, is_flag=True, help="Enable the front pages to have Print & Play (registration marks).")

def cli(front_dir_path, back_img_path, pdf_path, template_type, front_registration):
    generate_pdf(front_dir_path, back_img_path, pdf_path, template_type, front_registration)

if __name__ == '__main__':
    cli()