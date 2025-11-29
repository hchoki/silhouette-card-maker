"""
URL and filename utilities for MTG card processing.
"""

import os
import re
import sys
from typing import Tuple

# Handle both relative and absolute imports
try:
    from .config import SCRYFALL_BASE_URL, ART_CROP_EXTENSION, CARD_IMAGE_EXTENSION, DEFAULT_ART_DIR
except ImportError:
    # Add current directory to path for script execution
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    from config import SCRYFALL_BASE_URL, ART_CROP_EXTENSION, CARD_IMAGE_EXTENSION, DEFAULT_ART_DIR

def build_scryfall_image_url(set_code: str, collector_number: str, art_crop: bool = False) -> str:
    """Build a Scryfall image URL for card download."""
    image_version = 'art_crop' if art_crop else 'png'
    return f'{SCRYFALL_BASE_URL}/cards/{set_code}/{collector_number}/?format=image&version={image_version}'

def build_scryfall_card_info_url(set_code: str, collector_number: str) -> str:
    """Build a Scryfall URL for card information."""
    return f'{SCRYFALL_BASE_URL}/cards/{set_code}/{collector_number}'

def build_scryfall_named_card_url(card_name: str) -> str:
    """Build a Scryfall URL for named card lookup."""
    clean_name = remove_nonalphanumeric(card_name)
    return f'{SCRYFALL_BASE_URL}/cards/named?exact={clean_name}'

def remove_nonalphanumeric(text: str) -> str:
    """Remove non-alphanumeric characters from text, keeping spaces."""
    return re.sub(r'[^\w\s]', '', text)

def generate_proxyshop_filename(
    card_name: str, 
    set_code: str, 
    collector_number: str, 
    quantity_number: int = 0
) -> str:
    """
    Generate a Proxyshop-compatible filename.
    
    Format: "CardName [SET] {collector}.jpg" or "CardName [SET] {collector} (2).jpg"
    """
    # Clean the card name for filename use
    clean_name = ''.join(c for c in card_name if c.isalnum() or c in ' -\'.,').strip()
    base_filename = f"{clean_name} [{set_code.upper()}] {{{collector_number}}}{ART_CROP_EXTENSION}"
    
    if quantity_number > 0:
        name_part, ext = os.path.splitext(base_filename)
        base_filename = f"{name_part} ({quantity_number + 1}){ext}"
    
    return base_filename

def generate_game_filename(
    index: int, 
    clean_card_name: str, 
    counter: int
) -> str:
    """Generate a filename for game directory storage."""
    return f'{index}{clean_card_name}{counter + 1}{CARD_IMAGE_EXTENSION}'

def create_frame_directory(frame_folder: str, base_dir: str = DEFAULT_ART_DIR) -> str:
    """Create and return the path for frame-organized directory."""
    art_dir = os.path.join(base_dir, frame_folder)
    os.makedirs(art_dir, exist_ok=True)
    return art_dir

def get_card_image_paths(
    card_data: dict,
    quantity: int,
    art_crop: bool = False,
    frame_folder: str = None,
    front_img_dir: str = None,
    index: int = None
) -> Tuple[list, list]:
    """
    Generate all image paths for a card based on quantity and settings.
    
    Returns:
        Tuple of (front_paths, back_paths) lists
    """
    front_paths = []
    back_paths = []
    
    card_name = card_data.get('name', 'Unknown')
    set_code = card_data.get('set', '')
    collector_number = card_data.get('collector_number', '')
    clean_name = remove_nonalphanumeric(card_name)
    
    for counter in range(quantity):
        if art_crop and frame_folder:
            # Proxyshop art crop mode
            art_dir = create_frame_directory(frame_folder)
            filename = generate_proxyshop_filename(
                card_name, set_code, collector_number, 
                counter if quantity > 1 else 0
            )
            front_paths.append(os.path.join(art_dir, filename))
        else:
            # Game directory mode
            filename = generate_game_filename(index or 0, clean_name, counter)
            front_paths.append(os.path.join(front_img_dir or 'front', filename))
    
    return front_paths, back_paths