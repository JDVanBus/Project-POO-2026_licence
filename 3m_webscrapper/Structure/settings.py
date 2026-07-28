# Scrapy settings for OlimpicaWebscrapper project

BOT_NAME = "3m_Webscrapper"

SPIDER_MODULES = ["3m_webscrapper.Structure.spiders"]
NEWSPIDER_MODULE = "3m_webscrapper.Structure.spiders"

# Obedece robots.txt
ROBOTSTXT_OBEY = False

# Configurar delays entre requests
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True


# # Habilitar middleware
DOWNLOADER_MIDDLEWARES = {
    "3m_webscrapper.Structure.middlewares.MMM_Middleware": 400,
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
}

# Habilitar pipelines
ITEM_PIPELINES = {
    "3m_webscrapper.Structure.pipelines.MMM_ProductPipeline": 300,
}

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"

# Memory usage limits
MEMDEBUG_ENABLED = False
TELNETCONSOLE_ENABLED = False

# Timeout
DOWNLOAD_TIMEOUT = 10

FEED_EXPORT_ENCODING = "utf-8"
# FEEDS = {
#     "items.json": {
#         "format": "json",
#         "encoding": "utf-8",
#         "indent": 2,
#         "overwrite": True,
#     }
# }

# Headers estandar
DEFAULT_REQUEST_HEADERS = {
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
}

# Paralelismo

CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 8
