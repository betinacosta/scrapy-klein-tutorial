import scrapy

from tutorial.tutorial.items import Quote


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def __init__(self, tag):
        self.tag = tag
        self.start_urls = ["http://quotes.toscrape.com/"]

    def start_requests(self):
        base_url = "http://quotes.toscrape.com/tag/"
        urls = [
            base_url + self.tag,
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        quotes_selectors = response.css("div.quote")

        for selector in quotes_selectors:
            quote = Quote()

            quote["text"] = selector.css("span.text::text").extract_first()
            quote["author"] = selector.css("small.author::text").extract_first()

            yield quote

        next_page_url = response.css("li.next>a::attr(href)").extract_first()

        if next_page_url:
            next_page_url = response.urljoin(next_page_url)
            yield scrapy.Request(url=next_page_url, callback=self.parse)

        
