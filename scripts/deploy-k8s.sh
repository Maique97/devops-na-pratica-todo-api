#!/usr/bin/env bash
# Deploy no Kubernetes (rolling update) com verificação e rollback automático.
# Uso: scripts/deploy-k8s.sh ghcr.io/maique97/devops-na-pratica-todo-api:<tag> [ambiente]
set -euo pipefail

IMAGE="${1:?Informe a imagem com a tag a implantar}"
ENVIRONMENT="${2:-staging}"
NAMESPACE="todo-api"
TIMEOUT="${ROLLOUT_TIMEOUT:-180s}"
cd "$(dirname "$0")/.."

echo ">> Aplicando manifests (k8s/) no ambiente ${ENVIRONMENT}"
kubectl apply -k k8s/
kubectl -n "$NAMESPACE" patch configmap todo-api-config \
  --type merge -p "{\"data\":{\"APP_ENV\":\"${ENVIRONMENT}\"}}"

echo ">> Atualizando imagem para ${IMAGE}"
kubectl -n "$NAMESPACE" set image deployment/todo-api todo-api="$IMAGE"
kubectl -n "$NAMESPACE" annotate deployment/todo-api \
  kubernetes.io/change-cause="deploy ${IMAGE}" --overwrite

if ! kubectl -n "$NAMESPACE" rollout status deployment/todo-api --timeout="$TIMEOUT"; then
  echo "!! Rollout falhou, executando rollback" >&2
  kubectl -n "$NAMESPACE" rollout undo deployment/todo-api
  kubectl -n "$NAMESPACE" rollout status deployment/todo-api --timeout="$TIMEOUT"
  exit 1
fi

echo ">> Smoke test via port-forward"
kubectl -n "$NAMESPACE" port-forward svc/todo-api 8080:80 >/tmp/port-forward.log 2>&1 &
PF_PID=$!
trap 'kill $PF_PID 2>/dev/null || true' EXIT
sleep 3
if ! bash scripts/smoke-test.sh http://localhost:8080; then
  echo "!! Smoke test falhou, executando rollback" >&2
  kubectl -n "$NAMESPACE" rollout undo deployment/todo-api
  exit 1
fi

kubectl -n "$NAMESPACE" get deploy,pods,svc -o wide
kubectl -n "$NAMESPACE" rollout history deployment/todo-api
echo ">> Deploy concluído: ${IMAGE}"
