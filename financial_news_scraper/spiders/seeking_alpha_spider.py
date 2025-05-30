# financial_news_scraper/spiders/seeking_alpha_spider.py

import scrapy
from datetime import datetime, timedelta
from financial_news_scraper.items import NewsArticleItem

class SeekingAlphaSpider(scrapy.Spider):
    name = 'seeking_alpha'
    allowed_domains = ['seekingalpha.com']
    start_urls = [
        'https://seekingalpha.com/market-news',
        'https://seekingalpha.com/news/trending',
    ]

    def parse(self, response):
        for href in response.css('a[data-test-id="post-list-item-title"]::attr(href)').getall():
            yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'Seeking Alpha'
        item['url'] = response.url
        item['title'] = response.css('h1[data-test-id="post-title"]::text').get(default='').strip()
        item['author'] = response.css('[data-test-id="post-author-name"]::text').get(default='').strip()

        pub_iso = response.css('time::attr(datetime)').get()
        if not pub_iso:
            return
        item['published_date'] = pub_iso
        pub = datetime.fromisoformat(pub_iso)
        if pub < datetime.utcnow() - timedelta(hours=24):
            return

        paragraphs = response.css('[data-test-id="content-container"] p::text').getall()
        clean_pars = [p.strip() for p in paragraphs if p.strip()]
        item['summary'] = clean_pars[0] if clean_pars else ''
        item['content'] = ' '.join(clean_pars)

        item['tags'] = response.css('[data-test-id="post-tags"] a::text').getall()
        img = response.css('.sa-image img::attr(src)').get()
        if img:
            item['image_url'] = response.urljoin(img)

        yield item
