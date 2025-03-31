import os

import click
from utilities import TemplateType, generate_pdf

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
@click.option("--template_type", default=TemplateType.STANDARD.value, type=click.Choice([t.value for t in TemplateType], case_sensitive=False), show_default=True, help="The desired card size.")
@click.option("--front_registration", default=False, is_flag=True, help="Enable the front pages to have Print & Play (registration marks).")
@click.option("--only_fronts", default=False, is_flag=True, help="Only use the card fronts, exclude the card backs.")

def cli(front_dir_path, back_dir_path, double_sided_dir_path, output_pdf_path, template_type, front_registration, only_fronts):
    generate_pdf(front_dir_path, back_dir_path, double_sided_dir_path, output_pdf_path, template_type, front_registration, only_fronts)

if __name__ == '__main__':
    cli()