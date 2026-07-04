#!/bin/bash
set -e

echo "=== StandTall Pro - macOS Build ==="
echo ""

# Step 1: Install Python dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt
pip3 install pyobjc-framework-Cocoa  # Required by pystray on macOS

# Step 2: Build with PyInstaller
echo ""
echo "Building StandTall Pro.app..."
pyinstaller --onedir --windowed --noconfirm \
    --name "StandTall Pro" \
    --icon assets/icon.icns \
    --paths src \
    --add-data "themes:themes" \
    --add-data "assets:assets" \
    src/main.py

# Step 3: Notify user
echo ""
echo "Build complete! App bundle is at: dist/StandTall Pro.app"
echo "You can drag it to your Applications folder."
