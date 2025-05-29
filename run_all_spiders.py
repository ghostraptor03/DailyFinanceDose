#!/usr/bin/env python3
import subprocess
import time
from datetime import datetime

SPIDERS = ['reuters', 'bloomberg', 'cnbc', 'marketwatch', 'yahoo_finance', 'seeking_alpha']
DELAY   = 30  # seconds between each spider

def run_spider(name):
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] ▶ Starting {name}")
    result = subprocess.run(
        ['scrapy', 'crawl', name],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print(f"[{datetime.now():%H:%M:%S}] ✓ {name} finished")
    else:
        print(f"[{datetime.now():%H:%M:%S}] ✗ {name} failed:")
        print(result.stderr)
    return result.returncode == 0

if __name__ == '__main__':
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Starting all spiders")
    for spider in SPIDERS:
        run_spider(spider)
        time.sleep(DELAY)
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] All done.")
