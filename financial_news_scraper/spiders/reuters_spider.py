# financial_news_scraper/spiders/reuters_spider.py

import scrapy
from datetime import datetime, timedelta
from financial_news_scraper.items import NewsArticleItem

class ReutersSpider(scrapy.Spider):
    name = 'reuters'
    allowed_domains = ['reuters.com']
    start_urls = [
        'https://www.reuters.com/business/',
        'https://www.reuters.com/markets/',
        'https://www.reuters.com/technology/',
    ]

    def parse(self, response):
        links = response.css('a[data-testid="Heading"]::attr(href)').getall()
        for href in links:
            yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'Reuters'
        item['url'] = response.url
        item['title'] = response.css('h1[data-testid="Heading"]::text').get(default='').strip()
        item['author'] = response.css('span[data-testid="AuthorName"]::text').get(default='').strip()

        # published_date + 24h filter
        pub_iso = response.css('time::attr(datetime)').get()
        if not pub_iso:
            return
        item['published_date'] = pub_iso
        pub = datetime.fromisoformat(pub_iso)
        if pub < datetime.utcnow() - timedelta(hours=24):
            return

        # full content
        paragraphs = response.css('div[data-testid="paragraph"] p::text').getall()
        item['content'] = ' '.join(p.strip() for p in paragraphs)
        item['tags'] = response.css('a[data-testid="Link"]::text').getall()

        # lead image
        img = response.css('img::attr(src)').get()
        if img:
            item['image_url'] = response.urljoin(img)

        yield item
