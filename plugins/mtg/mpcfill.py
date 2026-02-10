import os
from base64 import b64decode
import requests
from filetype.filetype import guess_extension

from common import remove_nonalphanumeric
from download_manager import RateLimitedDownloader, DownloadTask, DownloadQueue

def download_cardback(cardback_id: str, back_img_dir: str) -> None:
    """
    Download a cardback image from MPCFill and save it to the back directory.
    
    Args:
        cardback_id: The MPCFill ID for the cardback image
        back_img_dir: Directory to save the cardback image
    """
    print(f"Downloading cardback with ID: {cardback_id}")
    try:
        card_art = request_mpcfill(cardback_id).content
        
        if card_art is not None:
            card_art = b64decode(card_art)
            card_art_ext = guess_extension(card_art)
            image_path = os.path.join(back_img_dir, f'cardback.{card_art_ext}')
            
            with open(image_path, 'wb') as f:
                f.write(card_art)
            
            print(f"Cardback saved to: {image_path}")
    except Exception as e:
        print(f"Error downloading cardback: {e}")

def request_mpcfill(card_id: str) -> requests.Response:
    base_url = "https://script.google.com/macros/s/AKfycbw8laScKBfxda2Wb0g63gkYDBdy8NWNxINoC4xDOwnCQ3JMFdruam1MdmNmN4wI5k4/exec?id="
    r = requests.get(base_url + card_id, headers = {"user-agent": "silhouette-card-maker/0.1", "accept": "*/*"})

    r.raise_for_status()

    return r

def fetch_card(
        index: int,
        quantity: int,

        card_id: str,
        name: str,
        back_card_id: str | None,

        front_img_dir: str,
        double_sided_dir: str,
        
        # These parameters are for signature compatibility with parallel downloads
        card_set: str = None,  # Not used for mpcfill
        collector_number: str = None,  # Not used for mpcfill
        layout: str = None,  # Not used for mpcfill
        art_crop: bool = False,  # Not used for mpcfill
        original_card_name: str = None,  # Not used for mpcfill
        card_json: dict = None,  # Not used for mpcfill
) -> None:
    card_art = request_mpcfill(card_id).content

    clean_card_name = remove_nonalphanumeric(name)

    if card_art is not None:
        card_art = b64decode(card_art)
        card_art_ext = guess_extension(card_art)
        for counter in range(quantity):
            image_path = os.path.join(front_img_dir, f'{str(index)}{clean_card_name}{str(counter + 1)}.{card_art_ext}')

            with open(image_path, 'wb') as f:
                f.write(card_art)

    if back_card_id:
        card_art = request_mpcfill(back_card_id).content

        if card_art is not None:
            card_art = b64decode(card_art)
            card_art_ext = guess_extension(card_art)
            for counter in range(quantity):
                image_path = os.path.join(double_sided_dir, f'{str(index)}{clean_card_name}{str(counter + 1)}.{card_art_ext}')

                with open(image_path, 'wb') as f:
                    f.write(card_art)

def get_handle_card(
    front_img_dir: str,
    double_sided_dir: str,
    parallel: bool = True,
    max_workers: int = 6,
):
    """
    Create a card handler for MPC Fill XML format.
    
    Args:
        front_img_dir: Directory for front card images
        double_sided_dir: Directory for double-sided card images
        parallel: Enable parallel downloads (default: True)
        max_workers: Number of parallel download threads (default: 6)
    """
    # Set up parallel download infrastructure if enabled
    download_queue = None
    downloader = None
    
    if parallel:
        download_queue = DownloadQueue()
        downloader = RateLimitedDownloader(max_workers=max_workers)
    
    def configured_fetch_card(index: int, card_id, name: str, back_card_id: str | None, quantity: int = 1):
        if parallel:
            # Queue the download task instead of downloading immediately
            task = DownloadTask(
                index=index,
                card_name=card_id,  # Use card_id as card_name for MPC Fill
                card_set=card_id,  # Store card_id in card_set field for later retrieval
                collector_number=back_card_id or "",  # Store back_card_id if exists
                quantity=quantity,
                layout="mpcfill",  # Use custom layout identifier
                original_name=name,  # Store the display name
            )
            download_queue.add_task(task)
            print(f"Queued: {name}")
        else:
            # Download immediately (non-parallel mode)
            fetch_card(
                index,
                quantity,
                card_id,
                name,
                back_card_id,
                front_img_dir,
                double_sided_dir,
            )
    
    # Attach parallel download attributes to the function
    configured_fetch_card.download_queue = download_queue
    configured_fetch_card.downloader = downloader
    configured_fetch_card.front_img_dir = front_img_dir
    configured_fetch_card.double_sided_dir = double_sided_dir
    
    # Create a wrapper that matches the parallel download signature
    def mpcfill_fetch_wrapper(index, quantity, card_name, card_set, collector_number, 
                              layout, front_dir, double_sided_dir, art_crop, 
                              original_name, card_json):
        """Wrapper to adapt mpcfill fetch_card to parallel download interface."""
        # card_set contains the card_id
        # collector_number contains the back_card_id (if any)
        fetch_card(
            index,
            quantity,
            card_set,  # card_id stored in card_set
            original_name,  # name
            collector_number if collector_number else None,  # back_card_id
            front_dir,
            double_sided_dir,
        )
    
    configured_fetch_card.fetch_card = mpcfill_fetch_wrapper
    
    return configured_fetch_card