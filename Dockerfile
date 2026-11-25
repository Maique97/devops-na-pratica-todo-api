# ---------- Estágio 1: build das dependências ----------
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---------- Estágio 2: imagem final enxuta ----------
FROM python:3.12-slim

ARG APP_VERSION=dev
ARG VCS_REF=unknown
LABEL org.opencontainers.image.title="todo-api" \
      org.opencontainers.image.description="To-Do API - DevOps na Pratica" \
      org.opencontainers.image.source="https://github.com/Maique97/devops-na-pratica-todo-api" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_VERSION=${APP_VERSION} \
    APP_ENV=production \
    LOG_LEVEL=INFO \
    PORT=5000

WORKDIR /app
COPY --from=builder /install /usr/local
COPY app ./app
COPY wsgi.py .

RUN useradd --create-home --uid 10001 appuser
USER 10001

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:5000/health')"
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT} --workers 2 wsgi:app"]
