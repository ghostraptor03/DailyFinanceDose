# financial_news_scraper/spiders/marketwatch_spider.py

import scrapy
from datetime import datetime, timedelta
from financial_news_scraper.items import NewsArticleItem

class MarketWatchSpider(scrapy.Spider):
    name = 'marketwatch'
    allowed_domains = ['marketwatch.com']
    start_urls = [
        'https://www.marketwatch.com/markets',
        'https://www.marketwatch.com/economy-politics',
        'https://www.marketwatch.com/personal-finance',
    ]

    def parse(self, response):
        for href in response.css('a.link::attr(href)').getall():
            if href.startswith('/story/'):
                yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'MarketWatch'
        item['url'] = response.url
        item['title'] = response.css('h1.article__headline::text').get(default='').strip()
        item['author'] = response.css('.author__name::text').get(default='').strip()

        pub_iso = response.css('time.timestamp::attr(datetime)').get()
        if not pub_iso:
            return
        item['published_date'] = pub_iso
        pub = datetime.fromisoformat(pub_iso)
        if pub < datetime.utcnow() - timedelta(hours=24):
            return

        item['content'] = ' '.join(response.css('.articleBody p::text').getall())
        # MarketWatch tags not easily exposed; leave blank or customize
        item['tags'] = []
        yield item
