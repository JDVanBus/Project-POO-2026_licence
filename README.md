# Analisis actual 22/06/2026: Web Scraping Startup

> Proyecto académico de Programación Orientada a Objetos enfocado en la extracción, organización y procesamiento de información de la pagina web de Olimpica

---

## Descripción

Actualmente existe una gran cantidad de información disponible en internet, pero gran parte de estos datos se encuentran desorganizados o distribuidos entre múltiples páginas web. Esto dificulta la búsqueda eficiente de información específica y su posterior análisis.

Como solución a este problema, surge el web scraping, una técnica utilizada para extraer información automáticamente desde sitios web y transformarla en datos organizados y procesables.

El presente royecto busca desarrollar un aplicativo webscrapper que facilite la busqueda y comparaciòn de precios en el mercado virtual  
---

# Objetivos

## Objetivo General

Desarrollar un sistema orientado a objetos capaz de extraer y organizar información desde  la pagina olimpica hasta una base de datos, pasando por el servidor remoto de cada aplicaciòn 

## Objetivos Específicos

- Implementar solicitudes HTTP para obtener información de [Olimpica](https://www.olimpica.com).
- Parsear y filtrar contenido HTML utilizando el entorno de trabajo **SCPARY**.
- Organizar los datos obtenidos en estructuras JSON.
- Aplicar principios de Programación Orientada a Objetos como encapsulamiento, composición y polimorfismo para mejorar la organización y eficiencia del algortimo
- Diseñar una arquitectura modular y escalable para futuros desarrollos.

---

# Tecnologías Utilizadas

- Python 3.13
- Visual Studio Code
## Entorno Virtual
El desarollo principal surge del framework SCRAPY, un sistema predefinido que facilita la integración del pradigma OO en el webscrapping; modulado y extensible

## Librerías

- `requests` → realización de peticiones HTTP
- `bs4 (BeautifulSoup)` → análisis y extracción de contenido HTML
- `json` → almacenamiento estructurado de datos

---

# Funcionamiento General

El sistema seguirá tres etapas principales:

| Etapa | Descripción |
|---|---|
| Extracción | Obtención del contenido HTML de una página web |
| Procesamiento | Filtrado y organización de la información relevante |
| Almacenamiento | Conversión y guardado de los datos en formato JSON |

---

## Datos a Extraer

- Categorias: Como principal referencia que guie al usuario en las diversas categorias que ofrece el mercado
- Stock: Actualización de disponibilidad por producto en el momento de realizar el *request*
- Precios: Enfoque central de la base de datos, propuesto para realizar estudios estadísticos y estimación a largo plazo
- Tendencias: analisis de objetos más vendidos por temporada, basado en la extracción de los datos constante


# Programación Orientada a Objetos

El proyecto será desarrollado siguiendo los principios fundamentales de POO:

- Encapsulamiento
- Herencia
- Composición
- Polimorfismo

La arquitectura de scrapy predispone estos elementos base, cómo medio de comunicación entre modulos 

---

# Estado del Proyecto

Tras la fase de diseño, se han realizado las principales tareas cómo reconocimiento del entorno, y primera prueba de extracción de datos-

Pendientes:
- Definicion Final de clases totales presentes y Diagramas UML
- Aplicación de middlewares y extensión de items
- Diseño de la arquitectura interna
- Implementación del sistema de almacenamiento
- Posible desarrollo de interfaz de usuario

---

# analisis UML actual
``` mermaid
classDiagram
    direction 
    class OlimpicaSpider {
    + str name
    + list Allowed_Domains
    + list start_urls
    + parse(response)
    + parse_categories(categories)
    + build_breadcrumbs()
    }
    
    class OlimpicaItem {
    + source 
    + item_type 
    + id 
    + name 
    + url 
    + parent_id 
    + parent_name 
    + has_children 
    + level 
    + category 
    + brand 
    + price 
    + old_price 
    + promotion 
    + image_url 
    + sku 
    + description 
    + breadcrumbs 
    + raw_data 

    }

    class OlimpicaProductPipeline {
     + dict  spider
     + open_spider(spider)
     + process_item()
     + close_spider() 
    }



    OlimpicaSpider *-- OlimpicaProductPipeline 
    OlimpicaProductPipeline *-- Parser
    OlimpicaSpider *-- Parser : 1
    Parser --> OlimpicaItem : create
```
# Referencias

- [Curso básico de Web Scraping](https://github.com/GEJ1/web_scraping_freecodecamp.git)
- [Web Scraping Nivel Medio](https://www.youtube.com/watch?v=mBoX_JCKZTE)
- [Olimpica: Pagina a scrapear](https://www.olimpica.com/)
