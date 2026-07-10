import time
import tkinter as tk
from tkinter import ttk


def show_break_nudge(message: str, duration_seconds: int = 20):
    root = tk.Tk()
    root.title("Eye Break")
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.configure(bg="#0D0D0D")

    frame = tk.Frame(root, bg="#1A1A2E", highlightbackground="#2A2A4A", highlightthickness=1)
    frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(
        frame,
        text="\U0001f441\ufe0f Eye Break Time",
        font=("Segoe UI", 32, "bold"),
        fg="#4FC3F7", bg="#1A1A2E",
    ).pack(pady=(30, 10), padx=60)

    tk.Label(
        frame,
        text=message,
        font=("Segoe UI", 16),
        fg="#B0BEC5", bg="#1A1A2E",
        wraplength=500, justify="center",
    ).pack(pady=(0, 20), padx=40)

    remaining = tk.IntVar(value=duration_seconds)
    tk.Label(
        frame,
        textvariable=remaining,
        font=("Segoe UI", 48, "bold"),
        fg="#FFFFFF", bg="#1A1A2E",
    ).pack(pady=(0, 10))

    tk.Label(
        frame,
        text="seconds remaining",
        font=("Segoe UI", 12),
        fg="#78909C", bg="#1A1A2E",
    ).pack(pady=(0, 20))

    progress = ttk.Progressbar(frame, length=300, mode="determinate", maximum=100)
    progress.pack(pady=(0, 20), padx=40)

    dismissed = False

    def skip():
        nonlocal dismissed
        dismissed = True

    tk.Button(
        frame,
        text="Dismiss",
        command=skip,
        font=("Segoe UI", 14),
        bg="#37474F", fg="#FFFFFF",
        activebackground="#455A64", activeforeground="#FFFFFF",
        borderwidth=0, padx=30, pady=6, cursor="hand2",
    ).pack(pady=(0, 30))

    progress["value"] = 100
    start = time.time()
    deadline = start + duration_seconds

    while root.winfo_exists() and time.time() < deadline and not dismissed:
        elapsed = time.time() - start
        left = max(0, duration_seconds - int(elapsed))
        remaining.set(left)
        progress["value"] = (left / duration_seconds) * 100 if duration_seconds else 0
        root.update()
        time.sleep(0.05)

    try:
        root.destroy()
    except tk.TclError:
        pass
