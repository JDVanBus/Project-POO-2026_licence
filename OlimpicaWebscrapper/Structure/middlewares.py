import random
import logging


class OlimpicaMiddleware:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
        self.logger = logging.getLogger(__name__)
        self.max_retries = 3

    def process_request(self, request, spider):
        random_ua = random.choice(self.user_agents)
        request.headers["User-Agent"] = random_ua

        spider.logger.info(f"Middleware aplicando User-Agent: {random_ua[:40]}...")

        return None

    def process_response(self, request, response, spider):
        if response.status in [403, 429]:
            retry_count = request.meta.get("retry_count", 0)
            if retry_count < self.max_retries:
                self.logger.warning(
                    f"¡Bloqueo detectado ({response.status}) en {request.url}. Reintentando ({retry_count + 1}/{self.max_retries})"
                )
                new_ua = random.choice(self.user_agents)
                return request.replace(
                    headers={"User-Agent": new_ua},
                    meta={**request.meta, "retry_count": retry_count + 1},
                )
            else:
                self.logger.error(f"Máximo de reintentos alcanzado para {request.url}")
        return response

    def process_exception(self, request, exception, spider):
        self.logger.error(f"Fallo de conexión en {request.url}: {exception}")
        return None
