output "vpc_id" {
  description = "ID da VPC criada."
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "IDs das sub-redes públicas."
  value       = aws_subnet.public[*].id
}

output "instance_id" {
  description = "ID da instância EC2 da aplicação."
  value       = aws_instance.app.id
}

output "app_url" {
  description = "URL pública da API."
  value       = "http://${aws_instance.app.public_dns}"
}
