# financial_news_scraper/spiders/morningstar_spider.py

import scrapy
from datetime import datetime, timedelta
from financial_news_scraper.items import NewsArticleItem

class MorningstarSpider(scrapy.Spider):
    name = 'morningstar'
    allowed_domains = ['morningstar.com']
    start_urls = ['https://www.morningstar.com/news']

    def parse(self, response):
        for href in response.css('a.ts-article-link::attr(href)').getall():
            yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'Morningstar'
        item['url'] = response.url
        item['title'] = response.css('h1::text').get(default='').strip()
        item['author'] = response.css('.byline__author::text').get(default='').strip()

        pub_iso = response.css('time::attr(datetime)').get()
        if not pub_iso:
            return
        item['published_date'] = pub_iso
        pub = datetime.fromisoformat(pub_iso)
        if pub < datetime.utcnow() - timedelta(hours=24):
            return

        paragraphs = response.css('div.article-body p::text').getall()
        clean = [p.strip() for p in paragraphs if p.strip()]
        item['content'] = ' '.join(clean)
        item['tags'] = response.css('.tag-list a::text').getall()

        img = response.css('figure img::attr(src)').get()
        if img:
            item['image_url'] = response.urljoin(img)

        yield item
