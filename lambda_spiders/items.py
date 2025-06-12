import scrapy

class NewsArticleItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    source = scrapy.Field()
    author = scrapy.Field()
    published_date = scrapy.Field()
    scraped_date = scrapy.Field()
    summary = scrapy.Field()
    content = scrapy.Field()
    category = scrapy.Field()
    tags = scrapy.Field()
    image_url = scrapy.Field()
    ticker_symbols = scrapy.Field()
    sentiment_score = scrapy.Field()
    article_id = scrapy.Field()
