#!/usr/bin/env python3
"""Application Health Checker â€“ checks HTTP status of apps/URLs"""

import requests, logging, datetime, time, sys

# â”€â”€ Apps to monitor (add/edit your URLs here) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
APPS = [
    {"name": "Google",   "url": "https://www.google.com"},
    {"name": "GitHub",   "url": "https://www.github.com"},
    {"name": "My App",   "url": "http://localhost:8080"},  # replace with your app URL
]

TIMEOUT        = 5    # seconds to wait for a response
CHECK_INTERVAL = 30   # seconds between each round of checks
LOG_FILE       = "app_health.log"

# â”€â”€ Logger (console + file, UTF-8 safe) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)
sys.stdout.reconfigure(encoding="utf-8")
log = logging.getLogger()

# â”€â”€ Single app check â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def check_app(app):
    name, url = app["name"], app["url"]
    try:
        res = requests.get(url, timeout=TIMEOUT)
        if res.status_code < 400:
            log.info    (f"[UP]   {name:<15} | HTTP {res.status_code} | {res.elapsed.total_seconds():.2f}s")
        else:
            log.critical(f"[DOWN] {name:<15} | HTTP {res.status_code} â€“ server error")
    except requests.ConnectionError:
        log.critical(f"[DOWN] {name:<15} | No connection")
    except requests.Timeout:
        log.critical(f"[DOWN] {name:<15} | Timed out after {TIMEOUT}s")
    except Exception as e:
        log.critical(f"[DOWN] {name:<15} | Error: {e}")

# â”€â”€ Auto loop â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
log.info("App Health Checker started. Press Ctrl+C to stop.")
try:
    while True:
        log.info("=" * 55)
        log.info(f"Health Check @ {datetime.datetime.now():%Y-%m-%d %H:%M:%S}")
        log.info("=" * 55)
        for app in APPS:
            check_app(app)
        time.sleep(CHECK_INTERVAL)
except KeyboardInterrupt:
    log.info("Checker stopped.")
