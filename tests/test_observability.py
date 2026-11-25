"""Testes de observabilidade: métricas Prometheus, readiness e logs estruturados."""
import json
import logging

from app import create_app
from app.observability import JsonFormatter


def test_ready(client):
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ready"


def test_health_reports_environment():
    app = create_app({"TESTING": True, "APP_ENV": "staging"})
    body = app.test_client().get("/health").get_json()
    assert body["environment"] == "staging"


def test_metrics_endpoint_exposes_counters(client):
    client.post("/tasks", json={"title": "Observar"})
    client.get("/tasks")
    r = client.get("/metrics")
    assert r.status_code == 200
    text = r.get_data(as_text=True)
    assert 'http_requests_total{endpoint="/tasks",method="POST",status="201"} 1.0' in text
    assert "http_request_duration_seconds_bucket" in text
    assert "todo_tasks 1.0" in text
    assert "app_info{" in text


def test_metrics_count_not_found(client):
    client.get("/nao-existe")
    text = client.get("/metrics").get_data(as_text=True)
    assert 'endpoint="not_found"' in text


def test_request_id_header_propagated(client):
    r = client.get("/health", headers={"X-Request-ID": "abc-123"})
    assert r.headers["X-Request-ID"] == "abc-123"
    assert client.get("/health").headers["X-Request-ID"]


def test_json_formatter_outputs_valid_json():
    record = logging.LogRecord("todo_api", logging.INFO, __file__, 1, "ola", None, None)
    record.extra_fields = {"status": 200}
    data = json.loads(JsonFormatter().format(record))
    assert data["message"] == "ola"
    assert data["status"] == 200
    assert data["level"] == "INFO"


def test_json_formatter_includes_exception():
    try:
        raise ValueError("falhou")
    except ValueError:
        import sys
        record = logging.LogRecord("todo_api", logging.ERROR, __file__, 1, "erro", None,
                                   sys.exc_info())
    data = json.loads(JsonFormatter().format(record))
    assert "ValueError" in data["exception"]
