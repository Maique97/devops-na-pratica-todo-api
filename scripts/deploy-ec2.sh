#!/usr/bin/env bash
# Deploy em produção na instância EC2 criada pelo Terraform, via AWS Systems Manager
# (sem SSH). Requer AWS CLI autenticada (no CI: OIDC com role da AWS).
# Uso: scripts/deploy-ec2.sh <instance-id> <imagem>
set -euo pipefail

INSTANCE_ID="${1:?Informe o ID da instância (terraform output instance_id)}"
IMAGE="${2:?Informe a imagem com a tag a implantar}"

read -r -d '' COMMANDS <<CMDS || true
set -e
docker pull ${IMAGE}
docker rm -f todo-api-new 2>/dev/null || true
docker run -d --name todo-api-new -p 8081:5000 -e APP_ENV=production ${IMAGE}
for i in \$(seq 1 20); do curl -fs http://localhost:8081/ready && break; sleep 3; done
curl -fs http://localhost:8081/ready
docker rm -f todo-api || true
docker rm -f todo-api-new
docker run -d --name todo-api --restart unless-stopped -p 80:5000 -e APP_ENV=production ${IMAGE}
CMDS

PARAMS=$(python3 -c 'import json,sys; print(json.dumps({"commands": sys.stdin.read().splitlines()}))' <<<"$COMMANDS")

CMD_ID=$(aws ssm send-command \
  --instance-ids "$INSTANCE_ID" \
  --document-name AWS-RunShellScript \
  --comment "deploy ${IMAGE}" \
  --parameters "$PARAMS" \
  --query Command.CommandId --output text)

echo ">> Comando SSM ${CMD_ID} enviado; aguardando..."
aws ssm wait command-executed --command-id "$CMD_ID" --instance-id "$INSTANCE_ID"
aws ssm get-command-invocation --command-id "$CMD_ID" --instance-id "$INSTANCE_ID" \
  --query '{Status:Status,Saida:StandardOutputContent}' --output table
