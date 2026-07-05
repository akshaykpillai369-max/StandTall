# StandTall Pro

A cross-platform desktop app that reminds you to stand up and rest your eyes, featuring a system tray icon and customizable settings.

## About

StandTall Pro is a health-focused utility designed for people who spend long hours at their desk. Prolonged sitting and screen staring can lead to back pain, poor posture, and digital eye strain. This app runs quietly in your system tray and sends timely reminders to stand up, stretch, and give your eyes a break using the 20-20-20 rule, helping you build healthier work habits without disrupting your flow.

![StandTall Pro Screenshot](<img width="497" height="757" alt="image" src="https://github.com/user-attachments/assets/63583257-d594-4ab3-a7a8-d98d798797b7" />
)

## Features

- **Posture Reminders** — configurable intervals (1-60 min) to remind you to stand up
- **Eye Care (20-20-20 Rule)** — configurable intervals (1-30 min) to remind you to look away from the screen
- **System Tray** — runs in the background with quick access to Settings, Pause/Resume, and Quit
- **Custom Themes** — Dark, Light, and High Contrast
- **Auto-start** — option to launch on system startup
- **Desktop Notifications** — native notifications on Windows, macOS, and Linux
- **Streak Tracking** — shows time since your last break
- **Cross-platform** — works on Windows, macOS, and Linux

## First Launch

On the very first run, the settings window opens automatically so you can configure your preferences. After that, the app starts silently in the system tray. Right-click the tray icon to open Settings at any time.

## Installation

### Windows

**Option 1 — Standalone .exe (recommended, no Python needed)**

1. Download `StandTall Pro.exe` from the release
2. Double-click to run
3. On first launch, the settings window appears — configure your preferences
4. The app will appear in the system tray (near the clock)
5. Right-click the tray icon to access Settings, Pause/Resume, or Quit

**Option 2 — Run from source**

```bash
git clone https://github.com/akshaykpillai369-max/StandTall.git
cd StandTall
pip install -r requirements.txt
python src/main.py
```

### macOS

**Option 1 — Build standalone .app (no Python needed for end users)**

On a Mac with Python 3 installed:

```bash
# Clone the repo
git clone https://github.com/akshaykpillai369-max/StandTall.git
cd StandTall

# Install dependencies
pip3 install -r requirements.txt
pip3 install pyobjc-framework-Cocoa  # required by pystray on macOS

# Build the .app bundle
chmod +x build_mac.sh
./build_mac.sh
```

The standalone app will be at `dist/StandTall Pro.app`. You can:
- Drag it to your **Applications** folder for permanent access
- Right-click and select **Open** (macOS may show a security warning for unsigned apps — go to **System Preferences > Security & Privacy** and click **Open Anyway**)
- On first launch, the settings window appears; after closing it, the app runs in the **menu bar** (top-right of your screen)
- Click the menu bar icon to access Settings

**Option 2 — Run from source (requires Python)**

```bash
git clone https://github.com/akshaykpillai369-max/StandTall.git
cd StandTall
pip3 install -r requirements.txt
pip3 install pyobjc-framework-Cocoa
python3 src/main.py
```

### Linux

**Option 1 — Build standalone executable (no Python needed for end users)**

On a Linux machine with Python 3 installed:

```bash
# Clone the repo
git clone https://github.com/akshaykpillai369-max/StandTall.git
cd StandTall

# Install system dependencies
sudo apt-get install -y python3-tk libnotify-bin  # Debian/Ubuntu
# or: sudo yum install -y python3-tkinter libnotify  # Fedora/RHEL

# Install Python dependencies
pip3 install -r requirements.txt
pip3 install python-xlib  # required by pystray on Linux

# Build the standalone package
chmod +x build_linux.sh
./build_linux.sh
```

The standalone package will be at `dist/StandTall Pro/`. To run it:

```bash
./dist/StandTall\ Pro/StandTall\ Pro
```

You can create a desktop shortcut:
1. Create `~/.local/share/applications/standtall.desktop`:

```ini
[Desktop Entry]
Type=Application
Name=StandTall Pro
Exec=/path/to/dist/StandTall Pro/StandTall Pro
Icon=/path/to/assets/logo.png
Categories=Utility;
```

2. Make it executable: `chmod +x ~/.local/share/applications/standtall.desktop`

On first launch, the settings window appears. After closing it, the app runs in the **system tray** (notification area). Click the tray icon to access Settings.

**Option 2 — Run from source (requires Python)**

```bash
git clone https://github.com/akshaykpillai369-max/StandTall.git
cd StandTall
pip3 install -r requirements.txt
pip3 install python-xlib
python3 src/main.py
```

## Configuration

Settings are stored in `config.json`:

| Key | Default | Description |
|-----|---------|-------------|
| `stand_interval_seconds` | 3600 | Interval between stand reminders (seconds) |
| `eye_care_interval_seconds` | 1200 | Interval between eye care reminders (seconds) |
| `eye_care_duration_seconds` | 20 | Eye break duration (seconds) |
| `theme` | `"dark"` | UI theme (`dark`, `light`, `high_contrast`) |
| `start_on_boot` | `false` | Launch on system startup |
| `notifications_enabled` | `true` | Enable/disable desktop notifications |

## Uninstall

### Windows
1. **Disable auto-start** (if enabled): Open the app Settings and turn off **Start on Windows startup**, or run:
   ```reg
   reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "StandTall Pro" /f
   ```
2. **Delete the app**: Remove the downloaded `StandTall Pro.exe` file
3. **Remove config** (optional): Delete `config.json` from the same folder as the exe

### macOS
1. **Disable auto-start** (if enabled): Remove the LaunchAgent:
   ```bash
   rm ~/Library/LaunchAgents/com.standtall.plist
   ```
2. **Delete the app**: Move `StandTall Pro.app` from Applications to Trash
3. **Remove config** (optional): Delete `config.json` from the same folder as the .app

### Linux
1. **Disable auto-start** (if enabled): Remove the autostart entry:
   ```bash
   rm ~/.config/autostart/standtall.desktop
   ```
2. **Delete the app**: Remove the build folder:
   ```bash
   rm -rf path/to/dist/StandTall\ Pro
   ```
3. **Remove config** (optional): Delete `config.json` from the same folder as the executable

## Tech Stack

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — modern UI
- [pystray](https://github.com/moses-palmer/pystray) — system tray icon
- [Pillow](https://python-pillow.org/) — image processing
- [PyInstaller](https://pyinstaller.org/) — builds standalone packages

## License

MIT
