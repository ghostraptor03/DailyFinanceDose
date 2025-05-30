# financial_news_scraper/spiders/yahoo_finance_spider.py

import scrapy
from datetime import datetime, timedelta
from financial_news_scraper.items import NewsArticleItem

class YahooFinanceSpider(scrapy.Spider):
    name = 'yahoo_finance'
    allowed_domains = ['finance.yahoo.com']
    start_urls = [
        'https://finance.yahoo.com/news/',
        'https://finance.yahoo.com/topic/stock-market-news/',
    ]

    def parse(self, response):
        for href in response.css('h3 a::attr(href)').getall():
            yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'Yahoo Finance'
        item['url'] = response.url
        item['title'] = response.css('h1[data-test-locator="headline"]::text').get(default='').strip()
        item['author'] = response.css('.caas-author-byline-collapse::text').get(default='').strip()

        pub_iso = response.css('time::attr(datetime)').get()
        if not pub_iso:
            return
        item['published_date'] = pub_iso
        pub = datetime.fromisoformat(pub_iso)
        if pub < datetime.utcnow() - timedelta(hours=24):
            return

        paragraphs = response.css('.caas-body p::text').getall()
        item['content'] = ' '.join(p.strip() for p in paragraphs)
        # No clear tag selector; leave blank or add custom logic
        item['tags'] = []
        # Yahoo sometimes includes a lead image
        img = response.css('.caas-img img::attr(src)').get()
        if img:
            item['image_url'] = response.urljoin(img)

        yield item
