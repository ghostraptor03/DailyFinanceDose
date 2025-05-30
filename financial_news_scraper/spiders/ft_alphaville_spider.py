# financial_news_scraper/spiders/ft_alphaville_spider.py

import scrapy
from datetime import datetime, timedelta
from financial_news_scraper.items import NewsArticleItem

class FTAlphavilleSpider(scrapy.Spider):
    name = 'ft_alphaville'
    allowed_domains = ['ft.com']
    start_urls = ['https://ftalphaville.ft.com/']

    def parse(self, response):
        for href in response.css('.o-teaser-collection__heading a::attr(href)').getall():
            yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'FT Alphaville'
        item['url'] = response.url
        item['title'] = response.css('h1::text').get(default='').strip()
        item['author'] = response.css('.article__byline__author-link::text').get(default='').strip()

        pub_iso = response.css('time::attr(datetime)').get()
        if not pub_iso:
            return
        item['published_date'] = pub_iso
        pub = datetime.fromisoformat(pub_iso)
        if pub < datetime.utcnow() - timedelta(hours=24):
            return

        paras = response.css('article p::text').getall()
        clean = [p.strip() for p in paras if p.strip()]
        item['content'] = ' '.join(clean)
        item['tags'] = response.css('.o-tags__item a::text').getall()

        img = response.css('figure img::attr(src)').get()
        if img:
            item['image_url'] = response.urljoin(img)

        yield item
