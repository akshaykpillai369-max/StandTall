import os
import sys
import json
import threading
import tempfile
import time
import platform
from typing import Optional

import pystray
from PIL import Image, ImageDraw

from logic import TimerEngine, TimerConfig
from paths import config_path, project_root
from notify import notify


_signal_path = os.path.join(tempfile.gettempdir(), "StandTallPro.show")
_ui_signal_path = os.path.join(tempfile.gettempdir(), "StandTallPro.open_ui")
_lock_dir = os.path.join(tempfile.gettempdir(), ".standtall-lock")


class StandTallApp:
    def __init__(self):
        self.config = self._load_config()
        self.timer_config = TimerConfig(
            stand_interval_seconds=self.config.get("stand_interval_seconds", 3600),
            eye_care_interval_seconds=self.config.get("eye_care_interval_seconds", 1200),
            eye_care_duration_seconds=self.config.get("eye_care_duration_seconds", 20),
            notifications_enabled=self.config.get("notifications_enabled", True),
        )
        self.engine = TimerEngine(self.timer_config)
        self.engine.on_stand_reminder = lambda m: notify("StandTall Pro", m)
        self.engine.on_eye_care_reminder = lambda m: notify("StandTall Pro \u2014 Eye Care", m)

        self._tray_icon: Optional[pystray.Icon] = None
        self._ui_window = None
        self.root = None

    # ── config ──────────────────────────────────────────────────────

    def _load_config(self) -> dict:
        path = config_path()
        defaults = {
            "stand_interval_seconds": 3600,
            "eye_care_interval_seconds": 1200,
            "eye_care_duration_seconds": 20,
            "theme": "dark",
            "start_on_boot": False,
            "notifications_enabled": True,
            "first_launch": True,
        }
        try:
            with open(path, "r") as f:
                cfg = json.load(f)
                for k, v in defaults.items():
                    cfg.setdefault(k, v)
            return cfg
        except (FileNotFoundError, json.JSONDecodeError):
            try:
                with open(path, "w") as f:
                    json.dump(defaults, f, indent=4)
            except Exception:
                pass
            return dict(defaults)

    def _save_config(self):
        try:
            with open(config_path(), "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception:
            pass

    def _enable_startup(self, enabled: bool):
        system = platform.system()
        try:
            if system == "Windows":
                import winreg
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run",
                    0, winreg.KEY_SET_VALUE)
                if enabled:
                    winreg.SetValueEx(key, "StandTall Pro", 0, winreg.REG_SZ, sys.executable)
                else:
                    try: winreg.DeleteValue(key, "StandTall Pro")
                    except FileNotFoundError: pass
                winreg.CloseKey(key)
            elif system == "Darwin":
                plist = os.path.expanduser("~/Library/LaunchAgents/com.standtall.plist")
                if enabled:
                    content = (
                        '<?xml version="1.0" encoding="UTF-8"?>\n'
                        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
                        '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
                        '<plist version="1.0"><dict>'
                        "<key>Label</key><string>com.standtall</string>"
                        "<key>ProgramArguments</key><array>"
                        f"<string>{sys.executable}</string>"
                        "</array>"
                        "<key>RunAtLoad</key><true/>"
                        "</dict></plist>"
                    )
                    with open(plist, "w") as f:
                        f.write(content)
                else:
                    try: os.unlink(plist)
                    except FileNotFoundError: pass
            elif system == "Linux":
                desktop = os.path.expanduser("~/.config/autostart/standtall.desktop")
                if enabled:
                    content = (
                        "[Desktop Entry]\n"
                        "Type=Application\n"
                        "Name=StandTall Pro\n"
                        f"Exec={sys.executable}\n"
                        "X-GNOME-Autostart-enabled=true\n"
                    )
                    os.makedirs(os.path.dirname(desktop), exist_ok=True)
                    with open(desktop, "w") as f:
                        f.write(content)
                else:
                    try: os.unlink(desktop)
                    except FileNotFoundError: pass
        except Exception:
            pass

    # ── tray icon ───────────────────────────────────────────────────

    def _create_tray_image(self):
        png_path = os.path.join(project_root(), "assets", "logo.png")
        if os.path.exists(png_path):
            try:
                img = Image.open(png_path).convert("RGBA")
                w, h = img.size
                side = min(w, h)
                left = (w - side) // 2
                top = (h - side) // 2
                img = img.crop((left, top, left + side, top + side))
                return img.resize((64, 64), Image.Resampling.LANCZOS)
            except Exception:
                pass

        size = 64
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse([2, 2, size - 2, size - 2], fill="#1A1A2E")
        draw.ellipse([2, 2, size - 2, size - 2], outline="#2A2A4A", width=1)
        cx1 = size // 4
        cy = size // 2
        hr = 5
        draw.ellipse([cx1 - hr, cy - hr - 6, cx1 + hr, cy - 6], fill="#4CAF50")
        draw.rectangle([cx1 - 2, cy - 6, cx1 + 2, cy + 5], fill="#4CAF50")
        draw.line([cx1 - 8, cy - 2, cx1 + 8, cy - 2], fill="#4CAF50", width=2)
        draw.line([cx1, cy + 5, cx1 - 6, cy + 14], fill="#4CAF50", width=2)
        draw.line([cx1, cy + 5, cx1 + 6, cy + 14], fill="#4CAF50", width=2)
        cx2 = 3 * size // 4
        draw.arc([cx2 - 8, cy - 5, cx2 + 8, cy + 5], 0, 360, fill="#FFB300", width=2)
        draw.ellipse([cx2 - 3, cy - 2, cx2 + 3, cy + 2], fill="#FFB300")
        return image

    def _on_tray_settings(self, icon, item):
        try:
            with open(_ui_signal_path, "w") as f:
                f.write("")
        except Exception:
            pass

    def _on_tray_quit(self, icon, item):
        self.engine.stop()
        icon.stop()
        os._exit(0)

    def _on_tray_pause(self, icon, item):
        if self.engine.is_paused:
            self.engine.resume()
            icon.title = "StandTall Pro"
        else:
            self.engine.pause()
            icon.title = "StandTall Pro [PAUSED]"

    # ── settings UI (lazy customtkinter) ────────────────────────────

    def _open_ui(self):
        if self._ui_window is not None and self._ui_window.winfo_exists():
            self._ui_window.deiconify()
            self._ui_window.lift()
            self._ui_window.focus()
            return

        try:
            os.remove(_ui_signal_path)
        except Exception:
            pass

        import customtkinter as ctk

        self.root = ctk.CTk()
        self.root.withdraw()

        ico_path = os.path.join(project_root(), "assets", "icon.ico")
        png_path = os.path.join(project_root(), "assets", "logo.png")
        icon_path = ico_path if os.path.exists(ico_path) else png_path
        if os.path.exists(icon_path):
            try:
                from PIL import ImageTk
                img = Image.open(icon_path).convert("RGBA")
                self.root.iconphoto(True, ImageTk.PhotoImage(img))
            except Exception:
                pass

        from ui import SettingsWindow
        self._ui_window = SettingsWindow(self)
        self._ui_window.protocol("WM_DELETE_WINDOW", self._on_close_ui)

        self.root.after(500, self._poll_signals)
        self.root.mainloop()

        self.root.destroy()
        self.root = None
        self._ui_window = None

    def _on_close_ui(self):
        try:
            os.remove(_ui_signal_path)
        except Exception:
            pass
        if self._ui_window is not None:
            self._ui_window.withdraw()
        if self.root:
            self.root.quit()

    def _poll_signals(self):
        for path in (_signal_path, _ui_signal_path):
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass
                self._open_ui()
                return
        if self.root:
            self.root.after(500, self._poll_signals)

    # ── public API ──────────────────────────────────────────────────

    def update_config(self, key: str, value):
        self.config[key] = value
        self._save_config()
        if key == "stand_interval_seconds":
            self.timer_config.stand_interval_seconds = value
        elif key == "eye_care_interval_seconds":
            self.timer_config.eye_care_interval_seconds = value
        elif key == "eye_care_duration_seconds":
            self.timer_config.eye_care_duration_seconds = value
        elif key == "notifications_enabled":
            self.timer_config.notifications_enabled = value
        elif key == "start_on_boot":
            self._enable_startup(value)

    def run(self):
        self.engine.start()

        image = self._create_tray_image()
        menu = pystray.Menu(
            pystray.MenuItem("Settings", self._on_tray_settings),
            pystray.MenuItem("Pause / Resume", self._on_tray_pause),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._on_tray_quit),
        )
        self._tray_icon = pystray.Icon("StandTall Pro", image, "StandTall Pro", menu)
        threading.Thread(target=self._tray_icon.run, daemon=True).start()

        if self.config.get("first_launch", True):
            self.config["first_launch"] = False
            self._save_config()

        time.sleep(0.5)
        self._open_ui()

        while True:
            for path in (_signal_path, _ui_signal_path):
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except Exception:
                        pass
                    self._open_ui()
            time.sleep(0.5)


def _acquire_lock() -> bool:
    try:
        os.mkdir(_lock_dir)
        return True
    except FileExistsError:
        return False


def _release_lock():
    try:
        os.rmdir(_lock_dir)
    except Exception:
        pass


if __name__ == "__main__":
    if not _acquire_lock():
        try:
            with open(_signal_path, "w") as f:
                f.write("show")
        except Exception:
            pass
        sys.exit(0)

    import atexit
    atexit.register(_release_lock)

    app = StandTallApp()
    app.run()
