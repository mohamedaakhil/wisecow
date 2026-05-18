#!/usr/bin/env python3
"""System Health Monitor â€“ Automatic Checking for every 60 seconds After running the file"""

import psutil, logging, datetime, time

# â”€â”€ Thresholds â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
CPU_TH, MEM_TH, DISK_TH, PROC_TH = 80, 80, 85, 300
LOG_FILE = "health_monitor.log"

# â”€â”€ Logger â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(LOG_FILE)],
)
log = logging.getLogger()
alert = lambda msg: log.critical("ðŸ”´ ALERT: " + msg)

# â”€â”€ Checks â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def check_cpu():
    usage = psutil.cpu_percent(interval=1)
    log.info(f"CPU Usage     : {usage}%")
    if usage > CPU_TH: alert(f"CPU {usage}% exceeds {CPU_TH}%")

def check_memory():
    m = psutil.virtual_memory()
    log.info(f"Memory Usage  : {m.percent}%  ({round(m.used/1e9,1)}/{round(m.total/1e9,1)} GB)")
    if m.percent > MEM_TH: alert(f"Memory {m.percent}% exceeds {MEM_TH}%")

def check_disk(path="/"):
    d = psutil.disk_usage(path)
    log.info(f"Disk [{path}]   : {d.percent}%  ({round(d.used/1e9,1)}/{round(d.total/1e9,1)} GB)")
    if d.percent > DISK_TH: alert(f"Disk {d.percent}% exceeds {DISK_TH}%")

def check_processes():
    procs = list(psutil.process_iter(["pid", "name", "cpu_percent"]))
    top5  = sorted(procs, key=lambda p: p.info["cpu_percent"] or 0, reverse=True)[:5]
    log.info(f"Processes     : {len(procs)} running")
    log.info("Top 5 by CPU  : " + ", ".join(f"{p.info['name']}({p.info['cpu_percent']}%)" for p in top5))
    if len(procs) > PROC_TH: alert(f"Process count {len(procs)} exceeds {PROC_TH}")

# â”€â”€ Auto Loop â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
log.info("Monitoring started. Press Ctrl+C to stop.")
try:
    while True:
        log.info("=" * 50)
        log.info(f"Health Check @ {datetime.datetime.now():%Y-%m-%d %H:%M:%S}")
        log.info("=" * 50)
        for fn in [check_cpu, check_memory, check_disk, check_processes]:
            fn()
        time.sleep(10)  # change to 60 for every minute
except KeyboardInterrupt:
    log.info("Monitoring stopped.")
