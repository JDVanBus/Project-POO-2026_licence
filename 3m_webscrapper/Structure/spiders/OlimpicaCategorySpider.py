import scrapy

from ..items import CategoryItem


class CategorySpider(scrapy.Spider):
    name = "OlimpicaCategorySpider"
    allowed_domains = ["olimpica.com"]
    start_urls = ["https://olimpica.com/api/catalog_system/pub/category/tree/1"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_categories = set()

    def parse(self, response):
        categories = response.json()
        yield from self.parse_categories(categories, current_breadcrumbs=[])

    def parse_categories(
        self, categories, parent=None, level=0, current_breadcrumbs=None
    ):
        for category in categories:
            parent_id = parent.get("id") if parent else None
            url = (category.get("url") or "").strip().lower()
            name = (category.get("name") or "").strip().lower()
            dedup_key = (parent_id, url if url else name)

            if dedup_key in self.seen_categories:
                children = category.get("children") or []
                if children:
                    path_duplicado = (current_breadcrumbs or []) + [
                        category.get("name")
                    ]
                    yield from self.parse_categories(
                        children,
                        parent=category,
                        level=level + 1,
                        current_breadcrumbs=path_duplicado,
                    )
                continue

            self.seen_categories.add(dedup_key)
            actual_path = (current_breadcrumbs or []) + [category.get("name")]

            item = CategoryItem()
            item["source"] = "olimpica.com"
            item["item_type"] = "category"
            item["id"] = category.get("id")
            item["name"] = category.get("name")
            item["url"] = category.get("url")
            # item["raw_data"] = category datos crudos, sin modificaciòn
            item["parent_id"] = parent.get("id") if parent else None
            item["parent_name"] = parent.get("name") if parent else None
            item["has_children"] = bool(category.get("children"))
            item["level"] = level
            item["breadcrumbs"] = actual_path

            yield item

            if item.get("has_children"):
                children = category.get("children") or []
                yield from self.parse_categories(
                    children,
                    parent=category,
                    level=level + 1,
                    current_breadcrumbs=actual_path,
                )
