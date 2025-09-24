# dashboard.py
import tkinter as tk
from tkinter import ttk
from monitor.core import get_system_stats, psutil
import platform
from collections import deque
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

UPDATE_INTERVAL_MS = 1000
GRAPH_LENGTH = 60

DARK_BG = "#2b2b2b"
FRAME_BG = "#3c3f41"
TEXT_FG = "#ffffff"
PROGRESS_TROUGH = "#555555"
USAGE_COLOR = "lime"
TEMP_COLOR = "red"

class SystemMonitorDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("System Monitor Dashboard")
        self.configure(bg=DARK_BG)
        self.geometry("950x650")
        self.resizable(True, True)

        # Configure progress bar styles
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure("green.Horizontal.TProgressbar", troughcolor=PROGRESS_TROUGH, background=USAGE_COLOR)
        self.style.configure("red.Horizontal.TProgressbar", troughcolor=PROGRESS_TROUGH, background=TEMP_COLOR)

        # Notebook tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.cpu_tab = tk.Frame(self.notebook, bg=DARK_BG)
        self.gpu_tab = tk.Frame(self.notebook, bg=DARK_BG)
        self.mem_tab = tk.Frame(self.notebook, bg=DARK_BG)
        self.disk_tab = tk.Frame(self.notebook, bg=DARK_BG)

        self.notebook.add(self.cpu_tab, text="CPU")
        self.notebook.add(self.gpu_tab, text="GPU")
        self.notebook.add(self.mem_tab, text="Memory")
        self.notebook.add(self.disk_tab, text="Disk")

        # Graph data storage
        self.cpu_history = deque(maxlen=GRAPH_LENGTH)
        self.cpu_temp_history = deque(maxlen=GRAPH_LENGTH)
        self.gpu_history = deque(maxlen=GRAPH_LENGTH)
        self.gpu_temp_history = deque(maxlen=GRAPH_LENGTH)
        self.mem_history = deque(maxlen=GRAPH_LENGTH)
        self.disk_history = {}

        # Initialize tabs
        self.create_cpu_tab()
        self.create_gpu_tab()
        self.create_mem_tab()
        self.create_disk_tab()

        # Start updating stats
        self.update_stats()

    # Retrieve CPU name based on OS
    def get_cpu_name(self):
        system = platform.system()
        if system == "Windows":
            try:
                import wmi
                c = wmi.WMI()
                for cpu in c.Win32_Processor():
                    return cpu.Name.strip()
            except Exception:
                return platform.processor() or "CPU"
        elif system == "Linux":
            try:
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if "model name" in line:
                            return line.split(":",1)[1].strip()
            except Exception:
                return "CPU"
        return "CPU"

    # Determine progress bar style based on thresholds
    def get_color_style(self, value, thresholds=(50,80)):
        if value is None:
            return "green.Horizontal.TProgressbar"
        if value <= thresholds[0]:
            return "green.Horizontal.TProgressbar"
        elif value <= thresholds[1]:
            return "red.Horizontal.TProgressbar"
        else:
            return "red.Horizontal.TProgressbar"

    # Create CPU tab layout and graph
    def create_cpu_tab(self):
        self.cpu_left = tk.Frame(self.cpu_tab, bg=FRAME_BG, padx=10, pady=10)
        self.cpu_left.pack(side="left", fill="y", padx=5, pady=5)

        self.cpu_name_label = tk.Label(self.cpu_left, text=self.get_cpu_name(), bg=FRAME_BG, fg=TEXT_FG, font=("Segoe UI", 11, "bold"))
        self.cpu_name_label.pack(pady=5)
        self.cpu_usage_label = tk.Label(self.cpu_left, text="Usage: 0%", bg=FRAME_BG, fg=TEXT_FG)
        self.cpu_usage_label.pack(pady=2)
        self.cpu_usage_bar = ttk.Progressbar(self.cpu_left)
        self.cpu_usage_bar.pack(fill="x", pady=2)
        self.cpu_temp_label = tk.Label(self.cpu_left, text="Temp: N/A", bg=FRAME_BG, fg=TEXT_FG)
        self.cpu_temp_label.pack(pady=2)
        self.cpu_clock_label = tk.Label(self.cpu_left, text="Clock: N/A MHz", bg=FRAME_BG, fg=TEXT_FG)
        self.cpu_clock_label.pack(pady=2)

        # CPU graph
        self.cpu_fig = Figure(figsize=(5,3), dpi=100)
        self.cpu_ax = self.cpu_fig.add_subplot(111)
        self.cpu_ax.set_title("CPU Usage & Temp")
        self.cpu_ax.set_ylim(0,100)
        self.cpu_line, = self.cpu_ax.plot([],[], color=USAGE_COLOR, label="Usage")
        self.cpu_temp_line, = self.cpu_ax.plot([],[], color=TEMP_COLOR, label="Temp")
        self.cpu_ax.legend(loc="upper right")

        self.cpu_canvas = FigureCanvasTkAgg(self.cpu_fig, master=self.cpu_tab)
        self.cpu_canvas.get_tk_widget().pack(side="right", fill="both", expand=True)

    # Create GPU tab layout and graph
    def create_gpu_tab(self):
        self.gpu_left = tk.Frame(self.gpu_tab, bg=FRAME_BG, padx=10, pady=10)
        self.gpu_left.pack(side="left", fill="y", padx=5, pady=5)

        self.gpu_name_label = tk.Label(self.gpu_left, text="GPU: N/A", bg=FRAME_BG, fg=TEXT_FG, font=("Segoe UI", 11, "bold"))
        self.gpu_name_label.pack(pady=5)
        self.gpu_usage_label = tk.Label(self.gpu_left, text="Usage: N/A%", bg=FRAME_BG, fg=TEXT_FG)
        self.gpu_usage_label.pack(pady=2)
        self.gpu_usage_bar = ttk.Progressbar(self.gpu_left)
        self.gpu_usage_bar.pack(fill="x", pady=2)
        self.gpu_temp_label = tk.Label(self.gpu_left, text="Temp: N/A°C", bg=FRAME_BG, fg=TEXT_FG)
        self.gpu_temp_label.pack(pady=2)

        # GPU graph
        self.gpu_fig = Figure(figsize=(5,3), dpi=100)
        self.gpu_ax = self.gpu_fig.add_subplot(111)
        self.gpu_ax.set_title("GPU Usage & Temp")
        self.gpu_ax.set_ylim(0,100)
        self.gpu_line, = self.gpu_ax.plot([],[], color=USAGE_COLOR, label="Usage")
        self.gpu_temp_line, = self.gpu_ax.plot([],[], color=TEMP_COLOR, label="Temp")
        self.gpu_ax.legend(loc="upper right")

        self.gpu_canvas = FigureCanvasTkAgg(self.gpu_fig, master=self.gpu_tab)
        self.gpu_canvas.get_tk_widget().pack(side="right", fill="both", expand=True)

    # Create Memory tab layout and graph
    def create_mem_tab(self):
        self.mem_left = tk.Frame(self.mem_tab, bg=FRAME_BG, padx=10, pady=10)
        self.mem_left.pack(side="left", fill="y", padx=5, pady=5)

        self.mem_usage_label = tk.Label(self.mem_left, text="Usage: 0%", bg=FRAME_BG, fg=TEXT_FG)
        self.mem_usage_label.pack(pady=2)
        self.mem_usage_bar = ttk.Progressbar(self.mem_left)
        self.mem_usage_bar.pack(fill="x", pady=2)
        self.mem_capacity_label = tk.Label(self.mem_left, text="Capacity: N/A GB", bg=FRAME_BG, fg=TEXT_FG)
        self.mem_capacity_label.pack(pady=2)

        # Memory graph
        self.mem_fig = Figure(figsize=(5,3), dpi=100)
        self.mem_ax = self.mem_fig.add_subplot(111)
        self.mem_ax.set_title("Memory Usage")
        self.mem_ax.set_ylim(0,100)
        self.mem_line, = self.mem_ax.plot([],[], color=USAGE_COLOR)

        self.mem_canvas = FigureCanvasTkAgg(self.mem_fig, master=self.mem_tab)
        self.mem_canvas.get_tk_widget().pack(side="right", fill="both", expand=True)

    # Create Disk tab layout and graphs
    def create_disk_tab(self):
        self.disk_left = tk.Frame(self.disk_tab, bg=FRAME_BG, padx=10, pady=10)
        self.disk_left.pack(side="left", fill="y", padx=5, pady=5)

        self.disk_fig = Figure(figsize=(5,3), dpi=100)
        self.disk_canvas = FigureCanvasTkAgg(self.disk_fig, master=self.disk_tab)
        self.disk_canvas.get_tk_widget().pack(side="right", fill="both", expand=True)
        self.disk_axes = {}
        self.disk_lines = {}
        self.disk_temp_lines = {}
        self.disk_history = {}
        self.disk_temp_history = {}

    # Update all stats and graphs
    def update_stats(self):
        stats = get_system_stats()

        # CPU updates
        cpu_percent = stats['cpu_percent']
        self.cpu_usage_label.config(text=f"Usage: {cpu_percent}%")
        self.cpu_usage_bar.config(style=self.get_color_style(cpu_percent))
        self.cpu_usage_bar['value'] = cpu_percent

        cpu_temp = stats['cpu_temp']
        self.cpu_temp_label.config(text=f"Temp: {cpu_temp:.1f}°C" if cpu_temp else "Temp: N/A")
        self.cpu_clock_label.config(text=f"Clock: {psutil.cpu_freq().current:.0f} MHz" if psutil.cpu_freq() else "Clock: N/A MHz")

        self.cpu_history.append(cpu_percent)
        self.cpu_temp_history.append(cpu_temp if cpu_temp else None)

        self.cpu_line.set_data(range(len(self.cpu_history)), list(self.cpu_history))
        self.cpu_temp_line.set_data(range(len(self.cpu_temp_history)), [v if v is not None else 0 for v in self.cpu_temp_history])
        self.cpu_ax.set_xlim(0, max(GRAPH_LENGTH, len(self.cpu_history)))
        self.cpu_canvas.draw()

        # GPU updates
        if stats['gpus']:
            gpu = stats['gpus'][0]
            gpu_percent = gpu['utilization']
            gpu_temp = gpu['temperature']

            self.gpu_name_label.config(text=gpu['name'])
            self.gpu_usage_label.config(text=f"Usage: {gpu_percent}%")
            self.gpu_usage_bar.config(style=self.get_color_style(gpu_percent))
            self.gpu_usage_bar['value'] = gpu_percent
            self.gpu_temp_label.config(text=f"Temp: {gpu_temp}°C")

            self.gpu_history.append(gpu_percent)
            self.gpu_temp_history.append(gpu_temp)

            self.gpu_line.set_data(range(len(self.gpu_history)), list(self.gpu_history))
            self.gpu_temp_line.set_data(range(len(self.gpu_temp_history)), list(self.gpu_temp_history))
            self.gpu_ax.set_xlim(0, max(GRAPH_LENGTH, len(self.gpu_history)))
        else:
            self.gpu_name_label.config(text="N/A")
            self.gpu_usage_label.config(text="Usage: N/A")
            self.gpu_usage_bar['value'] = 0
            self.gpu_temp_label.config(text="Temp: N/A")
            self.gpu_history.append(0)
            self.gpu_temp_history.append(0)
            self.gpu_line.set_data(range(len(self.gpu_history)), list(self.gpu_history))
            self.gpu_temp_line.set_data(range(len(self.gpu_temp_history)), list(self.gpu_temp_history))

        self.gpu_canvas.draw()

        # Memory updates
        mem = psutil.virtual_memory()
        mem_percent = mem.percent
        self.mem_usage_label.config(text=f"Usage: {mem_percent}%")
        self.mem_usage_bar.config(style=self.get_color_style(mem_percent))
        self.mem_usage_bar['value'] = mem_percent
        self.mem_capacity_label.config(text=f"Capacity: {mem.total / (1024**3):.1f} GB")
        self.mem_history.append(mem_percent)
        self.mem_line.set_data(range(len(self.mem_history)), list(self.mem_history))
        self.mem_ax.set_xlim(0, max(GRAPH_LENGTH, len(self.mem_history)))
        self.mem_canvas.draw()

        # Disk updates
        partitions = psutil.disk_partitions(all=False)
        for widget in self.disk_left.winfo_children():
            widget.destroy()
        self.disk_fig.clf()
        self.disk_axes.clear()
        self.disk_lines.clear()

        for idx, part in enumerate(partitions):
            try:
                usage = psutil.disk_usage(part.mountpoint)
            except PermissionError:
                continue

            frame = tk.Frame(self.disk_left, bg=FRAME_BG)
            frame.pack(pady=5)
            tk.Label(frame, text=f"Disk {idx}: ({part.device})", bg=FRAME_BG, fg=TEXT_FG, font=("Segoe UI", 10, "bold")).pack()
            tk.Label(frame, text=f"Usage: {usage.percent}%", bg=FRAME_BG, fg=TEXT_FG).pack()
            bar = ttk.Progressbar(frame)
            bar.pack(fill="x", padx=20, pady=(0,2))
            bar.config(value=usage.percent, style=self.get_color_style(usage.percent))
            tk.Label(frame, text=f"Capacity: {usage.total / (1024**3):.1f} GB", bg=FRAME_BG, fg=TEXT_FG).pack()

            if part.device not in self.disk_history:
                self.disk_history[part.device] = deque([usage.percent]*GRAPH_LENGTH, maxlen=GRAPH_LENGTH)
            else:
                self.disk_history[part.device].append(usage.percent)

            ax = self.disk_fig.add_subplot(len(partitions), 1, idx+1)
            ax.set_title(f"Disk {idx} Usage (%)")
            ax.set_ylim(0,100)
            line, = ax.plot(range(len(self.disk_history[part.device])), list(self.disk_history[part.device]), color=USAGE_COLOR)
            self.disk_axes[part.device] = ax
            self.disk_lines[part.device] = line

        self.disk_canvas.draw()
        self.after(UPDATE_INTERVAL_MS, self.update_stats)


if __name__ == "__main__":
    app = SystemMonitorDashboard()
    app.mainloop()
