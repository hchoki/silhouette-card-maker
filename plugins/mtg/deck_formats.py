import re

from enum import Enum
from typing import Optional

# def parse_deck_helper(deck_text, pattern: re.Pattern, extract_regex_matches, handle_card):
def parse_deck_helper(deck_text, is_card_line, extract_card_data, handle_card):
    error_lines = []

    index = 0
    for line in deck_text.strip().split('\n'):
        if is_card_line(line):
            index = index + 1

            name, set_code, collector_number, quantity = extract_card_data(line)

            print(f'Index: {index}, quantity: {quantity}, name: {name}, set code: {set_code}, collector number: {collector_number}')
            try:
                handle_card(index, name, set_code, collector_number, quantity)
            except Exception as e:
                print(f'Error: {e}')
                error_lines.append((line, e))

        else:
            print(f'Skipping: "{line}"')

    if len(error_lines) > 0:
        print(f'Errors: {error_lines}')

# Isshin, Two Heavens as One
# Arid Mesa
# Battlefield Forge
# Blazemire Verge
# Blightstep Pathway
# Blood Crypt
def parse_simple_list(deck_text, handle_card):
    # for line in deck_text.strip().split('\n'):
    #     name = line.strip()
    #     if name:
    #         handle_card(0, name)

    def is_simple_card_line(line):
        return line.strip()

    def extract_simple_card_data(line):
        return (line.strip(), "", "", 1)

    parse_deck_helper(deck_text, is_simple_card_line, extract_simple_card_data, handle_card)


# About
# Name Musashi's Mosh Pit [Primer]

# Commander
# 1x Isshin, Two Heavens as One (NEO) 488

# Deck
# 1x Arid Mesa (MH2) 244
# 1x Battlefield Forge (ORI) 244
# 1x Blazemire Verge (DSK) 256
# 1x Blightstep Pathway (KHM) 291
# 1x Blood Crypt (RNA) 245
def parse_mtga(deck_text, handle_card):
    pattern = re.compile(r'(\d+)x?\s+(.+?)\s+\((\w+)\)\s+(\d+)', re.IGNORECASE)
    fallback_pattern = re.compile(r'(\d+)x?\s+(.+)')

    # for line in deck_text.strip().splitlines():
    #     line = line.strip()
    #     if not line:
    #         continue

    #     match = pattern.match(line)
    #     if match:
    #         quantity = int(match.group(1))
    #         name = match.group(2).strip()
    #         set_code = match.group(3).strip()
    #         collector_number = match.group(4).strip()
    #         handle_card(0, name, set_code, collector_number, quantity)
    #     else:
    #         # Handle simpler "1x Mountain" lines
    #         fallback_match = fallback_pattern.match(line)
    #         if fallback_match:
    #             quantity = int(fallback_match.group(1))
    #             name = fallback_match.group(2).strip()
    #             handle_card(0, name)

    def is_mtga_card_line(line):
        return pattern.match(line) or fallback_pattern.match(line)

    def extract_mtga_card_data(line):
        match = pattern.match(line)
        if match:
            quantity = int(match.group(1))
            name = match.group(2).strip()
            set_code = match.group(3).strip()
            collector_number = match.group(4).strip()

            return (name, set_code, collector_number, quantity)
        else:
            # Handle simpler "1x Mountain" lines
            fallback_match = fallback_pattern.match(line)
            quantity = int(fallback_match.group(1))
            name = fallback_match.group(2).strip()

            return (name, "", "", quantity)

    parse_deck_helper(deck_text, is_mtga_card_line, extract_mtga_card_data, handle_card)

# 1 Abzan Battle Priest
# 1 Abzan Falconer
# 1 Aerial Surveyor
# 1 Ainok Bond-Kin
# 1 Angel of Condemnation
def parse_mtgo(deck_text, handle_card):
    # for line in deck_text.strip().split('\n'):
    #     line = line.strip()
    #     if not line or not line[0].isdigit():
    #         continue
    #     parts = line.split(' ', 1)
    #     if len(parts) == 2:
    #         quantity = int(parts[0])
    #         name = parts[1].strip()
    #         handle_card(0, name)

    def is_mtgo_card_line(line):
        line = line.strip()
        return line and line[0].isdigit()

    def extract_mtgo_card_data(line):
        parts = line.split(' ', 1)
        quantity = int(parts[0])
        name = parts[1].strip()
        return (name, "", "", quantity)

    parse_deck_helper(deck_text, is_mtgo_card_line, extract_mtgo_card_data, handle_card)





# def extract_archidekt_regex_matches(line: str):
#     quantity = int(match.group(1))
#     name = match.group(2).strip()
#     set_code = match.group(3).strip()
#     collector_number = match.group(4).strip()

#     return (name, set_code, collector_number, quantity)

# 1x Agadeem's Awakening // Agadeem, the Undercrypt (znr) 90 [Resilience,Land]
# 1x Ancient Cornucopia (big) 16 [Maybeboard{noDeck}{noPrice},Mana Advantage]
# 1x Arachnogenesis (cmm) 647 [Maybeboard{noDeck}{noPrice},Mass Disruption]
# 1x Ashnod's Altar (ema) 218 *F* [Mana Advantage]
# 1x Assassin's Trophy (sld) 139 [Targeted Disruption]
def parse_archidekt(deck_text, handle_card):
    pattern = re.compile(r'^(\d+)x?\s+(.+?)\s+\((\w+)\)\s+(\d+).*')
    def is_archidekt_card_line(line: str):
        return pattern.match(line)
    
    def extract_archidekt_card_data(line: str):
        match = pattern.match(line)
        quantity = int(match.group(1))
        name = match.group(2).strip()
        set_code = match.group(3).strip()
        collector_number = match.group(4).strip()

        return (name, set_code, collector_number, quantity)

    # for line in deck_text.strip().split('\n'):
    #     if not line.strip():
    #         continue
    #     match = pattern.match(line)
    #     if match:
    #         quantity = int(match.group(1))
    #         name = match.group(2).strip()
    #         set_code = match.group(3).strip()
    #         collector_number = match.group(4).strip()
    #         handle_card(0, name, set_code, collector_number, quantity)
    parse_deck_helper(deck_text, is_archidekt_card_line, extract_archidekt_card_data, handle_card)



