#!/bin/bash
# Build script for Silhouette Card Maker (macOS/Linux)
# This script redirects to the build_tools folder

echo "========================================"
echo "Silhouette Card Maker - Build Script"
echo "========================================"
echo ""
echo "Build files have been moved to: build_tools/"
echo "Redirecting to: build_tools/build.sh"
echo ""

# Change to build_tools directory and run the build script
cd "$(dirname "$0")/build_tools"
chmod +x build.sh
./build.sh

# Return to original directory
cd ..
