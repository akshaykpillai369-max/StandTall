import time
import random
import threading
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, Callable

from idle import IdleTracker

IDLE_THRESHOLD_SECONDS = 300


STAND_MESSAGES = [
    "Time to stand up! Your body will thank you.",
    "Rise and stretch! A moving body stays healthy.",
    "Stand tall \u2014 your posture deserves a break.",
    "Sitting too long? Take a quick stand-up break.",
    "Your spine needs a change of position. Stand up!",
    "Stand up, stretch, and reset your focus.",
    "Prolonged sitting slows circulation. Get on your feet!",
    "Every hour of sitting needs a few minutes of standing.",
    "Stand up, walk around, feel the energy flow.",
    "Your body wasn't designed to sit all day. Move!",
]

EYE_CARE_MESSAGES = [
    "Eye Care Break: Look at an object 20 ft away for 20 seconds.",
    "Rest your eyes \u2014 gaze into the distance and blink slowly.",
    "20-20-20 Rule: Every 20 min, look 20 ft away for 20 sec.",
    "Give your eyes a moment. Focus on something far away.",
    "Digital eye strain is real. Take 20 seconds to look away.",
    "Blink a few times, then focus on a distant object.",
    "Your eyes work hard. Reward them with a 20-second break.",
    "Look away from the screen. Your retina will appreciate it.",
    "Eye break! Stare at the horizon (or a far wall) for 20s.",
    "Prevent eye fatigue \u2014 practice the 20-20-20 rule now.",
]


@dataclass
class TimerConfig:
    stand_interval_seconds: int = 1800
    eye_care_interval_seconds: int = 1200
    eye_care_duration_seconds: int = 20
    overlay_duration_seconds: int = 20
    notifications_enabled: bool = True
    nudge_enabled: bool = False


class TimerEngine:
    def __init__(self, config: TimerConfig, idle_tracker: Optional[IdleTracker] = None):
        self.config = config
        self.idle_tracker = idle_tracker
        self._running = False
        self._paused = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        self._last_stand_time: Optional[datetime] = None
        self._last_eye_care_time: Optional[datetime] = None
        self._session_start: datetime = datetime.now()
        self._idle_frozen_seconds: float = 0.0
        self._idle_freeze_start: Optional[datetime] = None

        self.on_stand_reminder: Optional[Callable[[str], None]] = None
        self.on_eye_care_reminder: Optional[Callable[[str], None]] = None

    def start(self):
        if self._running:
            return
        self._running = True
        self._last_stand_time = datetime.now()
        self._last_eye_care_time = datetime.now()
        self._session_start = datetime.now()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def pause(self):
        with self._lock:
            self._paused = True

    def resume(self):
        with self._lock:
            self._paused = False

    @property
    def is_paused(self) -> bool:
        return self._paused

    def get_streak_hours(self) -> float:
        if self._last_stand_time is None or self._last_eye_care_time is None:
            return 0.0
        eff = self._effective_now()
        last_break = min(self._last_stand_time, self._last_eye_care_time)
        return (eff - last_break).total_seconds() / 3600

    def get_next_stand_seconds(self) -> float:
        if self._last_stand_time is None:
            return 0.0
        eff = self._effective_now()
        elapsed = (eff - self._last_stand_time).total_seconds()
        return max(0.0, self.config.stand_interval_seconds - elapsed)

    def get_next_eye_care_seconds(self) -> float:
        if self._last_eye_care_time is None:
            return 0.0
        eff = self._effective_now()
        elapsed = (eff - self._last_eye_care_time).total_seconds()
        return max(0.0, self.config.eye_care_interval_seconds - elapsed)

    def _pick_message(self, pool: list[str]) -> str:
        return random.choice(pool)

    def _effective_now(self) -> datetime:
        now = datetime.now()
        frozen = self._idle_frozen_seconds
        if self._idle_freeze_start is not None:
            frozen += (now - self._idle_freeze_start).total_seconds()
        return now - timedelta(seconds=frozen)

    def _loop(self):
        while self._running:
            if self._paused:
                time.sleep(1)
                continue

            now = datetime.now()
            idle = self._is_idle()

            with self._lock:
                if idle:
                    if self._idle_freeze_start is None:
                        self._idle_freeze_start = now
                else:
                    if self._idle_freeze_start is not None:
                        self._idle_frozen_seconds += (now - self._idle_freeze_start).total_seconds()
                        self._idle_freeze_start = None

                if not idle:
                    eff = self._effective_now()
                    if (eff - self._last_stand_time).total_seconds() >= self.config.stand_interval_seconds:
                        self._last_stand_time = eff
                        message = self._pick_message(STAND_MESSAGES)
                        if self.on_stand_reminder:
                            self.on_stand_reminder(message)

                    if (eff - self._last_eye_care_time).total_seconds() >= self.config.eye_care_interval_seconds:
                        self._last_eye_care_time = eff
                        message = self._pick_message(EYE_CARE_MESSAGES)
                        if self.on_eye_care_reminder:
                            self.on_eye_care_reminder(message)

            time.sleep(1)

    def _is_idle(self) -> bool:
        if self.idle_tracker is None:
            return False
        return self.idle_tracker.get_idle_time_seconds() >= IDLE_THRESHOLD_SECONDS
