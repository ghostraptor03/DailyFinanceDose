# financial_news_scraper/spiders/cnbc_spider.py

import scrapy
from datetime import datetime, timedelta
from financial_news_scraper.items import NewsArticleItem

class CNBCSpider(scrapy.Spider):
    name = 'cnbc'
    allowed_domains = ['cnbc.com']
    start_urls = [
        'https://www.cnbc.com/finance/',
        'https://www.cnbc.com/markets/',
        'https://www.cnbc.com/business/',
    ]

    def parse(self, response):
        links = (
            response.css('a.LatestNews-headline::attr(href)').getall()
            + response.css('a.Card-title::attr(href)').getall()
        )
        for href in links:
            yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'CNBC'
        item['url'] = response.url
        item['title'] = response.css('h1.ArticleHeader-headline::text').get(default='').strip()
        item['author'] = response.css('.AuthorInfo-name::text').get(default='').strip()

        pub_iso = response.css('time::attr(datetime)').get()
        if not pub_iso:
            return
        item['published_date'] = pub_iso
        pub = datetime.fromisoformat(pub_iso)
        if pub < datetime.utcnow() - timedelta(hours=24):
            return

        item['content'] = ' '.join(response.css('.ArticleBody-articleBody p::text').getall())
        # CNBC provides no explicit tags; you can leave empty or parse elsewhere
        item['tags'] = []
        img = response.css('.ArticleHeader-eyebrow img::attr(src)').get()
        if img:
            item['image_url'] = response.urljoin(img)

        yield item
