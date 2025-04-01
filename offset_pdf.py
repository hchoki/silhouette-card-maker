import os
from typing import Tuple
from xml.dom import ValidationErr

import click
import json
from pydantic import BaseModel
import pypdfium2 as pdfium

from utilities import offset_images

# Dimensions of the resized letter-sized sheet
print_width = 3300
print_height = 2550

output_directory = os.path.join('game', 'output')
default_output_pdf_path = os.path.join(output_directory, 'game.pdf')

@click.command()
@click.option("--pdf_path", default=default_output_pdf_path, help="The path of the input PDF.")
@click.option("--output_pdf_path", help="The desired path of the offset PDF.")
@click.option("-x", "--x_offset", type=int, help="The desired offset in the x-axis.")
@click.option("-y", "--y_offset", type=int, help="The desired offset in the y-axis.")

def offset_pdf(pdf_path = None, output_pdf_path = None, x_offset = None, y_offset = None):
    x_from_config, y_from_config = load_offset_data()

    # Use to check if user wants to store new offset values
    new_x_offset = 0
    new_y_offset = 0

    if x_from_config is not None:
        new_x_offset = x_from_config
    if x_offset is not None:
        new_x_offset = x_offset

    if y_from_config is not None:
        new_y_offset = y_from_config
    if y_offset is not None:
        new_y_offset = y_offset

    print(f'Using x offset: {new_x_offset}')
    print(f'Using y offset: {new_y_offset}')

    # Save new offset data
    if new_x_offset != x_from_config or new_y_offset != y_from_config:
        print('Would you like to save your offset data for future use? [y/n]')

        user_input = input().strip().lower()
        if user_input == 'y' or user_input == 'yes':
            save_offset_data(new_x_offset, new_y_offset)

    pdf = pdfium.PdfDocument(pdf_path)

    # Get all the raw page images from the PDF
    raw_images = []
    for page_number in range(len(pdf)):
        print(f"page {page_number + 1}")
        page = pdf.get_page(page_number)
        raw_images.append(page.render(scale=300/72).to_pil().resize((print_width, print_height)))
        
    # Offset images
    final_images = offset_images(raw_images, new_x_offset, new_y_offset)

    # The default for output_pdf_path is the original path but with _offset.py appended to the end.
    if output_pdf_path is None:
        output_pdf_path = f'{pdf_path.removesuffix(".pdf")}_offset.pdf'

    final_images[0].save(output_pdf_path, save_all=True, append_images=final_images[1:], resolution=300)
    print(f'offset PDF: {output_pdf_path}')


def save_offset_data(x_offset, y_offset) -> None:
    # Create the directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Save the offset data to a JSON file
    with open('data/offset_data.json', 'w') as offset_file:
        offset_file.write(OffsetData(x_offset=x_offset, y_offset=y_offset).model_dump_json(indent=4))

    print('Offset data saved!')

def load_offset_data() -> Tuple[int, int]:
    if os.path.exists('data/offset_data.json'):
        with open('data/offset_data.json', 'r') as offset_file:
            print("Loaded saved offset values")
            try:
                data = json.load(offset_file)
                offset_data = OffsetData(**data)
                return (offset_data.x_offset, offset_data.y_offset)

            except ValidationErr as e:
                print(f'Cannot validate offset data: {e}.')

    return (None, None)

class OffsetData(BaseModel):
    x_offset: int
    y_offset: int

if __name__ == '__main__':
    offset_pdf()