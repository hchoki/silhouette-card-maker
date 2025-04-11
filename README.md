# Custom Card Games with the Cameo Cutting Machine

![](images/display.jpg)

Ever wanted to make your own custom card game but without the hassle of a craft knife, a rotary cutter, or a paper guillotine? How about making your own proxies to playtest your favorite TCG?

You can do it all with the press of a button and a cutting machine! And I can show you how!

If this is your first time here, check out the [tutorial](tutorial.md)! We also have a [Discord server](https://discord.gg/jhsKmAgbXc) too!

## Purpose

The purpose of this repo is to enable you to use a Silhouette cutting machine to create card games and proxies. Proxies are only intended to be used for casual play and playtesting. You may not use this repo to disguise fake cards to decieve people or to play in sanctioned tournaments. You are only permitted to sell cards made this way if you are the full privileged copyright holder.

## Contents

* [tutorial.md](tutorial.md), an in-depth tutorial
* [cutting_templates/](cutting_templates/), a directory containing Silhoutte Studio cutting templates
* [examples/](examples/), a directory containing sample games
* [create_pdf.py](#create_pdfpy), a script for laying out your cards in a PDF
* [offset_pdy.py](#offset_pdfpy), a script for adding an offset to your PDF

## Cutting Templates

This project supports the following card and paper sizes, with more in the future:

| Paper size | `standard`* | `japanese`** | `poker` | `poker_half` | `bridge` |
| ---------- | ----------- | ------------ | ------- | ------------ | -------- |
| Letter     | ✅         | ✅           | ✅     |  ✅          | ✅      |
| A4         | ✅         | ✅           | ✅     |  ✅          | ✅      |

Card size measurements:

| Card size    | Inches       | Millimeters   |
| ------------ | ------------ | ------------- |
| `standard`*  | 2.48 x 3.46  | 63 x 88       |
| `japanese`** | 2.32 x 3.39  | 59 x 86       |
| `poker`      | 2.5 x 3.5    | 63.5 x 88.9   |
| `poker_half` | 1.75 x 2.45  | 44.45 x 62.23 |
| `bridge`     | 2.25 x 3.5   | 57.15 x 88.9  |

\* including: Magic the Gathering, Pokémon, Lorcana, One Piece, Digimon, Star Wars: Unlimited, and Flesh and Blood.

** including: Yu-Gi-Oh!.

You can find all the cutting templates for Silhouette Studio in [`cutting_templates/`](cutting_templates/).

## create_pdf.py
`create_pdf.py` is a CLI tool that layouts your card images into a printable PDF. Then, you can cut out the cards with the appropriate cutting template in [`cutting_templates/`](cutting_templates/).

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

### Double-Sided Cards

To create double-sided cards, put front images in `game/front` and back images in `game/double_sided`. The filenames must match for each pair.

### White Corners

If your card images have rounded corners, they may be missing print bleed in the PDF. You may have seen white Xs appear in your PDF; these are artifacts from rounded corners. Because of the missing print bleed, when these cards are cut, they may have a sliver of white on the corners.

![Extend corners](images/extend_corners.jpg)

The `--extend_corners` option can ameliorate this issue. You may need to experiment with the value but I recommend starting with `10`

```shell
python create_pdf.py --extend_corners 10
```

### CLI Options

```
Usage: create_pdf.py [OPTIONS]

Options:
  --front_dir_path TEXT           The path to the directory containing the
                                  card fronts.  [default: game/front]
  --back_dir_path TEXT            The path to the directory containing one
                                  or no card backs.  [default: game/back]
  --double_sided_dir_path TEXT    The path to the directory containing card
                                  backs for double-sided cards.  [default:
                                  game/double_sided]
  --output_pdf_path TEXT          The desired path to the output PDF.
                                  [default: game/output/game.pdf]
  --card_size [standard|japanese|poker|poker_half|bridge]
                                  The desired card size.  [default:
                                  standard]
  --paper_size [letter|a4]        The desired paper size.  [default: letter]
  --front_registration            Enable the front pages to have Print &
                                  Play (registration marks).
  --only_fronts                   Only use the card fronts, exclude the card
                                  backs.
  --extend_corners INTEGER RANGE  Reduce artifacts produced by rounded
                                  corners in card images.  [default: 0;
                                  x>=0]
  --help                          Show this message and exit.
```

## offset_pdf.py

It's pivotal to ensure that your the fronts and backs are aligned. However, it's not always possible to calibrate a printer.

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

### CLI Options

```
Usage: offset_pdf.py [OPTIONS]

Options:
  --pdf_path TEXT         The path of the input PDF.
  --output_pdf_path TEXT  The desired path of the offset PDF.
  -x, --x_offset INTEGER  The desired offset in the x-axis.
  -y, --y_offset INTEGER  The desired offset in the y-axis.
  --help                  Show this message and exit.
```