# Financial News Scraper

A comprehensive Scrapy-based web scraper for collecting daily financial news from multiple major sources.

## Features
- Scrapes today's financial news
- Drops articles older than 24 hours
- Deduplication, ticker extraction, sentiment analysis
- JSON/CSV output + SQLite persistence
- JavaScript rendering via Playwright

## Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/financial_news_scraper.git
   cd financial_news_scraper
   pip install -r requirements.txt
   python run_all_spiders.py