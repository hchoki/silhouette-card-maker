import os
import requests
import sys
import time

# Add the root directory to the path to import utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from utilities import upscale_image_with_waifu2x

def request_api(query: str) -> requests.Response:
    r = requests.get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})
    r.raise_for_status()
    time.sleep(0.15)

    return r

def fetch_card_art(passcode: int, quantity: int, front_img_dir: str, upscale: bool = False, upscale_factor: int = 2, noise_level: int = 1):
    card_front_image_query = f'https://images.ygoprodeck.com/images/cards/{passcode}.jpg'
    card_art = request_api(card_front_image_query).content
    if card_art is not None:

        # Save image based on quantity
        for counter in range(quantity):
            image_path = os.path.join(front_img_dir, f'{passcode}_{counter + 1}.jpg')

            with open(image_path, 'wb') as f:
                f.write(card_art)

            # Upscale the image if requested
            if upscale:
                upscale_image_with_waifu2x(image_path, upscale_factor, noise_level)

            print(f'{image_path}')