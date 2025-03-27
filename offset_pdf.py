import os

import click
import pypdfium2 as pdfium

from offset_images import offset_images

# Dimensions of the resized letter-sized sheet
print_width = 3300
print_height = 2550

@click.command()
@click.argument("pdf_path")
@click.option("--output_pdf_path", help="The desired path of the output PDF.")
@click.option("--x_offset", default=0, show_default=True, help="The desired offset in the x-axis.")
@click.option("--y_offset", default=0, show_default=True, help="The desired offset in the y-axis.")

def offset_pdf(pdf_path: str, output_pdf_path: str, x_offset, y_offset):
    pdf = pdfium.PdfDocument(pdf_path)
    
    # Get all the raw page images from the PDF
    raw_images = []
    for page_number in range(len(pdf)):
        page = pdf.get_page(page_number)
        raw_images.append(page.render(scale = 300/72).to_pil().resize((print_width, print_height)))
        
    # Offset images
    final_images = offset_images(raw_images, int(x_offset), int(y_offset))
    
    # The default for output_pdf_path is the original path but with _offset.py appended to the end.
    if output_pdf_path is None:
        output_pdf_path = f'{pdf_path.removesuffix(".py")}_offset.py'
    
    pdf_path = os.path.join(f"{pdf_path}_adjusted.pdf")
    final_images[0].save(pdf_path, save_all=True, append_images=final_images[1:])

if __name__ == '__main__':
    offset_pdf()