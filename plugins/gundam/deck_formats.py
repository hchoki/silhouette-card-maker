from re import compile
from enum import Enum
from typing import Callable, Tuple

card_data_tuple = Tuple[str, int] # Card Number, Quantity

def parse_deck_helper(deck_text: str, handle_card: Callable, is_card_line: Callable[[str], bool], extract_card_data: Callable[[str], card_data_tuple]) -> None:
    error_lines = []

    index = 0
    for line in deck_text.strip().split('\n'):
        if is_card_line(line):
            index = index + 1

            card_number, quantity = extract_card_data(line)

            print(f'Index: {index}, quantity: {quantity}, card number: {card_number}')
            try:
                handle_card(index, card_number, quantity)
            except Exception as e:
                print(f'Error: {e}')
                error_lines.append((line, e))

        else:
            print(f'Skipping: "{line}"')

    if len(error_lines) > 0:
        print(f'Errors: {error_lines}')

def parse_deckplanet(deck_text: str, handle_card: Callable) -> None:
    pattern = compile(r'^(\d+)\s+.+\s+\[(.+)\]$') # '{Quantity} {Name} [{Card Number}]'

    def is_deckplanet_line(line) -> bool:
        return bool(pattern.match(line))
    
    def extract_deckplanet_card_data(line) -> card_data_tuple:
        match = pattern.match(line)
        if match:
            card_number = match.group(2).strip()
            quantity = int( match.group(1).strip() )

            return (card_number, quantity)
        
    parse_deck_helper(deck_text, handle_card, is_deckplanet_line, extract_deckplanet_card_data)

class DeckFormat(str, Enum):
    DECKPLANET = 'deckplanet'

def parse_deck(deck_text: str, format: DeckFormat, handle_card: Callable) -> None:
    if format == DeckFormat.DECKPLANET:
        return parse_deckplanet(deck_text, handle_card)
    else:
        raise ValueError('Unrecognized deck format.')

if __name__ == '__main__':
    parse_deck()