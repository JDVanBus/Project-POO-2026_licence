import scrapy


class BaseItem(scrapy.Item):
    """
    Plantilla Base de objetos scrapeables de Olímpica.
    item_type: "category" | "product" | "promotion" | "trend"
    """

    source = scrapy.Field()
    item_type = scrapy.Field()  # tipo de objeto
    id = scrapy.Field()
    name = scrapy.Field()
    url = scrapy.Field()
    raw_data = scrapy.Field()


class CategoryItem(BaseItem):
    # Categoría

    parent_id = scrapy.Field()
    parent_name = scrapy.Field()
    has_children = scrapy.Field()
    level = scrapy.Field()
    breadcrumbs = scrapy.Field()

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.setdefault("item_type", "category")


class ProductItem(BaseItem):
    # Producto
    price = scrapy.Field()
    sale_price = scrapy.Field()  # precio con descuento (antes old_price)
    image_url = scrapy.Field()
    brand = scrapy.Field()
    category_id = scrapy.Field()
    category_name = scrapy.Field()
    available = scrapy.Field()
    sku = scrapy.Field()
    description = scrapy.Field()

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.setdefault("item_type", "product")
