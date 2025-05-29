import scrapy
from financial_news_scraper.items import NewsArticleItem

class BaseFinancialSpider(scrapy.Spider):
    def build_item(self, response, source_name):
        item = NewsArticleItem()
        item['title'] = response.css('h1::text').get(default='').strip()
        item['url'] = response.url
        item['source'] = source_name
        item['author'] = response.css('.author::text').get(default='').strip()
        item['published_date'] = response.css('time::attr(datetime)').get()
        paras = response.css('p::text').getall()
        item['summary'] = paras[0] if paras else ''
        item['content'] = ' '.join(paras)
        return item