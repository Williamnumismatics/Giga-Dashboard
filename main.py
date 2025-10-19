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

def get_network_stats():
    """Returns network I/O statistics."""
    last_io = psutil.net_io_counters()
    time.sleep(1)
    new_io = psutil.net_io_counters()
    bytes_sent_per_sec = new_io.bytes_sent - last_io.bytes_sent
    bytes_recv_per_sec = new_io.bytes_recv - last_io.bytes_recv
    upload_speed = (bytes_sent * 8) / (1024 * 1024)
    download_speed = (bytes_recv * 8) / (1024 * 1024)
    return {"internet upload speed": upload_speed, "internet download speed": download_speed}

def get_system_volume():
    """Returns system volume percentage on Windows."""
    if not is_Windows: return{"level" : 0.0}
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        return {"level": volume.GetMasterVolumeLevelScalar() * 100}     
    except Exception:
        return {"level": 0.0}

def get_hackatime_stats():
    """Fetches HackaTime stats from the API."""
    if not HACKATIME_API_KEY or HACKATIME_API_KEY == "YOUR_API_KEY_HERE":
        return {"time": "No API Key"}
    try:
        api_endpoint = f"{HACKATIME_API_URL}/users/current/summaries/range=today"
        response = requests.get(api_endpoint, params={'api_key': HACKATIME_API_KEY})
        response.raise_for_status()
        data = response.json()
        today_summary = data['data'][0]
        return {"time": today_summary['grand_total']['text']}
    except requests.exceptions.RequestException as e:
        print(f"Error fetching HackaTime data: {e}")
        return {"time": "Error"}
