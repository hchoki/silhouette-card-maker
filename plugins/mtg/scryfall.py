import csv
import os
from typing import List
import pandas as pd
import re
import requests
import time

double_sided_layouts = ['transform', 'modal_dfc']

def request_scryfall(
    query: str,
):
    r = requests.get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})
    
    # Check for 2XX response code
    r.raise_for_status()

    # Sleep for 150 milliseconds, greater than the 100ms requested by scryfall API documentation
    time.sleep(0.15)

    return r

def fetch_card_art(
    index: int,
    quantity: int,

    clean_card_name: str,
    card_set: int,
    card_collector_number: int,
    layout: str,

    front_img_dir: str,
    double_sided_dir: str
):
    # Query for the front side
    card_front_image_query = f'https://api.scryfall.com/cards/{card_set}/{card_collector_number}/?format=image&version=large'
    card_art = request_scryfall(card_front_image_query).content
    if card_art is not None:

        # Save image based on quantity
        for counter in range(quantity):
            image_path = os.path.join(front_img_dir, f'{str(index)}{clean_card_name}{str(counter)}.jpg')

            with open(image_path, 'wb') as f:
                f.write(card_art)

    # Get backside of card, if it exists
    if layout in double_sided_layouts:
        card_back_image_query = f'{card_front_image_query}&face=back'
        card_art = request_scryfall(card_back_image_query).content
        if card_art is not None:

            # Save image based on quantity
            for counter in range(quantity):
                image_path = os.path.join(double_sided_dir, f'{str(index)}{clean_card_name}{str(counter)}.jpg')

                with open(image_path, 'wb') as f:
                    f.write(card_art)

def remove_nonalphanumeric(s: str) -> str:
    return re.sub(r'[^\w]', '', s)

def fetch_card(
    index: int,
    quantity: int,

    card_set: str,
    card_collector_number: str,
    use_set_and_collector_number: bool,

    name: str,
    preferred_sets: List[str],
    enforce_preferred_sets: bool,

    prefer_older_sets: bool,

    front_img_dir: str,
    double_sided_dir: str
):
    if use_set_and_collector_number and card_set != "" and card_collector_number != "":
        card_info_query = f"https://api.scryfall.com/cards/{card_set}/{card_collector_number}"

        # Query for card info
        card_json = request_scryfall(card_info_query).json()

        fetch_card_art(index, quantity, remove_nonalphanumeric(card_json['name']), card_set, card_collector_number, card_json['layout'], front_img_dir, double_sided_dir)

    else:
        if name == "":
            raise Exception()

        # Filter out symbols from card names
        clear_card_name = remove_nonalphanumeric(name)

        card_info_query = f'https://api.scryfall.com/cards/named?exact={clear_card_name}'

        # Query for card info
        card_json = request_scryfall(card_info_query).json()

        # Get available printings
        prints_search_json = request_scryfall(card_json['prints_search_uri']).json()
        card_printings = prints_search_json['data']

        # Remove promo, digital, and full art printings
        filtered_card_printings = list(filter(lambda card_print: card_print['lang'] == 'en' and card_print['nonfoil'] and not card_print['promo'] and not card_print['digital'] and not card_print['full_art'], card_printings))
        if len(filtered_card_printings) == 0:
            raise Exception(f'after cleaning, no acceptable printings for "{name}"')

        # Flip the order of the list if older printings are preferred
        if prefer_older_sets:
            filtered_card_printings.reverse()

        # If there are no preferred sets, then just select the first appropriate card printing
        if len(preferred_sets) == 0:
            card_print = filtered_card_printings[0]
            fetch_card_art(index, quantity, clear_card_name, card_print["set"], card_print["collector_number"], card_json['layout'], front_img_dir, double_sided_dir)

        else:
            added_card = False
            for card_print in filtered_card_printings:
                if card_print['set'] in preferred_sets:
                    added_card = True
                    fetch_card_art(index, quantity, clear_card_name, card_print["set"], card_print["collector_number"], card_json['layout'], front_img_dir, double_sided_dir)

                    break

            # Check if a printing has been selected
            if not added_card:
                if enforce_preferred_sets:
                    raise Exception(f'cannot find a print for "{name}" in the sets {preferred_sets}')
                else:
                    print(f'no preferred printing for "{name}", defaulting to random printing')
                    card_print = filtered_card_printings[0]
                    fetch_card_art(index, quantity, clear_card_name, card_print["set"], card_print["collector_number"], card_json['layout'], front_img_dir, double_sided_dir)

def get_handle_card(
    use_set_and_collector_number: bool,

    preferred_sets: List[str],
    enforce_preferred_sets: bool,
    prefer_older_sets: bool,

    front_img_dir: str,
    double_sided_dir: str
):
    def configured_fetch_card(index: int, name: str, card_set: str = None, card_collector_number: int = None, quantity: int = 1):
        fetch_card(
            index,
            quantity,

            card_set,
            card_collector_number,
            use_set_and_collector_number,

            name,
            preferred_sets,
            enforce_preferred_sets,

            prefer_older_sets,

            front_img_dir,
            double_sided_dir
        )
    return configured_fetch_card

# def get_handle_card(
#     use_set_and_collector_number: bool,

#     preferred_sets: List[str],
#     enforce_preferred_sets: bool,
#     prefer_older_sets: bool,

#     front_img_dir: str,
#     double_sided_dir: str
# ):
#     return lambda index, name, card_set=None, card_collector_number=None, quantity=1: fetch_card(
#         index,
#         quantity,

#         card_set,
#         card_collector_number,
#         use_set_and_collector_number,

#         name,
#         preferred_sets,
#         enforce_preferred_sets,

#         prefer_older_sets,

#         front_img_dir,
#         double_sided_dir
#     )