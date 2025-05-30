# financial_news_scraper/spiders/bbc_business_spider.py

import scrapy
from datetime import datetime, timedelta
from financial_news_scraper.items import NewsArticleItem

class BBCBusinessSpider(scrapy.Spider):
    name = 'bbc_business'
    allowed_domains = ['bbc.com']
    start_urls = ['https://www.bbc.com/news/business']

    def parse(self, response):
        for href in response.css('a.gs-c-promo-heading::attr(href)').getall():
            if href.startswith('/news/business'):
                yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'BBC Business'
        item['url'] = response.url
        item['title'] = response.css('h1::text').get(default='').strip()
        # BBC often omits author
        item['author'] = response.css('.byline__name::text').get(default='').strip()

        pub_iso = response.css('meta[property="article:published_time"]::attr(content)').get()
        if not pub_iso:
            return
        item['published_date'] = pub_iso
        pub = datetime.fromisoformat(pub_iso)
        if pub < datetime.utcnow() - timedelta(hours=24):
            return

        paras = response.css('article .ssrcss-uf6wea-RichTextComponentWrapper p::text').getall()
        item['content'] = ' '.join(p.strip() for p in paras if p.strip())

        # BBC tags via section meta
        section = response.css('meta[property="article:section"]::attr(content)').get()
        item['tags'] = [section] if section else []

        img = response.css('meta[property="og:image"]::attr(content)').get()
        if img:
            item['image_url'] = img

        yield item
