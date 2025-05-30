# financial_news_scraper/spiders/gurufocus_spider.py

import scrapy
from datetime import datetime, timedelta
from financial_news_scraper.items import NewsArticleItem

class GuruFocusSpider(scrapy.Spider):
    name = 'gurufocus'
    allowed_domains = ['gurufocus.com']
    start_urls = ['https://www.gurufocus.com/news']

    def parse(self, response):
        for href in response.css('.headline a::attr(href)').getall():
            yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'GuruFocus'
        item['url'] = response.url
        item['title'] = response.css('h1::text').get(default='').strip()
        item['author'] = response.css('.byAuthor a::text').get(default='').strip()

        pub_iso = response.css('time::attr(datetime)').get()
        if not pub_iso:
            return
        item['published_date'] = pub_iso
        pub = datetime.fromisoformat(pub_iso)
        if pub < datetime.utcnow() - timedelta(hours=24):
            return

        paras = response.css('.postContent p::text').getall()
        clean = [p.strip() for p in paras if p.strip()]
        item['content'] = ' '.join(clean)
        item['tags'] = response.css('.tags a::text').getall()

        img = response.css('.postContent img::attr(src)').get()
        if img:
            item['image_url'] = response.urljoin(img)

        yield item
