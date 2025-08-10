from re import compile
from enum import Enum
from typing import Callable, Tuple

class PitchOption(str, Enum):
    RED = '1'
    YELLOW = '2'
    BLUE = '3'
    NONE = ''

card_data_tuple = Tuple[str, PitchOption, int] # name, pitch, quantity

def parse_deck_helper(deck_text: str, handle_card: Callable, is_card_line: Callable[[str], bool], extract_card_data: Callable[[str], card_data_tuple]) -> None:
    error_lines = []

    index = 0
    for line in deck_text.strip().split('\n'):
        if is_card_line(line):
            index = index + 1

            name, pitch, quantity = extract_card_data(line)

            print(f'Index: {index}, quantity: {quantity}, name: {name}, pitch: {pitch}')
            try:
                handle_card(index, name, pitch, quantity)
            except Exception as e:
                print(f'Error: {e}')
                error_lines.append((line, e))

        else:
            print(f'Skipping: "{line}"')

    if len(error_lines) > 0:
        print(f'Errors: {error_lines}')

def parse_fabrary(deck_text: str, handle_card: Callable) -> None:
    pattern = compile(r'(\d+)x\s+([^(]+?)(?:\s+\((red|yellow|blue)\))?$') # '{Quantity}x {Card Name} {Pitch?}' where pitch is necessary

    def is_fabrary_line(line) -> bool:
        return bool(pattern.match(line))
    
    def extract_fabrary_card_data(line) -> card_data_tuple:
        match = pattern.match(line)
        if match:
            quantity = int( match.group(1).strip() )
            name = match.group(2).strip()
            pitch_extract = '' if match.group(3) is None else match.group(3).strip()
            if pitch_extract == 'red':
                pitch = PitchOption.RED
            elif pitch_extract == 'yellow':
                pitch = PitchOption.YELLOW
            elif pitch_extract == 'blue':
                pitch = PitchOption.BLUE
            else:
                pitch = PitchOption.NONE

            return (name, pitch, quantity)
        
    parse_deck_helper(deck_text, handle_card, is_fabrary_line, extract_fabrary_card_data)

class DeckFormat(str, Enum):
    FABRARY = 'fabrary'

def parse_deck(deck_text: str, format: DeckFormat, handle_card: Callable) -> None:
    if format == DeckFormat.FABRARY:
        return parse_fabrary(deck_text, handle_card)
    else:
        raise ValueError('Unrecognized deck format.')

if __name__ == '__main__':
    parse_deck()