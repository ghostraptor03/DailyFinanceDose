import scrapy
import urllib.parse
from financial_news_scraper.items import NewsArticleItem

SCRAPERAPI_KEY = "049f0bf1e28d549e626e40d6d8c4df6f"

def wrap_scraperapi(url):
    return (
        f"http://api.scraperapi.com/?api_key={SCRAPERAPI_KEY}"
        f"&url={urllib.parse.quote(url)}&render=true"
    )

class EconomistFinanceSpider(scrapy.Spider):
    name = 'economist'
    allowed_domains = ['economist.com']
    start_urls = ['https://www.economist.com/finance-and-economics/']

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                wrap_scraperapi(url),
                callback=self.parse,
                errback=self.errback_debug,
                dont_filter=True,
            )

    def parse(self, response):
        for href in response.css('a.teaser__link::attr(href)').getall():
            yield scrapy.Request(
                wrap_scraperapi(response.urljoin(href)),
                callback=self.parse_article,
                errback=self.errback_debug,
                dont_filter=True,
            )

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'The Economist'
        item['url'] = response.url
        item['title'] = response.css('h1::text').get(default='').strip()
        item['author'] = response.css('.byline__name::text').get(default='').strip()
        item['published_date'] = response.css('time::attr(datetime)').get()
        paragraphs = response.css('article p::text').getall()
        clean = [p.strip() for p in paragraphs if p.strip()]
        item['content'] = ' '.join(clean)
        item['tags'] = response.css('.tags__list a::text').getall()
        img = response.css('figure img::attr(src)').get()
        if img:
            item['image_url'] = response.urljoin(img)
        yield item

    def errback_debug(self, failure):
        self.logger.error(repr(failure))