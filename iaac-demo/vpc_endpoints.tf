resource "aws_ec2_instance_connect_endpoint" "ec2_conn" {
  subnet_id = module.network.private_subnets[0].id

  security_group_ids = [
    module.security.sg-eice.id
  ]

  tags = {
    Name = "${var.tag-base}-ec2-conn-endpoint"
  }
}