# //Main
# 1 [2XM#310] Ash Barrens
# 1 Blinkmoth Nexus
# 1 Bloodstained Mire
# 1 Buried Ruin
# 1 Command Beacon
def parse_deckstats(deck_text, handle_card):
    # pattern = re.compile(r'^\d+\s+(?:\[(.*?)#(\w+)\]\s+)?(.+)$')
    pattern = re.compile(r'^(\d+)\s+(?:\[(\w+)?#(\w+)\]\s+)?(.+)$')
    def is_deckstats_card_line(line: str):
        return pattern.match(line)

    def extract_deckstats_card_data(line: str):
        match = pattern.match(line)
        quantity = int(match.group(1))
        set_code = match.group(2) or ""
        collector_number = match.group(3) or ""
        name = match.group(4).strip()

        return (name, set_code, collector_number, quantity)

    # for line in deck_text.strip().split('\n'):
    #     if line.startswith('//') or not line.strip():
    #         continue
    #     match = pattern.match(line)
    #     if match:
    #         set_code = match.group(1)
    #         collector_number = match.group(2)
    #         name = match.group(3).strip()
    #         quantity = int(line.split()[0])
    #         handle_card(0, name, set_code, collector_number, quantity)
    parse_deck_helper(deck_text, is_deckstats_card_line, extract_deckstats_card_data, handle_card)



# 1 Lulu, Loyal Hollyphant (CLB) 477 *E*
# 1 Abzan Battle Priest (IMA) 2
# 1 Abzan Falconer (ZNC) 9
# 1 Aerial Surveyor (NEC) 5
# 1 Ainok Bond-Kin (2X2) 5
# 1 Pegasus Guardian // Rescue the Foal (CLB) 36
# 4 Plains (MOM) 277
# 2 Witch Enchanter // Witch-Blessed Meadow (MH3) 239

# SIDEBOARD:
# 1 Containment Priest (M21) 13
# 1 Deafening Silence (MB2) 9
# 1 Disruptor Flute (MH3) 209
def parse_moxfield(deck_text, handle_card):
    pattern = re.compile(r'^(\d+)\s+(.+?)\s+\((\w+)\)\s+([\w\-]+)')
    def is_moxfield_card_line(line: str):
        return pattern.match(line)

    def extract_moxfield_card_data(line: str):
        match = pattern.match(line)
        quantity = int(match.group(1))
        name = match.group(2).strip()
        set_code = match.group(3).strip()
        collector_number = match.group(4).strip()

        return (name, set_code, collector_number, quantity)
    # for line in deck_text.strip().split('\n'):
    #     match = pattern.match(line)
    #     if match:
    #         quantity = int(match.group(1))
    #         name = match.group(2).strip()
    #         set_code = match.group(3).strip()
    #         collector_number = match.group(4).strip()
    #         handle_card(0, name, set_code, collector_number, quantity)

    parse_deck_helper(deck_text, is_moxfield_card_line, extract_moxfield_card_data, handle_card)




# moxfield_pattern = re.compile(r'^(\d+)\s+(.+?)\s+\((\w+)\)\s+([\w\-]+)')
# def match_moxfield(deck_line: str):
#     match = pattern.match(line)
#     quantity = int(match.group(1))
#     name = match.group(2).strip()
#     set_code = match.group(3).strip()
#     collector_number = match.group(4).strip()


# def detect_format(deck_text):
#     lines = deck_text.strip().splitlines()

#     if any('Deck' in line for line in lines) and any('About' in line for line in lines):
#         return 'mtga'
#     elif all(re.match(r'^\d+\s+.+', line) for line in lines if line.strip() and not line.startswith('//')):
#         if any('[' in line and '#' in line for line in lines):
#             return 'deckstats'
#         elif any('x' in line or '*' in line or '[' in line for line in lines):
#             return 'archidekt'
#         elif any('(' in line and ')' in line for line in lines):
#             return 'moxfield'
#         else:
#             return 'mtgo'
#     elif all(line.strip() for line in lines if not line.startswith('//')):
#         return 'simple'
#     return 'unknown'

class DeckFormat(str, Enum):
    SIMPLE = "simple"
    MTGA = "mtga"
    MTGO = "mtgo"
    ARCHIDEKT = "archidekt"
    DECKSTATS = "deckstats"
    MOXFIELD = "moxfield"

def parse_deck(deck_text: str, format: DeckFormat, handle_card):
    # format_type = detect_format(deck_text)
    if format == DeckFormat.SIMPLE:
        parse_simple_list(deck_text, handle_card)
    elif format == DeckFormat.MTGA:
        parse_mtga(deck_text, handle_card)
    elif format == DeckFormat.MTGO:
        parse_mtgo(deck_text, handle_card)
    elif format == DeckFormat.ARCHIDEKT:
        parse_archidekt(deck_text, handle_card)
    elif format == DeckFormat.DECKSTATS:
        parse_deckstats(deck_text, handle_card)
    elif format == DeckFormat.MOXFIELD:
        parse_moxfield(deck_text, handle_card)
    else:
        raise ValueError("Unrecognized deck format")