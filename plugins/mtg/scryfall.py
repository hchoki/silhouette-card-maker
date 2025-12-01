import os
from typing import List, Set, Tuple
import requests
import time
import threading

from common import remove_nonalphanumeric
from frame_detection import detect_card_frame_info, get_frame_summary
from download_manager import RateLimitedDownloader, DownloadTask, DownloadQueue

double_sided_layouts = ['transform', 'modal_dfc', 'double_faced_token', 'reversible_card']

# Global API delay setting and lock for thread-safe rate limiting
_api_delay = 0.05
_api_lock = threading.Lock()
_last_api_call = 0

def request_scryfall(
    query: str,
) -> requests.Response:
    global _last_api_call
    
    # Thread-safe rate limiting for API calls
    with _api_lock:
        current_time = time.time()
        time_since_last = current_time - _last_api_call
        
        if time_since_last < _api_delay:
            sleep_time = _api_delay - time_since_last
            time.sleep(sleep_time)
        
        r = requests.get(query, headers = {'user-agent': 'silhouette-card-maker/0.1', 'accept': '*/*'})
        
        # Update last call time after request
        _last_api_call = time.time()
    
    # Check for 2XX response code
    r.raise_for_status()

    return r

def fetch_card_art(
    index: int,
    quantity: int,

    clean_card_name: str,
    card_set: int,
    card_collector_number: int,
    layout: str,

    front_img_dir: str,
    double_sided_dir: str,
    art_crop: bool = False,
    original_card_name: str = None,
    card_json: dict = None
) -> None:
    # If card_json not provided, fetch it from API
    if card_json is None:
        card_info_query = f'https://api.scryfall.com/cards/{card_set}/{card_collector_number}'
        card_json = request_scryfall(card_info_query).json()
    
    # Get the direct CDN URL for the image (not rate-limited)
    image_version = 'art_crop' if art_crop else 'png'
    
    # Extract image URL from card data
    if 'image_uris' in card_json:
        card_front_image_url = card_json['image_uris'].get(image_version)
    else:
        # For double-faced cards, get the front face
        card_front_image_url = card_json['card_faces'][0]['image_uris'].get(image_version)
    
    if card_front_image_url:
        # Download from CDN (no rate limiting needed)
        card_art = requests.get(card_front_image_url, headers={'user-agent': 'silhouette-card-maker/0.1'}).content
    else:
        card_art = None
    
    if card_art is not None:

        # Save image based on quantity
        for counter in range(quantity):
            if art_crop:
                # Detect frame information
                frame_info = detect_card_frame_info(card_json)
                
                # Create frame-organized folder structure
                base_art_dir = 'art'
                frame_folder = frame_info.folder_name
                art_dir = os.path.join(base_art_dir, frame_folder)
                os.makedirs(art_dir, exist_ok=True)
                
                # Generate Proxyshop filename: CardName [SET] {collector}.jpg
                display_name = original_card_name or clean_card_name
                proxyshop_name = ''.join(c for c in display_name if c.isalnum() or c in ' -\'.,').strip()
                proxyshop_filename = f"{proxyshop_name} [{card_set.upper()}] {{{card_collector_number}}}.jpg"
                
                if counter > 0:
                    # For multiple quantities, add counter
                    base_name = proxyshop_filename.rsplit('.', 1)[0]
                    extension = proxyshop_filename.rsplit('.', 1)[1]
                    proxyshop_filename = f"{base_name} ({counter + 1}).{extension}"
                
                image_path = os.path.join(art_dir, proxyshop_filename)
                
                # Display frame information
                frame_summary = get_frame_summary(display_name, frame_info)
                print(f"🎯 {frame_summary}")
                print(f"💾 Saving to: {frame_folder}/{proxyshop_filename}")
            else:
                # Standard game folder structure
                image_path = os.path.join(front_img_dir, f'{str(index)}{clean_card_name}{str(counter + 1)}.png')

            with open(image_path, 'wb') as f:
                f.write(card_art)

    # Get backside of card, if it exists
    if layout in double_sided_layouts:
        # Extract back face image URL from card data (already fetched above)
        if 'card_faces' in card_json and len(card_json['card_faces']) > 1:
            card_back_image_url = card_json['card_faces'][1]['image_uris'].get(image_version)
            if card_back_image_url:
                # Download from CDN (no rate limiting needed)
                card_art = requests.get(card_back_image_url, headers={'user-agent': 'silhouette-card-maker/0.1'}).content
            else:
                card_art = None
        else:
            card_art = None
            
        if card_art is not None:

            # Save image based on quantity
            for counter in range(quantity):
                if art_crop:
                    # Use the same frame detection as front face
                    frame_info = detect_card_frame_info(card_json)
                    
                    # Create frame-organized folder structure for back face
                    base_art_dir = 'art'
                    frame_folder = frame_info.folder_name
                    art_dir = os.path.join(base_art_dir, frame_folder)
                    os.makedirs(art_dir, exist_ok=True)
                    
                    # Generate Proxyshop filename for back face
                    display_name = original_card_name or clean_card_name
                    proxyshop_name = ''.join(c for c in display_name if c.isalnum() or c in " -'.,").strip()
                    proxyshop_filename = f"{proxyshop_name} [{card_set.upper()}] {{{card_collector_number}}} (Back).jpg"
                    
                    if counter > 0:
                        base_name = proxyshop_filename.rsplit('.', 1)[0]
                        extension = proxyshop_filename.rsplit('.', 1)[1]
                        proxyshop_filename = f"{base_name} ({counter + 1}).{extension}"
                    
                    image_path = os.path.join(art_dir, proxyshop_filename)
                    print(f"💾 Saving back face to: {frame_folder}/{proxyshop_filename}")
                else:
                    # Standard game folder structure
                    image_path = os.path.join(double_sided_dir, f'{str(index)}{clean_card_name}{str(counter + 1)}.png')

                with open(image_path, 'wb') as f:
                    f.write(card_art)

