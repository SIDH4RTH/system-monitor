# System Monitor Dashboard

A Python desktop application to monitor CPU, GPU, Memory, and Disk usage in real-time.  
It uses **Tkinter** for GUI, **Matplotlib** for graphs, and **psutil** for system statistics.

## Features

- Real-time monitoring of CPU, GPU, Memory, and Disk.
- Usage and temperature graphs with live updates.
- Progress bars with color coding.
- CPU and GPU temperature display.
- Cross-platform support (Windows & Linux).
- Modular design:
  - `core.py` → fetches system stats
  - `dashboard.py` → GUI dashboard
  - `logger.py` → CSV logging
  - `main.py` → CLI display

## Installation

1. Clone the repository:
```bash
git clone https://github.com/SIDH4RTH/system-monitor.git
cd system-monitor
```

2.(Recommended) Create a virtual environment inside the project folder:
```bash
python -m venv venv
```
-Activate it:
    -Windows: venv\Scripts\activate
    -Linux/macOS: source venv/bin/activate

3.Install dependencies from requirements.txt in the project folder:
```bash
pip install -r requirements.txt
```

## Usage

-Run CLI mode:
```bash
python main.py
```

-Run GUI dashboard:
```bash
python dashboard.py
```
