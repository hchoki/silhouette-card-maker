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