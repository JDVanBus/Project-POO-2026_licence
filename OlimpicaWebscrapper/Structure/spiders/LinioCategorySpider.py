import json
import re
import scrapy

try:
    from ..items import CategoryItem
except ImportError:
    ("No se hallo el Archivo Items.py")


class LinioCategorySpider(scrapy.Spider):
    name = "LinioCategorySpider"
    allowed_domains = ["falabella.com.co", "linio.falabella.com.co"]

    # Empezamos en la página principal de Linio para "descubrir" las categorías reales
    start_urls = ["https://linio.falabella.com.co/linio-co"]

    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9",
            "Cache-Control": "max-age=0",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        },
        # Agregamos un retardo para ser amigables con el servidor y evitar bloqueos temporales
        "DOWNLOAD_DELAY": 0.5,
        "CONCURRENT_REQUESTS": 8,
    }

    def __init__(self, max_categories=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.max_categories = int(max_categories) if max_categories else None
        except (TypeError, ValueError):
            self.max_categories = None

    def parse(self, response):
        # Si estamos en la página principal, buscamos todos los enlaces de categorías
        if (
            response.url == "https://linio.falabella.com.co/linio-co"
            or response.url.endswith("/linio-co/")
        ):
            self.logger.info(
                "Página principal detectada. Extrayendo enlaces de categorías..."
            )

            # Buscamos enlaces en el HTML que apunten a /category/
            links = response.css("a::attr(href)").getall()
            category_urls = set()

            for link in links:
                if "/category/" in link:
                    # Normalizamos la URL para que sea absoluta
                    absolute_url = response.urljoin(link)
                    # Evitamos duplicados y URLs de paginación o filtros
                    if "?" not in absolute_url and "#" not in absolute_url:
                        category_urls.add(absolute_url)
            category_urls = list(category_urls)
            if self.max_categories:
                category_urls = category_urls[: self.max_categories]

            self.logger.info(
                f"Se descubrieron {len(category_urls)} categorías únicas (limite: {self.max_categories or 'sin limite'})."
            )

            # Enviamos cada una de las categorías descubiertas al método parse_category
            for url in category_urls:
                yield scrapy.Request(
                    url=url,
                    headers=self.settings.get("DEFAULT_REQUEST_HEADERS"),
                    callback=self.parse_category,
                    dont_filter=False,
                )
        else:
            # Si por alguna razón entra aquí directamente, la procesa como categoría
            yield from self.parse_category(response)

    def parse_category(self, response):
        self.logger.info(f"Procesando categoría: {response.url}")

        # Buscamos el objeto de hidratación __NEXT_DATA__
        match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            response.text,
            re.S,
        )

        if not match:
            self.logger.warning(
                f"No se encontró el bloque __NEXT_DATA__ en: {response.url}"
            )
            return

        try:
            payload = json.loads(match.group(1))
        except json.JSONDecodeError:
            self.logger.error("No se pudo decodificar el JSON de __NEXT_DATA__")
            return

        breadcrumbs_list = []

        try:
            # Buscamos los breadcrumbs en el payload de Next.js
            breadcrumbs_data = payload["props"]["pageProps"]["breadcrumbs"] or []
            if not breadcrumbs_data:
                breadcrumbs_data = (
                    payload["props"]["pageProps"]["fallbackBreadcrumbs"] or []
                )
            breadcrumbs_list = [
                bc["name"].strip() for bc in breadcrumbs_data if bc.get("name")
            ]
        except (KeyError, TypeError):
            pass

        # Fallback CSS si no viene en el JSON
        if not breadcrumbs_list:
            breadcrumbs_list = response.css(
                "ol.breadcrumbs_list li a::text, .breadcrumbs li::text"
            ).getall()
            breadcrumbs_list = [b.strip() for b in breadcrumbs_list if b.strip()]

        # Limpieza de breadcrumbs corporativos
        if breadcrumbs_list and breadcrumbs_list[0].lower() in [
            "home",
            "inicio",
            "falabella",
            "falabella.com",
            "linio",
        ]:
            breadcrumbs_list.pop(0)

        if not breadcrumbs_list:
            titulo = response.css("h1::text").get()
            if titulo:
                breadcrumbs_list = [titulo.strip()]
            else:
                self.logger.warning(
                    f"No se pudo determinar el nombre de la categoría para {response.url}"
                )
                return

        name = breadcrumbs_list[-1]
        level = len(breadcrumbs_list) - 1

        parent_name = None
        parent_id = None
        if len(breadcrumbs_list) > 1:
            parent_name = breadcrumbs_list[-2]
            parent_id = parent_name.lower().replace(" ", "-")

        # Construcción del Item
        item = CategoryItem()
        item["source"] = "linio.falabella.com.co"
        item["item_type"] = "category"
        try:
            # Extrae el ID real de la URL (ej: CATG33244)
            item["id"] = response.url.strip("/").split("/")[-2]
        except Exception:
            item["id"] = None

        item["name"] = name
        item["url"] = response.url
        item["parent_id"] = parent_id
        item["parent_name"] = parent_name
        item["has_children"] = False
        item["level"] = level
        item["breadcrumbs"] = breadcrumbs_list

        yield item
