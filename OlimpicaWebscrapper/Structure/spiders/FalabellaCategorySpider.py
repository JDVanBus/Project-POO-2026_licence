import json
import re
import sys
from pathlib import Path

import scrapy
from scrapy.spiders import SitemapSpider

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from ..items import CategoryItem
except Exception:
    ("No se hallo el Archivo Items.py")


class FalabellaCategorySpider(SitemapSpider):
    name = "FalabellaCategorySpider"
    allowed_domains = ["falabella.com.co", "www.falabella.com.co"]
    sitemap_urls = [
        "https://www.falabella.com.co/static/site/sitemaps/categories/categories_co_FA_COM-0.xml"
    ]
    sitemap_rules = [
        ("/category/", "parse_category"),
    ]

    def __init__(self, max_categories=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.max_categories = int(max_categories) if max_categories else None
        except (TypeError, ValueError):
            self.max_categories = None
        self.processed_count = 0

    def parse_category(self, response):
        if self.max_categories and self.processed_count >= self.max_categories:
            return
        match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            response.text,
            re.S,
        )
        if not match:
            return

        try:
            payload = json.loads(match.group(1))
        except json.JSONDecodeError:
            return

        # 3. Buscaremos los breadcrumbs reales de esta categoría en los metadatos de la página
        breadcrumbs_list = []

        # Next.js suele guardar los breadcrumbs de la página activa en pageProps -> breadcrumbs
        try:
            breadcrumbs_data = payload["props"]["pageProps"]["breadcrumbs"] or []
            # Extraemos solo los nombres de la miga de pan (ej: ["Tecnología", "Computadores", "Laptops"])
            breadcrumbs_list = [
                bc["name"].strip() for bc in breadcrumbs_data if bc.get("name")
            ]
        except (KeyError, TypeError):
            # Alternativa por si la estructura cambia ligeramente en algunas categorías
            pass

        # Si Next.js falló, intentamos extraer los breadcrumbs directamente del HTML usando CSS
        if not breadcrumbs_list:
            breadcrumbs_list = response.css(
                "ol.breadcrumbs-list li a::text, .breadcrumb li::text"
            ).getall()
            breadcrumbs_list = [b.strip() for b in breadcrumbs_list if b.strip()]

        # Limpiamos elementos genéricos de la miga de pan como "Home" o "Inicio"
        if breadcrumbs_list and breadcrumbs_list[0].lower() in [
            "home",
            "inicio",
            "falabella",
            "falabella.com",
        ]:
            breadcrumbs_list.pop(0)

        if not breadcrumbs_list:
            # Si de verdad no tiene miga de pan, usamos el título de la página como categoría única
            titulo = response.css("h1::text").get()
            if titulo:
                breadcrumbs_list = [titulo.strip()]
            else:
                return

        # 4. Reconstrucción de Jerarquía
        name = breadcrumbs_list[-1]  # La categoría actual es el último elemento
        level = (
            len(breadcrumbs_list) - 1
        )  # El nivel de profundidad (0 = principal, 1 = sub, etc.)

        parent_name = None
        parent_id = None
        if len(breadcrumbs_list) > 1:
            parent_name = breadcrumbs_list[-2]  # El padre es el penúltimo elemento
            parent_id = parent_name.lower().replace(" ", "-")

        # 5. Construcción del Item Limpio
        item = CategoryItem()
        item["source"] = "falabella.com.co"
        item["item_type"] = "category"
        item["id"] = response.url.strip("/").split("/")[
            -2
        ]  # Extrae el ID real de la URL (ej: cat1234)
        item["name"] = name
        item["url"] = response.url
        item["parent_id"] = parent_id
        item["parent_name"] = parent_name
        item["has_children"] = (
            False  # En un sitemap todas son hojas finales o intermedias con URL activa
        )
        item["level"] = level
        item["breadcrumbs"] = breadcrumbs_list

        self.processed_count += 1
        yield item
