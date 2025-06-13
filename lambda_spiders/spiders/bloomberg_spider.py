import scrapy
import urllib.parse
from items import NewsArticleItem

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

class BloombergSpider(scrapy.Spider):
    name = 'bloomberg'
    allowed_domains = ['bloomberg.com']
    start_urls = [
        
        'https://www.bloomberg.com/economics'
        
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
        links = response.css('a[data-module="Story"]::attr(href)').getall()
        for href in links:
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
        item['source'] = 'Bloomberg'
        item['url'] = response.url
        item['title'] = response.css('h1[data-module="ArticleHeader"]::text').get(default='').strip()
        item['author'] = response.css('.author-link::text').get(default='').strip()
        item['published_date'] = response.css('time::attr(datetime)').get()
        item['content'] = ' '.join(response.css('.body-copy p::text').getall())
        item['tags'] = response.css('.article__topics a::text').getall()
        img = response.css('.main-image img::attr(src)').get()
        if img:
            item['image_url'] = response.urljoin(img)
        yield item

    def errback_debug(self, failure):
        self.logger.error(repr(failure))