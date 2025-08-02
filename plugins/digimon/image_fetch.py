from os import path
from re import compile, search
from requests import Response, get, HTTPError
from time import sleep

def request_digimoncard(query: str) -> Response:
    r = get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    r.raise_for_status()
    sleep(0.15)
    
    return r

def fetch_card_art(index: int, card_number: str, quantity: int, front_img_dir: str):

    card_art = request_digimoncard(f'https://images.digimoncard.io/images/cards/{card_number}.jpg').content
    
    # Save image based on quantity
    for counter in range(quantity):
        image_path = path.join(front_img_dir, f'{index}{card_number}_{counter + 1}.jpg')

        with open(image_path, 'wb') as f:
            f.write(card_art)

        print(f'{image_path}')