import csv
import os
from typing import List
import pandas as pd
import re
import requests
import time

# User configurable options:

csv_name = 'MOM_test.csv'

# Use the printings of the following sets
preferred_sets = []
# preferred_sets = ["akh", "hou", "otj"]

# Throw an error if there are not printings of the preferred sets
enforce_preferred_sets = True

# Prioritize older sets rather than newer sets
prefer_older_sets = True

# Add maybeboard in the list of cards
add_maybeboard = False

use_set_and_collector_number = True
# use_set_and_collector_number = False



# System options:

# https://scryfall.com/docs/api
query_headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'}
# card_info_query = 'https://api.scryfall.com/cards/named?exact='

# card_info_columns = ['name', 'layout', 'Set', 'Collector Number', 'Quantity']
# card_info = []



# # Query all the card information from scryfall
# csv_dir = 'mtg'
# csv_path = os.path.join(csv_dir, csv_name)

# counter = 0

# with open(csv_path) as csvfile:
#     cube_list = csv.DictReader(csvfile)

#     # Iterate through all the cards
#     for card in cube_list:
#         card_name = card['name']

#         if 'maybeboard' in card and card['maybeboard'] == 'true' and not add_maybeboard:
#             print(f'skipping maybeboard card: "{card_name}"')
#             continue

#         card_quantity = 1
#         if 'Quantity' in card:
#             card_quantity = card['Quantity']

#         print(f'{counter}: {card_name}')
#         counter = counter + 1

#         try:
#             info = []

#             if use_set_and_collector_number:
#                 card_info_query_full = f"https://api.scryfall.com/cards/{card['Set']}/{card['Collector Number']}"

#                 # Query the card using scryfall's API
#                 r = requests.get(card_info_query_full, headers = query_headers)

#                 # Sleep for 150 milliseconds, greater than the 100ms requested by scryfall API documentation
#                 time.sleep(0.15)

#                 # Check for 2XX response code
#                 r.raise_for_status()

#                 # Parse JSON
#                 card_json = r.json()

#                 card_info.append([card_name, card_json['layout'], card['Set'], card['Collector Number'], card_quantity])

#             else:
#                 # Filter out symbols from card names
#                 card_name = re.sub(r'[^\w]', '', card_name)
#                 card_info_query_full = card_info_query + card_name
#                 # print(f"query: {card_info_query_full}")

#                 # Query the card using scryfall's API
#                 r = requests.get(card_info_query_full, headers = query_headers)

#                 # Sleep for 150 milliseconds, greater than the 100ms requested by scryfall API documentation
#                 time.sleep(0.15)

#                 # Check for 2XX response code
#                 r.raise_for_status()

#                 # Parse JSON
#                 card_json = r.json()

#                 # Make request for all printings
#                 prints_search_r = requests.get(card_json['prints_search_uri'])

#                 # Sleep for 150 milliseconds, greater than the 100ms requested by scryfall API documentation
#                 time.sleep(0.15)

#                 # Check for 2XX response code
#                 prints_search_r.raise_for_status()

#                 # Parse JSON
#                 prints_search_json = prints_search_r.json()

#                 # Ensure there is at least one printing
#                 card_printings = prints_search_json['data']
#                 if len(card_printings) == 0:
#                     raise Exception(f'cannot find printings for "{card_name}"')

#                 # Remove promo, digital, and full art printings
#                 clean_card_printings = list(filter(lambda card_print: card_print['lang'] == 'en' and card_print['nonfoil'] and not card_print['promo'] and not card_print['digital'] and not card_print['full_art'], card_printings))
#                 if len(clean_card_printings) == 0:
#                     raise Exception(f'after cleaning, no acceptable printings for "{card_name}"')

#                 # Flip the order of the list if older printings are preferred
#                 if prefer_older_sets:
#                     clean_card_printings.reverse()

#                 # If there are no preferred sets, then just select the first appropriate card printing
#                 if len(preferred_sets) == 0:
#                     card_print = clean_card_printings[0]
#                     card_info.append([card_name, card_print['layout'], card_print['set'], card_print['collector_number'], card_quantity])

#                 else:
#                     added_card = False
#                     for card_print in clean_card_printings:
#                         if card_print['set'] in preferred_sets:
#                             added_card = True
#                             card_info.append([card_name, card_print['layout'], card_print['set'], card_print['collector_number'], card_quantity])
#                             break

#                     # Check if a printing has been selected
#                     if not added_card:
#                         if enforce_preferred_sets:
#                             raise Exception(f'cannot find a print for "{card_name}" in the sets {preferred_sets}')
#                         else:
#                             print(f'no preferred printing for "{card_name}", defaulting to random printing')
#                             card_print = clean_card_printings[0]
#                             card_info.append([card_name, card_print['layout'], card_print['set'], card_print['collector_number'], card_quantity])

#             # if 'Quantity' in card:
#             #     for i in range(int(card['Quantity'])):
#             #         card_info.append(info)

#             # else:
#             #     card_info.append(info)

#         except requests.HTTPError as e:
#             raise e
#         except KeyError as e:
#             print(f'Key error for card "{card_name}"')
#             raise e
#             # print(card_json)

# # Convert card_info into a DataFrame
# card_df = pd.DataFrame(card_info, columns = card_info_columns)

