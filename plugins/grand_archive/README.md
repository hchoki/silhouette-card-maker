# Grand Archive Plugin

This plugin reads a decklist, fetches the card image from the [Grand Archive website](https://gatcg.com), and puts the card images into the proper `game/` directories.

This plugin currently supports the ``Cockatrice/Omnidex`` format.

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
python plugins/grand_archive/fetch.py game/decklist/deck.txt cockatrice
```

And finally, you can generate the [PDF files](../../README.md#create_pdfpy) for the deck to print so that you can play at the table!

## CLI Options

```
Usage: fetch.py [OPTIONS] DECK_PATH {cockatrice}

Options:
  --help  Show this message and exit.
```

## Formats

### `cockatrice`

The format for ``Cockatrice/Omnidex``.

```
# Main Deck
3 Incapacitate
4 Sable Remnant
4 Slice and Dice
2 Aesan Protector
3 Blackmarket Broker
4 Dream Fairy
4 Fairy Whispers
4 Galewhisper Rogue
4 Reclaim
4 Shimmercloak Assassin
3 Stifling Trap
4 Surveil the Winds
3 Tempest Downfall
3 Veiling Breeze
4 Winbless Lookout
4 Windmill Engineer
3 Zephyr

# Material Deck
1 Spirit of Wind
1 Tristan, Underhanded
1 Tristan, Hired Blade
1 Assassin's Ripper
1 Bauble of Abundance
1 Blinding Orb
1 Curved Dagger
1 Poisoned Coating Oil
1 Poisoned Dagger
1 Smoke Bombs
1 Tariff Ring
1 Windwalker Boots
```