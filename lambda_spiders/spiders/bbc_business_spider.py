import scrapy
import urllib.parse
from financial_news_scraper.items import NewsArticleItem

SCRAPERAPI_KEY = "049f0bf1e28d549e626e40d6d8c4df6f"

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

class BBCBusinessSpider(scrapy.Spider):
    name = 'bbc_business'
    allowed_domains = ['bbc.com']
    start_urls = [
        'https://www.bbc.com/news/business',
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
        for href in response.css('a.gs-c-promo-heading::attr(href)').getall():
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
        item['source'] = 'BBC Business'
        item['url'] = response.url
        item['title'] = response.css('h1::text').get(default='').strip()
        item['author'] = response.css('.ssrcss-1rv4g5u-Contributor::text').get(default='').strip()
        item['published_date'] = response.css('time::attr(datetime)').get()
        paragraphs = response.css('article p::text').getall()
        item['content'] = ' '.join(p.strip() for p in paragraphs)
        item['tags'] = []
        img = response.css('figure img::attr(src)').get()
        if img:
            item['image_url'] = response.urljoin(img)
        yield item

    def errback_debug(self, failure):
        self.logger.error(repr(failure))