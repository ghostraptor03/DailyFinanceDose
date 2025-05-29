import scrapy
from .base_financial import BaseFinancialSpider

class BloombergSpider(BaseFinancialSpider):
    name = 'bloomberg'
    allowed_domains = ['bloomberg.com']
    start_urls = [
        'https://www.bloomberg.com/markets',
        'https://www.bloomberg.com/economics',
        'https://www.bloomberg.com/technology',
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={'playwright': True}
            )

    def parse(self, response):
        for link in response.css('a[data-module="Story"]::attr(href)').getall()[:15]:
            yield response.follow(
                link,
                self.parse_article,
                meta={'playwright': True}
            )

    def parse_article(self, response):
        yield self.build_item(response, 'Bloomberg')