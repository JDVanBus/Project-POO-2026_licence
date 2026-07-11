import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

import scrapy

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from ..items import CategoryItem
except Exception:
    pass


class FalabellaCategorySpider(scrapy.Spider):
    name = "FalabellaCategorySpider"
    allowed_domains = ["falabella.com.co", "www.falabella.com.co"]
    start_urls = ["https://www.falabella.com.co/falabella-co/"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Registramos URLs procesadas para evitar duplicaciones
        self.urls_procesadas = set()
        
        # Lista negra extendida para erradicar enlaces corporativos e institucionales
        self.blacklist_keywords = [
            "banco", "seguro", "términos", "condiciones", "vende", "trabaja",
            "ayuda", "servicio al cliente", "inversionistas", "sostenibilidad",
            "cmr", "puntos", "tarjeta", "corporativo", "nosotros", "política",
            "privacidad", "cookies", "contacto", "tiendas", "despacho", "cambios",
            "mi cuenta", "mis compras", "cerrar sesión", "inicia sesión", "home web"
        ]

    def parse(self, response):
        match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            response.text,
            re.S,
        )
        if not match:
            self.logger.warning("No se encontró __NEXT_DATA__ en %s", response.url)
            return

        try:
            payload = json.loads(match.group(1))
        except json.JSONDecodeError:
            self.logger.warning("No se pudo decodificar __NEXT_DATA__")
            return

        self.logger.info("JSON cargado con éxito. Extrayendo árbol de categorías limpio...")
        yield from self._walk_payload(payload, level=0, breadcrumbs=[], parent=None)

    def _walk_payload(self, data, level=0, breadcrumbs=None, parent=None):
        if breadcrumbs is None:
            breadcrumbs = []

        if isinstance(data, dict):
            name = data.get("name") or data.get("label") or data.get("title") or data.get("displayName")
            raw_url = data.get("url") or data.get("href") or data.get("slug") or ""
            
            next_parent = parent
            next_breadcrumbs = breadcrumbs

            if name and isinstance(name, str):
                name_clean = name.strip()
                name_lower = name_clean.lower()

                # 1. Filtro básico de nombres y lista negra corporativa
                if len(name_clean) >= 2 and not any(kw in name_lower for kw in self.blacklist_keywords):
                    
                    url_str = str(raw_url).lower().strip()
                    
                    # 2. FILTRO EXPLICITO ANTI-BASURA (Imágenes, Marcas, Búsquedas y Promociones)
                    es_imagen = any(url_str.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg", ".json", ".xml"])
                    es_marca_o_busqueda = any(bad_path in url_str for bad_path in ["/search", "/brand", "promociones", "collection", "exclusivo"])
                    es_categoria_real = "/category/cat" in url_str

                    # Solo procesamos si tiene formato válido de categoría, y NO es imagen ni marca/búsqueda
                    if url_str and es_categoria_real and not es_imagen and not es_marca_o_busqueda:
                        url_completa = self._normalize_url(raw_url)

                        if url_completa not in self.urls_procesadas:
                            self.urls_procesadas.add(url_completa)

                            # Si dice "Ver todo", heredamos contextualmente la información del nodo padre anterior
                            if name_lower == "ver todo" and parent:
                                name_clean = f"Ver todo {parent.get('name', '')}"

                            item = CategoryItem()
                            item["source"] = "falabella.com.co"
                            item["item_type"] = "category"
                            item["id"] = data.get("id") or data.get("categoryId") or data.get("category_id") or url_completa.strip("/").split("/")[-1]
                            item["name"] = name_clean
                            item["url"] = url_completa
                            item["parent_id"] = parent.get("id") if parent else None
                            item["parent_name"] = parent.get("name") if parent else None
                            item["has_children"] = bool(data.get("children") or data.get("subcategories") or data.get("items"))
                            item["level"] = level
                            item["breadcrumbs"] = breadcrumbs + [name_clean]

                            yield item

                            next_parent = {"id": item["id"], "name": item["name"]}
                            next_breadcrumbs = item["breadcrumbs"]
                    else:
                        # Si es un contenedor jerárquico intermedio (ej: "Tecnología") sin link directo aún,
                        # preservamos su nombre para la descendencia y los breadcrumbs de sus hijos reales.
                        if name_lower != "ver todo":
                            dummy_id = data.get("id") or data.get("categoryId") or name_lower.replace(" ", "-")
                            next_parent = {"id": str(dummy_id), "name": name_clean}
                            next_breadcrumbs = breadcrumbs + [name_clean]

            # Continuamos recorriendo el JSON recursivamente buscando las ramas de subcategorías
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    es_subnivel = key in {"children", "subcategories", "items", "categories", "nodes", "menu"}
                    yield from self._walk_payload(
                        value,
                        level=level + 1 if es_subnivel else level,
                        breadcrumbs=next_breadcrumbs,
                        parent=next_parent,
                    )

        elif isinstance(data, list):
            for entry in data:
                if isinstance(entry, (dict, list)):
                    yield from self._walk_payload(entry, level=level, breadcrumbs=breadcrumbs, parent=parent)

    def _normalize_url(self, value):
        if not value:
            return ""
        value_str = str(value).strip()
        if value_str.startswith("http"):
            return value_str
        return urljoin("https://www.falabella.com.co", value_str.lstrip("/"))