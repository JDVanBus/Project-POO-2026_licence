import scrapy
import json

from OlimpicaWebscrapper.items import OlimpicaItem


class OlimpicaSpider(scrapy.Spider):
    name = "OlimpicaSpider"
    allowed_domains = ["olimpica.com"]
    start_urls = ["https://olimpica.com/api/catalog_system/pub/category/tree/1"]

    def parse(self, response):
        self.seen_categories = set()
        categories = json.loads(response.text)
        yield from self.parse_categories(categories)

    def parse_categories(self, categories, parent=None, level=0):
        for category in categories:
            parent_id = parent.get("id") if parent else None
            url = (category.get("url") or "").strip().lower()
            name = (category.get("name") or "").strip().lower()
            dedup_key = (parent_id, url if url else name)

            if dedup_key in self.seen_categories:
                children = category.get("children") or []
                if children:
                    yield from self.parse_categories(children, parent=category, level=level + 1)
                continue

            self.seen_categories.add(dedup_key)  

            item = OlimpicaItem()
            item["source"] = "olimpica.com"
            item["item_type"] = "category"
            item["id"] = category.get("id")
            item["name"] = category.get("name")
            item["url"] = category.get("url")
            item["parent_id"] = parent.get("id") if parent else None
            item["parent_name"] = parent.get("name") if parent else None
            item["has_children"] = bool(category.get("children"))
            item["level"] = level
            item["breadcrumbs"] = self.build_breadcrumbs(category, parent)
            item["raw_data"] = category
            yield item

            children = category.get("children") or []
            if children:
                yield from self.parse_categories(children, parent=category, level = level + 1)
  

    def build_breadcrumbs(self, category, parent=None):
        breadcrumbs = []
        if parent:
            parent_breadcrumbs = parent.get("breadcrumbs") or []
            breadcrumbs.extend(parent_breadcrumbs)
            breadcrumbs.append(parent.get("name"))
        breadcrumbs.append(category.get("name"))
        return breadcrumbs
