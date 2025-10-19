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

HACKATIME_API_URL = "https://hackatime.hackclub.com/api/hackatime/v1"
HACKATIME_API_KEY = "63c0a6d2-6bcd-46be-ae82-9e1a583d1833"
