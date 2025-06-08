# Financial News Scraper

A comprehensive Scrapy-based web scraper for collecting daily financial news from multiple major sources.

## Features
- Scrapes today's financial news
- Drops articles older than 24 hours
- Deduplication, ticker extraction, sentiment analysis
- JSON/CSV output + SQLite persistence
- JavaScript rendering via Playwright

## Installation
root run py -3 -m venv .venv
 to make the venv
# 1) Activate your venv
.\.venv\Scripts\Activate.ps1

# 2) (Re)install dependencies & patch libs
pip install --upgrade pip
pip install -r requirements.txt
pip install legacy-cgi

# 3) Ensure output & log folders exist
mkdir logs
mkdir output
playwright install
pip install python-dateutil
# 4) Verify Scrapy sees your spiders
scrapy list

# 6) When that succeeds, run them all
python run_all_spiders.py
