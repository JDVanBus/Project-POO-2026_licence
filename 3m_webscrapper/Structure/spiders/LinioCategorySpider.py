import json
import re
import scrapy


from ..items import CategoryItem


class LinioCategorySpider(scrapy.Spider):
    name = "LinioCategorySpider"
    allowed_domains = ["falabella.com.co", "linio.falabella.com.co"]

    # Empezamos en la página principal de Linio para "descubrir" las categorías reales
    start_urls = ["https://linio.falabella.com.co/linio-co"]

    def __init__(self, max_categories=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.max_categories = int(max_categories)
        except (TypeError, ValueError):
            self.max_categories = None

    def parse(self, response):
        # Si estamos en la página principal, buscamos todos los enlaces de categorías
        if response.url.strip("/").endswith("/linio-co"):
            self.logger.info(
                "Página principal detectada. Extrayendo enlaces de categorías..."
            )

            # Buscamos enlaces en el HTML que apunten a /category/
            links = response.css("a::attr(href)").getall()
            category_urls = set()

            for link in links:
                if "/category/" in link:
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
            breadcrumbs_list = [
                bc["name"].strip() for bc in breadcrumbs_data if bc.get("name")
            ]
        except (KeyError, TypeError):
            pass

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
        if level > 1:
            parent_name = breadcrumbs_list[-2]
            parent_id = parent_name.lower().replace(" ", "-")

        item = CategoryItem()
        item["source"] = "linio.falabella.com.co"
        item["item_type"] = "category"
        try:
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
