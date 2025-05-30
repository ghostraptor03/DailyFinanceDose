# financial_news_scraper/spiders/bloomberg_spider.py

import scrapy
from datetime import datetime, timedelta
from financial_news_scraper.items import NewsArticleItem

class BloombergSpider(scrapy.Spider):
    name = 'bloomberg'
    allowed_domains = ['bloomberg.com']
    start_urls = [
        'https://www.bloomberg.com/markets',
        'https://www.bloomberg.com/economics',
        'https://www.bloomberg.com/technology',
    ]

    def parse(self, response):
        links = response.css('a[data-module="Story"]::attr(href)').getall()
        for href in links:
            yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'Bloomberg'
        item['url'] = response.url
        item['title'] = response.css('h1[data-module="ArticleHeader"]::text').get(default='').strip()
        item['author'] = response.css('.author-link::text').get(default='').strip()

        pub_iso = response.css('time::attr(datetime)').get()
        if not pub_iso:
            return
        item['published_date'] = pub_iso
        pub = datetime.fromisoformat(pub_iso)
        if pub < datetime.utcnow() - timedelta(hours=24):
            return

        item['content'] = ' '.join(response.css('.body-copy p::text').getall())
        item['tags'] = response.css('.article__topics a::text').getall()
        img = response.css('.main-image img::attr(src)').get()
        if img:
            item['image_url'] = response.urljoin(img)

        yield item
