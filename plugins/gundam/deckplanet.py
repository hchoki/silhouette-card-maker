from os import path
from requests import Response, get
from time import sleep

def request_deckplanet(query: str) -> Response:
    r = get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    r.raise_for_status()
    sleep(0.15)

    return r

def fetch_card(
    index: int,
    quantity: int,
    card_number: str,
    front_img_dir: str,
):

    # Query for card info
    card_art = request_deckplanet(f'https://multi-deckplanet.us-southeast-1.linodeobjects.com/gundam/{card_number}.webp').content
    
    for counter in range(quantity):
        image_path = path.join(front_img_dir, f'{str(index)}{card_number}{str(counter + 1)}.png')

        with open(image_path, 'wb') as f:
            f.write(card_art)

def get_handle_card(
    front_img_dir: str,
):
    def configured_fetch_card(index: int, card_number: str, quantity: int = 1):
        fetch_card(
            index,
            quantity,
            card_number,
            front_img_dir
        )

    return configured_fetch_card