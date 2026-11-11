# To-Do API — DevOps na Prática (Fase 1)

[![CI](https://github.com/Maique97/devops-na-pratica-todo-api/actions/workflows/ci.yml/badge.svg)](https://github.com/Maique97/devops-na-pratica-todo-api/actions/workflows/ci.yml)

Projeto da disciplina **DevOps na Prática** (PUCRS Online) — Fase 1: *Configuração e Automação Inicial*.
API REST simples de gerenciamento de tarefas, usada como base para praticar Integração Contínua (GitHub Actions),
conteinerização (Docker) e Infraestrutura como Código (Terraform na AWS).

## Estrutura

```
app/                      # código da API (Flask)
tests/                    # testes automatizados (pytest)
Dockerfile                # imagem de produção (gunicorn)
.github/workflows/ci.yml  # pipeline de CI
infra/terraform/          # scripts de IaC (VPC, sub-redes, SG, IAM, EC2)
```

## Endpoints

| Método | Rota            | Descrição                 |
|--------|-----------------|---------------------------|
| GET    | `/health`       | Health check              |
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

Com Docker:

```bash
docker build -t todo-api .
docker run -p 5000:5000 todo-api
```

## Pipeline de CI (GitHub Actions)

Disparado em `push` e `pull_request` para `main` (e manualmente):

1. **Lint e testes** — flake8 + pytest com cobertura mínima de 80%; relatório `coverage.xml` publicado como artefato.
2. **Validação do Terraform** — `terraform fmt -check`, `init -backend=false` e `validate`.
3. **Docker** — build da imagem, *smoke test* do container (`/health`) e, em `push` na `main`,
   publicação no GitHub Container Registry (`ghcr.io`).

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
