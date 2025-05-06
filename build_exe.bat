@echo off
REM === Build Me XP app into a standalone EXE with icon ===

REM Go to project root
cd /d "%~dp0"

REM Clean previous builds
rmdir /s /q dist
rmdir /s /q build
del /q main.spec

REM Set PYTHONPATH to current dir
set PYTHONPATH=%cd%

REM Build the executable with included icon and UI/Core modules
pyinstaller ^
  --onefile ^
  --windowed ^
  --icon=assets/icon.ico ^
  --add-data "assets;assets" ^
  --add-data "data;data" ^
  --add-data "specializations;specializations" ^
  "Me XP.py"

echo.
echo ✅ Build complete! EXE located in the 'dist' folder.