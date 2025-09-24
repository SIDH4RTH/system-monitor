#core.py
import psutil
import subprocess
from collections import deque
from datetime import datetime

# Historical data storage
CPU_HISTORY = deque(maxlen=60)
MEM_HISTORY = deque(maxlen=60)
DISK_HISTORY = deque(maxlen=60)
GPU_HISTORY = deque(maxlen=60)

# CPU, memory, disk usage functions
def get_cpu_usage():
    usage = psutil.cpu_percent(interval=None)
    CPU_HISTORY.append(usage)
    return usage

def get_memory_usage():
    mem = psutil.virtual_memory()
    usage = mem.percent
    MEM_HISTORY.append(usage)
    return usage

def get_disk_usage():
    disk = psutil.disk_usage('/')
    usage = disk.percent
    DISK_HISTORY.append(usage)
    return usage

# CPU temperature (Return None if unavailable)
def get_cpu_temp():
    if not hasattr(psutil, "sensors_temperatures"):
        return None
    temps = psutil.sensors_temperatures()
    if not temps:
        return None
    for key in temps:
        if key.lower().startswith("core") or key.lower().startswith("cpu"):
            core_temps = temps[key]
            return sum(t.current for t in core_temps) / len(core_temps)
    return None

# GPU stats via nvidia-smi
def get_gpu_stats():
    gpus = []
    try:
        result = subprocess.run(
            ["nvidia-smi",
             "--query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().split("\n")
        for line in lines:
            if not line.strip():
                continue
            name, mem_used, mem_total, util, temp = [x.strip() for x in line.split(",")]
            gpu_info = {
                "name": name,
                "memory_used": int(mem_used),
                "memory_total": int(mem_total),
                "utilization": int(util),
                "temperature": int(temp)
            }
            gpus.append(gpu_info)
            GPU_HISTORY.append(gpu_info)
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return gpus

# Collect all system stats in a dictionary
def get_system_stats():
    stats = {
        "timestamp": datetime.now(),
        "cpu_percent": get_cpu_usage(),
        "memory_percent": get_memory_usage(),
        "disk_percent": get_disk_usage(),
        "cpu_temp": get_cpu_temp(),
        "gpus": get_gpu_stats()
    }
    return stats

# Simple CLI test loop
if __name__ == "__main__":
    import time
    while True:
        stats = get_system_stats()
        print(f"[{stats['timestamp']}] CPU: {stats['cpu_percent']}% | Mem: {stats['memory_percent']}% | Disk: {stats['disk_percent']}%")
        if stats["cpu_temp"]:
            print(f"CPU Temp: {stats['cpu_temp']:.1f}°C")
        if stats["gpus"]:
            for i, gpu in enumerate(stats["gpus"]):
                print(f"GPU{i} ({gpu['name']}): {gpu['utilization']}% | {gpu['memory_used']}/{gpu['memory_total']} MB | Temp: {gpu['temperature']}°C")
        else:
            print("No GPU detected or nvidia-smi not available")
        print("-" * 50)
        time.sleep(1)