def partition_printings(printings: List, condition: List) -> Tuple[List, List]:
    matches = []
    non_matches = []
    for card in printings:
        (matches if condition(card) else non_matches).append(card)
    return matches, non_matches

def progressive_filtering(printings: List, filters):
    pool = printings
    leftovers = []

    for condition in filters:
        matched, not_matched = partition_printings(pool, condition)
        leftovers = not_matched + leftovers
        pool = matched or pool  # Only narrow if we have any matches

    return pool + leftovers

def filtering(printings: List, filters):
    pool = printings

    for condition in filters:
        matched, _ = partition_printings(pool, condition)
        pool = matched

    return pool

def fetch_card(
    index: int,
    quantity: int,

    card_set: str,
    card_collector_number: str,
    ignore_set_and_collector_number: bool,

    name: str,

    prefer_older_sets: bool,
    preferred_sets: Set[str],

    prefer_showcase: bool,
    prefer_extra_art: bool,
    tokens: bool,
    art_crop: bool,

    front_img_dir: str,
    double_sided_dir: str
):
    if not ignore_set_and_collector_number and card_set != "" and card_collector_number != "":
        card_info_query = f"https://api.scryfall.com/cards/{card_set}/{card_collector_number}"

        # Query for card info
        card_json = request_scryfall(card_info_query).json()

        fetch_card_art(index, quantity, remove_nonalphanumeric(card_json['name']), card_set, card_collector_number, card_json['layout'], front_img_dir, double_sided_dir, art_crop, card_json['name'], card_json)

        # Fetch tokens
        if tokens:
            if all_parts := card_json.get("all_parts"):
                for related in all_parts:
                    if related["component"] == "token":
                        card_info_query = related["uri"]
                        token_json = request_scryfall(card_info_query).json()
                        fetch_card_art(index, quantity, remove_nonalphanumeric(related["name"]), token_json["set"], token_json["collector_number"], token_json["layout"], front_img_dir, double_sided_dir, art_crop, related["name"], token_json)

    else:
        if name == "":
            raise Exception()

        # Filter out symbols from card names
        clean_card_name = remove_nonalphanumeric(name)

        card_info_query = f'https://api.scryfall.com/cards/named?exact={clean_card_name}'

        # Query for card info
        card_json = request_scryfall(card_info_query).json()

        set = card_json["set"]
        collector_number = card_json["collector_number"]

        # If preferred options are used, then filter over prints
        if prefer_older_sets or len(preferred_sets) > 0 or prefer_showcase or prefer_extra_art:
            # Get available printings
            prints_search_json = request_scryfall(card_json['prints_search_uri']).json()
            card_printings = prints_search_json['data']

            # Optional reverse for older preferences
            if prefer_older_sets:
                card_printings.reverse()

            # Define filters in order of preference
            filters = [
                lambda c: c['nonfoil'],
                lambda c: not c['digital'],
                lambda c: not c['promo'],
                lambda c: c['set'] in preferred_sets,
                lambda c: not prefer_showcase ^ ('frame_effects' in c and 'showcase' in c['frame_effects']),
                lambda c: not prefer_extra_art ^ (c['full_art'] or c['border_color'] == "borderless" or ('frame_effects' in c and 'extendedart' in c['frame_effects']))
            ]

            # Apply progressive filtering
            filtered_printings = progressive_filtering(card_printings, filters)

            if len(filtered_printings) == 0:
                print(f'No printings found for "{name}" with preferred options. Using default instead.')
            else:
                best_print = filtered_printings[0]
                set = best_print["set"]
                collector_number = best_print["collector_number"]

        # Fetch card art
        fetch_card_art(
            index,
            quantity,
            clean_card_name,
            set,
            collector_number,
            card_json['layout'],
            front_img_dir,
            double_sided_dir,
            art_crop,
            card_json['name'],
            card_json
        )

        # Fetch tokens
        if tokens:
            if all_parts := card_json.get("all_parts"):
                for related in all_parts:
                    if related["component"] == "token":
                        card_info_query = related["uri"]
                        token_json = request_scryfall(card_info_query).json()
                        fetch_card_art(index, quantity, remove_nonalphanumeric(related["name"]), token_json["set"], token_json["collector_number"], token_json["layout"], front_img_dir, double_sided_dir, art_crop, related["name"], token_json)

