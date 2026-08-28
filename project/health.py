import logging

from django.conf import settings
from django.db import connection
from django.http import JsonResponse
import redis

logger = logging.getLogger(__name__)


def health_check(request):
    try:
        connection.ensure_connection()
        redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            socket_connect_timeout=3,
        ).ping()
    except Exception:
        logger.exception("Health check failed")
        return JsonResponse({"status": "error"}, status=503)
    return JsonResponse({"status": "ok"})
