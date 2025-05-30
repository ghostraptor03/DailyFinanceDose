# financial_news_scraper/settings.py

import os
from datetime import datetime

# ─── Project directories ────────────────────────────────────────────────────
# Determine the project root (one level above this settings.py file)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

# Paths for output and logs
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')
LOGS_DIR   = os.path.join(PROJECT_ROOT, 'logs')

# Ensure they exist before anything else
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
# ────────────────────────────────────────────────────────────────────────────

BOT_NAME = 'financial_news_scraper'
SPIDER_MODULES = ['financial_news_scraper.spiders']
NEWSPIDER_MODULE = 'financial_news_scraper.spiders'

# Respect robots.txt
ROBOTSTXT_OBEY = True

# Throttling & concurrency
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = 0.5
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 4

# Custom user-agent
USER_AGENT = 'financial_news_scraper (+http://www.yourdomain.com)'

# AutoThrottle
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = False

# ─── Pipelines & Middlewares ─────────────────────────────────────────────────
ITEM_PIPELINES = {
    'financial_news_scraper.pipelines.ValidationPipeline':        100,
    'financial_news_scraper.pipelines.DuplicationPipeline':       200,
    'financial_news_scraper.pipelines.FinancialFilterPipeline':   300,
    'financial_news_scraper.pipelines.TickerExtractionPipeline':  400,
    'financial_news_scraper.pipelines.SentimentAnalysisPipeline': 500,
    'financial_news_scraper.pipelines.DatabasePipeline':          600,
    'financial_news_scraper.pipelines.ExportPipeline':            700,
}

DOWNLOADER_MIDDLEWARES = {
    'financial_news_scraper.middlewares.RotateUserAgentMiddleware': 400,
    'financial_news_scraper.middlewares.ProxyMiddleware':           500,
}
# ────────────────────────────────────────────────────────────────────────────

# ─── Feed exports ────────────────────────────────────────────────────────────
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
FEEDS = {
    # JSON export
    os.path.join(OUTPUT_DIR, f'financial_news_{timestamp}.json'): {
        'format':    'json',
        'encoding':  'utf8',
        'store_empty': False,
        'indent':    2,
    },
    # CSV export
    os.path.join(OUTPUT_DIR, f'financial_news_{timestamp}.csv'): {
        'format':    'csv',
        'encoding':  'utf8',
        'store_empty': False,
    },
}
# ────────────────────────────────────────────────────────────────────────────

# Fingerprinting & reactor
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'
TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

# Logging
LOG_LEVEL = 'INFO'
LOG_FILE  = os.path.join(LOGS_DIR, f'scraper_{timestamp}.log')

# Financial keyword filter
FINANCIAL_KEYWORDS = [
    'stock','market','trading','investment','finance','economy',
    'earnings','revenue','profit','loss','GDP','inflation',
    'interest rate','fed','federal reserve','cryptocurrency',
    'bitcoin','nasdaq','dow jones','sp500','s&p','bond',
    'mortgage','banking','loan','credit','debt','merger',
    'acquisition','ipo','dividend','commodity','oil','gold',
    'forex','currency','treasury','securities','hedge fund',
    'private equity','venture capital','fintech','blockchain'
]

# SQLite for persistence
DATABASE_URL = 'sqlite:///financial_news.db'

# Export formats (if you ever want XML)
EXPORT_FORMATS = ['json','csv','xml']

# ─── Python 3.13 ExecutionEngine workaround ────────────────────────────────
import scrapy.core.engine as _engine
_engine.ExecutionEngine.close = lambda self: None
# ────────────────────────────────────────────────────────────────────────────
