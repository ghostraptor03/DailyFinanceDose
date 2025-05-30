# financial_news_scraper/spiders/cnn_business_spider.py

import scrapy
from datetime import datetime, timedelta
from financial_news_scraper.items import NewsArticleItem

class CNNBusinessSpider(scrapy.Spider):
    name = 'cnn_business'
    allowed_domains = ['cnn.com']
    start_urls = ['https://www.cnn.com/business']

    def parse(self, response):
        # article links live under h3.cd__headline
        for href in response.css('h3.cd__headline a::attr(href)').getall():
            yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'CNN Business'
        item['url'] = response.url
        item['title'] = response.css('h1.pg-headline::text').get(default='').strip()
        item['author'] = response.css('.metadata__byline__author::text').get(default='').strip()

        # published_date + 24h filter
        pub_iso = response.css('meta[itemprop="datePublished"]::attr(content)').get()
        if not pub_iso:
            return
        item['published_date'] = pub_iso
        pub = datetime.fromisoformat(pub_iso)
        if pub < datetime.utcnow() - timedelta(hours=24):
            return

        # full content
        paras = response.css('div.l-container article p::text').getall()
        item['content'] = ' '.join(p.strip() for p in paras if p.strip())

        # tags from keywords meta
        kw = response.css('meta[name="keywords"]::attr(content)').get(default='')
        item['tags'] = [k.strip() for k in kw.split(',') if k.strip()]

        # lead image
        img = response.css('meta[property="og:image"]::attr(content)').get()
        if img:
            item['image_url'] = img

        yield item
