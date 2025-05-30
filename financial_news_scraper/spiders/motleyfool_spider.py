# financial_news_scraper/spiders/motleyfool_spider.py

import scrapy
from datetime import datetime, timedelta
from financial_news_scraper.items import NewsArticleItem

class MotleyFoolSpider(scrapy.Spider):
    name = 'motleyfool'
    allowed_domains = ['fool.com']
    start_urls = [
        'https://www.fool.com/investing/',
        'https://www.fool.com/earnings/',
        'https://www.fool.com/market-news/',
    ]

    def parse(self, response):
        for href in response.css('a.card__title::attr(href)').getall():
            yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'The Motley Fool'
        item['url'] = response.url
        item['title'] = response.css('h1::text').get(default='').strip()
        item['author'] = response.css('.publisher__name::text').get(default='').strip()

        pub_iso = response.css('time::attr(datetime)').get()
        if not pub_iso:
            return
        item['published_date'] = pub_iso
        pub = datetime.fromisoformat(pub_iso)
        if pub < datetime.utcnow() - timedelta(hours=24):
            return

        paras = response.css('div.entry-content p::text').getall()
        clean = [p.strip() for p in paras if p.strip()]
        item['content'] = ' '.join(clean)
        item['tags'] = response.css('.topic__link::text').getall()

        img = response.css('.hero__image img::attr(src)').get()
        if img:
            item['image_url'] = response.urljoin(img)

        yield item
