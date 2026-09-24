import threading
from datetime import datetime
from typing import Optional


class IdleTracker:
    """Tracks the last time of user activity using pynput background listeners.

    The listeners run on lightweight daemon threads and only stamp a timestamp
    on mouse/keyboard events. If pynput is unavailable or the listeners fail to
    start (e.g. missing permissions on macOS/Linux), the tracker degrades to
    reporting 0 idle seconds so reminders behave as before.
    """

    def __init__(self):
        self._last_activity = datetime.now()
        self._lock = threading.Lock()
        self._running = False
        self._enabled = False
        self._mouse_listener = None
        self._keyboard_listener = None

    # ── lifecycle ──────────────────────────────────────────────────

    def start(self) -> bool:
        """Start background listeners. Returns True if tracking is active."""
        if self._running:
            return self._enabled
        self._running = True

        try:
            from pynput import mouse, keyboard
        except Exception:
            return False

        self._mouse_listener = mouse.Listener(
            on_move=self._register_activity,
            on_click=self._register_activity,
            on_scroll=self._register_activity,
        )
        self._keyboard_listener = keyboard.Listener(
            on_press=self._register_activity,
            on_release=self._register_activity,
        )

        started = True
        for listener in (self._mouse_listener, self._keyboard_listener):
            try:
                listener.start()
            except Exception:
                started = False

        self._enabled = started and (
            self._mouse_listener is not None and self._keyboard_listener is not None
        )
        return self._enabled

    def stop(self):
        """Stop the background listeners cleanly."""
        self._running = False
        for listener in (self._mouse_listener, self._keyboard_listener):
            if listener is not None:
                try:
                    listener.stop()
                except Exception:
                    pass
        self._mouse_listener = None
        self._keyboard_listener = None
        self._enabled = False

    # ── activity tracking ──────────────────────────────────────────

    def _register_activity(self, *args):
        now = datetime.now()
        with self._lock:
            self._last_activity = now

    def get_idle_time_seconds(self) -> float:
        """Seconds elapsed since the last user input event."""
        if not self._enabled:
            return 0.0
        with self._lock:
            return (datetime.now() - self._last_activity).total_seconds()
