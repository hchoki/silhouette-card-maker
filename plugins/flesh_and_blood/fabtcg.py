from os import path
from requests import Response, get
from time import sleep
from re import sub
from deck_formats import PitchOption

def request_fabtcg(query: str) -> Response:
    r = get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})

    print(r.url)

    r.raise_for_status()
    sleep(0.15)

    return r

def fetch_card(
    index: int,
    quantity: int,
    name: str,
    pitch: PitchOption,
    front_img_dir: str,
):

    # Query for card info
    filtered_name_for_url = sub(r'\s+', '+', sub(r'[^A-Za-z0-9 ]+', '', name)).lower()
    pitch_argument = f'&pitch_lookup=exact&pitch={pitch.value}' if pitch != PitchOption.NONE else ''
    json = request_fabtcg(f'https://cards.fabtcg.com/api/search/v1/cards/?name={filtered_name_for_url}{pitch_argument}').json()
    card_art = request_fabtcg(json.get('results')[0].get('image').get('normal')).content
    
    for counter in range(quantity):
        image_path = path.join(front_img_dir, f'{str(index)}{sub(r'[^A-Za-z0-9 ]+', '', name)}{str(counter + 1)}.png')

        with open(image_path, 'wb') as f:
            f.write(card_art)

def get_handle_card(
    front_img_dir: str,
):
    def configured_fetch_card(index: int, name: str, pitch: PitchOption, quantity: int = 1):
        fetch_card(
            index,
            quantity,
            name,
            pitch,
            front_img_dir
        )

    return configured_fetch_card
    