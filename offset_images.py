from typing import List
from PIL import Image, ImageChops

# print_mtg = True

# mtg_x_offset = 9
# mtg_y_offset = 12

# Dimensions of the resized letter-sized sheet
print_width = 3300
print_height = 2550

def offset_images(images: List[Image.Image], x_offset: int, y_offset: int) -> List[Image.Image]:
    offset_images = []

    add_offset = False
    for image in images:
        if add_offset:
            # if print_mtg:
            #     offset_images.append(ImageChops.offset(pil_image, x_offset + mtg_x_offset, y_offset + mtg_y_offset))
            # else:
                offset_images.append(ImageChops.offset(image, x_offset, y_offset))
        else:
            offset_images.append(image)
        
        add_offset = not add_offset

    return offset_images