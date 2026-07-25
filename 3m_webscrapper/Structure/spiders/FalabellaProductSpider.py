import json
import re
from urllib.parse import urlencode, urljoin, urlparse, parse_qs

import scrapy

from ..items import ProductItem


class FalabellaProductSpider(scrapy.Spider):
    name = "FalabellaProductSpider"
    allowed_domains = ["falabella.com.co", "www.falabella.com.co"]

    def __init__(
        self,
        url=None,
        name=None,
        paginas_maximas=None,
        category_url=None,
        category_name=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        raw_url = url or category_url
        if isinstance(raw_url, (list, tuple)):
            self.start_urls = [
                str(item).strip() for item in raw_url if str(item).strip()
            ]
            self.start_url = self.start_urls[0] if self.start_urls else None
        else:
            self.start_url = str(raw_url).strip() if raw_url else None
            self.start_urls = [self.start_url] if self.start_url else []

        self.category_name = category_name or name

        try:
            self.paginas_maximas = int(paginas_maximas)
        except (ValueError, TypeError):
            self.paginas_maximas = 1

    def start_requests(self):
        if not self.start_urls:
            self.logger.error(
                "No se proporcionó una URL de categoría válida. Usa: -a url='...' o -a category_url='...'"
            )
            return

        for start_url in self.start_urls:
            yield scrapy.Request(
                url=start_url, callback=self.parse, meta={"pagina_actual": 1}
            )

    def parse(self, response):
        pagina_actual = response.meta.get("pagina_actual", 1)
        self.logger.info(
            f"Procesando página {pagina_actual} de la categoría: {self.category_name}"
        )

        match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            response.text,
            re.S,
        )

        if not match:
            self.logger.warning(
                f"No se encontró __NEXT_DATA__ en la página {pagina_actual}."
            )
            return

        try:
            payload = json.loads(match.group(1))
        except json.JSONDecodeError:
            self.logger.error(f"Error al decodificar los datos de {pagina_actual}")
            return

        productos_raw = self._find_products_grid(payload)

        if not productos_raw:
            self.logger.warning(
                "No se localizó la lista de productos dentro del JSON de Next.js."
            )
            return

        # 3. Procesamiento e instanciación de ítems
        for prod in productos_raw:
            item = ProductItem()
            item["source"] = "falabella.com.co"
            item["item_type"] = "product"
            item["category_name"] = self.category_name
            item["id"] = prod.get("productId") or prod.get("skuId") or prod.get("id")
            item["name"] = (
                prod.get("displayName") or prod.get("title") or prod.get("name")
            )
            item["brand"] = prod.get("brand") or prod.get("brandName") or "Genérico"
            raw_prod_url = prod.get("url") or prod.get("href") or ""
            item["url"] = (
                urljoin("https://www.falabella.com.co", raw_prod_url.strip())
                if raw_prod_url
                else response.url
            )
            precios = prod.get("prices") or prod.get("price") or []
            if isinstance(precios, list):
                for p in precios:
                    tipo = str(p.get("type", "")).lower()
                    monto = p.get("originalAmount") or p.get("amount") or p.get("price")
                    if "referencia" in tipo or "normal" in tipo:
                        item["sale_price"] = monto
                    elif "evento" in tipo or "cmr" in tipo or "internet" in tipo:
                        item["sale_price"] = monto

            if not item["sale_price"]:
                item["sale_price"] = (
                    prod.get("price") or prod.get("highPrice") or prod.get("lowPrice")
                )

            yield item

        # 4. Control de paginación recursiva mediante la lógica de Olímpica
        if pagina_actual < self.paginas_maximas:
            siguiente_pagina = pagina_actual + 1
            nueva_url = self._build_page_url(response.url, siguiente_pagina)

            yield scrapy.Request(
                url=nueva_url,
                callback=self.parse,
                meta={"pagina_actual": siguiente_pagina},
            )

    def _find_products_grid(self, data):
        """
        Busca recursivamente dentro del objeto JSON de Next.js la clave que
        contiene la lista de productos de la categoría actual.
        """
        if isinstance(data, dict):
            # Claves habituales donde Falabella guarda la lista de productos en Next.js
            for target_key in ["results", "products", "items"]:
                if target_key in data and isinstance(data[target_key], list):
                    # Nos aseguramos de que el primer elemento parezca un producto real
                    lista = data[target_key]
                    if (
                        lista
                        and isinstance(lista[0], dict)
                        and (
                            "productId" in lista[0]
                            or "skuId" in lista[0]
                            or "displayName" in lista[0]
                        )
                    ):
                        return lista

            # Si no está en las llaves primarias, seguimos buscando en profundidad
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

    def _build_page_url(self, base_url, page_number):
        """
        Inyecta o actualiza de forma segura el parámetro '?page=X' preservando
        otros posibles parámetros que ya existan en la URL de categoría.
        """
        parsed_url = urlparse(base_url)
        query_params = parse_qs(parsed_url.query)
        query_params["page"] = [str(page_number)]

        new_query = urlencode(query_params, doseq=True)
        new_url = parsed_url._replace(query=new_query).geturl()
        return new_url
