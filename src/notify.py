import ctypes
import os
import sys
import threading
import tempfile
import io

from PIL import Image
from paths import resource_path, is_frozen


NIM_ADD = 0
NIM_MODIFY = 1
NIM_DELETE = 2
NIF_INFO = 0x10
NIF_ICON = 0x2
NIIF_INFO = 0x1


class NOTIFYICONDATAW(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_ulong),
        ("hWnd", ctypes.c_void_p),
        ("uID", ctypes.c_uint),
        ("uFlags", ctypes.c_uint),
        ("uCallbackMessage", ctypes.c_uint),
        ("hIcon", ctypes.c_void_p),
        ("szTip", ctypes.c_wchar * 128),
        ("dwState", ctypes.c_ulong),
        ("dwStateMask", ctypes.c_ulong),
        ("szInfo", ctypes.c_wchar * 256),
        ("uVersion", ctypes.c_uint),
        ("szInfoTitle", ctypes.c_wchar * 64),
        ("dwInfoFlags", ctypes.c_ulong),
        ("guidItem", ctypes.c_byte * 16),
        ("hBalloonIcon", ctypes.c_void_p),
    ]


shell32 = ctypes.windll.shell32
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

shell32.ExtractIconW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint]
shell32.ExtractIconW.restype = ctypes.c_void_p
user32.LoadImageW.argtypes = [
    ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint,
    ctypes.c_int, ctypes.c_int, ctypes.c_uint,
]
user32.LoadImageW.restype = ctypes.c_void_p
shell32.Shell_NotifyIconW.argtypes = [ctypes.c_uint, ctypes.c_void_p]
shell32.Shell_NotifyIconW.restype = ctypes.c_bool
user32.DestroyIcon.argtypes = [ctypes.c_void_p]
user32.DestroyIcon.restype = ctypes.c_bool

shell32.SetCurrentProcessExplicitAppUserModelID.argtypes = [ctypes.c_wchar_p]
shell32.SetCurrentProcessExplicitAppUserModelID.restype = ctypes.c_ulong

shell32.SetCurrentProcessExplicitAppUserModelID("StandTallPro")


_lock = threading.Lock()
_hwnd = None


def initialize(hwnd):
    global _hwnd
    _hwnd = hwnd


def _get_default_icon():
    # 1) Extract icon from the current executable
    if is_frozen():
        hicon = shell32.ExtractIconW(None, sys.executable, 0)
        if hicon:
            return hicon

    # 2) Try loading icon.ico directly
    ico_path = resource_path(os.path.join("assets", "icon.ico"))
    if os.path.exists(ico_path):
        hicon = user32.LoadImageW(None, ico_path, 1, 32, 32, 0x00000010)
        if hicon:
            return hicon

    # 3) Load logo.png and convert to HICON
    png_path = resource_path(os.path.join("assets", "logo.png"))
    if os.path.exists(png_path):
        try:
            img = Image.open(png_path).convert("RGBA")
            img = img.resize((32, 32), Image.Resampling.LANCZOS)
            ico_bytes = io.BytesIO()
            img.save(ico_bytes, format="ICO", sizes=[(32, 32)])
            ico_bytes.seek(0)
            with tempfile.NamedTemporaryFile(suffix=".ico", delete=False) as f:
                f.write(ico_bytes.read())
                temp_ico = f.name
            hicon = user32.LoadImageW(None, temp_ico, 1, 32, 32, 0x00000010)
            try:
                os.unlink(temp_ico)
            except Exception:
                pass
            if hicon:
                return hicon
        except Exception:
            pass

    return None


def _show(title, message):
    global _hwnd
    if _hwnd is None:
        return

    hicon = _get_default_icon()

    nid = NOTIFYICONDATAW()
    nid.cbSize = ctypes.sizeof(NOTIFYICONDATAW)
    nid.hWnd = _hwnd
    nid.uID = 1

    # Add the icon without NIF_INFO so it doesn't show a balloon yet
    add_flags = NIF_ICON if hicon else 0
    nid.uFlags = add_flags
    if hicon:
        nid.hIcon = hicon
    shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(nid))

    # Now modify with NIF_INFO to show a single balloon notification
    nid.uFlags = NIF_INFO
    if hicon:
        nid.uFlags |= NIF_ICON
    nid.szInfo = message[:255]
    nid.szInfoTitle = title[:63]
    nid.dwInfoFlags = NIIF_INFO
    nid.uVersion = 4

    with _lock:
        shell32.Shell_NotifyIconW(NIM_MODIFY, ctypes.byref(nid))

    def cleanup():
        with _lock:
            shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(nid))
        if hicon:
            user32.DestroyIcon(hicon)

    threading.Timer(8.0, cleanup).start()


def notify(title, message):
    threading.Thread(target=_show, args=(title, message), daemon=True).start()
