# StandTall Pro

A Windows desktop app that reminds you to stand up and rest your eyes, featuring a system tray icon and customizable settings.

## About

StandTall Pro is a health-focused utility designed for people who spend long hours at their desk. Prolonged sitting and screen staring can lead to back pain, poor posture, and digital eye strain. This app runs quietly in your system tray and sends timely reminders to stand up, stretch, and give your eyes a break using the 20-20-20 rule — helping you build healthier work habits without disrupting your flow.

![StandTall Pro Screenshot](screenshot.png)

## Features

- **Posture Reminders** — configurable intervals (1–60 min) to remind you to stand up
- **Eye Care (20-20-20 Rule)** — configurable intervals (1–30 min) to remind you to look away from the screen
- **System Tray** — runs in the background with quick access to Settings, Pause/Resume, and Quit
- **Custom Themes** — Dark, Light, and High Contrast
- **Auto-start** — option to launch on Windows startup
- **Desktop Notifications** — native Windows balloon notifications
- **Streak Tracking** — shows time since your last break

## Getting Started

### Prerequisites

- Python 3.8+
- Windows (uses Win32 API for notifications and single-instance)

### Installation

```bash
# Clone the repo
git clone https://github.com/akshaykpillai369-max/StandTall.git
cd StandTall

# Install dependencies
pip install -r requirements.txt
```

### Run

```bash
python src/main.py
```

### Build to .exe

```bash
build.bat
```

The executable will be created in the `dist/` folder.

### Alternative installation methods

1, Download the zip file from the assets
2, Unzip it
3, Open the exe file
4, It does not show any windows at first; look at the system tray and right-click the application, then select Settings
5, Done. Now  you can adjust the remainder
## Configuration

Settings are stored in `config.json`:

| Key | Default | Description |
|-----|---------|-------------|
| `stand_interval_seconds` | 3600 | Interval between stand reminders (seconds) |
| `eye_care_interval_seconds` | 60 | Interval between eye care reminders (seconds) |
| `eye_care_duration_seconds` | 20 | Eye break duration (seconds) |
| `theme` | `"dark"` | UI theme (`dark`, `light`, `high_contrast`) |
| `start_on_boot` | `false` | Launch on Windows startup |
| `notifications_enabled` | `true` | Enable/disable desktop notifications |

## Tech Stack

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — modern UI
- [pystray](https://github.com/moses-palmer/pystray) — system tray icon
- [Pillow](https://python-pillow.org/) — image processing
- PyInstaller — builds to standalone .exe

## License

MIT
