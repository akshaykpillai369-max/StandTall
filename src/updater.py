import json
import threading
import urllib.request
import urllib.error
from typing import Optional

__version__ = "1.1.0"

_GITHUB_API = "https://api.github.com/repos/akshaykpillai369-max/StandTall/releases/latest"


def get_current_version() -> str:
    return __version__


def check_for_update() -> Optional[dict]:
    try:
        req = urllib.request.Request(_GITHUB_API, headers={"Accept": "application/vnd.github.v3+json", "User-Agent": "StandTall-Pro"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        latest_tag = data.get("tag_name", "").lstrip("v")
        if _compare_versions(latest_tag, __version__) > 0:
            return {
                "version": latest_tag,
                "url": data.get("html_url", ""),
                "body": (data.get("body") or "")[:500],
            }
        return None
    except Exception:
        return None


def check_for_update_async(callback):
    def _run():
        result = check_for_update()
        if callback:
            callback(result)
    threading.Thread(target=_run, daemon=True).start()


def _compare_versions(a: str, b: str) -> int:
    def _parse(v):
        return [int(x) for x in v.replace("-", ".").split(".")]
    ap = _parse(a)
    bp = _parse(b)
    for i in range(max(len(ap), len(bp))):
        av = ap[i] if i < len(ap) else 0
        bv = bp[i] if i < len(bp) else 0
        if av > bv:
            return 1
        if av < bv:
            return -1
    return 0
