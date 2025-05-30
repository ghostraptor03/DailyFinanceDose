# financial_news_scraper/spiders/financialpost_spider.py

import scrapy
from datetime import datetime, timedelta
from financial_news_scraper.items import NewsArticleItem

class FinancialPostSpider(scrapy.Spider):
    name = 'financialpost'
    allowed_domains = ['financialpost.com']
    start_urls = ['https://financialpost.com/category/markets']

    def parse(self, response):
        for href in response.css('h2.entry-title a::attr(href)').getall():
            yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'Financial Post'
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
        clean = [p.strip() for p in paras if p.strip()]
        item['content'] = ' '.join(clean)
        item['tags'] = response.css('.tag-list a::text').getall()

        img = response.css('.featured-image img::attr(src)').get()
        if img:
            item['image_url'] = response.urljoin(img)

        yield item
