import scrapy
import urllib.parse
from items import NewsArticleItem

SCRAPERAPI_KEY = ""

def wrap_scraperapi(url):
    return (
        f"http://api.scraperapi.com/?api_key={SCRAPERAPI_KEY}"
        f"&url={urllib.parse.quote(url)}&render=true"
    )

class InvestopediaSpider(scrapy.Spider):
    name = 'investopedia'
    allowed_domains = ['investopedia.com']
    start_urls = [
        'https://www.investopedia.com/news/',
        'https://www.investopedia.com/markets-news-4427704',
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
        for href in response.css('a.card__title__link::attr(href)').getall():
            yield scrapy.Request(
                wrap_scraperapi(response.urljoin(href)),
                callback=self.parse_article,
                errback=self.errback_debug,
                dont_filter=True,
            )

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'Investopedia'
        item['url'] = response.url
        item['title'] = response.css('h1::text').get(default='').strip()
        item['author'] = response.css('.author-name::text').get(default='').strip()
        item['published_date'] = response.css('time::attr(datetime)').get()
        paragraphs = response.css('div.article-body__content p::text').getall()
        item['content'] = ' '.join(p.strip() for p in paragraphs)
        item['tags'] = response.css('.tags__list a::text').getall()
        img = response.css('img.article-image::attr(src)').get()
        if img:
            item['image_url'] = response.urljoin(img)
        yield item

    def errback_debug(self, failure):
        self.logger.error(repr(failure))