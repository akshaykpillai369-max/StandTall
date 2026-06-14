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


def config_path():
    if is_frozen():
        return os.path.join(os.path.dirname(sys.executable), "config.json")
    return os.path.join(project_root(), "config.json")
