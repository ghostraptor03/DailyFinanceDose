# financial_news_scraper/spiders/thestreet_spider.py

import scrapy
from datetime import datetime, timedelta
from financial_news_scraper.items import NewsArticleItem

class TheStreetSpider(scrapy.Spider):
    name = 'thestreet'
    allowed_domains = ['thestreet.com']
    start_urls = ['https://www.thestreet.com/markets']

    def parse(self, response):
        for href in response.css('a.article__title::attr(href)').getall():
            yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'TheStreet'
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

        paragraphs = response.css('.article-content p::text').getall()
        clean = [p.strip() for p in paragraphs if p.strip()]
        item['content'] = ' '.join(clean)
        item['tags'] = response.css('.tags-list a::text').getall()

        img = response.css('article img::attr(src)').get()
        if img:
            item['image_url'] = response.urljoin(img)

        yield item
