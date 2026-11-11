variable "aws_region" {
  description = "Região AWS onde a infraestrutura será criada."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Nome do projeto (prefixo dos recursos)."
  type        = string
  default     = "todo-api"
}

variable "environment" {
  description = "Ambiente de implantação (dev, staging, prod)."
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment deve ser dev, staging ou prod."
  }
}

variable "vpc_cidr" {
  description = "Bloco CIDR da VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDRs das sub-redes públicas (uma por zona de disponibilidade)."
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "instance_type" {
  description = "Tipo da instância EC2 (t3.micro é elegível ao free tier)."
  type        = string
  default     = "t3.micro"
}

variable "container_image" {
  description = "Imagem Docker publicada pelo pipeline de CI no GitHub Container Registry."
  type        = string
  default     = "ghcr.io/maique97/devops-na-pratica-todo-api:latest"
}

variable "ssh_allowed_cidr" {
  description = "CIDR autorizado a acessar a porta 22. Vazio = SSH desabilitado (use SSM)."
  type        = string
  default     = ""
}
