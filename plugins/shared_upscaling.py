"""
Shared upscaling utilities for all plugins.

This module provides common upscaling functionality that can be used across
all card game plugins to enhance downloaded images using Waifu2x AI upscaling.
"""

import os
import sys
import click
from typing import Optional, Callable

# Add the root directory to the path to import utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utilities import upscale_image_with_waifu2x


def add_upscale_options(f):
    """
    Decorator to add standard upscaling options to a Click command.
    
    Usage:
        @add_upscale_options
        @click.command()
        def cli(upscale, upscale_factor, noise_level, ...):
            pass
    """
    f = click.option(
        '--noise_level', 
        default=1, 
        type=click.IntRange(min=-1, max=3), 
        show_default=True, 
        help="Waifu2x noise reduction level (-1=no effect, 0=no denoise, 1=low, 2=medium, 3=high)."
    )(f)
    f = click.option(
        '--upscale_factor', 
        default=2, 
        type=click.IntRange(min=1, max=4), 
        show_default=True, 
        help="Upscale factor for Waifu2x (1=no scaling, 2=2x, 4=4x)."
    )(f)
    f = click.option(
        '--upscale', 
        default=False, 
        is_flag=True, 
        show_default=True, 
        help="Upscale downloaded images using Waifu2x AI upscaling."
    )(f)
    return f


def upscale_if_enabled(
    image_path: str, 
    upscale: bool, 
    upscale_factor: int = 2, 
    noise_level: int = 1
) -> bool:
    """
    Upscale an image if upscaling is enabled.
    
    Args:
        image_path: Path to the image file to upscale
        upscale: Whether upscaling is enabled
        upscale_factor: Upscale ratio (1/2/4, default=2)
        noise_level: Denoise level (-1/0/1/2/3, default=1)
    
    Returns:
        bool: True if upscaling was successful or not needed, False if failed
    """
    if not upscale:
        return True
    
    return upscale_image_with_waifu2x(image_path, upscale_factor, noise_level)


def create_upscaling_wrapper(original_fetch_function: Callable):
    """
    Create a wrapper around an image fetching function to add upscaling support.
    
    Args:
        original_fetch_function: The original function that downloads/saves images
    
    Returns:
        A new function that includes upscaling functionality
    """
    def wrapper(*args, upscale=False, upscale_factor=2, noise_level=1, **kwargs):
        # Call the original function
        result = original_fetch_function(*args, **kwargs)
        
        # If the original function returned image paths, upscale them
        if isinstance(result, str) and os.path.exists(result):
            # Single image path returned
            upscale_if_enabled(result, upscale, upscale_factor, noise_level)
        elif isinstance(result, (list, tuple)):
            # Multiple image paths returned
            for path in result:
                if isinstance(path, str) and os.path.exists(path):
                    upscale_if_enabled(path, upscale, upscale_factor, noise_level)
        
        return result
    
    return wrapper


def upscale_directory_images(
    directory_path: str, 
    upscale: bool, 
    upscale_factor: int = 2, 
    noise_level: int = 1,
    file_pattern: str = "*.png"
) -> int:
    """
    Upscale all images in a directory that match a pattern.
    
    Args:
        directory_path: Path to the directory containing images
        upscale: Whether upscaling is enabled
        upscale_factor: Upscale ratio (1/2/4, default=2)
        noise_level: Denoise level (-1/0/1/2/3, default=1)
        file_pattern: Glob pattern for image files (default="*.png")
    
    Returns:
        int: Number of images successfully upscaled
    """
    if not upscale or not os.path.exists(directory_path):
        return 0
    
    import glob
    
    image_files = glob.glob(os.path.join(directory_path, file_pattern))
    successful_upscales = 0
    
    for image_path in image_files:
        if upscale_image_with_waifu2x(image_path, upscale_factor, noise_level):
            successful_upscales += 1
    
    return successful_upscales


# Convenience function for common use cases
def add_upscaling_to_fetch_function(fetch_func, image_path_getter=None):
    """
    Decorator factory to add upscaling to existing fetch functions.
    
    Args:
        fetch_func: The function to wrap
        image_path_getter: Optional function to extract image path from fetch_func result
    
    Returns:
        Decorated function with upscaling support
    """
    def decorator(upscale=False, upscale_factor=2, noise_level=1):
        def wrapper(*args, **kwargs):
            result = fetch_func(*args, **kwargs)
            
            if upscale:
                if image_path_getter:
                    image_path = image_path_getter(result, *args, **kwargs)
                else:
                    # Try to extract image path from common locations in args
                    image_path = None
                    for arg in args:
                        if isinstance(arg, str) and (arg.endswith('.png') or arg.endswith('.jpg') or arg.endswith('.jpeg')):
                            image_path = arg
                            break
                
                if image_path and os.path.exists(image_path):
                    upscale_image_with_waifu2x(image_path, upscale_factor, noise_level)
            
            return result
        return wrapper
    return decorator