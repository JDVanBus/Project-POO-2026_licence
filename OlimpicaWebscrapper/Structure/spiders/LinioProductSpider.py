import json
import re
import unicodedata
import scrapy

from ..items import ProductItem


class LinioProductSpider(scrapy.Spider):
    name = "LinioProductSpider"
    allowed_domains = ["falabella.com.co", "linio.falabella.com.co"]

    def __init__(
        self,
        category_id=None,
        category_name=None,
        max_pages=1,
        *args,
        **kwargs,
    ):
        """
        Constructor que recibe ID y Nombre en lugar de URLs pesadas.
        """
        super().__init__(*args, **kwargs)
        self.category_id = category_id
        self.category_name = category_name

        try:
            self.max_pages = int(max_pages)
        except (TypeError, ValueError):
            self.max_pages = 1

        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9",
            "Cache-Control": "max-age=0",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }

        # Auto-construcción de la URL inicial usando la lógica de negocio
        if self.category_id and self.category_name:
            slug = self._slugify(self.category_name)
            built_url = f"https://linio.falabella.com.co/linio-co/category/{self.category_id}/{slug}"
            self.start_urls = [built_url]
        else:
            self.start_urls = []
            self.logger.error(
                "Se requiere 'category_id' y 'category_name' para inicializar el spider."
            )

    def start_requests(self):
        if not self.start_urls:
            return

        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                headers=self.headers,
                callback=self.parse,
                meta={"page_number": 1},  # Ya no dependemos de "base_url" en meta
            )

    def parse(self, response):
        page_number = response.meta.get("page_number", 1)
        self.logger.info(
            f"Escaneando productos de {self.category_name} - Página {page_number}"
        )

        # Extraemos el bloque Next Data
        match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            response.text,
            re.S,
        )

        if not match:
            self.logger.error(
                f"No se encontró __NEXT_DATA__ en la página {page_number}"
            )
            return

        try:
            payload = json.loads(match.group(1))
        except json.JSONDecodeError:
            return

        # Buscamos la lista de productos dentro del JSON de forma recursiva
        products_list = self._find_products_grid(payload)

        if not products_list:
            self.logger.warning("No se encontraron productos en esta página.")
            return

        for prod in products_list:
            item = ProductItem()
            item["id"] = prod.get("productId") or prod.get("skuId")
            item["name"] = prod.get("displayName") or prod.get("title")
            item["brand"] = prod.get("brand") or "Genérico"

            # Formateo del link del producto
            raw_url = prod.get("url") or ""
            if raw_url.startswith("http"):
                item["url"] = raw_url
            else:
                item["url"] = f"https://linio.falabella.com.co{raw_url}"

            item["category_id"] = self.category_id
            item["category_name"] = self.category_name

            # Extracción de precios
            prices = prod.get("prices") or []
            list_price = None
            sale_price = None

            if isinstance(prices, list):
                for p in prices:
                    tipo = str(p.get("type", "")).lower()
                    monto = p.get("originalAmount") or p.get("amount") or p.get("price")
                    if "referencia" in tipo or "normal" in tipo:
                        list_price = monto
                    elif "evento" in tipo or "cmr" in tipo or "internet" in tipo:
                        sale_price = monto

            if not sale_price:
                sale_price = prod.get("price") or list_price

            item["price"] = list_price
            item["sale_price"] = sale_price

            yield item

        # Paginación consecutiva automática (Inmune a redirecciones)
        if page_number < self.max_pages:
            next_page = page_number + 1

            # Limpiamos cualquier parámetro '?page=' previo de la URL de respuesta actual
            clean_url = response.url.split("?")[0]
            next_url = f"{clean_url}?page={next_page}"

            self.logger.info(f"Navegando a la siguiente página: {next_url}")
            yield scrapy.Request(
                url=next_url,
                headers=self.headers,
                callback=self.parse,
                meta={"page_number": next_page},
            )

    def _find_products_grid(self, data):
        if isinstance(data, dict):
            for target_key in ["results", "products", "items"]:
                if target_key in data and isinstance(data[target_key], list):
                    lista = data[target_key]
                    if (
                        lista
                        and isinstance(lista[0], dict)
                        and ("productId" in lista[0] or "skuId" in lista[0])
                    ):
                        return lista
            for value in data.values():
                res = self._find_products_grid(value)
                if res:
                    return res
        elif isinstance(data, list):
            for item in data:
                res = self._find_products_grid(item)
                if res:
                    return res
        return None

    def _slugify(self, value):
        """Convierte nombres como 'Celulares y Smartphones' en 'celulares-y-smartphones'"""
        if not value:
            return ""
        normalized = unicodedata.normalize("NFKD", value)
        ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
        ascii_value = ascii_value.lower()
        ascii_value = re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")
        return ascii_value
