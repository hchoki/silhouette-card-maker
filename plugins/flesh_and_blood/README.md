# Flesh and Blood Plugin

This plugin reads a decklist from [Fabrary](https://fabrary.net/) and puts the card images into the proper `game/` directories.

This plugin currently only supports the ``Fabrary`` format.

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
python plugins/flesh_and_blood/fetch.py game/decklist/deck.txt fabrary
```

And finally, you can generate the [PDF files](../../README.md#create_pdfpy) for the deck to print so that you can play at the table!

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {fabrary}

Options:
  --help  Show this message and exit.
```

## Format

### `fabrary`

The format for ``Fabrary``.

```
Name: Sweden National Championship 2025 1st 🇸🇪
Hero: Cindra, Dracai of Retribution
Format: Classic Constructed

Arena cards
1x Blood Splattered Vest
1x Claw of Vynserakai
1x Dragonscaler Flight Path
1x Flick Knives
2x Kunai of Retribution
1x Mask of Momentum
1x Mask of the Pouncing Lynx
1x Tide Flippers

Deck cards
3x Ancestral Empowerment (red)
3x Art of the Dragon: Blood (red)
3x Blaze Headlong (red)
2x Blood Runs Deep (red)
3x Brand with Cinderclaw (red)
2x Breaking Point (red)
3x Cut Through (red)
3x Demonstrate Devotion (red)
3x Display Loyalty (red)
3x Fire Tenet: Strike First (red)
3x Hot on Their Heels (red)
2x Hunt the Hunter (red)
3x Ignite (red)
1x Imperial Seal of Command (red)
2x Lava Burst (red)
2x Oath of Loyalty (red)
3x Rally the Coast Guard (red)
3x Ravenous Rabble (red)
3x Rising Resentment (red)
3x Ronin Renegade (red)
3x Shelter from the Storm (red)
2x Sink Below (red)
2x Snatch (red)
2x Spreading Flames (red)
1x Wrath of Retribution (red)
1x Salt the Wound (yellow)
1x Tenacity (yellow)
2x Concealed Blade (blue)
1x Dragon Power (blue)
3x Throw Dagger (blue)

Made with ❤️ at the FaBrary
See the full deck @ https://fabrary.net/decks/01JZKYA2135MAN58K9VKKR4JYA
```