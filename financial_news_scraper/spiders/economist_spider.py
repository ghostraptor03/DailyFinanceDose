# financial_news_scraper/spiders/economist_spider.py

import scrapy
from datetime import datetime, timedelta
from financial_news_scraper.items import NewsArticleItem

class EconomistFinanceSpider(scrapy.Spider):
    name = 'economist'
    allowed_domains = ['economist.com']
    start_urls = ['https://www.economist.com/finance-and-economics/']

    def parse(self, response):
        for href in response.css('a.teaser__link::attr(href)').getall():
            yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'The Economist'
        item['url'] = response.url
        item['title'] = response.css('h1::text').get(default='').strip()
        item['author'] = response.css('.byline__name::text').get(default='').strip()

        pub_iso = response.css('time::attr(datetime)').get()
        if not pub_iso:
            return
        item['published_date'] = pub_iso
        pub = datetime.fromisoformat(pub_iso)
        if pub < datetime.utcnow() - timedelta(hours=24):
            return

        paragraphs = response.css('article p::text').getall()
        clean = [p.strip() for p in paragraphs if p.strip()]
        item['content'] = ' '.join(clean)
        item['tags'] = response.css('.tags__list a::text').getall()

        img = response.css('figure img::attr(src)').get()
        if img:
            item['image_url'] = response.urljoin(img)

        yield item
