# silhouette-card-maker-testing


## create_pdf.py
`create_pdf.py` is a CLI tool that layouts your card images into a printable PDF. Then, you can cut out the cards with the appropriate cutting template in `cutting_templates/`.

### Basic Instructions:

Create a Python virtual environment.
```shell
python -m venv venv
```

Activate the Python virtual environment.
```shell
. venv/bin/activate
```

Download Python packages.
```shell
pip install -r requirements.txt
```

Put your front images in `game/front`.

Put your back image in `game/back`.

Run the script.
```shell
python create_pdf.py
```

Get your PDF at `game/output/game.pdf`.

### Double-sided cards

To create double sided cards, put front images in `game/front` and back images in `game/double_sided`. The filenames must match for each pair.

### CLI options

```
Usage: create_pdf.py [OPTIONS]

Options:
  --front_dir_path TEXT           The path to the directory containing the
                                  card fronts.  [default: game/front]
  --back_dir_path TEXT            The path to the directory containing one or
                                  no card backs.  [default: game/back]
  --double_sided_dir_path TEXT    The path to the directory containing card
                                  backs for double-sided cards.  [default:
                                  game/double_sided]
  --output_pdf_path TEXT          The desired path to the output PDF.
                                  [default: game/output/game.pdf]
  --template_type [standard|bridge|poker|poker_half]
                                  The desired card size.  [default: standard]
  --front_registration            Enable the front pages to have Print & Play
                                  (registration marks).
  --only_fronts                   Only use the card fronts, exclude the card
                                  backs.
  --help                          Show this message and exit.
```

## offset_pdf.py

It's pivatol to ensure that your the fronts and backs are aligned. However, it's not always possible to calibrate a printer.

`offset_pdf.py` is a CLI tool that adds an offset to every other page in a PDF, i.e. all the back pages. This offset can compensate for the natural offset from your printer.

### Basic Instructions

First, you must determine the offset by using `assets/calibration.pdf`.

`calibration.pdf` has a front page and a back page.

The front page is a simple grid of squares.

The back page is the same grid of squares, except each square has a slight offset. The following grid illustrates the applied offsets.

```
| (-2, -2) | (-1, -2) | ( 0, -2) | ( 1, -2) | ( 2, -2) |
--------------------------------------------------------
| (-2, -1) | (-1, -1) | ( 0, -1) | ( 1, -1) | ( 2, -1) |
--------------------------------------------------------
| (-2,  0) | (-1,  0) |  Center  | ( 1,  0) | ( 2,  0) |
--------------------------------------------------------
| (-2,  1) | (-1,  1) | ( 0,  1) | ( 1,  1) | ( 2,  1) |
--------------------------------------------------------
| (-2,  2) | (-1,  2) | ( 0,  2) | ( 1,  2) | ( 2,  2) |
```

To figure out the required offset, print out `calibration.pdf` with the card stock you plan to use.

Shine a strong light on the front so you can see the shadows on the back. Determine the square such that the front square and the back square are aligned with each other. This square will provide your offset. Now, you can use `offset_pdf.py` to apply the appropriate offset to your PDF.

If you have not already created and activated your virtual Python environment and installed the dependencies, please do so.

Run the script.
```shell
python offset_pdf.py game.pdf --x_offset -5 --y_offset 10
```

Get your offset PDF at `game/output/game_offset.pdf`.

### CLI options

```
Usage: offset_pdf.py [OPTIONS]

Options:
  --pdf_path TEXT         The path of the input PDF.
  --output_pdf_path TEXT  The desired path of the offset PDF.
  -x, --x_offset INTEGER  The desired offset in the x-axis.
  -y, --y_offset INTEGER  The desired offset in the y-axis.
  --help                  Show this message and exit.
```