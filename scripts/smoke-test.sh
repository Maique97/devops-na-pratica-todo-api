#!/usr/bin/env bash
# Smoke test pós-deploy: valida os endpoints essenciais da API.
# Uso: scripts/smoke-test.sh http://localhost:8080
set -euo pipefail

BASE_URL="${1:-http://localhost:8080}"
RETRIES="${RETRIES:-20}"

echo ">> Aguardando ${BASE_URL}/health ..."
for i in $(seq 1 "$RETRIES"); do
  if curl -fsS "${BASE_URL}/health" >/dev/null 2>&1; then
    break
  fi
  if [ "$i" -eq "$RETRIES" ]; then
    echo "!! API não respondeu após ${RETRIES} tentativas" >&2
    exit 1
  fi
  sleep 3
done

check() {
  local desc="$1" expected="$2"; shift 2
  local code
  code=$(curl -s -o /tmp/smoke_body -w '%{http_code}' "$@")
  if [ "$code" != "$expected" ]; then
    echo "!! FALHOU: ${desc} (esperado ${expected}, recebido ${code})" >&2
    cat /tmp/smoke_body >&2 || true
    exit 1
  fi
  echo "OK  ${desc} -> ${code}"
}

check "GET /health" 200 "${BASE_URL}/health"
check "GET /ready" 200 "${BASE_URL}/ready"
check "POST /tasks" 201 -X POST -H 'Content-Type: application/json' \
  -d '{"title":"smoke test"}' "${BASE_URL}/tasks"
check "GET /tasks" 200 "${BASE_URL}/tasks"
check "POST /tasks inválido" 400 -X POST -H 'Content-Type: application/json' \
  -d '{}' "${BASE_URL}/tasks"
check "GET /metrics" 200 "${BASE_URL}/metrics"
grep -q "http_requests_total" /tmp/smoke_body

echo ">> Smoke test concluído com sucesso."
