import threading
import time
import customtkinter as ctk


def show_break_nudge(message: str, duration_seconds: int = 20):
    threading.Thread(
        target=_run_nudge, args=(message, duration_seconds), daemon=True
    ).start()


def _run_nudge(message: str, duration_seconds: int):
    root = ctk.CTk()
    root.title("Eye Break")
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.configure(fg_color="#0D0D0D")

    frame = ctk.CTkFrame(root, fg_color="#1A1A2E", corner_radius=16)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    ctk.CTkLabel(
        frame,
        text="\U0001f441\ufe0f Eye Break Time",
        font=ctk.CTkFont(size=32, weight="bold"),
        text_color="#4FC3F7",
    ).pack(pady=(30, 10), padx=60)

    ctk.CTkLabel(
        frame,
        text=message,
        font=ctk.CTkFont(size=16),
        text_color="#B0BEC5",
        wraplength=500,
    ).pack(pady=(0, 20), padx=40)

    remaining = ctk.IntVar(value=duration_seconds)
    countdown_label = ctk.CTkLabel(
        frame,
        textvariable=remaining,
        font=ctk.CTkFont(size=48, weight="bold"),
        text_color="#FFFFFF",
    )
    countdown_label.pack(pady=(0, 10))

    ctk.CTkLabel(
        frame,
        text="seconds remaining",
        font=ctk.CTkFont(size=12),
        text_color="#78909C",
    ).pack(pady=(0, 20))

    progress = ctk.CTkProgressBar(frame, width=300, height=8)
    progress.pack(pady=(0, 20), padx=40)
    progress.set(1.0)

    def skip():
        root.destroy()

    ctk.CTkButton(
        frame,
        text="Dismiss",
        command=skip,
        fg_color="#37474F",
        hover_color="#455A64",
        font=ctk.CTkFont(size=14),
        width=120,
    ).pack(pady=(0, 30))

    start = time.time()

    def tick():
        elapsed = time.time() - start
        left = max(0, duration_seconds - int(elapsed))
        remaining.set(left)
        progress.set(left / duration_seconds if duration_seconds else 0)
        if left > 0:
            root.after(200, tick)
        else:
            root.destroy()

    root.after(200, tick)
    root.mainloop()
