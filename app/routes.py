"""Endpoints HTTP da API."""
from flask import Blueprint, current_app, jsonify, request

bp = Blueprint("api", __name__)


def _store():
    return current_app.extensions["task_store"]


def _error(message: str, status: int):
    return jsonify({"error": message}), status


@bp.get("/health")
def health():
    return jsonify(status="ok", version=current_app.config["APP_VERSION"])


@bp.get("/tasks")
def list_tasks():
    return jsonify([t.to_dict() for t in _store().list()])


@bp.post("/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        return _error("O campo 'title' é obrigatório.", 400)
    if len(title) > 200:
        return _error("O campo 'title' deve ter no máximo 200 caracteres.", 400)
    task = _store().create(title.strip())
    return jsonify(task.to_dict()), 201


@bp.get("/tasks/<int:task_id>")
def get_task(task_id: int):
    task = _store().get(task_id)
    if task is None:
        return _error("Tarefa não encontrada.", 404)
    return jsonify(task.to_dict())


@bp.put("/tasks/<int:task_id>")
def update_task(task_id: int):
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    done = data.get("done")
    if title is not None and (not isinstance(title, str) or not title.strip()):
        return _error("O campo 'title' deve ser um texto não vazio.", 400)
    if done is not None and not isinstance(done, bool):
        return _error("O campo 'done' deve ser booleano.", 400)
    task = _store().update(task_id, title.strip() if title else None, done)
    if task is None:
        return _error("Tarefa não encontrada.", 404)
    return jsonify(task.to_dict())


@bp.delete("/tasks/<int:task_id>")
def delete_task(task_id: int):
    if not _store().delete(task_id):
        return _error("Tarefa não encontrada.", 404)
    return "", 204
