import scrapy
import urllib.parse
from financial_news_scraper.items import NewsArticleItem

SCRAPERAPI_KEY = "049f0bf1e28d549e626e40d6d8c4df6f"

def wrap_scraperapi(url):
    return (
        f"http://api.scraperapi.com/?api_key={SCRAPERAPI_KEY}"
        f"&url={urllib.parse.quote(url)}&render=true"
    )

class ForbesSpider(scrapy.Spider):
    name = 'forbes'
    allowed_domains = ['forbes.com']
    start_urls = [
        'https://www.forbes.com/markets/',
        'https://www.forbes.com/money/',
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
        for href in response.css('a[data-ga-track*="article"]::attr(href)').getall():
            yield scrapy.Request(
                wrap_scraperapi(response.urljoin(href)),
                callback=self.parse_article,
                errback=self.errback_debug,
                dont_filter=True,
            )

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'Forbes'
        item['url'] = response.url
        item['title'] = response.css('h1::text').get(default='').strip()
        item['author'] = response.css('a.author::text').get(default='').strip()
        item['published_date'] = response.css('time::attr(datetime)').get()
        paragraphs = response.css('div.article-body p::text').getall()
        item['content'] = ' '.join(p.strip() for p in paragraphs)
        item['tags'] = response.css('a[data-ga-track*="tag"]::text').getall()
        img = response.css('img.article-image::attr(src)').get()
        if img:
            item['image_url'] = response.urljoin(img)
        yield item

    def errback_debug(self, failure):
        self.logger.error(repr(failure))