import re
import unicodedata
import urllib.parse
import scrapy

from ..items import ProductItem


class ProductSpider(scrapy.Spider):
    name = "OlimpicaProductSpider"
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

        # Generamos la URL de la API inicial
        if self.category_id or self.category_url or self.category_name:
            self.start_urls = [self._build_category_api_url(0)]
        else:
            self.start_urls = []

    def start_requests(self):
        if not self.start_urls:
            self.logger.error(
                "Error: Debes proporcionar un category_id, category_url o category_name para iniciar."
            )
            return

        self.logger.info(
            "Iniciando crawl de productos vía API VTEX para: %s",
            self.category_name or self.category_url or self.category_id,
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
        self.logger.info("Procesando API URL: %s", response.url)

        try:
            products = response.json()
        except ValueError:
            self.logger.error(
                "No se pudo decodificar el JSON de la API en: %s", response.url
            )
            return

        if not products or not isinstance(products, list):
            self.logger.warning(
                "No se encontraron productos en esta sección de la API."
            )
            return

        # Procesamos cada producto directamente desde el payload de la API
        for prod in products:
            item = ProductItem()
            item["id"] = prod.get("productId")
            item["name"] = prod.get("productName")
            item["brand"] = prod.get("brand")

            # URLs de Olímpica
            link_text = prod.get("link") or prod.get("linkText") or ""
            item["url"] = self._build_product_url(link_text)

            item["category_id"] = self.category_id or prod.get("categoryId")
            item["category_name"] = self.category_name

            # Extracción limpia de Precios e Inventario sin intermediarios
            list_price = None
            selling_price = None
            available = False

            items_list = prod.get("items") or []
            if items_list and isinstance(items_list, list):
                first_sku = items_list[0]

                # Navegamos hacia la oferta comercial del vendedor principal (Sellers -> CommertialOffer)
                sellers = first_sku.get("sellers") or []
                if sellers and isinstance(sellers, list):
                    commertial_offer = sellers[0].get("commertialOffer") or {}
                    if commertial_offer:
                        # VTEX retorna ListPrice (original) y Price (con descuento)
                        list_price = commertial_offer.get("ListPrice")
                        selling_price = commertial_offer.get("Price")

                        # Verificación de disponibilidad
                        available_qty = commertial_offer.get("AvailableQuantity", 0)
                        available = available_qty > 0

            # Asignación final al ítem
            item["price"] = list_price
            item["sale_price"] = selling_price
            item["available"] = available

            yield item

        # Paginación consecutiva controlada
        if len(products) >= self.page_size:
            if section_number + 1 < self.max_sections:
                next_start = start_idx + self.page_size
                next_url = self._build_category_api_url(next_start)
                self.logger.info(
                    "Paginando a la sección API %s/%s",
                    section_number + 2,
                    self.max_sections,
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
                    "Se alcanzó el límite establecido de %s secciones.",
                    self.max_sections,
                )

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
        path = "/" + path.strip("/")

        return f"https://www.olimpica.com/api/catalog_system/pub/products/search{path}?{urllib.parse.urlencode({'_from': start_idx, '_to': start_idx + self.page_size - 1})}"

    def _build_product_url(self, link_text):
        if not link_text:
            return ""
        if link_text.startswith("http"):
            return link_text
        return f"https://www.olimpica.com/{link_text.lstrip('/')}"

    def _slugify(self, value):
        if not value:
            return ""
        normalized = unicodedata.normalize("NFKD", value)
        ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
        ascii_value = ascii_value.lower()
        ascii_value = re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")
        return ascii_value
