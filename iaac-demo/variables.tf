# Arquivo com a definição das variáveis. O arquivo poderia ter qualquer outro nome, ex. valores.tf

variable "regiao" {
  description = "Região da AWS para provisionamento"
  type        = string
  default     = "us-east-1"
}

variable "profile" {
  description = "Profile com as credenciais criadas no IAM"
  type = string
}

variable "tag-base" {
  description = "Nome utilizado para nomenclaruras no projeto"
  type        = string
  default     = "projeto"
}


variable "ec2-ami" {
  description = "AMI base"
  type        = string
  default     = "ami-0c4f7023847b90238" # Canonical, Ubuntu, 20.04 LTS
}

variable "ec2-tipo-instancia" {
  description = "Tipo da instância do EC2"
  type        = string
  default     = "t2.micro" # 2 vCPU, 1 GB
}

variable "ec2-chave-instancia" {
  description = "Nome da chave para acesso SSH"
  type        = string
  default     = "automacao.pem"
}

variable "ec2-tamanho-ebs" {
  description = "Tamanho do disco"
  type        = number
  default     = 8
}

variable "use-nat-gateway" {
  description = "Se deve usar ou não NAT Gateway"
  type        = bool
  default     = false
}