# financial_news_scraper/spiders/nasdaq_spider.py

import scrapy
from datetime import datetime, timedelta
from financial_news_scraper.items import NewsArticleItem

class NasdaqSpider(scrapy.Spider):
    name = 'nasdaq'
    allowed_domains = ['nasdaq.com']
    start_urls = ['https://www.nasdaq.com/news']

    def parse(self, response):
        for href in response.css('.quote-news-headlines__item a::attr(href)').getall():
            yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'Nasdaq'
        item['url'] = response.url
        item['title'] = response.css('h1::text').get(default='').strip()
        item['author'] = response.css('.article-header__author a::text').get(default='').strip()

        pub_iso = response.css('meta[name="article:published_time"]::attr(content)').get()
        if not pub_iso:
            return
        item['published_date'] = pub_iso
        pub = datetime.fromisoformat(pub_iso)
        if pub < datetime.utcnow() - timedelta(hours=24):
            return

        paras = response.css('.article-body__content p::text').getall()
        item['content'] = ' '.join(p.strip() for p in paras if p.strip())

        kw = response.css('meta[name="keywords"]::attr(content)').get(default='')
        item['tags'] = [k.strip() for k in kw.split(',') if k.strip()]

        img = response.css('meta[property="og:image"]::attr(content)').get()
        if img:
            item['image_url'] = img

        yield item
