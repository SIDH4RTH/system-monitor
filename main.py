# main.py
import time
from monitor.core import get_system_stats

# Display system stats in console
def display_stats():
    stats = get_system_stats()

    # Print basic CPU, Memory, Disk info
    print(f"Time: {stats['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"CPU Usage: {stats['cpu_percent']}%")
    print(f"Memory Usage: {stats['memory_percent']}%")
    print(f"Disk Usage: {stats['disk_percent']}%")

    # Print GPU info if available
    if stats["gpus"]:
        for i, gpu in enumerate(stats["gpus"]):
            print(f"GPU{i} ({gpu['name']}): {gpu['utilization']}% | "
                  f"{gpu['memory_used']}/{gpu['memory_total']} MB")
    else:
        print("No GPU detected or nvidia-smi not available")

    print("-" * 50)

# Main monitoring loop
if __name__ == "__main__":
    interval = 1.0  # seconds
    try:
        while True:
            display_stats()
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Monitoring stopped.")