# # Save as a pickled object
# export_path = os.path.join(csv_dir, csv_name.split('.')[0]+'.pkl')
# card_df.to_pickle(export_path)

query_headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'}
card_image_query_1 = 'https://api.scryfall.com/cards'
card_image_query_2 = '?format=image&version=large'

double_sided_layouts = ['transform', 'modal_dfc']

def request_art(
    query: str,
    # image_path: str
):
    try:
        r = requests.get(query, headers = query_headers)
        # Check for 2XX response code

        r.raise_for_status()

        # for counter in range(card_quantity):
        #     with open(image_path, 'wb') as f:
        #         f.write(r.content)

        return r.content

        # Sleep for 150 milliseconds, greater than the 100ms requested by scryfall API documentation
        time.sleep(0.15)
    except requests.HTTPError as ex:
        raise ex

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
    # card_image_query_front = '/'.join([card_image_query_1, card_set, card_num]) + card_image_query_2
    # card_image_query_front = f'{card_image_query_1}/{card_set}/{card_num}/{card_image_query_2}'
    card_image_query_front = f'https://api.scryfall.com/cards/{card_set}/{card_collector_number}/?format=image&version=large'


    # image_path = os.path.join(front_img_dir, f'{str(index)}{clean_card_name}{str(counter)}.jpg')
    card_art = request_art(card_image_query_front)
    if card_art is not None:
        for counter in range(quantity):
            image_path = os.path.join(front_img_dir, f'{str(index)}{clean_card_name}{str(counter)}.jpg')

            with open(image_path, 'wb') as f:
                f.write(card_art)

    # try:
    #     # r = requests.get(card_image_query_front, headers = query_headers)
    #     # # Check for 2XX response code

    #     # r.raise_for_status()

    #     # for counter in range(card_quantity):
    #     #     image_path = os.path.join(front_img_dir, f'{str(index)}{clean_card_name}{str(counter)}a.jpg')
    #     #     with open(image_path, 'wb') as f:
    #     #         f.write(r.content)

    #     # # Sleep for 150 milliseconds, greater than the 100ms requested by scryfall API documentation
    #     # time.sleep(0.15)





    #     for counter in range(card_quantity):
    #         image_path = os.path.join(front_img_dir, f'{str(index)}{clean_card_name}{str(counter)}.jpg')

    #         with open(image_path, 'wb') as f:
    #             request_art(card_image_query_front)

    # except requests.HTTPError as ex:
    #     raise ex

    if layout in double_sided_layouts:
        # # Query for the back side
        # try:
        #     r = requests.get(f'{card_image_query_front}&face=back', headers = query_headers)

        #     # Check for 2XX response code
        #     r.raise_for_status()

        #     for counter in range(card_quantity):
        #         image_path = os.path.join(double_sided_dir, f'{str(index)}{clean_card_name}{str(counter)}.jpg')
        #         with open(image_path, 'wb') as f:
        #             f.write(r.content)

        #     # Sleep for 150 milliseconds, greater than the 100ms requested by scryfall API documentation
        #     time.sleep(0.15)
        # except requests.HTTPError as ex:
        #     raise ex

        # card_image_query_back = f'{card_image_query_front}&face=back'
        # for counter in range(card_quantity):
        #     image_path = os.path.join(double_sided_dir, f'{str(index)}{clean_card_name}{str(counter)}.jpg')

        #     with open(image_path, 'wb') as f:
        #         request_art(card_image_query_back)

        card_image_query_back = f'{card_image_query_front}&face=back'
        card_art = request_art(card_image_query_back)
        if card_art is not None:
            for counter in range(quantity):
                image_path = os.path.join(front_img_dir, f'{str(index)}{clean_card_name}{str(counter)}.jpg')

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
        card_info_query_full = f"https://api.scryfall.com/cards/{card_set}/{card_collector_number}"

        # Query the card using scryfall's API
        r = requests.get(card_info_query_full, headers = query_headers)

        # Sleep for 150 milliseconds, greater than the 100ms requested by scryfall API documentation
        time.sleep(0.15)

        # Check for 2XX response code
        r.raise_for_status()

        # Parse JSON
        card_json = r.json()

        fetch_card_art(index, quantity, remove_nonalphanumeric(card_json['name']), card_set, card_collector_number, card_json['layout'], front_img_dir, double_sided_dir)

    else:
        if name == "":
            raise Exception()

        # Filter out symbols from card names
        clear_card_name = remove_nonalphanumeric(name)
        card_info_query_full = f'https://api.scryfall.com/cards/named?exact={clear_card_name}'

        # Query the card using scryfall's API
        r = requests.get(card_info_query_full, headers = query_headers)

        # Sleep for 150 milliseconds, greater than the 100ms requested by scryfall API documentation
        time.sleep(0.15)

        # Check for 2XX response code
        r.raise_for_status()

        # Parse JSON
        card_json = r.json()

        # Make request for all printings
        prints_search_r = requests.get(card_json['prints_search_uri'])

        # Sleep for 150 milliseconds, greater than the 100ms requested by scryfall API documentation
        time.sleep(0.15)

        # Check for 2XX response code
        prints_search_r.raise_for_status()

        # Parse JSON
        prints_search_json = prints_search_r.json()

        # Ensure there is at least one printing
        card_printings = prints_search_json['data']
        # if len(card_printings) == 0:
        #     raise Exception(f'cannot find printings for "{name}"')

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