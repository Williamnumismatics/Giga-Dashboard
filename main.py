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

def get_cpu_stats():
    usage = psutil.cpu_percent(interval=1)
    temp = 0.0
    temps = psutil.sensors_temperatures()
    if 'k10temp' in temps:
        temp = temps['k10temp'][0].current
    elif 'coretemp' in temps:
        temp = sum(entry.current for entry in temps['coretemp']) / len(temps['coretemp'])
    elif temps:
        temp = next(iter(temps.values()))[0].current
    return {"usage": usage, "temp": temp}

def get_ram_stats():
    """Returns RAM usage statistics."""
    return {"usage": psutil.virtual_memory().percent}

def get_gpu_stats():
    return {"usage": 0.0, "temp": 0.0}

