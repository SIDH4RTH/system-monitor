#logger.py
import csv
from pathlib import Path
from datetime import datetime

# CSV logger for system stats
class CSVLogger:
    def __init__(self, path="monitor_log.csv"):
        self.path = Path(path)
        new_file = not self.path.exists()
        self.f = open(self.path, "a", newline="", encoding="utf-8")
        self.writer = csv.writer(self.f)
        if new_file:
            # Write CSV header if new file
            self.writer.writerow([
                "timestamp","cpu","memory","disk","net_sent","net_recv","gpu_load","gpu_temp"
            ])

    # Log one sample (dict) to CSV
    def log(self, sample: dict):
        self.writer.writerow([
            sample.get("timestamp", datetime.utcnow().isoformat()),
            sample.get("cpu"),
            sample.get("memory"),
            sample.get("disk"),
            sample.get("net_sent"),
            sample.get("net_recv"),
            sample.get("gpu_load"),
            sample.get("gpu_temp")
        ])
        self.f.flush()

    # Close CSV file
    def close(self):
        self.f.close()
