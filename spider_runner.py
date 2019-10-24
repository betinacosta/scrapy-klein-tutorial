from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.utils.serialize import ScrapyJSONEncoder


class SpiderRunner(CrawlerRunner):
    def crawl(self, spider, *args, **kwargs):
        self.items = []

        crawler = self.create_crawler(spider)
        crawler.signals.connect(self._collect_item, signals.item_scraped)

        deferred = self._crawl(crawler, *args, **kwargs)
        deferred.addCallback(self._return_items)

        return deferred

    def _collect_item(self, item, response, spider):
        self.items.append(item)

    def _return_items(self, result):
        return self.items