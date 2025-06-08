import scrapy
import urllib.parse
from financial_news_scraper.items import NewsArticleItem

SCRAPERAPI_KEY = "049f0bf1e28d549e626e40d6d8c4df6f"

def wrap_scraperapi(url):
    return (
        f"http://api.scraperapi.com/?api_key={SCRAPERAPI_KEY}"
        f"&url={urllib.parse.quote(url)}&render=true"
    )

class MarketWatchSpider(scrapy.Spider):
    name = 'marketwatch'
    allowed_domains = ['marketwatch.com']
    start_urls = [
        'https://www.marketwatch.com/markets',
        'https://www.marketwatch.com/economy-politics',
        'https://www.marketwatch.com/personal-finance',
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
        for href in response.css('a.link::attr(href)').getall():
            if href.startswith('/story/'):
                yield scrapy.Request(
                    wrap_scraperapi(response.urljoin(href)),
                    callback=self.parse_article,
                    errback=self.errback_debug,
                    dont_filter=True,
                )

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'MarketWatch'
        item['url'] = response.url
        item['title'] = response.css('h1.article__headline::text').get(default='').strip()
        item['author'] = response.css('.author__name::text').get(default='').strip()
        item['published_date'] = response.css('time.timestamp::attr(datetime)').get()
        item['content'] = ' '.join(response.css('.articleBody p::text').getall())
        item['tags'] = []
        yield item

    def errback_debug(self, failure):
        self.logger.error(repr(failure))