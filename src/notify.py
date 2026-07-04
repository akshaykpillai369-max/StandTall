import platform
import subprocess
import threading
import sys
import os

_system = platform.system()

if _system == "Windows":
    import ctypes

    _user32 = ctypes.windll.user32
    _kernel32 = ctypes.windll.kernel32
    _shell32 = ctypes.windll.shell32

    class _NOTIFYICONDATAW(ctypes.Structure):
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

    _NIM_ADD = 0
    _NIM_MODIFY = 1
    _NIM_DELETE = 2
    _NIF_INFO = 0x10
    _NIF_ICON = 0x2
    _NIIF_INFO = 0x1

    _WndProc = ctypes.WINFUNCTYPE(
        ctypes.c_long, ctypes.c_void_p, ctypes.c_uint,
        ctypes.c_void_p, ctypes.c_void_p,
    )(lambda hwnd, msg, w, l: _user32.DefWindowProcW(hwnd, msg, w, l))

    _hwnd = None
    _lock = threading.Lock()

    def _get_hwnd():
        global _hwnd
        if _hwnd is not None:
            return _hwnd
        with _lock:
            if _hwnd is not None:
                return _hwnd
            hi = _kernel32.GetModuleHandleW(None)
            cn = "StandTallNotify"
            class _W(ctypes.Structure):
                _fields_ = [
                    ("cbSize", ctypes.c_uint), ("style", ctypes.c_uint),
                    ("lpfnWndProc", ctypes.c_void_p), ("cbClsExtra", ctypes.c_int),
                    ("cbWndExtra", ctypes.c_int), ("hInstance", ctypes.c_void_p),
                    ("hIcon", ctypes.c_void_p), ("hCursor", ctypes.c_void_p),
                    ("hbrBackground", ctypes.c_void_p), ("lpszMenuName", ctypes.c_wchar_p),
                    ("lpszClassName", ctypes.c_wchar_p), ("hIconSm", ctypes.c_void_p),
                ]
            wc = _W()
            wc.cbSize = ctypes.sizeof(_W)
            wc.lpfnWndProc = ctypes.cast(_WndProc, ctypes.c_void_p)
            wc.hInstance = hi
            wc.lpszClassName = cn
            _user32.RegisterClassExW(ctypes.byref(wc))
            _hwnd = _user32.CreateWindowExW(0, cn, "", 0, 0, 0, 0, 0, 0, 0, hi, 0)
            return _hwnd

    def _notify_win(title, message):
        hwnd = _get_hwnd()
        if not hwnd:
            return
        hicon = _shell32.ExtractIconW(None, sys.executable, 0)
        nid = _NOTIFYICONDATAW()
        nid.cbSize = ctypes.sizeof(_NOTIFYICONDATAW)
        nid.hWnd = hwnd
        nid.uID = 1
        nid.uFlags = _NIF_ICON if hicon else 0
        if hicon:
            nid.hIcon = hicon
        with _lock:
            _shell32.Shell_NotifyIconW(_NIM_ADD, ctypes.byref(nid))
        nid.uFlags = _NIF_INFO
        if hicon:
            nid.uFlags |= _NIF_ICON
        nid.szInfo = message[:255]
        nid.szInfoTitle = title[:63]
        nid.dwInfoFlags = _NIIF_INFO
        nid.uVersion = 4
        with _lock:
            _shell32.Shell_NotifyIconW(_NIM_MODIFY, ctypes.byref(nid))

        def cleanup():
            import time
            time.sleep(8)
            with _lock:
                _shell32.Shell_NotifyIconW(_NIM_DELETE, ctypes.byref(nid))
            if hicon:
                _user32.DestroyIcon(hicon)

        threading.Thread(target=cleanup, daemon=True).start()


def notify(title, message):
    try:
        if _system == "Windows":
            _notify_win(title, message)
        elif _system == "Darwin":
            subprocess.Popen(
                ["osascript", "-e",
                 f'display notification "{message.replace(chr(34), chr(39))}" '
                 f'with title "{title}"'],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
        elif _system == "Linux":
            subprocess.Popen(
                ["notify-send", title, message],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
    except Exception:
        pass
