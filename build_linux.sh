#!/bin/bash
set -e

echo "=== StandTall Pro - Linux Build ==="
echo ""

# Step 1: Install system dependencies (may need sudo)
echo "Checking system dependencies..."
if ! command -v notify-send &>/dev/null; then
    echo "Installing libnotify (needed for desktop notifications)..."
    sudo apt-get install -y libnotify-bin 2>/dev/null || sudo yum install -y libnotify 2>/dev/null || true
fi

# Step 2: Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt
pip3 install python-xlib  # Required by pystray on Linux

# Step 3: Build with PyInstaller
echo ""
echo "Building StandTall Pro..."
pyinstaller --onedir --windowed --noconfirm \
    --name "StandTall Pro" \
    --icon assets/icon.png \
    --paths src \
    --add-data "themes:themes" \
    --add-data "assets:assets" \
    src/main.py

# Step 4: Notify user
echo ""
echo "Build complete! Executable is at: dist/StandTall Pro/"
echo "Run it with: ./dist/StandTall\\ Pro/StandTall\\ Pro"
