"""
Configuration constants and settings for MTG card processing.
"""

# Scryfall API Configuration
SCRYFALL_API_DELAY = 0.15  # 150ms delay as requested by Scryfall
SCRYFALL_USER_AGENT = 'silhouette-card-maker/0.1'
SCRYFALL_BASE_URL = 'https://api.scryfall.com'

# Card Layout Types
DOUBLE_SIDED_LAYOUTS = [
    'transform', 
    'modal_dfc', 
    'double_faced_token', 
    'reversible_card'
]

# Frame Era Mappings
VINTAGE_FRAMES = ['1993', '1997', '2003']
MODERN_FRAME = '2015'
FUTURE_FRAME = 'future'

# Directory Names
DEFAULT_ART_DIR = 'art'
DEFAULT_GAME_DIR = 'game'
DEFAULT_FRONT_DIR = 'front'
DEFAULT_BACK_DIR = 'back'
DEFAULT_DOUBLE_SIDED_DIR = 'double_sided'

# File Extensions
ART_CROP_EXTENSION = '.jpg'
CARD_IMAGE_EXTENSION = '.png'

# Processing Limits
DEFAULT_MAX_DOWNLOAD_WORKERS = 6
DEFAULT_MAX_UPSCALE_WORKERS = 3
DEFAULT_CARD_INFO_WORKERS = 4

# Frame Effect Keywords
SHOWCASE_KEYWORDS = ['showcase']
BORDERLESS_KEYWORDS = ['borderless']
EXTENDED_ART_KEYWORDS = ['extended', 'extendedart']
RETRO_KEYWORDS = ['retro', 'vintage']
UNIVERSES_BEYOND_KEYWORDS = ['universes beyond', 'universesbeyond']

# Proxyshop Template Mappings
FRAME_TEMPLATE_MAP = {
    'showcase': 'showcase',
    'borderless': 'borderless',
    'extended_art': 'extended',
    'transform': 'transform',
    'retro': 'retro',
    'universes_beyond': 'universes_beyond',
    '1993': 'vintage',
    '1997': 'vintage', 
    '2003': 'classic',
    '2015': 'modern',
    'future': 'future'
}

# Default folder names for frame organization
FRAME_FOLDER_MAP = {
    'showcase': 'showcase',
    'borderless': 'borderless',
    'extended_art': 'extended_art',
    'retro': 'retro',
    'transform': 'transform',
    'universes_beyond': 'universes_beyond',
    'vintage': 'vintage',
    'modern': 'modern',
    'future': 'future',
    'standard': 'standard'
}