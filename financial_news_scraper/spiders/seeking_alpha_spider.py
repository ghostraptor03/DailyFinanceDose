import scrapy
import urllib.parse
from financial_news_scraper.items import NewsArticleItem

SCRAPERAPI_KEY = "049f0bf1e28d549e626e40d6d8c4df6f"

def wrap_scraperapi(url):
    return (
        f"http://api.scraperapi.com/?api_key={SCRAPERAPI_KEY}"
        f"&url={urllib.parse.quote(url)}&render=true"
    )

class SeekingAlphaSpider(scrapy.Spider):
    name = 'seeking_alpha'
    allowed_domains = ['seekingalpha.com']
    start_urls = [
        'https://seekingalpha.com/market-news',
        'https://seekingalpha.com/news/trending',
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
        for href in response.css('a[data-test-id="post-list-item-title"]::attr(href)').getall():
            yield scrapy.Request(
                wrap_scraperapi(response.urljoin(href)),
                callback=self.parse_article,
                errback=self.errback_debug,
                dont_filter=True,
            )

    def parse_article(self, response):
        item = NewsArticleItem()
        item['source'] = 'Seeking Alpha'
        item['url'] = response.url
        item['title'] = response.css('h1[data-test-id="post-title"]::text').get(default='').strip()
        item['author'] = response.css('[data-test-id="post-author-name"]::text').get(default='').strip()
        item['published_date'] = response.css('time::attr(datetime)').get()
        paragraphs = response.css('[data-test-id="content-container"] p::text').getall()
        clean_pars = [p.strip() for p in paragraphs if p.strip()]
        item['summary'] = clean_pars[0] if clean_pars else ''
        item['content'] = ' '.join(clean_pars)
        item['tags'] = response.css('[data-test-id="post-tags"] a::text').getall()
        img = response.css('.sa-image img::attr(src)').get()
        if img:
            item['image_url'] = response.urljoin(img)
        yield item

    def errback_debug(self, failure):
        self.logger.error(repr(failure))