from re import compile
from enum import Enum
from _collections_abc import Set
from typing import Callable, Tuple
from ast import literal_eval

card_data_tuple = Tuple[str, str, int] # Name, Card Number, Quantity

def parse_deck_helper(
        deck_text: str,
        handle_card: Callable,
        deck_splitter: Callable[[str], Set[str]],
        is_card_line: Callable[[str], bool],
        extract_card_data: Callable[[str], card_data_tuple],
    ) -> None:
    error_lines = []

    index = 0

    for line in deck_splitter(deck_text):
        if is_card_line(line):
            index = index + 1

            name, card_number, quantity = extract_card_data(line)

            print(f'Index: {index}, quantity: {quantity}, card number: {card_number}, name: {name}')
            try:
                handle_card(index, card_number, quantity)
            except Exception as e:
                print(f'Error: {e}')
                error_lines.append((line, e))
        else:
            print(f'Skipping: "{line}"')

    if len(error_lines) > 0:
        print(f'Errors: {error_lines}')

def parse_tts(deck_text: str, handle_card: Callable):
    pattern = compile(r'^([a-zA-Z0-9]+-\d+)$') # '{Card Number}'

    def is_tts_line(line) -> bool:
        return bool(pattern.match(line))

    def extract_tts_card_data(line) -> card_data_tuple:
        match = pattern.match(line)
        if match:
            card_number = f'{ match.group(1).strip() }'

            return ('', card_number, 1)

    def split_tts_deck(deck_text: str) -> Set[str]:
        return literal_eval(deck_text.strip())

    parse_deck_helper(deck_text, handle_card, split_tts_deck, is_tts_line, extract_tts_card_data)

def parse_digimoncardio(deck_text: str, handle_card: Callable):
    pattern = compile(r'^(\d+)\s+(.+?)\s+([A-Z0-9]+-\d+)\s*$') # '{Quantity} {Name} {Card Number}'

    def is_digimoncardio_line(line) -> bool:
        return bool(pattern.match(line))

    def extract_digimoncardio_card_data(line) -> card_data_tuple:
        match = pattern.match(line)
        if match:
            quantity = int(match.group(1))
            name = match.group(2).strip()
            card_number = match.group(3).strip()

            return (name, card_number, quantity)

    def split_digimoncardio_deck(deck_text: str) -> Set[str]:
        return deck_text.strip().split('\n')

    parse_deck_helper(deck_text, handle_card, split_digimoncardio_deck, is_digimoncardio_line, extract_digimoncardio_card_data)

def parse_digimoncardapp(deck_text: str, handle_card: Callable):
    pattern = compile(r'^([A-Z0-9]+-\d+)\s+(.+?)\s+(\d+)\s*$') # '{Card Number} {Name} {Quantity}'

    def is_digimoncardapp_line(line) -> bool:
        return bool(pattern.match(line))

    def extract_digimoncardapp_card_data(line) -> card_data_tuple:
        match = pattern.match(line)
        if match:
            card_number = match.group(1).strip()
            name = match.group(2).strip()
            quantity = int(match.group(3))

            return (name, card_number, quantity)

    def split_digimoncardapp_deck(deck_text: str) -> Set[str]:
        return deck_text.strip().split('\n')

    parse_deck_helper(deck_text, handle_card, split_digimoncardapp_deck, is_digimoncardapp_line, extract_digimoncardapp_card_data)

def parse_digimonmeta(deck_text: str, handle_card: Callable):
    pattern = compile(r'^(\d+) \(([a-zA-Z0-9]+-\d+)\)$') # '{Quantity} ({Card Number})'

    def is_digimonmeta_line(line) -> bool:
        return bool(pattern.match(line))

    def extract_digimonmeta_card_data(line) -> card_data_tuple:
        match = pattern.match(line)
        if match:
            quantity = int(match.group(1))
            card_number = match.group(2).strip()

            return ('', card_number, quantity)

    def split_digimonmeta_deck(deck_text: str) -> Set[str]:
        return deck_text.strip().split('\n')

    parse_deck_helper(deck_text, handle_card, split_digimonmeta_deck, is_digimonmeta_line, extract_digimonmeta_card_data)

def parse_untap(deck_text: str, handle_card: Callable):
    # '{Quantity} {Name} (DCG) ({Card Number})'
    # '{Quantity} {Name} [DCG] ({Card Number})'
    pattern = compile(r'^(\d+)\s+(.+?)\s+(?:\(DCG\)|\[DCG\])\s+\(([A-Z0-9]+-\d+)\)\s*$')

    def is_untap_line(line) -> bool:
        return bool(pattern.match(line))

    def extract_untap_card_data(line) -> card_data_tuple:
        match = pattern.match(line)
        if match:
            quantity = int(match.group(1))
            name = match.group(2).strip()
            card_number = match.group(3).strip()

            return (name, card_number, quantity)

    def split_untap_deck(deck_text: str) -> Set[str]:
        return deck_text.strip().split('\n')

    parse_deck_helper(deck_text, handle_card, split_untap_deck, is_untap_line, extract_untap_card_data)

class DeckFormat(str, Enum):
    TTS         = 'tts'
    DIGIMONCARDIO = 'digimoncardio'
    DIGIMONCARDDEV = 'digimoncarddev'
    DIGIMONCARDAPP = 'digimoncardapp'
    DIGIMONMETA = 'digimonmeta'
    UNTAP       = 'untap'

def parse_deck(deck_text: str, format: DeckFormat, handle_card: Callable):
    if format == DeckFormat.TTS:
        parse_tts(deck_text, handle_card)
    elif format == DeckFormat.DIGIMONCARDIO:
        parse_digimoncardio(deck_text, handle_card)
    elif format == DeckFormat.DIGIMONCARDDEV:
        parse_digimoncardio(deck_text, handle_card) # same format as DIGIMONCARDIO
    elif format == DeckFormat.DIGIMONCARDAPP:
        parse_digimoncardapp(deck_text, handle_card)
    elif format == DeckFormat.DIGIMONMETA:
        parse_digimonmeta(deck_text, handle_card)
    elif format == DeckFormat.UNTAP:
        parse_untap(deck_text, handle_card)
    else:
        raise ValueError('Unrecognized deck format.')

if __name__ == '__main__':
    parse_deck()