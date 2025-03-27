import math
import os
import pypdfium2 as pdfium
from PIL import ImageChops, ImageDraw

front_pdf = pdfium.PdfDocument("assets/front_blank.pdf").get_page(0)
back_pdf = pdfium.PdfDocument("assets/back_blank.pdf").get_page(0)

# Dimensions of the resized print sheet
print_width = 3300
print_height = 2550

front_image = front_pdf.render(scale = 300/72).to_pil().resize((print_width, print_height))
back_image = back_pdf.render(scale = 300/72).to_pil().resize((print_width, print_height))

width, height = front_image.size

test_size = 25
test_distance = 75

matrix_size = 19
matrix_half_size = math.floor(matrix_size / 2)

start_x = 0
start_y = 0
if matrix_size % 2 > 0:
    start_x = math.floor(width / 2) - (matrix_half_size * test_distance) - ((matrix_half_size + .5) * test_size)
    start_y = math.floor(height / 2) - (matrix_half_size * test_distance) - ((matrix_half_size + .5) * test_size)
else:
    if matrix_size <= 0:
        raise Exception(f'matrix_size must be greater than 0; received: {matrix_size}')
    start_x = math.floor(width / 2) - ((matrix_half_size - .5) * test_distance) - (matrix_half_size * test_size)
    start_y = math.floor(height / 2) - ((matrix_half_size - .5) * test_distance) - (matrix_half_size * test_size)

front_draw = ImageDraw.Draw(front_image)
back_draw = ImageDraw.Draw(back_image)

for x_index in range(matrix_size):
    for y_index in range(matrix_size):
        offset_x = x_index * (test_distance + test_size)
        offset_y = y_index * (test_distance + test_size)

        front_element_x = start_x + offset_x
        front_element_y = start_y + offset_y
        front_shape = [(front_element_x, front_element_y), (front_element_x + test_size, front_element_y + test_size)]
        
        fill="black"
        if x_index == matrix_half_size or y_index == matrix_half_size:
            fill="blue"

        front_draw.rectangle(front_shape, fill=fill)

        back_element_x = front_element_x + x_index - matrix_half_size
        back_element_y = front_element_y + y_index - matrix_half_size
        back_shape = [(back_element_x, back_element_y), (back_element_x + test_size, back_element_y + test_size)]

        back_draw.rectangle(back_shape, fill=fill)

card_list = [front_image, back_image]
pdf_path = os.path.join(f"calibration.pdf")
card_list[0].save(pdf_path, save_all=True, append_images=card_list[1:])