from enum import Enum
import itertools
import json
import os
from pathlib import Path
from typing import List, Tuple

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

def get_back_card_image_path(back_dir_path) -> str | None:
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

def draw_card_with_border(card_image: Image, base_image: Image, box: tuple[int, int, int, int], thickness: int):
    origin_x, origin_y, origin_width, origin_height = box

    # Draw the card multiple times with different dimensions to create print bleed
    for i in reversed(range(thickness)):
        card_image_resize = card_image.resize((origin_width + (2 * i), origin_height + (2 * i)))
        base_image.paste(card_image_resize, (origin_x - i, origin_y - i))

def draw_card_layout(card_images: List[Image.Image], base_image: Image.Image, num_rows: int, num_cols: int, x_pos: List[int], y_pos: List[int], width: int, height: int, border_thickness: int, flip: bool):
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
            base_image,
            (new_origin_x, new_origin_y, width, height),
            border_thickness
        )

def get_base_images(blank_im: Image.Image, reg_im: Image.Image, front_registration: bool) -> Tuple[Image.Image, Image.Image]:
    if front_registration:
        return (reg_im.copy(), blank_im.copy())
    else:
        return (blank_im.copy(), reg_im.copy())

def add_front_back_pages(front_page: Image.Image, back_page: Image.Image, pages: List[Image.Image], selected_template, only_fronts: bool):
    # Add template version number to the back
    draw = ImageDraw.Draw(front_page)
    font = ImageFont.truetype(os.path.join(asset_directory, 'arial.ttf'), 40)

    # "Raw" specified location
    num_sheet = len(pages) + 1
    if only_fronts:
        num_sheet = int(len(pages) / 2) + 1

    draw.text((print_width - 800, print_height - 80), f'sheet: {num_sheet}, template: {selected_template["template"]}', fill = (0, 0, 0), font = font)

    # Add a back page for every front page template
    pages.append(front_page)
    if not only_fronts:
        pages.append(back_page)

def generate_pdf(
    front_dir_path: str,
    back_dir_path: str,
    double_sided_dir_path: str,
    pdf_path: str,
    selected_template_type: TemplateType,
    front_registration: bool = False,
    only_fronts: bool = False,
):
    f_path = Path(front_dir_path)
    if not f_path.exists() or not f_path.is_dir():
        raise Exception(f'Front image directory path "{f_path}" is invalid.')

    b_path = Path(back_dir_path)
    if not b_path.exists() or not b_path.is_dir():
        raise Exception(f'Back image directory path "{b_path}" is invalid.')

    d_path = Path(double_sided_dir_path)
    if not d_path.exists() or not d_path.is_dir():
        raise Exception(f'Double-sided image directory path "{d_path}" is invalid.')
    
    # Get the back image, if it exists
    use_default_back_page = False
    back_card_image_path = get_back_card_image_path(back_dir_path)
    if back_card_image_path is None:
        use_default_back_page = True
        print(f'No back image provided in back image directory "{back_dir_path}". Using default instead.')

    front_image_filenames = [f for f in os.listdir(front_dir_path) if os.path.isfile(os.path.join(front_dir_path, f)) and not f.endswith(".md")]
    ds_image_filenames = [f for f in os.listdir(double_sided_dir_path) if os.path.isfile(os.path.join(double_sided_dir_path, f)) and not f.endswith(".md")]

    # Check if double-sided back images has matching front images
    front_set = set(front_image_filenames)
    ds_set = set(ds_image_filenames)
    if not ds_set.issubset(front_set):
        raise Exception(f'Double-sided backs "{ds_set - front_set}" do not have matching fronts. Add the missing fronts to front image direcoty "{front_dir_path}".')

    if only_fronts:
        front_registration = True

        if len(ds_set) > 0:
            raise Exception(f'Cannot use "--only_fronts" with double-sided cards. Remove cards from double-side image directory "{double_sided_dir_path}".')

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

            # Create the array that will store the filled templates
            pages = []

            front_border_thickness = selected_template['border_thickness']
            back_border_thickness = cut_border_thickness
            if front_registration:
                front_border_thickness = cut_border_thickness
                back_border_thickness = selected_template['border_thickness']

            # Create reusable back page for single-sided cards
            _, single_sided_back_page = get_base_images(blank_im, reg_im, front_registration)
            if not use_default_back_page:

                # Load the card back image
                with Image.open(back_card_image_path) as back_im:
                    num_rows = len(selected_template['y_pos'])
                    num_cols = len(selected_template['x_pos'])
                    num_cards = num_rows * num_cols

                    draw_card_layout(
                        [back_im] * num_cards,
                        single_sided_back_page,
                        num_rows,
                        num_cols,
                        selected_template['x_pos'],
                        selected_template['y_pos'],
                        selected_template['width'],
                        selected_template['height'],
                        back_border_thickness,
                        True
                    )


            # Create single-sided card layout
            num_image = 1
            it = iter(natsorted(list(front_set - ds_set)))
            while True:
                file_group = list(itertools.islice(it, num_cards))
                if not file_group:
                    break

                # Fetch card art
                front_card_images = []
                for file in file_group:
                    print(f'image {num_image}: {file}')
                    num_image = num_image + 1

                    image_path = os.path.join(front_dir_path, file)
                    front_card_images.append(Image.open(image_path))

                single_sided_front_page, _ = get_base_images(blank_im, reg_im, front_registration)

                # Create front layout for single-sided cards
                draw_card_layout(
                    front_card_images,
                    single_sided_front_page,
                    num_rows,
                    num_cols,
                    selected_template['x_pos'],
                    selected_template['y_pos'],
                    selected_template['width'],
                    selected_template['height'],
                    front_border_thickness,
                    False
                )

                add_front_back_pages(single_sided_front_page, single_sided_back_page, pages, selected_template, only_fronts)

            # Create double-sided card layout
            it = iter(natsorted(list(ds_set)))
            while True:
                file_group = list(itertools.islice(it, num_cards))
                if not file_group:
                    break

                # Fetch card art
                front_card_images = []
                back_card_images = []
                for file in file_group:
                    print(f'image {num_image} (double-sided): {file}')
                    num_image = num_image + 1

                    image_path = os.path.join(front_dir_path, file)
                    front_card_images.append(Image.open(image_path))

                    image_path = os.path.join(double_sided_dir_path, file)
                    back_card_images.append(Image.open(image_path))

                double_sided_front_page, double_sided_back_page = get_base_images(blank_im, reg_im, front_registration)

                # Create front layout for double-sided cards
                draw_card_layout(
                    front_card_images,
                    double_sided_front_page,
                    num_rows,
                    num_cols,
                    selected_template['x_pos'],
                    selected_template['y_pos'],
                    selected_template['width'],
                    selected_template['height'],
                    front_border_thickness,
                    False
                )

                # Create back layout for double-sided cards
                draw_card_layout(
                    back_card_images,
                    double_sided_back_page,
                    num_rows,
                    num_cols,
                    selected_template['x_pos'],
                    selected_template['y_pos'],
                    selected_template['width'],
                    selected_template['height'],
                    back_border_thickness,
                    True
                )

                # Add the front and back layouts
                add_front_back_pages(double_sided_front_page, double_sided_back_page, pages, selected_template, False)

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