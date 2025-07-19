variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "Name of the S3 bucket"
  type        = string
}

variable "db_identifier" {
  description = "Identifier for RDS instance"
  type        = string
}

variable "db_username" {
  description = "RDS master username"
  type        = string
}

variable "db_password" {
  description = "RDS master password"
  type        = string
  sensitive   = true
}

variable "db_subnet_group_name" {
  description = "Subnet group name for RDS"
  type        = string
}

variable "subnet_ids" {
  description = "Common subnet IDs"
  type        = list(string)
}

variable "security_group_ids" {
  description = "Common security group IDs"
  type        = list(string)
}

variable "mq_cluster_name" {
  description = "Kafka cluster name"
  type        = string
}

variable "kms_key_arn" {
  description = "KMS key ARN for encryption"
  type        = string
}

variable "ecs_cluster_name" {
  description = "ECS cluster name"
  type        = string
}
