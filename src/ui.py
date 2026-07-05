import os
import json

import customtkinter as ctk
from PIL import Image, ImageTk
from paths import resource_path


THEMES_DIR = resource_path("themes")


class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, app):
        self.app = app
        self.engine = app.engine
        super().__init__(app.root)
        self.transient(None)

        png = resource_path(os.path.join("assets", "logo.png"))
        if os.path.exists(png):
            try:
                img = Image.open(png)
                self.iconphoto(True, ImageTk.PhotoImage(img))
            except Exception:
                pass

        self.after(100, self._init_ui)

    def _init_ui(self):
        self._load_theme()
        self._build()
        self._poll()

    def _load_theme(self):
        theme_name = self.app.config.get("theme", "dark")
        theme_file = f"{theme_name.lower().replace(' ', '_')}.json"
        path = os.path.join(THEMES_DIR, theme_file)
        if not os.path.exists(path):
            path = os.path.join(THEMES_DIR, "dark.json")
        try:
            with open(path, "r") as f:
                self.theme = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            with open(os.path.join(THEMES_DIR, "dark.json"), "r") as f:
                self.theme = json.load(f)
        is_dark = theme_name.lower() == "dark"
        ctk.set_appearance_mode("dark" if is_dark else "light")
        self.configure(fg_color=self.theme["colors"]["bg"])

    def _build(self):
        self.title("StandTall Pro")
        self.resizable(False, False)
        c = self.theme["colors"]

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        body = ctk.CTkFrame(self, fg_color=c["bg"], corner_radius=0)
        body.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        body.grid_columnconfigure(0, weight=1)

        row = 0

        # Header
        ctk.CTkLabel(
            body, text="StandTall Pro",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=c["fg"],
        ).grid(row=row, column=0, pady=(0, 4), sticky="w")
        row += 1

        ctk.CTkLabel(
            body, text="Posture & eye care reminders",
            font=ctk.CTkFont(size=12),
            text_color=c["text_secondary"],
        ).grid(row=row, column=0, pady=(0, 18), sticky="w")
        row += 1

        # Status bar
        status = ctk.CTkFrame(body, fg_color=c["card_bg"], corner_radius=10)
        status.grid(row=row, column=0, sticky="ew", pady=(0, 18))
        status.grid_columnconfigure((0, 1, 2), weight=1)
        row += 1

        status_font = ctk.CTkFont(size=12)
        self._next_stand_lbl = ctk.CTkLabel(
            status, text="\u25b6 Stand in \u2014",
            font=status_font, text_color=c["accent_stand"],
        )
        self._next_stand_lbl.grid(row=0, column=0, padx=12, pady=10, sticky="w")

        self._next_eye_lbl = ctk.CTkLabel(
            status, text="\u25b6 Eye break in \u2014",
            font=status_font, text_color=c["accent_eye"],
        )
        self._next_eye_lbl.grid(row=0, column=1, padx=4, pady=10, sticky="w")

        self._streak_lbl = ctk.CTkLabel(
            status, text="Streak 0.0h",
            font=status_font, text_color=c["text_secondary"],
        )
        self._streak_lbl.grid(row=0, column=2, padx=12, pady=10, sticky="e")

        # Stand reminder row
        self._build_slider(body, row, "\u23f1 Stand every", "stand_interval_seconds",
                           c["accent_stand"], c, 1, 60, 60)
        row += 1

        # Eye care row
        self._build_slider(body, row, "\u231a Eye break every", "eye_care_interval_seconds",
                           c["accent_eye"], c, 1, 30, 30)
        row += 1

        # Theme
        theme_frame = ctk.CTkFrame(body, fg_color=c["card_bg"], corner_radius=10)
        theme_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        theme_frame.grid_columnconfigure(1, weight=1)
        row += 1

        ctk.CTkLabel(
            theme_frame, text="\ud83c\udfa8 Theme",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=c["fg"],
        ).grid(row=0, column=0, padx=(14, 8), pady=12, sticky="w")

        self._theme_var = ctk.StringVar(value=self._current_theme_name())
        ctk.CTkOptionMenu(
            theme_frame,
            values=["Dark", "Light", "High Contrast"],
            variable=self._theme_var,
            command=self._on_theme,
            fg_color=c["dropdown_bg"],
            button_color=c["button_bg"],
            button_hover_color=c["button_hover"],
            text_color=c["dropdown_fg"],
            dropdown_fg_color=c["dropdown_bg"],
            dropdown_text_color=c["dropdown_fg"],
            dropdown_hover_color=c["button_bg"],
            font=ctk.CTkFont(size=12),
        ).grid(row=0, column=1, padx=(0, 14), pady=8, sticky="ew")

        # Auto-start
        auto_frame = ctk.CTkFrame(body, fg_color=c["card_bg"], corner_radius=10)
        auto_frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        row += 1

        self._startup_var = ctk.BooleanVar(value=self.app.config.get("start_on_boot", False))
        ctk.CTkSwitch(
            auto_frame,
            text="Launch at startup",
            variable=self._startup_var,
            command=self._on_startup,
            font=ctk.CTkFont(size=13),
            text_color=c["fg"],
            progress_color=c["accent_stand"],
        ).grid(row=0, column=0, padx=14, pady=12, sticky="w")

        # Size
        self.update_idletasks()
        w = 400
        h = self.winfo_reqheight()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    def _build_slider(self, parent, row, label, key, accent, c, from_, to, steps):
        frame = ctk.CTkFrame(parent, fg_color=c["card_bg"], corner_radius=10)
        frame.grid(row=row, column=0, sticky="ew", pady=(0, 10))
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frame, text=label,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=c["fg"],
        ).grid(row=0, column=0, padx=(14, 8), pady=(10, 4), sticky="w")

        current_val = min(
            getattr(self.engine.config, key) // 60, to
        )
        var = ctk.IntVar(value=current_val)
        value_label = ctk.CTkLabel(
            frame, text=f"{current_val} min",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=accent,
        )
        value_label.grid(row=0, column=1, padx=(0, 14), pady=(10, 4), sticky="e")

        slider = ctk.CTkSlider(
            frame, from_=from_, to=to, number_of_steps=steps - 1,
            variable=var,
            command=lambda v, k=key, vl=value_label, a=accent: self._on_slider(v, k, vl, a),
            fg_color=c["slider_bg"],
            progress_color=accent,
            button_color=accent,
            button_hover_color=accent,
        )
        slider.grid(row=1, column=0, columnspan=2, padx=14, pady=(0, 10), sticky="ew")

    def _on_slider(self, value, key, label, accent):
        val = int(value)
        label.configure(text=f"{val} min")
        self.app.update_config(key, val * 60)

    def _on_theme(self, choice):
        mapping = {"Dark": "dark", "Light": "light", "High Contrast": "high_contrast"}
        self.app.update_config("theme", mapping.get(choice, "dark"))
        for w in self.winfo_children():
            w.destroy()
        self._init_ui()

    def _on_startup(self):
        self.app.update_config("start_on_boot", self._startup_var.get())

    def _current_theme_name(self):
        m = {"light": "Light", "dark": "Dark", "high_contrast": "High Contrast"}
        return m.get(self.app.config.get("theme", "dark"), "Dark")

    def _poll(self):
        if not self.winfo_exists():
            return
        c = self.theme["colors"]
        ns = self.engine.get_next_stand_seconds()
        ne = self.engine.get_next_eye_care_seconds()
        streak = self.engine.get_streak_hours()
        self._next_stand_lbl.configure(
            text=f"\u25b6 Stand in {max(0, int(ns // 60))}m",
            text_color=c["accent_stand"],
        )
        self._next_eye_lbl.configure(
            text=f"\u25b6 Eye break in {max(0, int(ne // 60))}m",
            text_color=c["accent_eye"],
        )
        self._streak_lbl.configure(
            text=f"Streak {streak:.1f}h",
            text_color=c["text_secondary"],
        )
        self.after(2000, self._poll)
