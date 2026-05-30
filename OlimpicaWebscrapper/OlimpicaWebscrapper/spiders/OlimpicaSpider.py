import scrapy
import json

class OlimpicaSpider(scrapy.Spider):
    name = "OlimpicaSpider"
    allowed_domains = ["olimpica.com"]
    start_urls = ["https://olimpica.com/api/catalog_system/pub/category/tree/1"]

    def parse(self, response):
        categories = json.loads(response.text)
        for cat in categories:
            yield {
                'name': cat['name'],
                'url': cat['url']
            }