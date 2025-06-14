import scrapy
import urllib.parse
from items import NewsArticleItem

SCRAPERAPI_KEY = ""

def wrap_scraperapi(url):
    params = {
        "api_key": SCRAPERAPI_KEY,
        "url": url,
        "follow_redirect": "false",
        "render": "true",
        "retry_404": "true"
    }
    base = "http://api.scraperapi.com/"
    return base + "?" + urllib.parse.urlencode(params)

class YahooFinanceSpider(scrapy.Spider):
    name = 'yahoo_finance'
    allowed_domains = ['finance.yahoo.com']
    start_urls = [
        'https://finance.yahoo.com/news/',
    ]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                wrap_scraperapi(url),
                callback=self.parse,
                errback=self.errback_debug,
                dont_filter=True,
            )

    def parse(self, response):
        for href in response.css('h3 a::attr(href)').getall():
            if not href.startswith("http"):
                href = response.urljoin(href)
            yield scrapy.Request(
                wrap_scraperapi(href),
                callback=self.parse_article,
                errback=self.errback_debug,
                dont_filter=True,
            )

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'Yahoo Finance'
        item['url'] = response.url
        item['title'] = response.css('h1[data-test-locator="headline"]::text').get(default='').strip()
        item['author'] = response.css('.caas-author-byline-collapse::text').get(default='').strip()
        item['published_date'] = response.css('time::attr(datetime)').get()
        paragraphs = response.css('.caas-body p::text').getall()
        item['content'] = ' '.join(p.strip() for p in paragraphs)
        item['tags'] = []
        img = response.css('.caas-img img::attr(src)').get()
        if img:
            item['image_url'] = response.urljoin(img)
        yield item

    def errback_debug(self, failure):
        self.logger.error(repr(failure))