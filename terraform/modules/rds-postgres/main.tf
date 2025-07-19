resource "aws_db_subnet_group" "this" {
  name       = var.subnet_group_name
  subnet_ids = var.subnet_ids
}

resource "aws_db_instance" "this" {
  identifier               = var.identifier
  engine                   = "postgres"
  engine_version           = var.engine_version
  instance_class           = var.instance_class
  allocated_storage        = var.allocated_storage
  username                 = var.username
  password                 = var.password
  db_subnet_group_name     = aws_db_subnet_group.this.name
  vpc_security_group_ids   = var.security_group_ids
  storage_encrypted        = true
  skip_final_snapshot      = var.skip_final_snapshot
}
