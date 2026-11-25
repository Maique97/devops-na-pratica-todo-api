#!/usr/bin/env bash
# Deploy com Docker Compose (servidor único) com rollback automático.
# Uso: scripts/deploy-compose.sh ghcr.io/maique97/devops-na-pratica-todo-api:<tag> [ambiente]
set -euo pipefail

IMAGE="${1:?Informe a imagem, ex.: ghcr.io/maique97/devops-na-pratica-todo-api:latest}"
ENVIRONMENT="${2:-staging}"
API_PORT="${API_PORT:-8080}"
STATE_FILE=".deployed_image"
cd "$(dirname "$0")/.."

PREVIOUS=""
[ -f "$STATE_FILE" ] && PREVIOUS="$(cat "$STATE_FILE")"

deploy() {
  echo ">> Implantando $1 no ambiente ${ENVIRONMENT}"
  IMAGE="$1" APP_ENV="$ENVIRONMENT" API_PORT="$API_PORT" docker compose pull api
  IMAGE="$1" APP_ENV="$ENVIRONMENT" API_PORT="$API_PORT" docker compose up -d --no-build
}

deploy "$IMAGE"
if bash scripts/smoke-test.sh "http://localhost:${API_PORT}"; then
  echo "$IMAGE" > "$STATE_FILE"
  echo ">> Deploy concluído: $IMAGE"
else
  echo "!! Smoke test falhou." >&2
  if [ -n "$PREVIOUS" ]; then
    echo ">> Rollback para $PREVIOUS" >&2
    deploy "$PREVIOUS"
    bash scripts/smoke-test.sh "http://localhost:${API_PORT}"
  fi
  exit 1
fi
