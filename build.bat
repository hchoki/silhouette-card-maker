@echo off
REM Build script for Silhouette Card Maker (Windows)
REM This script redirects to the build_tools folder

echo ========================================
echo Silhouette Card Maker - Build Script
echo ========================================
echo.
echo Build files have been moved to: build_tools\
echo Redirecting to: build_tools\build.bat
echo.

REM Change to build_tools directory and run the build script
cd /d "%~dp0\build_tools"
call build.bat

REM Return to original directory
cd /d "%~dp0"
