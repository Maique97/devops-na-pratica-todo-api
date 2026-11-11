"""Aplicação Flask: API de gerenciamento de tarefas (To-Do API)."""
from flask import Flask

from .routes import bp
from .storage import TaskStore


def create_app(config: dict | None = None) -> Flask:
    """Factory da aplicação. Permite injetar configuração nos testes."""
    app = Flask(__name__)
    app.config.update(APP_VERSION="1.0.0")
    if config:
        app.config.update(config)
    app.extensions["task_store"] = TaskStore()
    app.register_blueprint(bp)
    return app
