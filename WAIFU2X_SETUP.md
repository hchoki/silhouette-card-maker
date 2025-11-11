# Waifu2x Minimal Setup Instructions

The AI upscaling functionality requires a minimal Waifu2x installation. This document explains how to set it up.

## Quick Setup

1. **Download Waifu2x-Extension-GUI** from: https://github.com/AaronFeng753/Waifu2x-Extension-GUI/releases

2. **Extract the downloaded archive** to a temporary location

3. **Create minimal installation** by copying only the essential files:

```bash
# Create the minimal directory
mkdir waifu2x-minimal

# Copy the executable
cp "Waifu2x-Extension-GUI-*/waifu2x-extension-gui/waifu2x-ncnn-vulkan/waifu2x-ncnn-vulkan_waifu2xEX.exe" waifu2x-minimal/

# Copy required DLLs
cp "Waifu2x-Extension-GUI-*/waifu2x-extension-gui/waifu2x-ncnn-vulkan/"*.dll waifu2x-minimal/

# Copy AI models
cp -r "Waifu2x-Extension-GUI-*/waifu2x-extension-gui/waifu2x-ncnn-vulkan/models-cunet" waifu2x-minimal/

# Copy license files
cp "Waifu2x-Extension-GUI-*/waifu2x-extension-gui/waifu2x-ncnn-vulkan/LICENSE" waifu2x-minimal/
cp "Waifu2x-Extension-GUI-*/waifu2x-extension-gui/waifu2x-ncnn-vulkan/README.md" waifu2x-minimal/
```

4. **Remove the temporary extraction** (optional - saves ~4.6GB of disk space)

## What's Included

The minimal installation contains only the essential files needed for command-line operation:

- `waifu2x-ncnn-vulkan_waifu2xEX.exe` - Main executable
- `*.dll` - Required runtime libraries  
- `models-cunet/` - AI models for upscaling
- `LICENSE` & `README.md` - Documentation

## Size Comparison

- **Full Installation**: ~4.6 GB (738 files)
- **Minimal Installation**: ~32 MB (25 files)
- **Space Saved**: 99.3% reduction!

## Verification

Test the installation by running any plugin with upscaling:

```bash
# Test with MTG plugin
python plugins/mtg/fetch.py deck.txt simple --upscale --upscale_factor 2

# Test with YuGiOh plugin  
python plugins/yugioh/fetch.py deck.ydk ydk --upscale --upscale_factor 2

# Test with Lorcana plugin
python plugins/lorcana/fetch.py deck.txt dreamborn --upscale --upscale_factor 2
```

If you see "Successfully upscaled image: [filename]" messages, the setup is working correctly.

## Troubleshooting

### "Waifu2x executable not found"
- Ensure `waifu2x-minimal/` folder exists in the project root
- Verify `waifu2x-ncnn-vulkan_waifu2xEX.exe` is in the folder
- Check file permissions (should be executable)

### "Missing DLL" errors
- Ensure all `.dll` files are copied to `waifu2x-minimal/`
- Install Visual C++ Redistributable if needed

### "Model not found" errors
- Verify `models-cunet/` folder exists and contains `.bin` and `.param` files
- Check that folder structure is: `waifu2x-minimal/models-cunet/[model files]`

## Advanced Configuration

You can specify a custom Waifu2x path by modifying the `upscale_image_with_waifu2x` function in `utilities.py` or by setting the `waifu2x_path` parameter when calling the function directly.

## System Requirements

- **OS**: Windows 64-bit
- **GPU**: Vulkan-compatible GPU recommended (NVIDIA, AMD, or Intel)
- **CPU**: Will fall back to CPU mode if GPU unavailable
- **RAM**: 4GB+ recommended for 2x upscaling, 8GB+ for 4x upscaling