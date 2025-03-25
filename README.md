# silhouette-card-maker-testing

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

Put your back image in `game/back`, name it `back.jpg`.

Run the script.
```shell
python create_pdf.py
```

Get your PDF at `game/output/card_game.pdf`.

***

The `create_pdf.py` has the following options.

```
Usage: create_pdf.py [OPTIONS]

Options:
  --front_dir_path TEXT           The path to the directory containing the
                                  card front images.  [default: game/front]
  --back_img_path TEXT            The path to the card back image.  [default:
                                  game/back/back.jpg]
  --pdf_path TEXT                 The desired path to the output PDF.
                                  [default: game/output/card_game.pdf]
  --template_type [standard|bridge|poker|poker_half]
                                  The desired path to the output PDF.
                                  [default: standard]
  --front_registration            Enable the front pages of the PDF to have
                                  registration marks.
  --help                          Show this message and exit.
```