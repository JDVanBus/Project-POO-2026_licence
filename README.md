# Analisis Proyecto 2026-1
> A partir del recorrido y desarrollo funcional del proyecto, se hace una socialización del trabajo realizado y un primer borrador al README final del proyecto

**3M WEBSCRAPPER** herramienta orientada a objetdos para extraer,procesar y almacenar datos productos e-commerce ([olimpica](https://www.olimpica.com), [fallabela](https://www.falabella.com.co/) y [Linio](https://linio.falabella.com.co/)) diseñado para facilitar la comparación de precios y el análisis de tendencias

El presente busca dar una primera aproximación al proyecto a partir de sus funcionamientos principales, requerimientos, etc. No reemplaza la exposición a detalle realizado en la sustentación.

## Catalogo
- [requerimientos](#requerimientos)
- [Instalación](#instalacion)
- [Características](#caracteristicas)
- [Primera Demostración](#demo)
- [Arquitectura](#arquitectura)
- [Contribuir](#contribuir)

### Requerimientos 

- Python 3.13
- Sistema operativo: Linux/macOS (Windows soportado con WSL o ajustes)
- Dependencias principales: Scrapy

### Instalacion

1.Clonar el repositorio

```bash
git clone https://github.com/JuanCuartasCasas/Project-POO-2026.git
cd Projecto-POO-2026
```

2.Crear entorno virtual

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r "requirements.txt"

```

3. Ejecutar `python main.py`

### caracteristicas
El programa se encarga de las funciones principales:

#### Diagrama UML
```mermaid
---
config:
  layout: elk
---
classDiagram
direction TB
    class FalabellaCategorySpider {
    + name: str$
    + allowed_domains: list[str]$
    + sitemap_urls : lisy[str]$
    + sitemap_rules : list[tuple]$
    + max_categories : int
    + sitemap_filter() Iterable
    + __init__() None
    + parse ()  Iterable
    
    }

    class FalabellaProductSpider {
    + name: str$
    + allowed_domains: list[str]$  
    + category_url: str
    + category_name : str
    + start_urls : list[str]
    + max_size : int
    + __init__() None
    + start_request() Iterable
    + parse ()  Iterable
    # find_products_grid() str
    # build_page_url() str
    
    }

    class LinioCategorySpider {
    + name : str$
    + allowed_domains : str$
    + start_urls: list[str]$
    + __init__() None
    + parse ()  Iterable
    + parse_category() Iterable
    }

    class LinioProductSpider {
    + name : str$
    + allowed_domains : str$
    + headers: dict
    + start_urls : list[str]
    + category_id : str
    + category_name : str
    + category_url : str  
    + max_size : int  
    + __init__() None
    + start_request() Iterable
    + parse ()  Iterable
    + find_products_grid() str
    }

    class OlimpicaProductSpider {
    + name : str$
    + allowed_domains : str$
    + category_id : str
    + category_name: str
    + category_url : str
    + category_slug : str
    + max_sections : str
    + page_size: int
    + __init__() None
    + start_request() Iterable
    + parse ()  Iterable
    # build_category_api_url() str
    # build_product_url() str 
    # slugigy() str
    
    }

    class OlimpicaCategorySpider {
    + name : str$
    + allowed_domains : str$
    + start_urls: list[str]$
    + seen_categories: Set
    + __init__() None
    + parse ()  Iterable
    + parse_categories() Iterable
    
    }

    class ScrapySpider {
    + name : str
    + allowed_domains : list[str]
    + start_urls: lit[str]
    + custom_settings : dict
    + settings : Settings
    + crawler : Crawler
    + logger : logging

    + __init__() None
    + start_request() Iterable
    + parse ()  Iterable
    + closed() None

    }

    class SitemapSpider {
      + sitemap_urls: list[str]
      + sitemap_rules : list[tuple]
      + parse_sitemap() Iterable
    }

    class BaseItem {
    + __init__()
    + source: list[str]
    + item_type : str
    + id : str
    + name : str
    + url : str
    + raw_data : list[str]
    }

    class CategoryItem {
    + __init__()
    + parent_id : str
    + parent_name : str
    + has_children : bool
    + level: int
    + breadcrumbs : list[str]
    }

    class ProductItem {
    + __init__()
    + price 
    + sale_price    
    + brand  
    + category_id
    + category_name 
    +available
    +sku 
    +description
    }
    class Item {
      + __init__() abstract
    }

    ScrapySpider "1"<|-- OlimpicaCategorySpider
    ScrapySpider "1"<|-- OlimpicaProductSpider
    ScrapySpider "1"<|-- FalabellaProductSpider
    ScrapySpider "1"<|-- LinioCategorySpider
    ScrapySpider "1"<|-- LinioProductSpider
    ScrapySpider "1"<|-- SitemapSpider
    SitemapSpider "1"<|-- FalabellaCategorySpider
    BaseItem "1"<|-- CategoryItem
    BaseItem "1"<|-- ProductItem
    Item "1"<|-- BaseItem

```
---


- Extracción de categorias y productos
- Serialización a JSON normalizado.
- Pipeline modular para validación
- Arquitectura Orientada a Objetos
  
### Demo
<img width="392" height="191" alt="image" src="https://github.com/user-attachments/assets/23e582fb-4e42-401f-9d38-e81370d3f45a" />

### Archivos generados


### arquitecura
```
PROJECT-POO-2026/
├─ 3m_webscrapper/
├─ main.py
│  ├─ Structure/
│  |  ├─ pipelines.py
│  |  ├─ middlewares.py
|  |  ├─ settings.py
|  |  ├─ excepts.py
│  |  ├─ Spiders/
|  |  |  ├─ FalabellaCategorySpider.py
|  |  |  ├─ FalabellaProductSpider.py
|  |  |  ├─ LinioCategorySpider.py
|  |  |  ├─ OlimpicaCategorySpider.py
|  |  |  ├─ OlimpicaProductSpider.py
├─ requirements.txt
└─ Scrapy.cfg
```
### Potencialidad de crecimiento

Con el fin de mantener una constancia en el desarollo, y afianzamiento en el paradigma OO, se pone a disposición temarios potencialmente aplicables a el proyecto:

- Agregación de GUI
- Conexión con bases de datos
- Estructura basada en Roles
- Autenticación Web

### Contribuir

Si se encuentra interesado en la contribución del desarollo del proyecto, realicé un PR con los cambios propuestos y haganoslo saber en nuestro [correo](mailto:jucuartasc@gmail.edu.co)

### Contactos

Developers: 
- Juan Diego Cuartas Casas -- [Github](https://github.com/JuanCuartasCasas)