def get_handle_card(
    ignore_set_and_collector_number: bool,

    prefer_older_sets: bool,
    preferred_sets: Set[str],

    prefer_showcase: bool,
    prefer_extra_art: bool,
    tokens: bool,
    art_crop: bool,
    parallel: bool,
    max_workers: int,
    api_delay: float,

    front_img_dir: str,
    double_sided_dir: str
):
    # Set global API delay
    global _api_delay
    _api_delay = api_delay
    
    # Initialize download queue for parallel processing
    download_queue = DownloadQueue() if parallel else None
    downloader = RateLimitedDownloader(max_workers=max_workers) if parallel else None
    
    def configured_fetch_card(index: int, name: str, card_set: str = None, card_collector_number: int = None, quantity: int = 1):
        if parallel:
            # For parallel mode, queue the task instead of fetching immediately
            # We'll need to resolve set/collector info first if not provided
            if card_set and card_collector_number:
                task = DownloadTask(
                    index=index,
                    card_name=remove_nonalphanumeric(name),
                    card_set=card_set,
                    collector_number=card_collector_number,
                    quantity=quantity,
                    layout='normal',  # Will be determined during fetch
                    original_name=name
                )
                download_queue.add_task(task)
            else:
                # For cards without set/collector, fetch immediately to resolve them
                fetch_card(
                    index,
                    quantity,
                    card_set,
                    card_collector_number,
                    ignore_set_and_collector_number,
                    name,
                    prefer_older_sets,
                    preferred_sets,
                    prefer_showcase,
                    prefer_extra_art,
                    tokens,
                    art_crop,
                    front_img_dir,
                    double_sided_dir
                )
        else:
            # Sequential mode - fetch immediately
            fetch_card(
                index,
                quantity,

                card_set,
                card_collector_number,
                ignore_set_and_collector_number,

                name,

                prefer_older_sets,
                preferred_sets,

                prefer_showcase,
                prefer_extra_art,
                tokens,
                art_crop,

                front_img_dir,
                double_sided_dir
            )
    
    # Return both the configured function and the download queue/downloader for parallel processing
    if parallel:
        configured_fetch_card.download_queue = download_queue
        configured_fetch_card.downloader = downloader
        configured_fetch_card.fetch_card_art = fetch_card_art
        configured_fetch_card.front_img_dir = front_img_dir
        configured_fetch_card.double_sided_dir = double_sided_dir
        configured_fetch_card.art_crop = art_crop
    
    return configured_fetch_card


