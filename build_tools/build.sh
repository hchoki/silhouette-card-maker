#!/bin/bash
# Build script for Silhouette Card Maker (macOS/Linux)
# This script creates a standalone executable using PyInstaller
# The executable/app will be output to the root folder (not dist/)

echo "========================================"
echo "Building Silhouette Card Maker"
echo "========================================"
echo ""

# Change to the build_tools directory
cd "$(dirname "$0")"

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller not found. Installing..."
    pip3 install pyinstaller
    if [ $? -ne 0 ]; then
        echo "Failed to install PyInstaller"
        exit 1
    fi
fi

# Clean previous build
echo "Cleaning previous build..."
rm -rf build dist
if [[ "$OSTYPE" == "darwin"* ]]; then
    rm -rf ../SilhouetteCardMaker.app
else
    rm -f ../SilhouetteCardMaker
fi

# Build the executable
echo ""
echo "Building executable..."
pyinstaller --clean --distpath .. --workpath build SilhouetteCardMaker.spec

if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "Build FAILED!"
    echo "========================================"
    exit 1
fi

# Clean up build artifacts
echo ""
echo "Cleaning up build artifacts..."
rm -rf build

echo ""
echo "========================================"
echo "Build SUCCESSFUL!"
echo "========================================"
echo ""

if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Application location: ../SilhouetteCardMaker.app"
    echo ""
    echo "The app will use these local directories:"
    echo "  - ../data/        (settings and offset profiles)"
    echo "  - ../game/        (card images and output PDFs)"
    echo "  - ../assets/      (registration marks, bundled in app)"
    echo "  - ../calibration/ (calibration PDFs, bundled in app)"
else
    echo "Executable location: ../SilhouetteCardMaker"
    echo ""
    echo "The executable will use these local directories:"
    echo "  - ../data/        (settings and offset profiles)"
    echo "  - ../game/        (card images and output PDFs)"
    echo "  - ../assets/      (registration marks, bundled)"
    echo "  - ../calibration/ (calibration PDFs, bundled)"
fi
echo ""
