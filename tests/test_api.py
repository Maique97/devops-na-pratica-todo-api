"""Testes automatizados da To-Do API (executados no pipeline de CI)."""


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_list_starts_empty(client):
    r = client.get("/tasks")
    assert r.status_code == 200
    assert r.get_json() == []


def test_create_task(client):
    r = client.post("/tasks", json={"title": "Configurar pipeline"})
    assert r.status_code == 201
    body = r.get_json()
    assert body["id"] == 1
    assert body["title"] == "Configurar pipeline"
    assert body["done"] is False


def test_create_task_trims_title(client):
    r = client.post("/tasks", json={"title": "  Terraform  "})
    assert r.get_json()["title"] == "Terraform"


def test_create_task_requires_title(client):
    assert client.post("/tasks", json={}).status_code == 400
    assert client.post("/tasks", json={"title": "   "}).status_code == 400
    assert client.post("/tasks", data="nao-json").status_code == 400


def test_create_task_title_too_long(client):
    r = client.post("/tasks", json={"title": "x" * 201})
    assert r.status_code == 400


def test_get_task(client):
    client.post("/tasks", json={"title": "A"})
    r = client.get("/tasks/1")
    assert r.status_code == 200
    assert r.get_json()["title"] == "A"


def test_get_missing_task(client):
    assert client.get("/tasks/99").status_code == 404


def test_update_task(client):
    client.post("/tasks", json={"title": "A"})
    r = client.put("/tasks/1", json={"done": True, "title": "B"})
    assert r.status_code == 200
    body = r.get_json()
    assert body["done"] is True
    assert body["title"] == "B"


def test_update_task_validation(client):
    client.post("/tasks", json={"title": "A"})
    assert client.put("/tasks/1", json={"done": "sim"}).status_code == 400
    assert client.put("/tasks/1", json={"title": ""}).status_code == 400


def test_update_missing_task(client):
    assert client.put("/tasks/42", json={"done": True}).status_code == 404


def test_delete_task(client):
    client.post("/tasks", json={"title": "A"})
    assert client.delete("/tasks/1").status_code == 204
    assert client.get("/tasks/1").status_code == 404
    assert client.delete("/tasks/1").status_code == 404


def test_list_after_creates(client):
    for t in ("A", "B", "C"):
        client.post("/tasks", json={"title": t})
    titles = [t["title"] for t in client.get("/tasks").get_json()]
    assert titles == ["A", "B", "C"]
