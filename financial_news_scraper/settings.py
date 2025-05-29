# financial_news_scraper/settings.py

import os
from datetime import datetime

BOT_NAME = 'financial_news_scraper'
SPIDER_MODULES = ['financial_news_scraper.spiders']
NEWSPIDER_MODULE = 'financial_news_scraper.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure delays for requests
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = 0.5
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 4

# User agent
USER_AGENT = 'financial_news_scraper (+http://www.yourdomain.com)'

# AutoThrottle settings
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = False

# Enable pipelines
ITEM_PIPELINES = {
    'financial_news_scraper.pipelines.ValidationPipeline': 100,
    'financial_news_scraper.pipelines.DuplicationPipeline': 200,
    'financial_news_scraper.pipelines.FinancialFilterPipeline': 300,
    'financial_news_scraper.pipelines.TickerExtractionPipeline': 400,
    'financial_news_scraper.pipelines.SentimentAnalysisPipeline': 500,
    'financial_news_scraper.pipelines.DatabasePipeline': 600,
    'financial_news_scraper.pipelines.ExportPipeline': 700,
}

# Enable middlewares
DOWNLOADER_MIDDLEWARES = {
    'financial_news_scraper.middlewares.RotateUserAgentMiddleware': 400,
    'financial_news_scraper.middlewares.ProxyMiddleware': 500,
}

# Configure feeds
FEEDS = {
    f'output/financial_news_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json': {
        'format': 'json',
        'encoding': 'utf8',
        'store_empty': False,
        'indent': 2,
    },
    f'output/financial_news_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv': {
        'format': 'csv',
        'encoding': 'utf8',
        'store_empty': False,
    },
}

# Request fingerprinting implementation
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'

# Configure Twisted reactor
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

# Log level
LOG_LEVEL = 'INFO'
LOG_FILE = f'logs/scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

# Custom settings
FINANCIAL_KEYWORDS = [
    'stock', 'market', 'trading', 'investment', 'finance', 'economy',
    'earnings', 'revenue', 'profit', 'loss', 'GDP', 'inflation',
    'interest rate', 'fed', 'federal reserve', 'cryptocurrency',
    'bitcoin', 'nasdaq', 'dow jones', 'sp500', 's&p', 'bond',
    'mortgage', 'banking', 'loan', 'credit', 'debt', 'merger',
    'acquisition', 'ipo', 'dividend', 'commodity', 'oil', 'gold',
    'forex', 'currency', 'treasury', 'securities', 'hedge fund',
    'private equity', 'venture capital', 'fintech', 'blockchain'
]

# Database settings (SQLite for simplicity)
DATABASE_URL = 'sqlite:///financial_news.db'

# Export settings
EXPORT_FORMATS = ['json', 'csv', 'xml']

# --- BEGIN patch to avoid ExecutionEngine.downloader bug on Python 3.13 ---
import scrapy.core.engine as _engine

# Prevent the ExecutionEngine.__init__ from calling .close() which fails on 3.13
_engine.ExecutionEngine.close = lambda self: None
# --- END patch ---
