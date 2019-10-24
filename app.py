from scrapy.utils.serialize import ScrapyJSONEncoder
import json

import app
from spider_runner import SpiderRunner
from bookstore.bookstore.spiders.books_spider import BooksSpider

from klein import Klein
app = Klein()

@app.route("/")
def index(request):
    return "Bom dia flor do dia"


@app.route('/search')
def get_quotes(request):
    content = json.loads(request.content.read())
    tag = content.get("tag")
   
    runner = SpiderRunner()

    deferred = runner.crawl(BooksSpider, tag=tag)
    deferred.addCallback(return_spider_output)

    return deferred

def return_spider_output(output):
    _encoder = ScrapyJSONEncoder()
    return _encoder.encode(output)

app.run("localhost", 8080)