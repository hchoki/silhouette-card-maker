@echo off
REM Build script for Silhouette Card Maker (Windows)
REM This script creates a standalone executable using PyInstaller

echo ========================================
echo Building Silhouette Card Maker
echo ========================================
echo.

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import requests, PIL, pypdfium2, natsort" 2>nul
if errorlevel 1 (
    echo Dependencies not found. Installing...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller
        echo.
        echo Please ensure Python and pip are properly installed.
        echo You can manually install with: python -m pip install pyinstaller
        pause
        exit /b 1
    )
)

REM Clean previous build
echo Cleaning previous build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the executable
echo.
echo Building executable...
python -m PyInstaller --clean SilhouetteCardMaker.spec

if errorlevel 1 (
    echo.
    echo ========================================
    echo Build FAILED!
    echo ========================================
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build SUCCESSFUL!
echo ========================================
echo.
echo Executable location: dist\SilhouetteCardMaker.exe
echo.
pause
