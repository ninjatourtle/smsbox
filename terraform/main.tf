
provider "aws" {
  region = var.aws_region
}

module "s3" {
  source         = "./modules/s3-storage"
  bucket_name    = var.bucket_name
  force_destroy  = true
  lifecycle_days = 30
}

module "rds" {
  source              = "./modules/rds-postgres"
  identifier          = var.db_identifier
  username            = var.db_username
  password            = var.db_password
  subnet_group_name   = var.db_subnet_group_name
  subnet_ids          = var.subnet_ids
  security_group_ids  = var.security_group_ids
}

module "mq" {
  source              = "./modules/message-queue"
  cluster_name        = var.mq_cluster_name
  subnet_ids          = var.subnet_ids
  security_group_ids  = var.security_group_ids
  kms_key_arn         = var.kms_key_arn
}

module "ecs" {
  source       = "./modules/ecs"
  cluster_name = var.ecs_cluster_name
}

output "s3_bucket_name" {
  value = module.s3.bucket_name
}

output "db_endpoint" {
  value = module.rds.db_instance_endpoint
}

output "mq_bootstrap_brokers" {
  value = module.mq.bootstrap_brokers
}

output "ecs_cluster_arn" {
  value = module.ecs.cluster_arn
}
