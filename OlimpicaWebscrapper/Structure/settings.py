# Scrapy settings for OlimpicaWebscrapper project

BOT_NAME = "OlimpicaWebscrapper"

SPIDER_MODULES = ["OlimpicaWebscrapper.OlimpicaWebscrapper.spiders"]
NEWSPIDER_MODULE = "OlimpicaWebscrapper.OlimpicaWebscrapper.spiders"

# Obedece robots.txt
ROBOTSTXT_OBEY = False

# Configurar delays entre requests
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True

# User-Agent (será sobrescrito por middleware)
USER_AGENT = "OlimpicaWebscrapper (+http://www.you-website.com)"

# # Habilitar middleware
# DOWNLOADER_MIDDLEWARES = {
#     'OlimpicaWebscrapper.middlewares.OlimpicawebscrapperDownloaderMiddleware': 543,
# }

# Habilitar pipelines
ITEM_PIPELINES = {
    "OlimpicaWebscrapper.OlimpicaWebscrapper.pipelines.OlimpicaProductPipeline": 300,
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
