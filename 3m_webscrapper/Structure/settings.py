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
