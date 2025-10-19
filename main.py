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

if __name__ == "__main__":
    print("booting :)")
    print("stop with ctrl+c")

    last_hackatime_fetch = 0
    hackatime_data = {"time": "starting"}
    hackatime_fetch_interval = 100

    try:
        while True:
            cpu_data = get_cpu_stats()
            ram_data = get_ram_stats()
            gpu_data = get_gpu_stats()
            net_data = get_network_stats()
            vol_data = get_system_volume()

            now = datetime.datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")

            if time.time() - last_hackatime_fetch > hackatime_fetch_interval:
                hackatime_data = get_hackatime_stats()
                last_hackatime_fetch = time.time()

            data_string = (
                f"CPU_U:{cpu_data['usage']:.1f}|"
                f"CPU_T:{cpu_data['temp']:.1f}|"
                f"RAM_U:{ram_data['usage']:.1f}|"
                f"GPU_U:{gpu_data['usage']:.1f}|"
                f"GPU_T:{gpu_data['temp']:.1f}|"
                f"NET_D:{net_data['download']:.2f}|"
                f"NET_U:{net_data['upload']:.2f}|"
                f"VOL:{vol_data['level']:.0f}|"
                f"DATE:{date_str}|"
                f"TIME:{time_str}|"
                f"HACK:{hackatime_data['time']}"
            )

            print(data_string)

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nScript stopped by user.")