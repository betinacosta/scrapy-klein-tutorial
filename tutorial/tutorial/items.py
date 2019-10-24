import scrapy


class Quote(scrapy.Item):
    text = scrapy.Field()
    author = scrapy.Field()