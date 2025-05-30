# financial_news_scraper/spiders/investingcom_spider.py

import scrapy
from datetime import datetime, timedelta
from financial_news_scraper.items import NewsArticleItem

class InvestingComSpider(scrapy.Spider):
    name = 'investingcom'
    allowed_domains = ['investing.com']
    start_urls = ['https://www.investing.com/news/']

    def parse(self, response):
        for href in response.css('.largeTitle a::attr(href)').getall():
            yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'Investing.com'
        item['url'] = response.url
        item['title'] = response.css('h1::text').get(default='').strip()
        item['author'] = response.css('.author-name::text').get(default='').strip()

        pub_iso = response.css('time::attr(datetime)').get()
        if not pub_iso:
            return
        item['published_date'] = pub_iso
        pub = datetime.fromisoformat(pub_iso)
        if pub < datetime.utcnow() - timedelta(hours=24):
            return

        # Full content
        paras = response.css('article p::text').getall()
        clean = [p.strip() for p in paras if p.strip()]
        item['content'] = ' '.join(clean)

        # Tags
        item['tags'] = response.css('.tags a::text').getall()

        # Lead image
        img = response.css('figure img::attr(src)').get()
        if img:
            item['image_url'] = response.urljoin(img)

        yield item
