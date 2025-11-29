"""
Frame Detection System for MTG Cards

This module analyzes Magic: The Gathering card frame information from the Scryfall API
to categorize cards for appropriate Proxyshop template selection and folder organization.
"""

import os
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional

# Handle both relative and absolute imports
try:
    from .config import (
        VINTAGE_FRAMES, MODERN_FRAME, FUTURE_FRAME,
        SHOWCASE_KEYWORDS, BORDERLESS_KEYWORDS, EXTENDED_ART_KEYWORDS, RETRO_KEYWORDS, UNIVERSES_BEYOND_KEYWORDS,
        DOUBLE_SIDED_LAYOUTS, FRAME_TEMPLATE_MAP, FRAME_FOLDER_MAP
    )
except ImportError:
    # Add current directory to path for script execution
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    from config import (
        VINTAGE_FRAMES, MODERN_FRAME, FUTURE_FRAME,
        SHOWCASE_KEYWORDS, BORDERLESS_KEYWORDS, EXTENDED_ART_KEYWORDS, RETRO_KEYWORDS, UNIVERSES_BEYOND_KEYWORDS,
        DOUBLE_SIDED_LAYOUTS, FRAME_TEMPLATE_MAP, FRAME_FOLDER_MAP
    )

@dataclass
class FrameInfo:
    """Structured data for card frame information."""
    frame: str
    frame_effects: List[str]
    border_color: str
    layout: str
    is_showcase: bool = False
    is_borderless: bool = False
    is_extended_art: bool = False
    is_retro: bool = False
    is_transform: bool = False
    is_special: bool = False
    is_universes_beyond: bool = False
    folder_name: str = ''
    proxyshop_template: str = ''
    template_tags: List[str] = None
    
    def __post_init__(self):
        if self.template_tags is None:
            self.template_tags = []
        
        # Auto-generate derived fields
        self.folder_name = self._generate_folder_name()
        self.proxyshop_template = self._generate_template_name()
        self.template_tags = self._generate_template_tags()
    
    def _generate_folder_name(self) -> str:
        """Generate appropriate folder name based on frame characteristics."""
        if self.is_universes_beyond:
            return FRAME_FOLDER_MAP['universes_beyond']
        elif self.is_showcase:
            return FRAME_FOLDER_MAP['showcase']
        elif self.is_borderless:
            return FRAME_FOLDER_MAP['borderless']
        elif self.is_extended_art:
            return FRAME_FOLDER_MAP['extended_art']
        elif self.is_retro:
            return FRAME_FOLDER_MAP['retro']
        elif self.is_transform:
            return FRAME_FOLDER_MAP['transform']
        elif self.frame in VINTAGE_FRAMES:
            return FRAME_FOLDER_MAP['vintage']
        elif self.frame == MODERN_FRAME:
            return FRAME_FOLDER_MAP['modern']
        elif self.frame == FUTURE_FRAME:
            return FRAME_FOLDER_MAP['future']
        else:
            return FRAME_FOLDER_MAP['standard']
    
    def _generate_template_name(self) -> str:
        """Generate appropriate Proxyshop template name based on frame characteristics."""
        if self.is_universes_beyond:
            return FRAME_TEMPLATE_MAP['universes_beyond']
        elif self.is_showcase:
            return FRAME_TEMPLATE_MAP['showcase']
        elif self.is_borderless:
            return FRAME_TEMPLATE_MAP['borderless']
        elif self.is_extended_art:
            return FRAME_TEMPLATE_MAP['extended_art']
        elif self.is_transform:
            return FRAME_TEMPLATE_MAP['transform']
        elif self.is_retro:
            return FRAME_TEMPLATE_MAP['retro']
        elif self.frame in VINTAGE_FRAMES:
            return FRAME_TEMPLATE_MAP.get(self.frame, 'vintage')
        elif self.frame == MODERN_FRAME:
            return FRAME_TEMPLATE_MAP[MODERN_FRAME]
        else:
            return 'normal'
    
    def _generate_template_tags(self) -> List[str]:
        """Generate template tags for Proxyshop filtering."""
        tags = []
        
        if self.is_special:
            tags.append('special')
        if self.is_showcase:
            tags.append('showcase')
        if self.is_borderless:
            tags.append('borderless')
        if self.is_extended_art:
            tags.append('extended')
        if self.is_transform:
            tags.append('transform')
        if self.is_retro:
            tags.append('retro')
        if self.is_universes_beyond:
            tags.append('universes_beyond')
        
        # Add frame era tags
        if self.frame in VINTAGE_FRAMES:
            tags.append('vintage')
        elif self.frame == MODERN_FRAME:
            tags.append('modern')
        elif self.frame == FUTURE_FRAME:
            tags.append('future')
        
        return tags

def _analyze_frame_effects(frame_effects: List[str]) -> Dict[str, bool]:
    """Analyze frame effects and return detected special characteristics."""
    characteristics = {
        'is_showcase': False,
        'is_borderless': False,
        'is_extended_art': False,
        'is_retro': False,
        'is_special': False,
        'is_universes_beyond': False
    }
    
    if not frame_effects:
        return characteristics
        
    for effect in frame_effects:
        effect_lower = effect.lower()
        
        if any(keyword in effect_lower for keyword in SHOWCASE_KEYWORDS):
            characteristics['is_showcase'] = True
            characteristics['is_special'] = True
        elif any(keyword in effect_lower for keyword in BORDERLESS_KEYWORDS):
            characteristics['is_borderless'] = True
            characteristics['is_special'] = True
        elif any(keyword in effect_lower for keyword in EXTENDED_ART_KEYWORDS):
            characteristics['is_extended_art'] = True
            characteristics['is_special'] = True
        elif any(keyword in effect_lower for keyword in RETRO_KEYWORDS):
            characteristics['is_retro'] = True
            characteristics['is_special'] = True
        elif any(keyword in effect_lower for keyword in UNIVERSES_BEYOND_KEYWORDS):
            characteristics['is_universes_beyond'] = True
            characteristics['is_special'] = True
    
    return characteristics

