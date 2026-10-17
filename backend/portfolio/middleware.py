import logging
import time

logger = logging.getLogger(__name__)


class ResponseTimeMiddleware:
    def __init__(self, get_response): self.get_response = get_response
    def __call__(self, request):
        start = time.perf_counter(); response = self.get_response(request)
        elapsed = round((time.perf_counter() - start) * 1000)
        response["X-Response-Time"] = f"{elapsed}ms"
        logger.info("%s %s -> %s (%sms)", request.method, request.path, response.status_code, elapsed)
        return response
