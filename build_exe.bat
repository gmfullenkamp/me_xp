@echo off
REM === Build Me XP app into a standalone EXE with icon ===

REM Ensure you're in the script directory
cd /d "%~dp0"

REM Clean previous builds
rmdir /s /q dist
rmdir /s /q build
del /q main.spec

REM Build the executable with icon and include asset
pyinstaller ^
  --onefile ^
  --windowed ^
  --icon=assets/icon.ico ^
  --add-data "assets/icon.ico;assets" ^
  main.py

echo.
echo ✅ Build complete! EXE located in the 'dist' folder.
