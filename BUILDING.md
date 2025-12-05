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

#### Windows
```bash
build.bat
```

#### macOS/Linux
```bash
chmod +x build.sh
./build.sh
```

The executable will be created in the `dist/` folder.

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
pyinstaller --clean SilhouetteCardMaker.spec
```

**Important:** You must install all project dependencies from `requirements.txt` before building, as PyInstaller needs them to bundle into the executable.

### Customization

Edit `SilhouetteCardMaker.spec` to customize:
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

## Troubleshooting

### Antivirus Warnings
Some antivirus software may flag PyInstaller executables. This is a false positive. To resolve:
- Add an exception in your antivirus
- Code-sign the executable (Windows/macOS)

### Missing Dependencies
If the built executable fails with import errors, add the missing module to `hiddenimports` in `SilhouetteCardMaker.spec`

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
3. Build executable with build script
4. Test the executable thoroughly
5. Create a release tag to trigger automated builds
