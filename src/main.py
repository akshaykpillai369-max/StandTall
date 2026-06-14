import os
import sys
import json
import ctypes
import threading
import winreg
import tempfile
from typing import Optional

import pystray
from PIL import Image, ImageDraw
import customtkinter as ctk

from logic import TimerEngine, TimerConfig
from paths import resource_path, config_path
from notify import notify, initialize as init_notifier

# Single-instance: signal file path
_signal_path = os.path.join(tempfile.gettempdir(), "StandTallPro.show")


class StandTallApp:
    def __init__(self):
        self.config = self._load_config()
        self.timer_config = TimerConfig(
            stand_interval_seconds=self.config.get("stand_interval_seconds", 30),
            eye_care_interval_seconds=self.config.get("eye_care_interval_seconds", 30),
            eye_care_duration_seconds=self.config.get("eye_care_duration_seconds", 20),
            notifications_enabled=self.config.get("notifications_enabled", True),
        )
        self.engine = TimerEngine(self.timer_config)
        self.engine.on_stand_reminder = self._notify_stand
        self.engine.on_eye_care_reminder = self._notify_eye_care

        self._tray_icon: Optional[pystray.Icon] = None
        self._ui_window = None
        self.root: Optional[ctk.CTk] = None

    def _load_config(self) -> dict:
        path = config_path()
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            result = {
                "stand_interval_seconds": 30,
                "eye_care_interval_seconds": 30,
                "eye_care_duration_seconds": 20,
                "theme": "dark",
                "start_on_boot": False,
                "notifications_enabled": True,
            }
            try:
                with open(path, "w") as f:
                    json.dump(result, f, indent=4)
            except Exception:
                pass
            return result

    def _save_config(self):
        path = config_path()
        try:
            with open(path, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception:
            pass

    def _set_startup(self, enabled: bool):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE,
            )
            if enabled:
                exe_path = sys.executable
                if getattr(sys, "frozen", False):
                    exe_path = sys.executable
                else:
                    exe_path = f'"{sys.executable}" "{os.path.abspath("src/main.py")}"'
                winreg.SetValueEx(key, "StandTall Pro", 0, winreg.REG_SZ, exe_path)
            else:
                try:
                    winreg.DeleteValue(key, "StandTall Pro")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception:
            pass

    def _notify_stand(self, message: str):
        if not self.timer_config.notifications_enabled:
            return
        notify("StandTall Pro", message)

    def _notify_eye_care(self, message: str):
        if not self.timer_config.notifications_enabled:
            return
        notify("StandTall Pro \u2014 Eye Care", message)

    def _create_tray_image(self):
        png_path = resource_path(os.path.join("assets", "logo.png"))
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

        # Fallback to manual drawing
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

    def _open_ui(self):
        if self._ui_window is not None and self._ui_window.winfo_exists():
            self._ui_window.deiconify()
            self._ui_window.lift()
            self._ui_window.focus()
            return

        from ui import SettingsWindow
        self._ui_window = SettingsWindow(self)
        self._ui_window.protocol("WM_DELETE_WINDOW", self._on_hide_ui)

    def _on_hide_ui(self):
        if self._ui_window is not None:
            self._ui_window.withdraw()

    def _on_show_settings(self, icon=None, item=None):
        self._open_ui()

    def _on_quit(self, icon=None, item=None):
        self.engine.stop()
        if self._tray_icon:
            self._tray_icon.stop()
        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except Exception:
                pass
        os._exit(0)

    def _toggle_pause(self, icon, item):
        if self.engine.is_paused:
            self.engine.resume()
            icon.title = "StandTall Pro"
        else:
            self.engine.pause()
            icon.title = "StandTall Pro [PAUSED]"

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
            self._set_startup(value)

    def run(self):
        self.root = ctk.CTk()
        self.root.withdraw()

        ico_path = resource_path(os.path.join("assets", "icon.ico"))
        png_path = resource_path(os.path.join("assets", "logo.png"))
        
        # Use iconbitmap for Windows taskbar (requires .ico)
        if os.path.exists(ico_path):
            try:
                self.root.iconbitmap(ico_path)
            except Exception:
                pass
        
        # Also set iconphoto for window title bar (fallback to png)
        icon_path = ico_path if os.path.exists(ico_path) else png_path
        if os.path.exists(icon_path):
            try:
                from PIL import ImageTk
                icon_img = Image.open(icon_path).convert("RGBA")
                self.root.iconphoto(True, ImageTk.PhotoImage(icon_img))
            except Exception:
                pass

        init_notifier(self.root.winfo_id())

        self.engine.start()

        image = self._create_tray_image()
        menu = pystray.Menu(
            pystray.MenuItem("Settings", self._on_show_settings),
            pystray.MenuItem("Pause / Resume", self._toggle_pause),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._on_quit),
        )
        self._tray_icon = pystray.Icon("StandTall Pro", image, "StandTall Pro", menu)
        threading.Thread(target=self._tray_icon.run, daemon=True).start()

        self._open_ui()

        # Poll for signal from second instance
        def _poll_signal():
            if os.path.exists(_signal_path):
                try:
                    os.remove(_signal_path)
                    self.root.after(0, self._open_ui)
                except Exception:
                    pass
            self.root.after(500, _poll_signal)

        self.root.after(500, _poll_signal)
        self.root.mainloop()


if __name__ == "__main__":
    # Single-instance: create named event at entry point
    _EVENT_NAME = "Global\\StandTallPro_SingleInstance_Event"
    _create_event = ctypes.windll.kernel32.CreateEventW
    _create_event.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_bool, ctypes.c_wchar_p]
    _create_event.restype = ctypes.c_void_p
    _get_last_error = ctypes.windll.kernel32.GetLastError

    _h_event = _create_event(None, True, False, _EVENT_NAME)
    if _get_last_error() == 183:  # ERROR_ALREADY_EXISTS
        # Another instance exists - signal it to show UI
        try:
            with open(_signal_path, "w") as f:
                f.write("show")
        except Exception:
            pass
        sys.exit(0)

    app = StandTallApp()
    app.run()
