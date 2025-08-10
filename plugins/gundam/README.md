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

### `deckplanet`

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

### `limitless`

The format for `Limitless TCG`.

```
4 Dopp GD01-039
4 Zaku Ⅰ ST03-007
1 Pisces GD01-021
4 Zaku Ⅱ ST03-008
4 Zaku Ⅱ GD01-035
3 Guntank GD01-008
4 Char's Zaku Ⅱ ST03-006
4 Char's Zaku Ⅱ GD01-026
2 G-Fighter GD01-009
2 Gouf ST03-009
4 Char's Gelgoog GD01-023
3 Gundam ST01-001

4 Char Aznable ST03-011
4 Amuro Ray ST01-010


3 Falmel ST03-016
```

### `egman`

The format for `Egman Events`.

```
4 GD01-039 Dopp
4 ST03-007 Zaku I | MS-05
4 GD01-035 Zaku II | MS-06
4 ST03-006 Char's Zaku II | MS-06S
4 GD01-026 Char's Zaku II | MS-065
4 ST03-008 Zaku II | MS-06
1 GD01-021 Pisces | OZ-09MMS
3 GD01-008 Guntank | RX-75
2 GD01-009 G-Fighter
2 ST03-009 Gouf | MS-078
4 GD01-023 Char's Gelgoog | MS-14S
3 ST01-001 Gundam | RX-78-2
4 ST03-011 Char Aznable
4 ST01-010 Amuro Ray
3 ST03-016 Falmel
```

### `exburst`

The format for `ExBurst`.

```
4 x ST04-008
4 x ST01-005
4 x GD01-059
4 x GD01-018
4 x ST01-001
3 x GD01-044
3 x GD01-003
2 x GD01-047
4 x ST01-010
4 x GD01-093
3 x ST04-016
1 x ST01-015
2 x GD01-112
2 x GD01-111
2 x ST03-013
4 x GD01-100

```