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
        self._load_theme_colors()
        self._build_ui()
        self._update_streak()

    def _load_theme_colors(self):
        theme_name = self.app.config.get("theme", "dark")
        theme_file = f"{theme_name.lower().replace(' ', '_')}.json"
        path = os.path.join(THEMES_DIR, theme_file)

        if not os.path.exists(path):
            path = os.path.join(THEMES_DIR, "dark.json")

        try:
            with open(path, "r") as f:
                self.theme = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            fallback = os.path.join(THEMES_DIR, "dark.json")
            with open(fallback, "r") as f:
                self.theme = json.load(f)

        ctk.set_appearance_mode("dark" if theme_name.lower() == "dark" else "light")
        self.configure(fg_color=self.theme["colors"]["bg"])

    def _build_ui(self):
        self.title("StandTall Pro \u2014 Settings")
        self.resizable(False, False)

        colors = self.theme["colors"]

        main = ctk.CTkFrame(self, fg_color=colors["bg"], corner_radius=0)
        main.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            main,
            text="StandTall Pro",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=colors["fg"],
        ).pack(pady=(0, 20))

        # Dashboard card
        streak_card = self._card(main)
        ctk.CTkLabel(
            streak_card, text="Dashboard",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["fg"],
        ).pack(anchor="w", padx=16, pady=(12, 4))

        self._streak_label = ctk.CTkLabel(
            streak_card, text="Current Streak: 0.0 hours",
            font=ctk.CTkFont(size=13), text_color=colors["text_secondary"],
        )
        self._streak_label.pack(anchor="w", padx=16, pady=(0, 4))

        info_frame = ctk.CTkFrame(streak_card, fg_color="transparent")
        info_frame.pack(fill="x", padx=16, pady=(0, 12))

        self._next_stand_label = ctk.CTkLabel(
            info_frame, text="Next stand: \u2014",
            font=ctk.CTkFont(size=12), text_color=colors["accent_stand"],
        )
        self._next_stand_label.pack(side="left", padx=(0, 20))

        self._next_eye_label = ctk.CTkLabel(
            info_frame, text="Next eye break: \u2014",
            font=ctk.CTkFont(size=12), text_color=colors["accent_eye"],
        )
        self._next_eye_label.pack(side="left")

        # Stand slider card
        stand_card = self._card(main)
        ctk.CTkLabel(
            stand_card, text="Posture Reminder",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["fg"],
        ).pack(anchor="w", padx=16, pady=(12, 4))
        ctk.CTkLabel(
            stand_card, text="Remind me to stand every:",
            font=ctk.CTkFont(size=12), text_color=colors["text_secondary"],
        ).pack(anchor="w", padx=16, pady=(0, 4))

        stand_slider_frame = ctk.CTkFrame(stand_card, fg_color="transparent")
        stand_slider_frame.pack(fill="x", padx=16, pady=(0, 12))

        self._stand_slider_var = ctk.IntVar(value=min(self.engine.config.stand_interval_seconds // 60, 60))
        ctk.CTkSlider(
            stand_slider_frame, from_=1, to=60, number_of_steps=59,
            variable=self._stand_slider_var, command=self._on_stand_slider,
            fg_color=colors["slider_bg"], progress_color=colors["slider_progress"],
            button_color=colors["accent_stand"], button_hover_color=colors["accent_stand"],
        ).pack(side="left", fill="x", expand=True, padx=(0, 12))

        self._stand_value_label = ctk.CTkLabel(
            stand_slider_frame, text=f"{self._stand_slider_var.get()} min",
            font=ctk.CTkFont(size=12), text_color=colors["accent_stand"], width=50,
        )
        self._stand_value_label.pack(side="right")

        # Eye slider card
        eye_card = self._card(main)
        ctk.CTkLabel(
            eye_card, text="Eye Care (20-20-20 Rule)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["fg"],
        ).pack(anchor="w", padx=16, pady=(12, 4))
        ctk.CTkLabel(
            eye_card, text="Remind me every:",
            font=ctk.CTkFont(size=12), text_color=colors["text_secondary"],
        ).pack(anchor="w", padx=16, pady=(0, 4))

        eye_slider_frame = ctk.CTkFrame(eye_card, fg_color="transparent")
        eye_slider_frame.pack(fill="x", padx=16, pady=(0, 12))

        self._eye_slider_var = ctk.IntVar(value=min(self.engine.config.eye_care_interval_seconds // 60, 30))
        ctk.CTkSlider(
            eye_slider_frame, from_=1, to=30, number_of_steps=29,
            variable=self._eye_slider_var, command=self._on_eye_slider,
            fg_color=colors["slider_bg"], progress_color=colors["slider_progress"],
            button_color=colors["accent_eye"], button_hover_color=colors["accent_eye"],
        ).pack(side="left", fill="x", expand=True, padx=(0, 12))

        self._eye_value_label = ctk.CTkLabel(
            eye_slider_frame, text=f"{self._eye_slider_var.get()} min",
            font=ctk.CTkFont(size=12), text_color=colors["accent_eye"], width=50,
        )
        self._eye_value_label.pack(side="right")

        # Theme card
        theme_card = self._card(main)
        ctk.CTkLabel(
            theme_card, text="Theme",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["fg"],
        ).pack(anchor="w", padx=16, pady=(12, 4))

        self._theme_var = ctk.StringVar(value=self._get_current_theme_display())
        ctk.CTkOptionMenu(
            theme_card,
            values=["Light", "Dark", "High Contrast"],
            variable=self._theme_var,
            command=self._on_theme_change,
            fg_color=colors["dropdown_bg"],
            button_color=colors["button_bg"],
            button_hover_color=colors["button_hover"],
            text_color=colors["dropdown_fg"],
            dropdown_fg_color=colors["dropdown_bg"],
            dropdown_text_color=colors["dropdown_fg"],
            dropdown_hover_color=colors["button_bg"],
        ).pack(anchor="w", padx=16, pady=(0, 12))

        # Startup card
        startup_card = self._card(main)
        ctk.CTkLabel(
            startup_card, text="Startup",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=colors["fg"],
        ).pack(anchor="w", padx=16, pady=(12, 4))

        self._startup_var = ctk.BooleanVar(value=self.app.config.get("start_on_boot", False))
        ctk.CTkSwitch(
            startup_card,
            text="Start StandTall Pro on Windows startup",
            variable=self._startup_var,
            command=self._on_startup_toggle,
            font=ctk.CTkFont(size=12),
            text_color=colors["text_secondary"],
            progress_color=colors["accent_stand"],
            button_color=colors["button_bg"],
            button_hover_color=colors["button_hover"],
        ).pack(anchor="w", padx=16, pady=(0, 12))

        self.update_idletasks()
        w = 420
        h = self.winfo_reqheight()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}")

    def _card(self, parent):
        c = ctk.CTkFrame(parent, fg_color=self.theme["colors"]["card_bg"], corner_radius=12)
        c.pack(fill="x", pady=(0, 16))
        return c

    def _get_current_theme_display(self):
        mapping = {"light": "Light", "dark": "Dark", "high_contrast": "High Contrast"}
        return mapping.get(self.app.config.get("theme", "dark"), "Dark")

    def _on_stand_slider(self, value):
        val = int(value)
        self._stand_value_label.configure(text=f"{val} min")
        self.app.update_config("stand_interval_seconds", val * 60)

    def _on_eye_slider(self, value):
        val = int(value)
        self._eye_value_label.configure(text=f"{val} min")
        self.app.update_config("eye_care_interval_seconds", val * 60)

    def _on_theme_change(self, choice: str):
        mapping = {"Light": "light", "Dark": "dark", "High Contrast": "high_contrast"}
        key = mapping.get(choice, "dark")
        self.app.update_config("theme", key)
        self._rebuild_ui()

    def _on_startup_toggle(self):
        self.app.update_config("start_on_boot", self._startup_var.get())

    def _rebuild_ui(self):
        self._load_theme_colors()
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()

    def _update_streak(self):
        if not self.winfo_exists():
            return

        colors = self.theme["colors"]
        streak = self.engine.get_streak_hours()
        self._streak_label.configure(
            text=f"Current Streak: {streak:.1f} hours since last break",
            text_color=colors["text_secondary"],
        )

        ns = self.engine.get_next_stand_seconds()
        ne = self.engine.get_next_eye_care_seconds()
        self._next_stand_label.configure(
            text=f"Next stand: {max(0, int(ns // 60))} min",
            text_color=colors["accent_stand"],
        )
        self._next_eye_label.configure(
            text=f"Next eye break: {max(0, int(ne // 60))} min",
            text_color=colors["accent_eye"],
        )

        self.after(1000, self._update_streak)
