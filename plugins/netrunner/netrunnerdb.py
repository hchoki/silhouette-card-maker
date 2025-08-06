from os import path
from requests import Response, get
from time import sleep
from re import sub
from unicodedata import normalize, category

def request_netrunnerdb(query: str) -> Response:
    r = get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    r.raise_for_status()
    sleep(0.15)

    return r

def fetch_card(
    index: int,
    quantity: int,
    name: str,
    front_img_dir: str,
):

    # Query for card info
    # Query for a normalized name of Latin scripts
    filtered_name_for_url = sub(r'\s+|-', '_', sub(r'[^A-Za-z0-9 \-]+', '', ''.join(c for c in normalize('NFD', name) if category(c) != 'Mn'))).lower()
    json = request_netrunnerdb(f'https://api-preview.netrunnerdb.com/api/v3/public/cards/{filtered_name_for_url}').json()

    print_id = json.get('data').get('attributes').get('latest_printing_id')
    card_art = request_netrunnerdb(f'https://nro-public.s3.nl-ams.scw.cloud/nro/card-printings/v2/webp/english/card/{print_id}.webp').content
    
    for counter in range(quantity):
        image_path = path.join(front_img_dir, f'{str(index)}{name}{str(counter + 1)}.png')

        with open(image_path, 'wb') as f:
            f.write(card_art)

def get_handle_card(
    front_img_dir: str,
):
    def configured_fetch_card(index: int, name: str, quantity: int = 1):
        fetch_card(
            index,
            quantity,
            name,
            front_img_dir
        )

    return configured_fetch_card
    