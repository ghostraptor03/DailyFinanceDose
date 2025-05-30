# financial_news_scraper/spiders/kiplinger_spider.py

import scrapy
from datetime import datetime, timedelta
from financial_news_scraper.items import NewsArticleItem

class KiplingerSpider(scrapy.Spider):
    name = 'kiplinger'
    allowed_domains = ['kiplinger.com']
    start_urls = ['https://www.kiplinger.com/news/stock-market-news']

    def parse(self, response):
        for href in response.css('article h3 a::attr(href)').getall():
            yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'Kiplinger'
        item['url'] = response.url
        item['title'] = response.css('h1::text').get(default='').strip()
        item['author'] = response.css('.byline a::text').get(default='').strip()

        pub_iso = response.css('time::attr(datetime)').get()
        if not pub_iso:
            return
        item['published_date'] = pub_iso
        pub = datetime.fromisoformat(pub_iso)
        if pub < datetime.utcnow() - timedelta(hours=24):
            return

        paras = response.css('.article-content p::text').getall()
        item['content'] = ' '.join(p.strip() for p in paras if p.strip())

        item['tags'] = response.css('.tags-list a::text').getall()

        img = response.css('meta[property="og:image"]::attr(content)').get()
        if img:
            item['image_url'] = img

        yield item
