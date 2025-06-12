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

class CNBCSpider(scrapy.Spider):
    name = 'cnbc'
    allowed_domains = ['cnbc.com']
    start_urls = [
        'https://www.cnbc.com/business/'
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
        self.logger.info(f"Parsing section page: {response.url} (status {response.status})")
        found_any = False
        for a in response.css('a[href*="/202"]'):
            link = a.attrib['href']
            if not link.startswith("http"):
                link = response.urljoin(link)
            found_any = True
            yield scrapy.Request(
                wrap_scraperapi(link),
                callback=self.parse_article,
                errback=self.errback_debug,
                dont_filter=True,
            )
        if not found_any:
            self.logger.warning("No articles found! Dumping HTML for debugging.")
            with open("debug_cnbc_section.html", "w", encoding="utf-8") as f:
                f.write(response.text)

    def parse_article(self, response):
        self.logger.info(f"Parsing article: {response.url} (status {response.status})")
        item = NewsArticleItem()
        item['source'] = 'CNBC'
        item['url'] = response.url
        item['title'] = response.css('h1::text').get(default='').strip()
        item['author'] = response.css('span.Author-authorName::text').get(default='').strip()
        item['published_date'] = response.css('time::attr(datetime)').get()
        paragraphs = response.css('div.ArticleBody-articleBody p::text').getall()
        if not paragraphs:
            paragraphs = response.css('article p::text').getall()
        item['content'] = ' '.join(p.strip() for p in paragraphs)
        item['tags'] = response.css('meta[name="keywords"]::attr(content)').get(default='').split(',')
        img = response.css('meta[property="og:image"]::attr(content)').get()
        if img:
            item['image_url'] = img
        yield item

    def errback_debug(self, failure):
        self.logger.error(repr(failure))
        response = getattr(failure.value, 'response', None)
        if response:
            self.logger.error(f"Error on {response.url} (status {response.status})")
            with open("debug_failed_cnbc.html", "w", encoding="utf-8") as f:
                f.write(response.text)