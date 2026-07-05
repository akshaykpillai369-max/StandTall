import os
import json
from datetime import datetime, date
from paths import _app_data_dir


_STATS_FILE = os.path.join(_app_data_dir(), "stats.json")


def _load() -> dict:
    defaults = {"days": {}}
    try:
        with open(_STATS_FILE, "r") as f:
            d = json.load(f)
            d.setdefault("days", {})
            return d
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(defaults)


def _save(data: dict):
    try:
        with open(_STATS_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass


def record_stand():
    data = _load()
    today = date.today().isoformat()
    day = data["days"].setdefault(today, {"stands": 0, "eye_breaks": 0})
    day["stands"] = day.get("stands", 0) + 1
    _save(data)


def record_eye_break():
    data = _load()
    today = date.today().isoformat()
    day = data["days"].setdefault(today, {"stands": 0, "eye_breaks": 0})
    day["eye_breaks"] = day.get("eye_breaks", 0) + 1
    _save(data)


def get_today() -> dict:
    data = _load()
    return data["days"].get(date.today().isoformat(), {"stands": 0, "eye_breaks": 0})


def get_last_7_days() -> list[dict]:
    data = _load()
    from datetime import timedelta
    today = date.today()
    result = []
    for i in range(6, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        day = data["days"].get(d, {"stands": 0, "eye_breaks": 0})
        result.append({"date": d, "stands": day.get("stands", 0), "eye_breaks": day.get("eye_breaks", 0)})
    return result


def get_all_time_totals() -> dict:
    data = _load()
    total_stands = 0
    total_eye = 0
    for day in data["days"].values():
        total_stands += day.get("stands", 0)
        total_eye += day.get("eye_breaks", 0)
    return {"stands": total_stands, "eye_breaks": total_eye}
