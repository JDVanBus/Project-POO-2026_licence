import re
import unicodedata
import json
import urllib.parse

import scrapy

from ..items import ProductItem


class ProductSpider(scrapy.Spider):
    name = "ProductSpider"
    allowed_domains = ["olimpica.com"]

    def __init__(
        self,
        category_id=None,
        category_name=None,
        category_url=None,
        category_slug=None,
        max_sections=5,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.category_id = category_id
        self.category_name = category_name
        self.category_url = category_url
        self.category_slug = category_slug
        self.page_size = 50
        try:
            self.max_sections = max(1, int(max_sections))
        except (TypeError, ValueError):
            self.max_sections = 5
        self.headers = {
            "Accept": "application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        if self.category_id:
            self.start_urls = [self._build_category_api_url(0)]
        else:
            self.start_urls = []

    def start_requests(self):
        if not self.category_id:
            self.logger.error(
                "Error: Debes proporcionar un category_id usando -a category_id=XXXX"
            )
            return

        self.logger.info(
            "Iniciando crawl de productos para %s (%s)",
            self.category_name or self.category_id,
            self.category_id,
        )
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                headers=self.headers,
                callback=self.parse,
                cb_kwargs={"start_idx": 0, "section_number": 0},
                dont_filter=True,
            )

    def parse(self, response, start_idx=0, section_number=0):
        self.logger.info("Procesando %s", response.url)
        products = None

        try:
            data = response.json()
            if isinstance(data, list):
                products = data
            elif isinstance(data, dict):
                products = data.get("products") or data.get("items") or []
        except ValueError:
            products = None

        if not products:
            html = response.text
            product_links = self._extract_product_links(html)
            if not product_links:
                self.logger.warning("No se encontraron productos en %s", response.url)
                return

            for product_url in product_links:
                yield scrapy.Request(
                    url=product_url,
                    callback=self.parse_products,
                    meta={
                        "category_id": self.category_id,
                        "category_name": self.category_name,
                        "source_url": response.url,
                    },
                )
            return

        for product in products:
            link_text = product.get("linkText") or product.get("link")
            if not link_text:
                continue

            product_url = self._build_product_url(link_text)
            yield scrapy.Request(
                url=product_url,
                callback=self.parse_products,
                meta={
                    "category_id": self.category_id,
                    "category_name": self.category_name,
                    "source_url": response.url,
                    "product_summary": product,
                },
            )

        if isinstance(products, list) and len(products) >= self.page_size:
            if section_number + 1 < self.max_sections:
                next_start = start_idx + self.page_size
                next_url = self._build_category_api_url(next_start)
                self.logger.info(
                    "Continuando a la siguiente sección %s/%s para %s",
                    section_number + 2,
                    self.max_sections,
                    response.url,
                )
                yield scrapy.Request(
                    url=next_url,
                    headers=self.headers,
                    callback=self.parse,
                    cb_kwargs={
                        "start_idx": next_start,
                        "section_number": section_number + 1,
                    },
                    dont_filter=True,
                )
            else:
                self.logger.info(
                    "Se alcanzó el límite de %s secciones para %s",
                    self.max_sections,
                    response.url,
                )

    def parse_products(self, response):
        text = response.text
        match = re.search(r'"product:[^\"]+":\s*\{', text)

        if not match:
            product_summary = response.meta.get("product_summary")
            if product_summary:
                yield self._build_item_from_data(product_summary, response)
                return

            self.logger.warning(
                "No se encontró el bloque estructurado del producto en %s", response.url
            )
            return

        start_idx = match.start()
        brace_count = 0
        end_idx = None

        for i in range(start_idx, len(text)):
            if text[i] == "{":
                brace_count += 1
            elif text[i] == "}":
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i + 1
                    break

        if end_idx is None:
            self.logger.warning(
                "No se pudo cerrar el bloque JSON del producto en %s", response.url
            )
            return

        block = text[start_idx:end_idx]

        try:
            data = json.loads(block)
            product_data = next(iter(data.values()), None)
        except Exception as e:
            self.logger.error(
                f"Error procesando JSON estructurado en {response.url}: {e}"
            )
            product_summary = response.meta.get("product_summary")
            if product_summary:
                yield self._build_item_from_data(product_summary, response)
            return

        if not product_data:
            product_summary = response.meta.get("product_summary")
            if product_summary:
                yield self._build_item_from_data(product_summary, response)
            else:
                self.logger.warning(
                    "El bloque JSON del producto no contiene datos en %s", response.url
                )
            return

        yield self._build_item_from_data(product_data, response)

    def _build_item_from_data(self, product_data, response):
        item = ProductItem()
        item["id"] = product_data.get("productId")
        item["name"] = product_data.get("productName")
        # item["description"] = product_data.get("description") or product_data.get("metaTagDescription")
        item["brand"] = product_data.get("brand")
        item["url"] = self._build_product_url(
            product_data.get("link") or product_data.get("linkText") or response.url
        )
        # item["sku"] = product_data.get("productReference") or product_data.get("productReferenceCode")

        item["category_id"] = response.meta.get("category_id") or product_data.get(
            "categoryId"
        )
        item["category_name"] = response.meta.get("category_name")

        list_price = product_data.get("listPrice") or {}
        selling_price = product_data.get("sellingPrice") or {}
        price_range = product_data.get("priceRange") or {}

        if not list_price and isinstance(price_range, dict):
            list_price = price_range.get("listPrice") or {}
        if not selling_price and isinstance(price_range, dict):
            selling_price = price_range.get("sellingPrice") or {}

        item["price"] = (
            (list_price.get("highPrice") or list_price.get("lowPrice"))
            if isinstance(list_price, dict)
            else None
        )
        item["sale_price"] = (
            (selling_price.get("highPrice") or selling_price.get("lowPrice"))
            if isinstance(selling_price, dict)
            else None
        )

        item["available"] = product_data.get("available")
        # 1 item["image_url"] = product_data.get("imageUrl")
        # if not item["image_url"] and isinstance(product_data.get("images"), list) and product_data.get("images"):
        #     item["image_url"] = product_data.get("images")[0].get("imageUrl")

        # item["raw_data"] = product_data
        return item

    def _extract_product_links(self, html):
        matches = re.findall(r'href="([^"]+/p)"', html)
        seen = []
        for link in matches:
            normalized = self._build_product_url(link)
            if normalized not in seen:
                seen.append(normalized)
        return seen

    def _build_category_api_url(self, start_idx=0):
        if self.category_url:
            if self.category_url.startswith("http"):
                parsed = urllib.parse.urlparse(self.category_url)
                path = parsed.path
            else:
                path = self.category_url
        elif self.category_name:
            slug = self.category_slug or self._slugify(self.category_name)
            path = f"/{slug}" if slug else ""
        else:
            return ""

        return f"https://www.olimpica.com/api/catalog_system/pub/products/search{path}?{urllib.parse.urlencode({'_from': start_idx, '_to': start_idx + self.page_size - 1})}"

    def _build_product_url(self, link_text):
        if not link_text:
            return ""
        if link_text.startswith("http"):
            return link_text
        return f"https://www.olimpica.com/{link_text.lstrip('/')}"

    def _slugify(self, value):
        normalized = unicodedata.normalize("NFKD", value or "")
        ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
        ascii_value = ascii_value.lower()
        ascii_value = re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")
        return ascii_value
