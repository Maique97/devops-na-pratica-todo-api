# To-Do API — DevOps na Prática (Fase 1)

[![CI](https://github.com/Maique97/devops-na-pratica-todo-api/actions/workflows/ci.yml/badge.svg)](https://github.com/Maique97/devops-na-pratica-todo-api/actions/workflows/ci.yml)
[![CD](https://github.com/Maique97/devops-na-pratica-todo-api/actions/workflows/cd.yml/badge.svg)](https://github.com/Maique97/devops-na-pratica-todo-api/actions/workflows/cd.yml)

Projeto da disciplina **DevOps na Prática** (PUCRS Online).
Fase 1: *Configuração e Automação Inicial* · Fase 2: *Entrega Contínua, Monitoramento e Segurança*.
API REST simples de gerenciamento de tarefas, usada como base para praticar Integração Contínua (GitHub Actions),
conteinerização (Docker) e Infraestrutura como Código (Terraform na AWS).

## Estrutura

```
app/                      # código da API (Flask) + métricas e logs JSON
tests/                    # testes automatizados (pytest)
Dockerfile                # imagem multi-stage, usuário não-root
docker-compose.yml        # API + Prometheus + Grafana
k8s/                      # manifests Kubernetes (Deployment, Service, HPA...)
scripts/                  # deploy (Compose, Kubernetes, EC2), rollback e smoke test
monitoring/               # Prometheus, alertas e dashboard do Grafana
.github/workflows/ci.yml  # pipeline de CI (lint, segurança, testes, build, scan)
.github/workflows/cd.yml  # pipeline de CD (staging no Kubernetes + produção)
infra/terraform/          # scripts de IaC (VPC, sub-redes, SG, IAM, EC2)
```

## Endpoints

| Método | Rota            | Descrição                 |
|--------|-----------------|---------------------------|
| GET    | `/health`       | Liveness (versão/ambiente)|
| GET    | `/ready`        | Readiness                 |
| GET    | `/metrics`      | Métricas Prometheus       |
| GET    | `/tasks`        | Lista tarefas             |
| POST   | `/tasks`        | Cria tarefa `{"title"}`   |
| GET    | `/tasks/{id}`   | Consulta tarefa           |
| PUT    | `/tasks/{id}`   | Atualiza `title`/`done`   |
| DELETE | `/tasks/{id}`   | Remove tarefa             |

## Executando localmente

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
flake8 .          # lint
pytest            # testes + cobertura (mínimo 80%)
python wsgi.py    # http://localhost:5000/health
```

Com Docker Compose (API em :8080, Prometheus em :9090, Grafana em :3000):

```bash
docker compose up -d --build
bash scripts/smoke-test.sh http://localhost:8080
```

## Pipeline de CI (GitHub Actions)

Disparado em `push` e `pull_request` para `main` (e manualmente):

1. **Lint e testes** — flake8 + pytest com cobertura mínima de 80%; relatório `coverage.xml` publicado como artefato.
2. **Validação do Terraform** — `terraform fmt -check`, `init -backend=false` e `validate`.
3. **Segurança** — Bandit (SAST), pip-audit (dependências) e Trivy (imagem).
4. **Scripts e manifests** — ShellCheck, `docker compose config` e `kubectl kustomize`.
5. **Docker** — build, scan, *smoke test* e, em `push` na `main`, publicação no `ghcr.io`.

## Pipeline de CD (GitHub Actions)

Disparado automaticamente quando o CI termina com sucesso na `main`:

1. **Staging** — cria um cluster Kubernetes (Kind), implanta a imagem do commit com
   `scripts/deploy-k8s.sh` (rolling update, rollback automático) e roda o smoke test.
2. **Produção** — ambiente protegido por aprovação manual; promove a imagem para a tag
   `production` e, se as variáveis `AWS_ROLE_ARN` e `EC2_INSTANCE_ID` estiverem configuradas,
   implanta na EC2 via SSM (`scripts/deploy-ec2.sh`).

## Scripts de deploy

| Script | Uso |
|--------|-----|
| `scripts/deploy-compose.sh <imagem> [ambiente]` | Deploy com Docker Compose e rollback automático |
| `scripts/deploy-k8s.sh <imagem> [ambiente]` | Deploy no Kubernetes com verificação e rollback |
| `scripts/rollback-k8s.sh [revisão]` | Rollback manual no Kubernetes |
| `scripts/deploy-ec2.sh <instance-id> <imagem>` | Deploy na EC2 (Terraform) via AWS SSM |
| `scripts/smoke-test.sh <url>` | Validação pós-deploy |

## Infraestrutura como Código (Terraform)

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars   # ajuste a imagem e a região
terraform init
terraform plan
terraform apply
terraform output app_url
terraform destroy   # remove tudo ao final
```

Recursos provisionados: VPC, 2 sub-redes públicas em AZs distintas, Internet Gateway, tabela de rotas,
Security Group (HTTP 80; SSH opcional e restrito), IAM Role com SSM e instância EC2 (Amazon Linux 2023, t3.micro)
que instala o Docker e executa a imagem publicada pelo pipeline.
