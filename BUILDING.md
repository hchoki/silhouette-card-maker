# Building Silhouette Card Maker

This guide explains how to build standalone executables for Silhouette Card Maker.

## For End Users

Download pre-built executables from the [Releases](https://github.com/hchoki/silhouette-card-maker/releases) page:
- **Windows**: Download `SilhouetteCardMaker.exe`
- **macOS**: Download `SilhouetteCardMaker-macOS.dmg`
- **Linux**: Download `SilhouetteCardMaker-Linux.tar.gz`

No Python installation required!

## For Developers

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Quick Build

All build files are in the `build_tools/` directory.

#### Windows
```bash
cd build_tools
build.bat
```

Or from the root:
```bash
build.bat
```

#### macOS/Linux
```bash
cd build_tools
chmod +x build.sh
./build.sh
```

Or from the root:
```bash
chmod +x build.sh
./build.sh
```

**Output Location**: The executable is created in the **root folder** (not `dist/`):
- Windows: `SilhouetteCardMaker.exe`
- macOS: `SilhouetteCardMaker.app`
- Linux: `SilhouetteCardMaker`

### Manual Build

1. **Install dependencies first:**
```bash
pip install -r requirements.txt
```

2. Install PyInstaller:
```bash
pip install pyinstaller
```

3. Build the executable:
```bash
cd build_tools
pyinstaller --clean --distpath .. --workpath build SilhouetteCardMaker.spec
```

**Important:** You must install all project dependencies from `requirements.txt` before building, as PyInstaller needs them to bundle into the executable.

### Customization

Edit `build_tools/SilhouetteCardMaker.spec` to customize:
- Add an application icon
- Include/exclude specific files
- Adjust build settings
- Add hidden imports for plugins

## Automated Builds (GitHub Actions)

Releases are automatically built for all platforms when you push a version tag:

```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

This triggers GitHub Actions to build executables for:
- Windows (`.exe`)
- macOS (`.dmg`)
- Linux (`.tar.gz`)

## File Size

Typical executable sizes:
- Windows: ~80-120 MB
- macOS: ~90-130 MB
- Linux: ~85-115 MB

The executables include:
- Python interpreter
- All dependencies (Pillow, requests, pypdf, etc.)
- GUI framework (Tkinter)
- All plugins and assets
- Bundled resources (calibration PDFs, cutting templates)

## Directory Structure

The application uses **local directories only** - both when running from source and as a packaged executable:

```
silhouette-card-maker/          # Root folder
├── SilhouetteCardMaker.exe     # Built executable (Windows)
├── data/                        # Settings and offset profiles (created on first run)
│   ├── gui_settings.json
│   └── offset_profiles.json
├── game/                        # User's card images and PDFs (created on first run)
│   ├── front/
│   ├── back/
│   ├── double_sided/
│   ├── output/
│   └── decklist/
├── assets/                      # Registration marks, fonts (bundled in exe)
├── calibration/                 # Calibration PDFs (bundled in exe)
├── cutting_templates/           # Silhouette Studio files (bundled in exe)
├── plugins/                     # Game plugins (bundled in exe)
└── build_tools/                 # Build scripts and spec file
    ├── SilhouetteCardMaker.spec
    ├── build.bat
    ├── build.sh
    └── README.md
```

### Bundled Resources
These are packed into the executable and extracted to the exe's directory on first run:

- **assets/** - Fonts (arial.ttf), layouts (layouts.json), registration mark images
- **calibration/** - Printer offset calibration PDFs
- **cutting_templates/** - Silhouette Studio cutting files (`.studio3`)
- **plugins/** - Game-specific card fetching plugins

### User Data (Local Directories)
Created next to the executable on first run:

- **data/** - Settings and offset profiles
  - `gui_settings.json` - GUI preferences  
  - `offset_profiles.json` - Printer offset profiles

- **game/** - User's card images and generated PDFs
  - `front/` - Card front images
  - `back/` - Card back images
  - `double_sided/` - Double-sided card images
  - `output/` - Generated PDFs
  - `decklist/` - Deck list files

### Benefits of Local Directory Structure

✅ **Portable**: Move the entire folder anywhere and it still works
✅ **Simple**: Everything in one location, no hidden APPDATA folders
✅ **Easy Backup**: Just copy the folder to backup everything
✅ **Multi-Instance**: Users can have multiple copies with different data
✅ **Consistent**: Identical behavior whether running from source or as exe

## Troubleshooting

### Antivirus Warnings
Some antivirus software may flag PyInstaller executables. This is a false positive. To resolve:
- Add an exception in your antivirus
- Code-sign the executable (Windows/macOS)

### Missing Dependencies
If the built executable fails with import errors, add the missing module to `hiddenimports` in `build_tools/SilhouetteCardMaker.spec`

### Large File Size
To reduce size:
- Use UPX compression (already enabled in spec file)
- Exclude unused packages in the spec file
- Consider using Nuitka instead of PyInstaller

### Slow Startup
First launch may be slower as PyInstaller unpacks files. Subsequent launches are faster.

## Development Workflow

1. Make changes to the code
2. Test with `python gui.py`
3. Build executable: `cd build_tools && build.bat` (or `build.sh`)
4. Test the executable in the root folder
5. Create a release tag to trigger automated builds
