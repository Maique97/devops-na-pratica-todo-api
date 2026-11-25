"""Aplicação Flask: API de gerenciamento de tarefas (To-Do API)."""
import os

from flask import Flask

from .observability import init_observability
from .routes import bp
from .storage import TaskStore


def create_app(config: dict | None = None) -> Flask:
    """Factory da aplicação. A configuração vem de variáveis de ambiente
    (12-factor) e pode ser sobrescrita nos testes."""
    app = Flask(__name__)
    app.config.update(
        APP_VERSION=os.getenv("APP_VERSION", "2.0.0"),
        APP_ENV=os.getenv("APP_ENV", "development"),
        LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
    )
    if config:
        app.config.update(config)
    app.extensions["task_store"] = TaskStore()
    app.register_blueprint(bp)
    init_observability(app)
    return app
