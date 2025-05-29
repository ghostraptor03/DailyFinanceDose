import scrapy
from .base_financial import BaseFinancialSpider

class ReutersSpider(BaseFinancialSpider):
    name = 'reuters'
    allowed_domains = ['reuters.com']
    start_urls = [
        'https://www.reuters.com/business/',
        'https://www.reuters.com/markets/',
    ]

    def parse(self, response):
        for href in response.css('a[data-testid="Heading"]::attr(href)').getall()[:20]:
            yield response.follow(href, self.parse_article)

    def parse_article(self, response):
        yield self.build_item(response, 'Reuters')