# Build Tools

This directory contains all files needed to build standalone executables of Silhouette Card Maker.

## Files

- **`SilhouetteCardMaker.spec`** - PyInstaller specification file
- **`build.bat`** - Windows build script
- **`build.sh`** - macOS/Linux build script

## Building

### Windows
```cmd
cd build_tools
build.bat
```

### macOS/Linux
```bash
cd build_tools
chmod +x build.sh
./build.sh
```

## Output Location

The executable is built to the **root folder** (not `dist/`):
- Windows: `SilhouetteCardMaker.exe`
- macOS: `SilhouetteCardMaker.app`
- Linux: `SilhouetteCardMaker`

## Directory Structure After Build

```
silhouette-card-maker/
├── SilhouetteCardMaker.exe     # Built executable (Windows)
├── data/                        # Created on first run - settings/profiles
├── game/                        # Created on first run - card images/PDFs
├── assets/                      # Bundled in exe, extracted on first run
├── calibration/                 # Bundled in exe, extracted on first run
├── cutting_templates/           # Bundled in exe, extracted on first run
├── plugins/                     # Bundled in exe, extracted on first run
└── build_tools/                 # Build scripts (this folder)
```

## How It Works

1. PyInstaller bundles the application and resources into a single executable
2. On first run, bundled resources (`assets/`, `calibration/`, etc.) are extracted to the exe's directory
3. User data directories (`data/`, `game/`) are created next to the exe
4. Everything stays local - no APPDATA, no hidden folders
5. Users can move the entire folder anywhere and it still works

## Requirements

- Python 3.x
- PyInstaller (`pip install pyinstaller`)
- All dependencies from `../requirements.txt`

The build script will automatically install PyInstaller if not present.
