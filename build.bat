@echo off
echo Building StandTall Pro...
echo.

echo Step 1: Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b %errorlevel%
)

echo.
echo Step 2: Running PyInstaller...
pyinstaller --onedir --windowed ^
    --name "StandTall Pro" ^
    --icon assets\icon.ico ^
    --paths src ^
    --add-data "themes;themes" ^
    --add-data "assets;assets" ^
    src\main.py

if %errorlevel% neq 0 (
    echo Build failed.
    pause
    exit /b %errorlevel%
)

echo.
echo Build complete! Executable is in the dist\ folder.
pause
