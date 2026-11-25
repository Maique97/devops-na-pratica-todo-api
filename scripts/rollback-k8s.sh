#!/usr/bin/env bash
# Rollback manual para a revisão anterior (ou uma revisão específica).
# Uso: scripts/rollback-k8s.sh [revisão]
set -euo pipefail
NAMESPACE="todo-api"
if [ -n "${1:-}" ]; then
  kubectl -n "$NAMESPACE" rollout undo deployment/todo-api --to-revision="$1"
else
  kubectl -n "$NAMESPACE" rollout undo deployment/todo-api
fi
kubectl -n "$NAMESPACE" rollout status deployment/todo-api --timeout=180s
kubectl -n "$NAMESPACE" rollout history deployment/todo-api
