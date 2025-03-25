import json
from natsort import natsorted
import os
from PIL import Image, ImageDraw, ImageFont

# -------------------------------------

# User editable parameters

# Acceptable values are:
# 'STANDARD'
# 'BRIDGE'
# 'POKER'
# 'POKER_HALF'
selected_template_type = 'STANDARD'

# -------------------------------------

# Specify directory locations
asset_directory = 'assets'
game_front_directory = os.path.join('game', 'front')
game_back_directory = os.path.join('game', 'back')
output_directory = os.path.join('game', 'output')

# Dimensions of the print sheet
print_width = 3300
print_height = 2550

blank_filename = 'blank_page.jpg'
blank_path = os.path.join(asset_directory, blank_filename)

registration_filename = 'registration_marks.jpg'
registration_path = os.path.join(asset_directory, registration_filename)

back_filename = 'back.jpg'
back_path = os.path.join(game_back_directory, back_filename)

enable_front_registration = False

def image_paste_with_border(image: Image, page: Image, box: tuple[int, int, int, int], thickness: int):
    origin_x, origin_y, origin_width, origin_height = box
    for i in reversed(range(thickness)):
        im_resize = image.resize((origin_width + (2 * i), origin_height + (2 * i)))
        page.paste(im_resize, (origin_x - i, origin_y - i))

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

        # Create a copy of the registration marks to paste the back images onto
        back_page = reg_im.copy()

        # Load the card back image
        with Image.open(back_path) as back_im:
            # Resize the back image to the specified dimensions
            back_im_corr = back_im.resize((selected_template['width'], selected_template['height']))

            # Rotate the back image to account for orientation
            back_im_corr = back_im_corr.rotate(180)

            # Fill all the spaces with the card back
            for i in range(num_cards):
                # Calculate the location of the new card based on what number the card is
                new_origin_x = selected_template['x_pos'][i % num_cards % num_cols]
                new_origin_y = selected_template['y_pos'][(i % num_cards) // num_cols]

                image_paste_with_border(
                    back_im_corr,
                   back_page,
                   (new_origin_x, new_origin_y, selected_template['width'], selected_template['height']),
                   selected_template['border_thickness']
                )

            # Add template version number to the back
            draw = ImageDraw.Draw(back_page)
            font = ImageFont.truetype(os.path.join(asset_directory, 'arial.ttf'), 40)

            # "Raw" specified location
            draw.text((print_width - 561, print_height - 77), selected_template['template'], fill = (0, 0, 0), font = font)


    # Create a copy of the blank template to paste the images onto
    front_page = blank_im.copy()
    if enable_front_registration:
        front_page = reg_im.copy()

    # Create the array that will store the filled templates
    pages = []

    # Create the front pages using the images in game/front directory
    for path, subdirs, files in os.walk(game_front_directory):

        # Sort with natural sort so it's easier to understand the whole PDF
        files[:] = natsorted(files)

        # Iterate through all the files in the game/front directory
        n = 0
        for name in files:            
            if name.endswith(".md"):
                print(f"skipping {name}")
                continue
            
            print(f"image {n + 1}: {name}")

            # If the template is full, add to pages and restart
            if n and not (n % num_cards):

                # Add a back page for every front page template
                pages.append(front_page)
                pages.append(back_page)

                # Create a blank copy for the next page
                front_page = blank_im.copy()

            # Load the image to process it
            front_path = os.path.join(path, name)
            with Image.open(front_path) as front_im:

                # Resize the front images to the specified dimension
                front_im_corr = front_im.resize((selected_template['width'], selected_template['height']))

                # Calculate the location of the new card based on what number the card is
                new_origin_x = selected_template['x_pos'][n % num_cards % num_cols]
                new_origin_y = selected_template['y_pos'][(n % num_cards) // num_cols]
                
                image_paste_with_border(
                    front_im_corr,
                    front_page,
                    (new_origin_x, new_origin_y, selected_template['width'], selected_template['height']),
                    selected_template['border_thickness']
                )
                
            n += 1


    # Export the final front page template (filled or not) with a back page
    pages.append(front_page)
    pages.append(back_page)

    # Save the pages array as a PDF
    pdf_path = os.path.join(output_directory, 'card_game.pdf')
    print(f'generated PDF: {pdf_path}')
    pages[0].save(pdf_path, format = 'PDF', save_all = True, append_images = pages[1:])