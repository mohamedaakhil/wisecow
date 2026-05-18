# Application Health Checker & System Health Monitor

Two Python scripts that monitor your system and applications automatically.

---

## 1. Application Health Checker (`app_health_checker.py`)

Checks if your web applications are **UP or DOWN** every 30 seconds by sending HTTP requests.

### Requirements
```
pip install requests
```

### Usage
```
python3 app_health_checker.py
```

### Add Your Apps
Edit the `APPS` list at the top of the script:
```python
APPS = [
    {"name": "Google",  "url": "https://www.google.com"},
    {"name": "My App",  "url": "http://localhost:8080"},  # replace with your URL
]
```

### Output
```
[INFO]     [UP]   Google          | HTTP 200 | 0.63s
[INFO]     [UP]   GitHub          | HTTP 200 | 0.36s
[CRITICAL] [DOWN] My App          | No connection
```

### Status Meanings
| Status   | Meaning                        |
|----------|--------------------------------|
| `[UP]`   | App is reachable (HTTP < 400)  |
| `[DOWN]` | No connection / timed out      |
| `[DOWN]` | Server error (HTTP 400–599)    |

### Configuration
| Setting          | Default | Description                  |
|------------------|---------|------------------------------|
| `TIMEOUT`        | 5s      | Wait time per request        |
| `CHECK_INTERVAL` | 30s     | Seconds between checks       |
| `LOG_FILE`       | app_health.log | Log output file       |

---

## 2. System Health Monitor (`system_health_monitor.py`)

Monitors **CPU, Memory, Disk, and Processes** every 10 seconds and alerts when thresholds are exceeded.

### Requirements
```
pip install psutil
```

### Usage
```
python3 system_health_monitor.py
```

### Output
```
[INFO] CPU Usage     : 23.0%
[INFO] Memory Usage  : 55.3%  (2.3/4.2 GB)
[INFO] Disk [/]      : 46.1%  (9.2/270.6 GB)
[INFO] Processes     : 54 running
[CRITICAL] [ALERT] CPU 85.0% exceeds 80%
```

### Alert Thresholds
| Metric    | Default | Description               |
|-----------|---------|---------------------------|
| CPU       | > 80%   | Triggers CPU alert        |
| Memory    | > 80%   | Triggers memory alert     |
| Disk      | > 85%   | Triggers disk alert       |
| Processes | > 300   | Triggers process alert    |

Change thresholds at the top of the script:
```python
CPU_TH, MEM_TH, DISK_TH, PROC_TH = 80, 80, 85, 300
```

### Configuration
| Setting          | Default          | Description            |
|------------------|------------------|------------------------|
| `CHECK_INTERVAL` | 10s              | Seconds between checks |
| `LOG_FILE`       | health_monitor.log | Log output file      |

---

## Works On
- Windows
- Linux
- macOS

## Stop the Scripts
Press `Ctrl+C` in the terminal to stop either script gracefully.

## Log Files
Both scripts save all output to log files in the same folder:
- `app_health.log` — app checker logs
- `health_monitor.log` — system monitor logs
