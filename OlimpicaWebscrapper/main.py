import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATEGORIES_FILE = ROOT / "categorias.json"


def sanitize_filename(value):
    invalid_chars = '<>:"/\\|?*'
    clean_value = "".join("_" if ch in invalid_chars else ch for ch in value)
    return clean_value.strip().rstrip(".")


def load_category_url(category_id, category_name):
    if not CATEGORIES_FILE.exists():
        return None

    try:
        with CATEGORIES_FILE.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except Exception:
        return None

    for category in data:
        if str(category.get("id")) == str(category_id):
            url = (category.get("url") or "").strip()
            if url:
                if url.startswith("http"):
                    return url
                return f"https://www.olimpica.com{url if url.startswith('/') else '/' + url}"

    return None


def run_scrapy(spider_name, **kwargs):
    command = [sys.executable, "-m", "scrapy", "crawl", spider_name]

    output = kwargs.pop("output", None)
    if output is not None:
        output_path = Path(output)
        if not output_path.is_absolute():
            output_path = ROOT / output_path
        command.extend(["-o", str(output_path)])

    for key, value in kwargs.items():
        command.extend(["-a", f"{key}={value}"])

    subprocess.run(command, cwd=str(ROOT), check=True)


def menu():
    print("=" * 20)
    print("OLIMPICA-WEBSCRAPPER")
    print("=" * 20)
    print("1. Extraer categorías de Olimpica")
    print("2. Extraer productos de Olimpica")
    print("3. Listar Categorias")
    print("4. Extraer categorías de Falabella")
    print("5. Extraer productos de Falabella")
    print("6. Extraer categorias de Linio")
    print("7. Extraer productos de Linio")

    choice = input("Elige una opción: ").strip()

    if choice == "1":
        run_scrapy("OlimpicaCategorySpider", output="Olimpica_categorias.json")
    elif choice == "2":
        category_id = input("Ingresa el ID de la categoría: ").strip()
        category_name = input("Ingresa el nombre de la categoría: ").strip()
        category_url = load_category_url(category_id, category_name)
        output_name = f"productos_Olimpica{sanitize_filename(category_id)}_{sanitize_filename(category_name)}.json"
        slug = category_name.lower().replace(" ", "-")
        max_sections = input(
            "Digite la cantidad de secciones máxima a scrapear (5 por defecto): "
        )
        if not category_name and not category_url:
            raise ValueError("Se requiere un name o un category_url para continuar")
        kwargs = {
            "category_id": category_id,
            "category_name": category_name,
            "output": output_name,
            "category_slug": slug,
            "max_sections": max_sections,
        }
        if category_url:
            kwargs["category_url"] = category_url

        run_scrapy("OlimpicaProductSpider", **kwargs)
        print(f"Archivo guardado en: {output_name}")
    elif choice == "3":
        if not CATEGORIES_FILE.exists():
            print(
                "No se encontró el archivo de categorías. Por favor, extrae las categorías primero."
            )
            return

        try:
            with CATEGORIES_FILE.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception as e:
            print(f"Error al leer el archivo de categorías: {e}")
            return

        if not data:
            print("No hay categorías disponibles.")
            return

        print("\nCategorías disponibles:")
        print("-" * 30)
        for i, category in enumerate(data):
            if i % 40 == 0 and i > 0:
                time.sleep(1)

            category_id = category.get("id", "N/A")
            category_name = category.get("name", "N/A")
            print(f"ID: {category_id}, Nombre: {category_name}")
    elif choice == "4":
        run_scrapy("FalabellaCategorySpider", output="falabella_categorias.json")

    elif choice == "5":
        category_url = input("Ingresa la URL de la categoría de Falabella: ").strip()
        category_name = input("Ingresa el nombre de la categoría: ").strip()
        max_pages = (
            input(
                "Ingresa el número máximo de páginas a scrapear (3 por defecto): "
            ).strip()
            or "3"
        )
        output_name = f"productos_falabella_{sanitize_filename(category_name)}.json"
        run_scrapy(
            "FalabellaProductSpider",
            category_url=category_url,
            category_name=category_name,
            max_pages=max_pages,
            output=output_name,
        )
        print(f"Archivo guardado en: {output_name}")

    elif choice == "6":
        run_scrapy("LinioCategorySpider", output="linio_categorias.json")

    elif choice == "7":
        # Guardamos el dato directamente en 'category_id' para que coincida con el Spider
        category_id = input(
            "Ingresa el id de la categoría de Linio (ej: CATG33244): "
        ).strip()
        category_name = input("Ingresa el nombre de la categoría: ").strip()
        max_pages = (
            input(
                "Ingresa el número máximo de páginas a scrapear (3 por defecto): "
            ).strip()
            or "3"
        )
        output_name = f"productos_linio_{sanitize_filename(category_name)}.json"

        # Ejecutamos pasando 'category_id' (en lugar de category_url) y 'output' (en lugar de output_name)
        run_scrapy(
            "LinioProductSpider",
            category_id=category_id,
            category_name=category_name,
            max_pages=max_pages,
            output=output_name,  # Cambiado a 'output' para que run_scrapy lo detecte
        )
        print(f"Archivo guardado en: {output_name}")
    else:
        print("Opción no válida")


def main():
    flag = True
    while flag:
        menu()
        out = input("¿Desea realizar otra operación? (s/n): ").strip().lower()

        if out == "s":
            continue
        else:
            break


if __name__ == "__main__":
    main()
