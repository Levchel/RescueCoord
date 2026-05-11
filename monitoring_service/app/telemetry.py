"""
Телеметрия и сбор метрик для Monitoring Service.

Предоставляет:
- StatsMiddleware — подсчёт запросов по HTTP-статусам
- record_startup() — фиксация времени запуска
- get_stats() — возврат сервисной статистики для /stats
- setup_opentelemetry() — инициализация OpenTelemetry трейсинга
"""

import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

SERVICE_NAME = "monitoring-service"
SERVICE_VERSION = "1.0.0"

_startup_time: datetime | None = None
_request_counts: dict[int, int] = defaultdict(int)


def record_startup() -> None:
    """Запоминает момент запуска сервиса (вызывается из lifespan)."""
    global _startup_time
    _startup_time = datetime.now(timezone.utc)


def get_stats() -> dict:
    """Возвращает сервисную статистику: версию, дату старта, счётчики запросов."""
    uptime = (
        (datetime.now(timezone.utc) - _startup_time).total_seconds()
        if _startup_time
        else None
    )
    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "startup_time": _startup_time.isoformat() if _startup_time else None,
        "uptime_seconds": uptime,
        "requests_by_status": dict(_request_counts),
        "total_requests": sum(_request_counts.values()),
    }


class StatsMiddleware(BaseHTTPMiddleware):
    """Middleware: засчитывает каждый обработанный запрос по коду ответа."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        _request_counts[response.status_code] += 1
        return response


def setup_opentelemetry(app: FastAPI, otlp_endpoint: str | None) -> None:
    """
    Инициализирует OpenTelemetry трейсинг и отправку span'ов на OTLP-коллектор.

    Если OTEL_ENDPOINT не задан или пакеты не установлены — пропускается без ошибки.
    """
    if not otlp_endpoint:
        logger.info("OTEL_ENDPOINT not configured, skipping OpenTelemetry setup")
        return
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create(
            {"service.name": SERVICE_NAME, "service.version": SERVICE_VERSION}
        )
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=f"{otlp_endpoint}/v1/traces")
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        FastAPIInstrumentor.instrument_app(app)
        logger.info("OpenTelemetry initialized, exporting traces to %s", otlp_endpoint)
    except ImportError:
        logger.warning("opentelemetry packages not installed, skipping instrumentation")
