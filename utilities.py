from enum import Enum
import itertools
import json
import math
import os
from pathlib import Path
from typing import Dict, List, Tuple
from xml.dom import ValidationErr

from natsort import natsorted
from PIL import Image, ImageChops, ImageDraw, ImageFont
from pydantic import BaseModel

# Specify directory locations
asset_directory = 'assets'

layouts_filename = 'layouts.json'
layouts_path = os.path.join(asset_directory, layouts_filename)

class CardSize(str, Enum):
    STANDARD = "standard"
    JAPANESE = "japanese"
    POKER = "poker"
    POKER_HALF = "poker_half"
    BRIDGE = "bridge"

class PaperSize(str, Enum):
    LETTER = "letter"
    A4 = "a4"

class CardLayout(BaseModel):
    width: int
    height: int
    x_pos: List[int]
    y_pos: List[int]
    template: str

class PaperLayout(BaseModel):
    width: int
    height: int
    card_layouts: Dict[CardSize, CardLayout]

class Layouts(BaseModel):
    paper_layouts: Dict[PaperSize, PaperLayout]

def get_back_card_image_path(back_dir_path) -> str | None:
    # List all files in the directory that do not end with .md
    # The directory may contain markdown files
    files = [f for f in os.listdir(back_dir_path) if (os.path.isfile(os.path.join(back_dir_path, f)) and not f.endswith(".md"))]

    # Check if there is exactly one file
    if len(files) == 0:
        return None
    elif len(files) == 1:
        return os.path.join(back_dir_path, files[0])
    else:
        raise Exception(f'Back image directory path "{back_dir_path}" contains more than one image. Files include "{files}".')

def draw_card_with_border(card_image: Image, base_image: Image, box: tuple[int, int, int, int], print_bleed: int):
    origin_x, origin_y, origin_width, origin_height = box

    # Draw the card multiple times with different dimensions to create print bleed
    for i in reversed(range(print_bleed)):
        card_image_resize = card_image.resize((origin_width + (2 * i), origin_height + (2 * i)))
        base_image.paste(card_image_resize, (origin_x - i, origin_y - i))

def draw_card_layout(card_images: List[Image.Image], base_image: Image.Image, num_rows: int, num_cols: int, x_pos: List[int], y_pos: List[int], width: int, height: int, print_bleed: int, extend_corners: int, flip: bool):
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

        card_image = card_image.resize((width, height))
        card_image = card_image.crop((extend_corners, extend_corners, card_image.width - extend_corners, card_image.height - extend_corners))

        draw_card_with_border(
            card_image,
            base_image,
            (new_origin_x + extend_corners, new_origin_y + extend_corners, width - (2 * extend_corners), height - (2 * extend_corners)),
            print_bleed + extend_corners
        )

def get_base_images(blank_im: Image.Image, reg_im: Image.Image, front_registration: bool) -> Tuple[Image.Image, Image.Image]:
    if front_registration:
        return (reg_im.copy(), blank_im.copy())
    else:
        return (blank_im.copy(), reg_im.copy())

def add_front_back_pages(front_page: Image.Image, back_page: Image.Image, pages: List[Image.Image], page_width: int, page_height: int, template: str, only_fronts: bool):
    # Add template version number to the back
    draw = ImageDraw.Draw(front_page)
    font = ImageFont.truetype(os.path.join(asset_directory, 'arial.ttf'), 40)

    # "Raw" specified location
    num_sheet = len(pages) + 1
    if not only_fronts:
        num_sheet = int(len(pages) / 2) + 1

    draw.text((page_width - 800, page_height - 60), f'sheet: {num_sheet}, template: {template}', fill = (0, 0, 0), font = font)

    # Add a back page for every front page template
    pages.append(front_page)
    if not only_fronts:
        pages.append(back_page)

