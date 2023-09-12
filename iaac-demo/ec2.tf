# Criando uma instância EC2
resource "aws_instance" "projeto" {
  count = length(module.network.private_subnets)
  ami = var.ec2-ami
  instance_type = "${var.ec2-tipo-instancia}"
  availability_zone = "${var.regiao}${module.network.zones[count.index]}"
  key_name = "${var.ec2-chave-instancia}"

  network_interface {
    device_index = 0 # ordem da interface 
    network_interface_id = aws_network_interface.nic-projeto-instance[count.index].id
  }

  # EBS root
  root_block_device {
    volume_size = var.ec2-tamanho-ebs
    volume_type = "gp2"
  }
  

  tags = {
      Name = "${var.tag-base}"
  }
}

# Criando Network Interface da instância
resource "aws_network_interface" "nic-projeto-instance" {
  count = length(module.network.private_subnets)
  subnet_id       = module.network.private_subnets[count.index].id
  private_ips     = ["10.0.${count.index + 1}.50"] # Redes privadas
  security_groups = [module.security.sg-web.id]
}
