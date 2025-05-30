# financial_news_scraper/spiders/business_insider_spider.py

import scrapy
from datetime import datetime, timedelta
from financial_news_scraper.items import NewsArticleItem

class BusinessInsiderSpider(scrapy.Spider):
    name = 'business_insider'
    allowed_domains = ['businessinsider.com']
    start_urls = ['https://www.businessinsider.com/finance']

    def parse(self, response):
        for href in response.css('a.js-article-link::attr(href)').getall():
            yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'Business Insider'
        item['url'] = response.url
        item['title'] = response.css('h1::text').get(default='').strip()
        item['author'] = response.css('.byline__author-link::text').get(default='').strip()

        pub_iso = response.css('time::attr(datetime)').get()
        if not pub_iso:
            return
        item['published_date'] = pub_iso
        pub = datetime.fromisoformat(pub_iso)
        if pub < datetime.utcnow() - timedelta(hours=24):
            return

        paragraphs = response.css('article p::text').getall()
        clean_pars = [p.strip() for p in paragraphs if p.strip()]
        item['summary'] = clean_pars[0] if clean_pars else ''
        item['content'] = ' '.join(clean_pars)

        item['tags'] = response.css('.tags-list a::text').getall()
        img = response.css('figure img::attr(src)').get()
        if img:
            item['image_url'] = response.urljoin(img)

        yield item