def generate_pdf(
    front_dir_path: str,
    back_dir_path: str,
    double_sided_dir_path: str,
    pdf_path: str,
    card_size: CardSize,
    paper_size: PaperSize,
    front_registration: bool,
    only_fronts: bool,
    extend_corners: int,
    load_offset: bool
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

    with open(layouts_path, 'r') as layouts_file:
        try:
            layouts_data = json.load(layouts_file)
            layouts = Layouts(**layouts_data)

        except ValidationErr as e:
            raise Exception(f'Cannot parse layouts.json: {e}.')

        paper_size_enum = PaperSize(paper_size)
        if paper_size_enum not in layouts.paper_layouts:
            print(paper_size)
            print(layouts.paper_layouts)
            raise Exception(f'Unsupported paper size "{paper_size}".')
        paper_layout = layouts.paper_layouts[paper_size_enum]

        card_size_enum = CardSize(card_size)
        if card_size_enum not in paper_layout.card_layouts:
            raise Exception(f'Unsupported card size "{card_size}" with paper size "{paper_size}". Try card sizes: {paper_layout.card_layouts.keys()}.')
        card_layout = paper_layout.card_layouts[card_size_enum]

        num_rows = len(card_layout.y_pos)
        num_cols = len(card_layout.x_pos)
        num_cards = num_rows * num_cols

        blank_filename = f'{paper_size}_blank.jpg'
        blank_path = os.path.join(asset_directory, blank_filename)

        registration_filename =  f'{paper_size}_registration.jpg'
        registration_path = os.path.join(asset_directory, registration_filename)

        # Load a blank page
        with Image.open(blank_path) as blank_im:

            # Load an image with the registration marks
            with Image.open(registration_path) as reg_im:

                # Create the array that will store the filled templates
                pages: List[Image.Image] = []

                max_print_bleed = calculate_max_print_bleed(card_layout.x_pos, card_layout.y_pos, card_layout.width, card_layout.height)

                # Create reusable back page for single-sided cards
                _, single_sided_back_page = get_base_images(blank_im, reg_im, front_registration)
                if not use_default_back_page:

                    # Load the card back image
                    with Image.open(back_card_image_path) as back_im:
                        draw_card_layout(
                            [back_im] * num_cards,
                            single_sided_back_page,
                            num_rows,
                            num_cols,
                            card_layout.x_pos,
                            card_layout.y_pos,
                            card_layout.width,
                            card_layout.height,
                            max_print_bleed,
                            extend_corners,
                            flip=True
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
                        print(f'Image {num_image}: {file}')
                        num_image = num_image + 1

                        front_image_path = os.path.join(front_dir_path, file)
                        front_card_images.append(Image.open(front_image_path))

                    single_sided_front_page, _ = get_base_images(blank_im, reg_im, front_registration)

                    # Create front layout for single-sided cards
                    draw_card_layout(
                        front_card_images,
                        single_sided_front_page,
                        num_rows,
                        num_cols,
                        card_layout.x_pos,
                        card_layout.y_pos,
                        card_layout.width,
                        card_layout.height,
                        max_print_bleed,
                        extend_corners,
                        flip=False
                    )

                    add_front_back_pages(single_sided_front_page, single_sided_back_page, pages, paper_layout.width, paper_layout.height, card_layout.template, only_fronts)

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
                        print(f'Image {num_image} (double-sided): {file}')
                        num_image = num_image + 1

                        front_image_path = os.path.join(front_dir_path, file)
                        front_card_images.append(Image.open(front_image_path))

                        back_image_path = os.path.join(double_sided_dir_path, file)
                        back_card_images.append(Image.open(back_image_path))

                    double_sided_front_page, double_sided_back_page = get_base_images(blank_im, reg_im, front_registration)

                    # Create front layout for double-sided cards
                    draw_card_layout(
                        front_card_images,
                        double_sided_front_page,
                        num_rows,
                        num_cols,
                        card_layout.x_pos,
                        card_layout.y_pos,
                        card_layout.width,
                        card_layout.height,
                        max_print_bleed,
                        extend_corners,
                        flip=False
                    )

                    # Create back layout for double-sided cards
                    draw_card_layout(
                        back_card_images,
                        double_sided_back_page,
                        num_rows,
                        num_cols,
                        card_layout.x_pos,
                        card_layout.y_pos,
                        card_layout.width,
                        card_layout.height,
                        max_print_bleed,
                        extend_corners,
                        flip=True
                    )

                    # Add the front and back layouts
                    add_front_back_pages(double_sided_front_page, double_sided_back_page, pages, paper_layout.width, paper_layout.height, card_layout.template, False)

                if len(pages) == 0:
                    print('No pages were generated')
                    return

                # Load saved offset if available
                if load_offset:
                    saved_offset = load_saved_offset()

                    if saved_offset is None:
                        print('Offset cannot be applied')
                    else:
                        print(f'Loaded x offset: {saved_offset.x_offset}, y offset: {saved_offset.y_offset}')
                        pages = offset_images(pages, saved_offset.x_offset, saved_offset.y_offset)

                # Save the pages array as a PDF
                pages[0].save(pdf_path, format='PDF', save_all=True, append_images=pages[1:], resolution=300)
                print(f'Generated PDF: {pdf_path}')

class OffsetData(BaseModel):
    x_offset: int
    y_offset: int

def save_offset(x_offset, y_offset) -> None:
    # Create the directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Save the offset data to a JSON file
    with open('data/offset_data.json', 'w') as offset_file:
        offset_file.write(OffsetData(x_offset=x_offset, y_offset=y_offset).model_dump_json(indent=4))

    print('Offset data saved!')

def load_saved_offset() -> OffsetData:
    if os.path.exists('data/offset_data.json'):
        with open('data/offset_data.json', 'r') as offset_file:
            try:
                data = json.load(offset_file)
                return OffsetData(**data)

            except json.JSONDecodeError as e:
                print(f'Cannot decode offset JSON: {e}')

            except ValidationErr as e:
                print(f'Cannot validate offset data: {e}.')

    return None

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

def calculate_max_print_bleed(x_pos: List[int], y_pos: List[int], width: int, height: int) -> int:
    if len(x_pos) == 1 & len(y_pos) == 1:
        return 0

    x_border_max = 100000
    if len(x_pos) >= 2:
        x_pos.sort()

        x_pos_0 = x_pos[0]
        x_pos_1 = x_pos[1]

        x_border_max = math.ceil((x_pos_1 - x_pos_0 - width) / 2)

        if x_border_max < 0:
            x_border_max = 100000

    y_border_max = 100000
    if len(y_pos) >= 2:
        y_pos.sort()

        y_pos_0 = y_pos[0]
        y_pos_1 = y_pos[1]

        y_border_max = math.ceil((y_pos_1 - y_pos_0 - height) / 2)

        if y_border_max < 0:
            y_border_max = 100000

    return min(x_border_max, y_border_max) + 1