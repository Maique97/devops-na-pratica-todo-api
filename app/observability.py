"""Observabilidade: logs estruturados em JSON e métricas no formato Prometheus."""
import json
import logging
import sys
import time
import uuid
from datetime import datetime, timezone

from flask import Flask, Response, g, request
from prometheus_client import (CONTENT_TYPE_LATEST, CollectorRegistry, Counter, Gauge,
                               Histogram, generate_latest)


class JsonFormatter(logging.Formatter):
    """Formata cada registro de log como uma linha JSON (fácil de indexar no Loki/ELK)."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        payload.update(getattr(record, "extra_fields", {}))
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("todo_api")
    logger.setLevel(level.upper())
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    logger.propagate = False
    return logger


def init_observability(app: Flask) -> None:
    """Registra métricas, logs de acesso e o endpoint /metrics na aplicação."""
    registry = CollectorRegistry()
    requests_total = Counter(
        "http_requests_total", "Total de requisições HTTP",
        ["method", "endpoint", "status"], registry=registry)
    latency = Histogram(
        "http_request_duration_seconds", "Latência das requisições HTTP",
        ["method", "endpoint"], registry=registry,
        buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5))
    tasks_gauge = Gauge("todo_tasks", "Quantidade de tarefas cadastradas", registry=registry)
    info = Gauge("app_info", "Informações da aplicação", ["version", "environment"],
                 registry=registry)
    info.labels(app.config["APP_VERSION"], app.config["APP_ENV"]).set(1)

    logger = configure_logging(app.config.get("LOG_LEVEL", "INFO"))
    app.extensions["metrics_registry"] = registry
    app.extensions["logger"] = logger

    @app.before_request
    def _start_timer():
        g.start_time = time.perf_counter()
        g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

    @app.after_request
    def _record(response):
        endpoint = request.url_rule.rule if request.url_rule else "not_found"
        if endpoint == "/metrics":
            return response
        elapsed = time.perf_counter() - g.get("start_time", time.perf_counter())
        requests_total.labels(request.method, endpoint, response.status_code).inc()
        latency.labels(request.method, endpoint).observe(elapsed)
        tasks_gauge.set(len(app.extensions["task_store"].list()))
        response.headers["X-Request-ID"] = g.get("request_id", "")
        logger.info("request", extra={"extra_fields": {
            "request_id": g.get("request_id"),
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration_ms": round(elapsed * 1000, 2),
        }})
        return response

    @app.get("/metrics")
    def metrics():
        return Response(generate_latest(registry), mimetype=CONTENT_TYPE_LATEST)
