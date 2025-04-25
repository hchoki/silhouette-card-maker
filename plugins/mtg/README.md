# MTG Plugin

This plugin reads a decklist and automatically fetches the card art and puts in the proper `game/` directories.

## Features

This plugin can support many different decklist formats such as, `simple`, `mtga`, `mtgo`, `archidekt`, `deckstats`, and `moxfield`.

`simple`: A list of card names.
```
# Isshin, Two Heavens as One
# Arid Mesa
# Battlefield Forge
# Blazemire Verge
# Blightstep Pathway
```

`mtga`: Magic: The Gathering Arena format.
```
# About
# Name Death & Taxes

# Companion
# 1 Yorion, Sky Nomad

# Deck
# 2 Arid Mesa
# 1 Lion Sash
# 1 Loran of the Third Path
# 2 Witch Enchanter
```

`mtgo`: Magic: The Gathering Online format.
```
# 1 Ainok Bond-Kin
# 1 Angel of Condemnation
# 2 Witch Enchanter

# SIDEBOARD:
# 1 Containment Priest
# 3 Deafening Silence
```

`archidekt`: Archidekt format.
```
# 1x Agadeem's Awakening // Agadeem, the Undercrypt (znr) 90 [Resilience,Land]
# 1x Ancient Cornucopia (big) 16 [Maybeboard{noDeck}{noPrice},Mana Advantage]
# 1x Arachnogenesis (cmm) 647 [Maybeboard{noDeck}{noPrice},Mass Disruption]
# 1x Ashnod's Altar (ema) 218 *F* [Mana Advantage]
# 1x Assassin's Trophy (sld) 139 [Targeted Disruption]
```

`deckstats`: Deckstats format.
```
# //Main
# 1 [2XM#310] Ash Barrens
# 1 Blinkmoth Nexus
# 1 Bloodstained Mire

# //Sideboard
# 1 [2XM#315] Darksteel Citadel

# //Maybeboard
# 1 [MID#159] Smoldering Egg // Ashmouth Dragon
```

`moxfield`: Moxfield format.
```
# 1 Ainok Bond-Kin (2X2) 5
# 1 Pegasus Guardian // Rescue the Foal (CLB) 36
# 2 Witch Enchanter // Witch-Blessed Meadow (MH3) 239

# SIDEBOARD:
# 1 Containment Priest (M21) 13
# 1 Deafening Silence (MB2) 9
```

## Basic instructions

Navigate to the root directory. This plugin is not meant to be run in `plugins\mtg\`.

Create and start your virtual Python environment and install Python dependencies if you have not done so already. See [here](../../README.md#basic-instructions) for more information.

Put your decklist into a text file. In this example, the decklist format is `simple` and the filename is  `deck.txt`.

Run the plugin.

```shell
python plugins/mtg/fetch.py deck.txt simple
```