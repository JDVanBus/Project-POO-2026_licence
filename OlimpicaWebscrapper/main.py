import json
import subprocess
import sys
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


def main():
    print("Menú del scraper")
    print("1. Extraer categorías")
    print("2. Extraer productos por categoría")

    choice = input("Elige una opción: ").strip()

    if choice == "1":
        run_scrapy("CategorySpider", output="categorias.json")
    elif choice == "2":
        category_id = input("Ingresa el ID de la categoría: ").strip()
        category_name = input("Ingresa el nombre de la categoría: ").strip()
        category_url = load_category_url(category_id, category_name)
        output_name = f"products_{sanitize_filename(category_id)}_{sanitize_filename(category_name)}.json"
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

        run_scrapy("ProductSpider", **kwargs)
        print(f"Archivo guardado en: {output_name}")
    else:
        print("Opción no válida")


if __name__ == "__main__":
    main()
