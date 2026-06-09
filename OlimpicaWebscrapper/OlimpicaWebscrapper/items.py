# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class OlimpicaItem(scrapy.Item):
    source = scrapy.Field()
    item_type = scrapy.Field()
    id = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    parent_id = scrapy.Field()
    parent_name = scrapy.Field()
    has_children = scrapy.Field()
    level = scrapy.Field()
    category = scrapy.Field()
    brand = scrapy.Field()
    price = scrapy.Field()
    old_price = scrapy.Field()
    promotion = scrapy.Field()
    image_url = scrapy.Field()
    sku = scrapy.Field()
    description = scrapy.Field()
    breadcrumbs = scrapy.Field()
    raw_data = scrapy.Field()
