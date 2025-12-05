#!/bin/bash
# Build script for Silhouette Card Maker (macOS/Linux)
# This script creates a standalone executable using PyInstaller

echo "========================================"
echo "Building Silhouette Card Maker"
echo "========================================"
echo ""

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

# Build the executable
echo ""
echo "Building executable..."
pyinstaller --clean SilhouetteCardMaker.spec

if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "Build FAILED!"
    echo "========================================"
    exit 1
fi

echo ""
echo "========================================"
echo "Build SUCCESSFUL!"
echo "========================================"
echo ""
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Application location: dist/SilhouetteCardMaker.app"
else
    echo "Executable location: dist/SilhouetteCardMaker"
fi
echo ""
