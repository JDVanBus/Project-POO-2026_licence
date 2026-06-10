import json


class OlimpicaProductPipeline:
    def open_spider(self, spider):
        self._items = []

    def process_item(self, item, spider):
        cleaned_item = {}

        for key, value in dict(item).items():
            if value is None:
                continue

            if isinstance(value, str):
                value = value.strip()
                if not value:
                    continue

            cleaned_item[key] = value

        # Accumulate cleaned items in-memory
        self._items.append(cleaned_item)

        return cleaned_item

    def close_spider(self, spider):
        # Convert to tuple (inmutable) and attach to spider for access
        items_tuple = tuple(self._items)
        try:
            spider.categorias_tuple = items_tuple
        except Exception:
            pass

        # Persist tuple to disk: pickle (preserves tuple) and JSON (readable)

        with open("categorias_tuple.json", "w", encoding="utf8") as f:
            json.dump(list(items_tuple), f, ensure_ascii=False, indent=2)

        # also keep reference in the pipeline instance
        self.items_tuple = items_tuple
