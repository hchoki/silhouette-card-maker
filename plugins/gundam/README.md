# Gundam Plugin

This plugin reads a decklist from [DeckPlanet](https://www.deckplanet.net/gundam/dashboard) and puts the card images into the proper `game/` directories.

This plugin currently only supports the ``DeckPlanet`` format.

## Instructions

Navigate to the [root directory](../..), as the plugins are not meant to be run in the [plugin directory](.).

Open a terminal on your device in the root directory.

> [!NOTE]
> On Windows, this would be the ``PowerShell`` application, unless you use another terminal of your choice.
>
> On MacOS or Linux, this would be the ``Terminal`` application, unless you use another terminal of your choice.

Create and start your Python virtual environment in the terminal.

> [!NOTE]
> Use the following command to create your Python virtual environment.
> ```bash
> python -m venv venv
> ```
>
> On Windows, use the following command to start your Python virtual environment.
> ```bash
> .\venv\Scripts\Activate.ps1
> ```
>
> On MacOS or Linux, use the following command to start your Python virtual environment.
> ```bash
> . venv/bin/activate
> ```

> [!WARNING]
> If this fails on Windows due to authorization policy issues, then run the following command to get around it.
> ```bash
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
> ```

Then install the Python dependencies in the Python virtual environment using the following command.
```bash
pip install -r requirements.txt  
```

Put your decklist into a text file within the [decklist directory/folder](../../game/decklist).

Now, you are ready to run the program to generate the images for the deck using the following command.
```bash
python plugins/gundam/fetch.py game/decklist/deck.txt deckplanet
```

And finally, you can generate the [PDF files](../../README.md#create_pdfpy) for the deck to print so that you can play at the table!

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {deckplanet}

Options:
  --help  Show this message and exit.
```

## Formats

### `DeckPlanet`

The format for `DeckPlanet`.

```
2 Guntank [GD01-008]
4 Gundam (MA Form) [ST01-002]
4 Demi Trainer [ST01-008]
4 Amuro Ray [ST01-010]
1 Gundam [ST01-001]
2 Kai's Resolve [ST01-013]
1 Suletta Mercury [ST01-011]
4 White Base [ST01-015]
2 Archangel [ST04-015]
2 Aile Strike Gundam [ST04-001]
4 Kira Yamato [ST04-010]
3 Strike Gundam [ST04-002]
2 Guncannon [GD01-004]
2 Darilbalde [GD01-075]
1 Perfect Strike Gundam [GD01-068]
2 Launcher Strike Gundam [GD01-072]
1 Intercept Orders [GD01-099]
2 A Show of Resolve [GD01-100]
2 The Witch and the Bride [GD01-117]
1 Naval Bombardment [GD01-120]
4 Overflowing Affection [GD01-118]
```