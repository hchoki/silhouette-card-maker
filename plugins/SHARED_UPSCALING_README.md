# Shared Upscaling System

This document describes the shared upscaling system that provides AI-powered image enhancement across all card game plugins.

## Overview

The shared upscaling system allows all plugins to easily add Waifu2x AI upscaling support to their image downloading functionality. This provides consistent upscaling options and behavior across all supported card games.

## Features

- **Consistent CLI Options**: All plugins get the same upscaling command-line options
- **Easy Integration**: Simple decorator-based system for adding upscaling to existing plugins
- **Flexible Configuration**: Configurable upscale factors and noise reduction levels
- **Error Handling**: Robust error handling and fallback behavior
- **Performance Optimization**: GPU acceleration when available

## Supported Plugins

The following plugins now support AI upscaling:

- ✅ **MTG (Magic: The Gathering)**: Full upscaling support for all card types
- ✅ **Lorcana**: Upscaling support for card images  
- ✅ **YuGiOh**: Upscaling support for card artwork
- ✅ **One Piece**: Upscaling support for card images
- 🔲 **Flesh and Blood**: *Pending implementation*
- 🔲 **Grand Archive**: *Pending implementation* 
- 🔲 **Gundam**: *Pending implementation*
- 🔲 **Netrunner**: *Pending implementation*
- 🔲 **Riftbound**: *Pending implementation*
- 🔲 **Star Wars Unlimited**: *Pending implementation*
- 🔲 **Altered**: *Pending implementation*
- 🔲 **Digimon**: *Pending implementation*

## Usage

All supported plugins now include these upscaling options:

```bash
# Basic upscaling (2x scale, low noise reduction)
python plugins/[game]/fetch.py deck.txt format --upscale

# High quality upscaling (4x scale, high noise reduction)
python plugins/[game]/fetch.py deck.txt format --upscale --upscale_factor 4 --noise_level 3

# Custom settings
python plugins/[game]/fetch.py deck.txt format --upscale --upscale_factor 2 --noise_level 0
```

### Command Line Options

- `--upscale`: Enable AI upscaling (disabled by default)
- `--upscale_factor`: Choose the upscaling factor:
  - `1`: No scaling (original size)
  - `2`: Double the resolution (default)
  - `4`: Quadruple the resolution (highest quality)
- `--noise_level`: Control noise reduction:
  - `-1`: No effect
  - `0`: No denoising
  - `1`: Low noise reduction (default)
  - `2`: Medium noise reduction
  - `3`: High noise reduction (best for heavily compressed images)

## Examples by Game

### Magic: The Gathering
```bash
# Fetch MTG cards with 2x upscaling
python plugins/mtg/fetch.py deck.txt mtga --upscale

# High quality upscaling with showcase preferences
python plugins/mtg/fetch.py deck.txt moxfield --upscale --upscale_factor 4 --prefer_showcase
```

### Disney Lorcana
```bash
# Fetch Lorcana cards with upscaling
python plugins/lorcana/fetch.py deck.txt dreamborn --upscale --upscale_factor 2
```

### Yu-Gi-Oh!
```bash
# Fetch YuGiOh cards with high quality upscaling
python plugins/yugioh/fetch.py deck.ydk ydk --upscale --upscale_factor 4 --noise_level 3
```

### One Piece
```bash
# Fetch One Piece cards with upscaling
python plugins/one_piece/fetch.py deck.txt format --upscale
```

## Technical Implementation

The shared system consists of:

1. **shared_upscaling.py**: Core upscaling utilities and decorators
2. **utilities.py**: Base upscaling function using Waifu2x
3. **Plugin Integration**: Each plugin imports and uses the shared system

### For Plugin Developers

To add upscaling support to a new plugin:

1. Import the shared upscaling module:
```python
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared_upscaling import add_upscale_options
```

2. Add the decorator to your CLI command:
```python
@add_upscale_options
@click.command()
def cli(..., upscale: bool, upscale_factor: int, noise_level: int):
```

3. Call upscaling after saving images:
```python
from shared_upscaling import upscale_if_enabled

# After saving an image
upscale_if_enabled(image_path, upscale, upscale_factor, noise_level)
```

## Performance Notes

- **Processing Time**: Upscaling typically takes 10-30 seconds per image
- **File Sizes**: Upscaled images are 3-4x larger for 2x scaling, 8-16x larger for 4x scaling
- **GPU Acceleration**: Automatically uses GPU when available for faster processing
- **Memory Usage**: Higher upscale factors require more GPU memory
- **Disk Space**: Consider available disk space when using high upscale factors

## Requirements

- Waifu2x-Extension-GUI installed in the project root directory
- Compatible GPU for optimal performance (optional, will fall back to CPU)
- Sufficient disk space for larger upscaled images

## Troubleshooting

### Common Issues

1. **"Waifu2x executable not found"**
   - Ensure Waifu2x-Extension-GUI is installed in the correct directory
   - Check that the executable path is correct

2. **"Upscaling timed out"**
   - Large images or high upscale factors may take longer
   - Try reducing the upscale factor or noise level

3. **"GPU out of memory"**
   - Reduce upscale factor from 4x to 2x
   - Close other GPU-intensive applications
   - Use CPU mode if necessary (slower but more stable)

### Performance Tips

- Use 2x upscaling for most cases (good quality/speed balance)
- Use 4x upscaling only for final high-quality prints
- Higher noise levels help with heavily compressed source images
- Process smaller batches to avoid memory issues