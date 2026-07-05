import os
import sys


def is_frozen():
    return getattr(sys, "frozen", False)


def project_root():
    if is_frozen():
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resource_path(relative_path):
    return os.path.join(project_root(), relative_path)


def _app_data_dir():
    import platform
    if platform.system() == "Windows":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    elif platform.system() == "Darwin":
        base = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
    else:
        base = os.environ.get("XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config"))
    d = os.path.join(base, "StandTall Pro")
    os.makedirs(d, exist_ok=True)
    return d


def config_path():
    if is_frozen():
        return os.path.join(_app_data_dir(), "config.json")
    return os.path.join(project_root(), "config.json")