def _detect_universes_beyond(card_json: dict) -> bool:
    """
    Detect if a card is from Universes Beyond based on set information and keywords.
    
    Args:
        card_json: Complete card data from Scryfall API
        
    Returns:
        bool: True if card is identified as Universes Beyond
    """
    # Check set name for UB indicators
    set_name = card_json.get('set_name', '').lower()
    set_code = card_json.get('set', '').lower()
    
    # Known Universes Beyond set codes
    ub_set_codes = {
        'sld',  # Secret Lair Drop
        'who',  # Doctor Who
        'ltr',  # Lord of the Rings
        'wh40k', # Warhammer 40,000
        'sld40k', # Secret Lair Warhammer 40k
        'wot',  # Wheel of Time (if exists)
        'tfm',  # Transformers (if exists)
        'acr',  # Assassin's Creed
        'pip',  # Fallout
        'j22',  # Jumpstart 2022 (has UB cards)
    }
    
    # Check if set code matches known UB sets
    if set_code in ub_set_codes:
        return True
    
    # Check set name for UB keywords
    ub_set_keywords = [
        'universes beyond',
        'secret lair',
        'doctor who',
        'lord of the rings',
        'warhammer',
        'transformers',
        'assassin\'s creed',
        'fallout',
        'street fighter',
        'stranger things',
        'walking dead',
        'fortnite'
    ]
    
    if any(keyword in set_name for keyword in ub_set_keywords):
        return True
    
    # Check promo type for UB promos
    promo_types = card_json.get('promo_types', [])
    if any('universes' in promo.lower() for promo in promo_types):
        return True
    
    return False

def detect_card_frame_info(card_json: dict) -> FrameInfo:
    """
    Analyze a card's frame information and return categorization details.
    
    Args:
        card_json: Complete card data from Scryfall API
        
    Returns:
        FrameInfo object containing frame analysis and suggestions
    """
    frame = card_json.get('frame', '').lower()
    frame_effects = card_json.get('frame_effects', [])
    border_color = card_json.get('border_color', '').lower()
    layout = card_json.get('layout', '').lower()
    
    # Analyze frame effects
    frame_characteristics = _analyze_frame_effects(frame_effects)
    
    # Detect Universes Beyond cards
    if _detect_universes_beyond(card_json):
        frame_characteristics['is_universes_beyond'] = True
        frame_characteristics['is_special'] = True
    
    # Analyze layout for transform cards
    if layout in DOUBLE_SIDED_LAYOUTS:
        frame_characteristics['is_transform'] = True
        frame_characteristics['is_special'] = True
    
    # Analyze border color for special treatments
    if border_color == 'borderless':
        frame_characteristics['is_borderless'] = True
        frame_characteristics['is_special'] = True
    
    # Create and return FrameInfo object
    return FrameInfo(
        frame=frame,
        frame_effects=frame_effects,
        border_color=border_color,
        layout=layout,
        **frame_characteristics
    )

def get_frame_summary(card_name: str, frame_info: FrameInfo) -> str:
    """
    Generate a human-readable summary of the frame detection results.
    
    Args:
        card_name: Name of the card
        frame_info: FrameInfo object from detect_card_frame_info
        
    Returns:
        Formatted summary string for display
    """
    card_type = "Special" if frame_info.is_special else "Standard"
    
    # Build feature list
    features = []
    if frame_info.is_universes_beyond:
        features.append("Universes Beyond")
    if frame_info.is_showcase:
        features.append("Showcase")
    if frame_info.is_borderless:
        features.append("Borderless")
    if frame_info.is_extended_art:
        features.append("Extended Art")
    if frame_info.is_retro:
        features.append("Retro")
    if frame_info.is_transform:
        features.append("Transform")
    
    if features:
        feature_str = f" ({', '.join(features)})"
    else:
        # Show frame era for standard cards
        if frame_info.frame == MODERN_FRAME:
            feature_str = " (Modern Frame)"
        elif frame_info.frame in VINTAGE_FRAMES:
            feature_str = f" ({frame_info.frame} Frame)"
        else:
            feature_str = ""
    
    return f"{card_type} frame{feature_str} -> {frame_info.proxyshop_template} template"

def analyze_deck_frame_distribution(deck_cards: List[dict]) -> Dict[str, int]:
    """
    Analyze the frame distribution across a deck of cards.
    
    Args:
        deck_cards: List of card JSON data from Scryfall
        
    Returns:
        Dictionary with frame type counts
    """
    distribution = {}
    
    for card_json in deck_cards:
        frame_info = detect_card_frame_info(card_json)
        folder_name = frame_info.folder_name
        
        distribution[folder_name] = distribution.get(folder_name, 0) + 1
    
    return distribution

def suggest_batch_processing_strategy(deck_cards: List[dict]) -> Dict[str, List[str]]:
    """
    Suggest optimal batch processing strategy based on frame distribution.
    
    Args:
        deck_cards: List of card JSON data from Scryfall
        
    Returns:
        Dictionary mapping template types to card lists for batch processing
    """
    template_batches = {}
    
    for card_json in deck_cards:
        frame_info = detect_card_frame_info(card_json)
        template = frame_info.proxyshop_template
        card_name = card_json.get('name', 'Unknown Card')
        
        if template not in template_batches:
            template_batches[template] = []
        
        template_batches[template].append(card_name)
    
    return template_batches