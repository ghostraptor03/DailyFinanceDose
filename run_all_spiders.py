#!/usr/bin/env python3
import subprocess
import time
import os
import sys
import glob
import json
from datetime import datetime

# ─── CONFIG ──────────────────────────────────────────────────────────────────
SPIDERS = [
    'reuters', 'bloomberg', 'cnbc', 'marketwatch', 'yahoo_finance',
    'seeking_alpha', 'financial_times', 'wall_street_journal', 'forbes',
    'business_insider', 'investopedia', 'barrons', 'economist', 'thestreet',
    'morningstar', 'investingcom', 'ft_alphaville', 'motleyfool',
    'gurufocus', 'financialpost', 'cnn_business', 'bbc_business', 'nasdaq',
    'kiplinger', 'investors_business_daily',
]

PER_SPIDER_DIR = os.path.join('output', 'per_spider')
MERGED_FILE     = os.path.join('output', 'all_financial_news.json')
DELAY = 1  # seconds between spiders
# ────────────────────────────────────────────────────────────────────────────

# Ensure folders exist
os.makedirs(PER_SPIDER_DIR, exist_ok=True)
os.makedirs('output', exist_ok=True)

# Path to the venv’s scrapy.exe
SCRAPY_EXE = os.path.join(os.path.dirname(sys.executable), 'scrapy.exe')

def run_spider(name):
    outfile = os.path.join(PER_SPIDER_DIR, f"{name}.json")
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] ▶ {name}")
    # Call scrapy.exe directly
    cmd = [SCRAPY_EXE, 'crawl', name, '-o', outfile, '-t', 'json']
    result = subprocess.run(cmd, cwd=os.getcwd(), capture_output=True, text=True)
    if result.returncode == 0:
        print(f"[{datetime.now():%H:%M:%S}] ✓ {name}")
    else:
        print(f"[{datetime.now():%H:%M:%S}] ✗ {name} FAILED")
        print(result.stderr.strip())
    return result.returncode == 0

def merge_all():
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] ▶ Merging JSON")
    all_items = []
    for path in sorted(glob.glob(os.path.join(PER_SPIDER_DIR, '*.json'))):
        try:
            data = json.load(open(path, encoding='utf-8'))
            all_items.extend(data if isinstance(data, list) else [data])
        except Exception as e:
            print(f"  ! skip {path}: {e}")
    with open(MERGED_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, indent=2, ensure_ascii=False)
    print(f"[{datetime.now():%H:%M:%S}] ✓ Merged {len(all_items)} items → {MERGED_FILE}")

if __name__ == '__main__':
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Starting")
    for spider in SPIDERS:
        run_spider(spider)
        time.sleep(DELAY)
    merge_all()
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] Done")
