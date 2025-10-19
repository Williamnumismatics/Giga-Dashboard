import psutil
import time
import datetime
import requests

try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    is_Windows = True
except ImportError:
    is_Windows = False