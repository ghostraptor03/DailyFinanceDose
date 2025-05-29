import re
import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
from dateutil import parser
from scrapy.exceptions import DropItem
from itemadapter import ItemAdapter

class ValidationPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if not adapter.get('title') or not adapter.get('url'):
            raise DropItem(f"Missing title or URL in {item}")
        adapter['scraped_date'] = datetime.utcnow().isoformat()
        adapter['article_id'] = hashlib.md5(
            f"{adapter['title']}{adapter['url']}".encode()
        ).hexdigest()
        return item

class DateFilterPipeline:
    def __init__(self, max_age_days):
        self.max_age = timedelta(days=max_age_days)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getint('MAX_ARTICLE_AGE_DAYS', 1))

    def process_item(self, item, spider):
        pub = item.get('published_date')
        if not pub:
            raise DropItem(f"No published_date on {item.get('url')}")
        published = parser.parse(pub)
        if datetime.utcnow() - published > self.max_age:
            raise DropItem(f"Too old: {item['title']} ({pub})")
        return item

class DuplicationPipeline:
    def __init__(self):
        self.seen_ids = set()

    def process_item(self, item, spider):
        article_id = ItemAdapter(item).get('article_id')
        if article_id in self.seen_ids:
            raise DropItem(f"Duplicate: {item['title']}")
        self.seen_ids.add(article_id)
        return item

class FinancialFilterPipeline:
    def __init__(self, financial_keywords):
        self.financial_keywords = financial_keywords

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get('FINANCIAL_KEYWORDS', []))

    def process_item(self, item, spider):
        text = ' '.join([
            item.get('title', '').lower(),
            item.get('summary', '').lower(),
            item.get('content', '').lower()
        ])
        if not any(k in text for k in self.financial_keywords):
            raise DropItem(f"Non-financial: {item['title']}")
        item['category'] = 'Finance'
        return item

class TickerExtractionPipeline:
    def __init__(self):
        self.ticker_pattern = re.compile(r'\b[A-Z]{2,5}\b')
        self.common_tickers = {
            'AAPL','GOOGL','MSFT','AMZN','TSLA','META','NVDA',
            'JPM','BAC','WFC','GS','MS','C','USB',
            'SPY','QQQ','IWM','DIA','VTI','VOO'
        }

    def process_item(self, item, spider):
        text = ' '.join([item.get('title',''), item.get('summary',''), item.get('content','')])
        found = self.ticker_pattern.findall(text)
        tickers = [t for t in found if t in self.common_tickers or len(t) <= 4]
        item['ticker_symbols'] = list(set(tickers))
        return item

class SentimentAnalysisPipeline:
    def __init__(self):
        self.pos = ['gain','rise','profit','bull','rally','soar']
        self.neg = ['fall','drop','loss','bear','crash','plunge']

    def process_item(self, item, spider):
        text = (item.get('title','') + ' ' + item.get('summary','')).lower()
        p = sum(t in text for t in self.pos)
        n = sum(t in text for t in self.neg)
        item['sentiment_score'] = 'positive' if p>n else 'negative' if n>p else 'neutral'
        return item

class DatabasePipeline:
    def __init__(self, database_url):
        self.database_url = database_url

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get('DATABASE_URL'))

    def open_spider(self, spider):
        path = self.database_url.replace('sqlite:///','')
        self.conn = sqlite3.connect(path)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id TEXT PRIMARY KEY,
                title TEXT,
                url TEXT,
                source TEXT,
                author TEXT,
                published_date TEXT,
                scraped_date TEXT,
                summary TEXT,
                content TEXT,
                category TEXT,
                tags TEXT,
                image_url TEXT,
                ticker_symbols TEXT,
                sentiment_score TEXT
            )
        ''' )
        self.conn.commit()

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        a = ItemAdapter(item)
        tick = json.dumps(a.get('ticker_symbols', []))
        tags = json.dumps(a.get('tags', []))
        self.conn.execute('''INSERT OR REPLACE INTO articles VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)''' ,(
            a.get('article_id'), a.get('title'), a.get('url'), a.get('source'),
            a.get('author'), a.get('published_date'), a.get('scraped_date'),
            a.get('summary'), a.get('content'), a.get('category'),
            tags, a.get('image_url'), tick, a.get('sentiment_score')
        ))
        self.conn.commit()
        return item

class ExportPipeline:
    def open_spider(self, spider):
        import os; os.makedirs('output', exist_ok=True); os.makedirs('logs', exist_ok=True)
    def process_item(self, item, spider):
        return item