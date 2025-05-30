# financial_news_scraper/spiders/barrons_spider.py

import scrapy
from datetime import datetime, timedelta
from financial_news_scraper.items import NewsArticleItem

class BarronsSpider(scrapy.Spider):
    name = 'barrons'
    allowed_domains = ['barrons.com']
    start_urls = ['https://www.barrons.com/']

    def parse(self, response):
        for href in response.css('h3.headline a::attr(href)').getall():
            yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'Barrons'
        item['url'] = response.url
        item['title'] = response.css('h1.headline::text').get(default='').strip()
        item['author'] = response.css('span.author::text').get(default='').strip()

        pub_iso = response.css('time::attr(datetime)').get()
        if not pub_iso:
            return
        item['published_date'] = pub_iso
        pub = datetime.fromisoformat(pub_iso)
        if pub < datetime.utcnow() - timedelta(hours=24):
            return

        paragraphs = response.css('div.article-body p::text').getall()
        clean = [p.strip() for p in paragraphs if p.strip()]
        item['content'] = ' '.join(clean)
        item['tags'] = response.css('a.tag::text').getall()

        img = response.css('figure img::attr(src)').get()
        if img:
            item['image_url'] = response.urljoin(img)

        yield item
