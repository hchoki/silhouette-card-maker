from enum import Enum
import itertools
import json
import os
from pathlib import Path
from typing import List

from natsort import natsorted
from PIL import Image, ImageChops, ImageDraw, ImageFont

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

def get_back_image_path(back_dir_path) -> str | None:
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

def draw_card_with_border(card_image: Image, page_image: Image, box: tuple[int, int, int, int], thickness: int):
    origin_x, origin_y, origin_width, origin_height = box

    # Draw the card multiple times with different dimensions to create print bleed
    for i in reversed(range(thickness)):
        card_image_resize = card_image.resize((origin_width + (2 * i), origin_height + (2 * i)))
        page_image.paste(card_image_resize, (origin_x - i, origin_y - i))

def draw_card_layout(card_images: List[Image.Image], page_image: Image.Image, num_rows: int, num_cols: int, x_pos: List[int], y_pos: List[int], width: int, height: int, border_thickness: int, flip: bool):
    num_cards = num_rows * num_cols

    # Fill all the spaces with the card back
    for i, card_image in enumerate(card_images):

        # Calculate the location of the new card based on what number the card is
        new_origin_x = x_pos[i % num_cards % num_cols]
        new_origin_y = y_pos[(i % num_cards) // num_cols]

        if flip:
            new_origin_y = y_pos[num_rows - ((i % num_cards) // num_cols) - 1]

            # Rotate the back image to account for orientation
            card_image = card_image.rotate(180)

        draw_card_with_border(
            card_image,
            page_image,
            (new_origin_x, new_origin_y, width, height),
            border_thickness
        )

def get_back_page(back_path: str, blank_im: Image.Image, reg_im: Image.Image, selected_template, enable_front_registration: bool, add_back_page: bool) -> Image.Image:
    border_thickness = cut_border_thickness
    if enable_front_registration:
        border_thickness = selected_template['border_thickness']

    # Create a copy of the registration marks to paste the back images onto
    back_page = reg_im.copy()
    if enable_front_registration:
        back_page = blank_im.copy()

    if add_back_page:
        # Load the card back image
        with Image.open(back_path) as back_im:
            num_rows = len(selected_template['y_pos'])
            num_cols = len(selected_template['x_pos'])
            num_cards = num_rows * num_cols

            draw_card_layout(
                [back_im] * num_cards,
                back_page,
                num_rows,
                num_cols,
                selected_template['x_pos'],
                selected_template['y_pos'],
                selected_template['width'],
                selected_template['height'],
                border_thickness,
                True
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

def generate_pdf(front_dir_path: str, back_dir_path: str, double_sided_dir_path: str, pdf_path: str, selected_template_type: TemplateType, enable_front_registration: bool = False):
    f_path = Path(front_dir_path)
    if not f_path.exists() or not f_path.is_dir():
        raise Exception(f'front image directory path "{f_path}" is invalid')

    b_path = Path(back_dir_path)
    if not b_path.exists() or not b_path.is_dir():
        raise Exception(f'back image directory path "{b_path}" is invalid')

    d_path = Path(double_sided_dir_path)
    if not d_path.exists() or not d_path.is_dir():
        raise Exception(f'double-sided image directory path "{d_path}" is invalid')

    front_image_filenames = [f for f in os.listdir(front_dir_path) if os.path.isfile(os.path.join(front_dir_path, f)) and not f.endswith(".md")]
    ds_image_filenames = [f for f in os.listdir(double_sided_dir_path) if os.path.isfile(os.path.join(double_sided_dir_path, f)) and not f.endswith(".md")]

    # Check if double-sided back images has matching front images
    front_set = set(front_image_filenames)
    ds_set = set(ds_image_filenames)
    if not ds_set.issubset(front_set):
        raise Exception(f'double-sided back images "{ds_set - front_set}" do not have matching front images.')

    # Get the back image, if it exists
    back_image_path = get_back_image_path(back_dir_path)

    # If there's no back image, then do not add back pages to the PDF
    add_back_page = True
    if back_image_path is None:
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

        # Load an image with the registration marks
        with Image.open(registration_path) as reg_im:

            back_page = get_back_page(back_image_path, blank_im, reg_im, selected_template, enable_front_registration, add_back_page)

            # Create the array that will store the filled templates
            pages = []

            front_border_thickness = selected_template['border_thickness']
            back_border_thickness = cut_border_thickness
            if enable_front_registration:
                front_border_thickness = cut_border_thickness
                back_border_thickness = selected_template['border_thickness']

            # # Create the front pages using the images in game/front directory
            # for path, subdirs, files in os.walk(front_dir_path):

            #     # Remove the .md file
            #     files = [file for file in files if not file.endswith(".md")]

            #     # Sort with natural sort so it's easier to understand the whole PDF
            #     files[:] = natsorted(files)


            # Create single-sided card layout
            num_image = 1
            it = iter(natsorted(list(front_set - ds_set)))
            while True:
                file_group = list(itertools.islice(it, num_cards))
                if not file_group:
                    break

                # Fetch card art
                front_images = []
                for file in file_group:
                    print(f'image {num_image}: {file}')
                    num_image = num_image + 1

                    image_path = os.path.join(front_dir_path, file)
                    front_images.append(Image.open(image_path))

                # Create a copy of the blank template to paste the images onto
                front_page = get_front_page(blank_im, reg_im, enable_front_registration)

                draw_card_layout(
                    front_images,
                    front_page,
                    num_rows,
                    num_cols,
                    selected_template['x_pos'],
                    selected_template['y_pos'],
                    selected_template['width'],
                    selected_template['height'],
                    front_border_thickness,
                    False
                )

                add_front_back_pages(front_page, back_page, pages, selected_template, add_back_page)

            # Create double-sided card layout
            it = iter(natsorted(list(ds_set)))
            while True:
                file_group = list(itertools.islice(it, num_cards))
                if not file_group:
                    break

                # Fetch card art
                front_images = []
                back_images = []
                for file in file_group:
                    print(f'image {num_image} (double-sided): {file}')
                    num_image = num_image + 1

                    image_path = os.path.join(front_dir_path, file)
                    front_images.append(Image.open(image_path))

                    image_path = os.path.join(double_sided_dir_path, file)
                    back_images.append(Image.open(image_path))

                front_page = blank_im.copy()
                back_page = reg_im.copy()
                if enable_front_registration:
                    front_page = reg_im.copy()
                    back_page = blank_im.copy()

                draw_card_layout(
                    front_images,
                    front_page,
                    num_rows,
                    num_cols,
                    selected_template['x_pos'],
                    selected_template['y_pos'],
                    selected_template['width'],
                    selected_template['height'],
                    front_border_thickness,
                    False
                )

                draw_card_layout(
                    back_images,
                    back_page,
                    num_rows,
                    num_cols,
                    selected_template['x_pos'],
                    selected_template['y_pos'],
                    selected_template['width'],
                    selected_template['height'],
                    back_border_thickness,
                    True
                )

                add_front_back_pages(front_page, back_page, pages, selected_template, add_back_page)

            # Save the pages array as a PDF
            pages[0].save(pdf_path, format = 'PDF', save_all = True, append_images = pages[1:])
            print(f'generated PDF: {pdf_path}')

def offset_images(images: List[Image.Image], x_offset: int, y_offset: int) -> List[Image.Image]:
    offset_images = []

    add_offset = False
    for image in images:
        if add_offset:
            offset_images.append(ImageChops.offset(image, x_offset, y_offset))
        else:
            offset_images.append(image)

        add_offset = not add_offset

    return offset_images