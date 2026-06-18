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

from logic import TimerEngine, TimerConfig
from paths import resource_path, config_path
from notify import notify, initialize as init_notifier


_signal_path = os.path.join(tempfile.gettempdir(), "StandTallPro.show")

# Minimal hidden window for notifications (no tkinter needed at startup)
_WndProc = ctypes.WINFUNCTYPE(
    ctypes.c_long, ctypes.c_void_p, ctypes.c_uint,
    ctypes.c_void_p, ctypes.c_void_p,
)(lambda hwnd, msg, wparam, lparam: ctypes.windll.user32.DefWindowProcW(hwnd, msg, wparam, lparam))


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
        self.root: Optional = None
        self._mode = "tray"
        self._notify_hwnd = None

    # ── config helpers ──────────────────────────────────────────────

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
                0, winreg.KEY_SET_VALUE,
            )
            if enabled:
                exe_path = sys.executable
                if not getattr(sys, "frozen", False):
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

    # ── notifications ──────────────────────────────────────────────

    def _notify_stand(self, message: str):
        if self.timer_config.notifications_enabled:
            notify("StandTall Pro", message)

    def _notify_eye_care(self, message: str):
        if self.timer_config.notifications_enabled:
            notify("StandTall Pro \u2014 Eye Care", message)

    def _create_notify_hwnd(self):
        hinstance = ctypes.windll.kernel32.GetModuleHandleW(None)
        class_name = "StandTallNotifyWnd"

        class WNDCLASSEXW(ctypes.Structure):
            _fields_ = [
                ("cbSize", ctypes.c_uint),
                ("style", ctypes.c_uint),
                ("lpfnWndProc", ctypes.c_void_p),
                ("cbClsExtra", ctypes.c_int),
                ("cbWndExtra", ctypes.c_int),
                ("hInstance", ctypes.c_void_p),
                ("hIcon", ctypes.c_void_p),
                ("hCursor", ctypes.c_void_p),
                ("hbrBackground", ctypes.c_void_p),
                ("lpszMenuName", ctypes.c_wchar_p),
                ("lpszClassName", ctypes.c_wchar_p),
                ("hIconSm", ctypes.c_void_p),
            ]

        wc = WNDCLASSEXW()
        wc.cbSize = ctypes.sizeof(WNDCLASSEXW)
        wc.lpfnWndProc = ctypes.cast(_WndProc, ctypes.c_void_p)
        wc.hInstance = hinstance
        wc.lpszClassName = class_name
        ctypes.windll.user32.RegisterClassExW(ctypes.byref(wc))

        return ctypes.windll.user32.CreateWindowExW(
            0, class_name, "", 0, 0, 0, 0, 0, 0, 0, hinstance, 0
        )

    def _destroy_notify_hwnd(self):
        if self._notify_hwnd:
            ctypes.windll.user32.DestroyWindow(self._notify_hwnd)
            self._notify_hwnd = None

    # ── tray icon ──────────────────────────────────────────────────

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

    def _run_tray(self):
        self._notify_hwnd = self._create_notify_hwnd()
        init_notifier(self._notify_hwnd)
        self.engine.start()

        image = self._create_tray_image()
        menu = pystray.Menu(
            pystray.MenuItem("Settings", self._on_show_settings),
            pystray.MenuItem("Pause / Resume", self._toggle_pause),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Quit", self._on_quit),
        )
        self._tray_icon = pystray.Icon("StandTall Pro", image, "StandTall Pro", menu)
        self._tray_icon.run()

        self._tray_icon = None
        self._destroy_notify_hwnd()

    def _on_show_settings(self, icon, item):
        self._mode = "ui"
        icon.stop()

    def _on_quit(self, icon, item):
        self._mode = "quit"
        self.engine.stop()
        icon.stop()

    def _toggle_pause(self, icon, item):
        if self.engine.is_paused:
            self.engine.resume()
            icon.title = "StandTall Pro"
        else:
            self.engine.pause()
            icon.title = "StandTall Pro [PAUSED]"

    # ── settings UI (lazy, uses customtkinter) ─────────────────────

    def _open_ui(self):
        if self._ui_window is not None and self._ui_window.winfo_exists():
            self._ui_window.deiconify()
            self._ui_window.lift()
            self._ui_window.focus()
            return

        import customtkinter as ctk

        self.root = ctk.CTk()
        self.root.withdraw()

        ico_path = resource_path(os.path.join("assets", "icon.ico"))
        png_path = resource_path(os.path.join("assets", "logo.png"))
        if os.path.exists(ico_path):
            try:
                self.root.iconbitmap(ico_path)
            except Exception:
                pass
        icon_path = ico_path if os.path.exists(ico_path) else png_path
        if os.path.exists(icon_path):
            try:
                from PIL import ImageTk
                icon_img = Image.open(icon_path).convert("RGBA")
                self.root.iconphoto(True, ImageTk.PhotoImage(icon_img))
            except Exception:
                pass

        init_notifier(self.root.winfo_id())

        from ui import SettingsWindow
        self._ui_window = SettingsWindow(self)
        self._ui_window.protocol("WM_DELETE_WINDOW", self._on_hide_ui)

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

        self.root.destroy()
        self.root = None
        self._ui_window = None

    def _on_hide_ui(self):
        self._mode = "tray"
        if self._ui_window is not None and self._ui_window.winfo_exists():
            self._ui_window.withdraw()
        if self.root:
            self.root.quit()

    # ── public API ─────────────────────────────────────────────────

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
        while True:
            self._run_tray()
            if self._mode == "quit":
                break
            elif self._mode == "ui":
                self._open_ui()
                if self._mode == "quit":
                    break
            self._mode = "tray"


if __name__ == "__main__":
    _EVENT_NAME = "Global\\StandTallPro_SingleInstance_Event"
    _create_event = ctypes.windll.kernel32.CreateEventW
    _create_event.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_bool, ctypes.c_wchar_p]
    _create_event.restype = ctypes.c_void_p
    _get_last_error = ctypes.windll.kernel32.GetLastError

    _h_event = _create_event(None, True, False, _EVENT_NAME)
    if _get_last_error() == 183:
        try:
            with open(_signal_path, "w") as f:
                f.write("show")
        except Exception:
            pass
        sys.exit(0)

    app = StandTallApp()
    app.run()
