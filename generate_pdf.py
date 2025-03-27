from enum import Enum
import json
import os
from pathlib import Path
from typing import List

from natsort import natsorted
from PIL import Image, ImageDraw, ImageFont

# Specify directory locations
asset_directory = 'assets'

blank_filename = 'letter_blank.jpg'
blank_path = os.path.join(asset_directory, blank_filename)

registration_filename = 'letter_registration.jpg'
registration_path = os.path.join(asset_directory, registration_filename)

# Dimensions of the resized letter-sized sheet
print_width = 3300
print_height = 2550

cut_border_thickness = 5

class TemplateType(Enum):
    STANDARD = "standard"
    BRIDGE = "bridge"
    POKER = "poker"
    POKER_HALF = "poker_half"

def get_back_path(back_dir_path) -> str | None:
    # List all files in the directory that do not end with .md
    # The directory should contain EMPTY.md
    files = [f for f in os.listdir(back_dir_path) if (os.path.isfile(os.path.join(back_dir_path, f)) and not f.endswith(".md"))]

    # Check if there is exactly one file
    if len(files) == 0:
        return None
    elif len(files) == 1:
        return os.path.join(back_dir_path, files[0])
    else:
        raise Exception(f'Back image directory path "{back_dir_path}" contains more than one image')

def image_paste_with_border(image: Image, page: Image, box: tuple[int, int, int, int], thickness: int):
    origin_x, origin_y, origin_width, origin_height = box
    for i in reversed(range(thickness)):
        im_resize = image.resize((origin_width + (2 * i), origin_height + (2 * i)))
        page.paste(im_resize, (origin_x - i, origin_y - i))

def get_back_page(back_path: str, blank_im: Image.Image, reg_im: Image.Image, selected_template, enable_front_registration: bool, add_back_page: bool) -> Image.Image:
    # Create a copy of the registration marks to paste the back images onto
    back_page = reg_im.copy()
    if enable_front_registration:
        back_page = blank_im.copy()

    if add_back_page:
        # Load the card back image
        with Image.open(back_path) as back_im:
            # Resize the back image to the specified dimensions
            back_im_corr = back_im.resize((selected_template['width'], selected_template['height']))

            # Rotate the back image to account for orientation
            back_im_corr = back_im_corr.rotate(180)

            num_rows = len(selected_template['y_pos'])
            num_cols = len(selected_template['x_pos'])
            num_cards = num_rows * num_cols

            # Fill all the spaces with the card back
            for i in range(num_cards):
                # Calculate the location of the new card based on what number the card is
                new_origin_x = selected_template['x_pos'][i % num_cards % num_cols]
                new_origin_y = selected_template['y_pos'][(i % num_cards) // num_cols]

                border_thickness = cut_border_thickness
                if enable_front_registration:
                    border_thickness = selected_template['border_thickness']

                image_paste_with_border(
                    back_im_corr,
                    back_page,
                    (new_origin_x, new_origin_y, selected_template['width'], selected_template['height']),
                    border_thickness
                )

    return back_page

def get_front_page(blank_im: Image.Image, reg_im: Image.Image, enable_front_registration: bool) -> Image.Image:
    front_page = blank_im.copy()
    if enable_front_registration:
        front_page = reg_im.copy()

    return front_page

def add_front_back_pages(front_page: Image.Image, back_page: Image.Image, pages: List[Image.Image], selected_template, add_back_page: bool):
    # Add template version number to the back
    draw = ImageDraw.Draw(front_page)
    font = ImageFont.truetype(os.path.join(asset_directory, 'arial.ttf'), 40)

    # "Raw" specified location
    num_sheet = len(pages) + 1
    if add_back_page:
        num_sheet = int(len(pages) / 2) + 1

    draw.text((print_width - 800, print_height - 80), f'sheet: {num_sheet}, template: {selected_template["template"]}', fill = (0, 0, 0), font = font)

    # Add a back page for every front page template
    pages.append(front_page)
    if add_back_page:
        pages.append(back_page)

# def generate_pdf(front_dir_path: str, back_path: str, pdf_path: str, selected_template_type: TemplateType, enable_front_registration: bool = False):
def generate_pdf(front_dir_path: str, back_dir_path: str, pdf_path: str, selected_template_type: TemplateType, enable_front_registration: bool = False):
    f_path = Path(front_dir_path)
    if not f_path.exists() or not f_path.is_dir():
        raise Exception(f'Front image directory path "{f_path}" is invalid')

    b_path = Path(back_dir_path)
    if not b_path.exists() or not b_path.is_dir():
        raise Exception(f'back image directory path "{b_path}" is invalid')

    # Get the back image, if it exists
    back_path = get_back_path(back_dir_path)

    # If there's no back image, then do not add back pages to the PDF
    add_back_page = True
    if back_path is None:
        add_back_page = False

        # If there are no back pages, then by default, use front registration
        enable_front_registration = True

    # Load the JSON with all the card sizing information
    json_filename = 'card_size_config.json'
    json_path = os.path.join(asset_directory, json_filename)
    with open(json_path, 'r') as f:
        templates = json.load(f)

    # Check if the selected template type is valid
    if selected_template_type not in templates.keys():
        raise Exception(f'Unknown template "{selected_template_type}"')

    # Load data from the selected template type
    selected_template = templates[selected_template_type]
    num_rows = len(selected_template['y_pos'])
    num_cols = len(selected_template['x_pos'])
    num_cards = num_rows * num_cols

    # Load a blank page
    with Image.open(blank_path) as blank_im:

        # Load an image with the registration marks for the Cameo 5
        with Image.open(registration_path) as reg_im:

            back_page = get_back_page(back_path, blank_im, reg_im, selected_template, enable_front_registration, add_back_page)

            # Create a copy of the blank template to paste the images onto
            front_page = get_front_page(blank_im, reg_im, enable_front_registration)

            # Create the array that will store the filled templates
            pages = []

            # Create the front pages using the images in game/front directory
            for path, subdirs, files in os.walk(front_dir_path):

                # Sort with natural sort so it's easier to understand the whole PDF
                files[:] = natsorted(files)

                # Iterate through all the files in the game/front directory
                n = 0
                for name in files:
                    if name.endswith(".md"):
                        continue

                    print(f"image {n + 1}: {name}")

                    # If the template is full, add to pages and restart
                    if n and not (n % num_cards):

                        add_front_back_pages(front_page, back_page, pages, selected_template, add_back_page)

                        # Create a blank copy for the next page
                        front_page = get_front_page(blank_im, reg_im, enable_front_registration)

                    # Load the image to process it
                    front_path = os.path.join(path, name)
                    with Image.open(front_path) as front_im:

                        # Resize the front images to the specified dimension
                        front_im_corr = front_im.resize((selected_template['width'], selected_template['height']))

                        # Calculate the location of the new card based on what number the card is
                        new_origin_x = selected_template['x_pos'][n % num_cards % num_cols]
                        new_origin_y = selected_template['y_pos'][(n % num_cards) // num_cols]

                        border_thickness = selected_template['border_thickness']
                        if enable_front_registration:
                            border_thickness = cut_border_thickness

                        image_paste_with_border(
                            front_im_corr,
                            front_page,
                            (new_origin_x, new_origin_y, selected_template['width'], selected_template['height']),
                            border_thickness
                        )

                    n += 1

            # Export the final front page template (filled or not) with a back page
            add_front_back_pages(front_page, back_page, pages, selected_template, add_back_page)

            # Save the pages array as a PDF
            pages[0].save(pdf_path, format = 'PDF', save_all = True, append_images = pages[1:])
            print(f'generated PDF: {pdf_path}')