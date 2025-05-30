# financial_news_scraper/spiders/wall_street_journal_spider.py

import scrapy
from datetime import datetime, timedelta
from financial_news_scraper.items import NewsArticleItem

class WallStreetJournalSpider(scrapy.Spider):
    name = 'wall_street_journal'
    allowed_domains = ['wsj.com']
    start_urls = ['https://www.wsj.com/news/markets']

    def parse(self, response):
        for href in response.css('div.wsj-card__headline a::attr(href)').getall():
            yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'Wall Street Journal'
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

        paragraphs = response.css('article p::text').getall()
        clean_pars = [p.strip() for p in paragraphs if p.strip()]
        item['summary'] = clean_pars[0] if clean_pars else ''
        item['content'] = ' '.join(clean_pars)

        item['tags'] = response.css('.wsj-article-topic a::text').getall()
        img = response.css('figure img::attr(src)').get()
        if img:
            item['image_url'] = response.urljoin(img)

        yield item
