import os
from datetime import datetime

BOT_NAME = 'financial_news_scraper'
SPIDER_MODULES = ['financial_news_scraper.spiders']
NEWSPIDER_MODULE = 'financial_news_scraper.spiders'

ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = 0.5
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 4
USER_AGENT = 'financial_news_scraper (+https://github.com/yourusername)'

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 10
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

ITEM_PIPELINES = {
    'financial_news_scraper.pipelines.ValidationPipeline': 100,
    'financial_news_scraper.pipelines.DateFilterPipeline': 150,
    'financial_news_scraper.pipelines.DuplicationPipeline': 200,
    'financial_news_scraper.pipelines.FinancialFilterPipeline': 300,
    'financial_news_scraper.pipelines.TickerExtractionPipeline': 400,
    'financial_news_scraper.pipelines.SentimentAnalysisPipeline': 500,
    'financial_news_scraper.pipelines.DatabasePipeline': 600,
    'financial_news_scraper.pipelines.ExportPipeline': 700,
}

MAX_ARTICLE_AGE_DAYS = 1

DOWNLOADER_MIDDLEWARES = {
    'financial_news_scraper.middlewares.RotateUserAgentMiddleware': 400,
    'financial_news_scraper.middlewares.ProxyMiddleware': 500,
    'scrapy_playwright.middleware.PlaywrightMiddleware': 800,
}
SPIDER_MIDDLEWARES = {
    'scrapy_playwright.middleware.PlaywrightSpiderMiddleware': 100,
}

PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 30_000

LOG_LEVEL = 'INFO'
LOG_FILE = f'logs/scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

DATABASE_URL = 'sqlite:///financial_news.db'