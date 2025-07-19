variable "cluster_name" {
  description = "MSK cluster name"
  type        = string
}

variable "kafka_version" {
  description = "Kafka version"
  type        = string
  default     = "3.4.0"
}

variable "number_of_broker_nodes" {
  description = "Number of broker nodes"
  type        = number
  default     = 2
}

variable "instance_type" {
  description = "Broker instance type"
  type        = string
  default     = "kafka.t3.small"
}

variable "subnet_ids" {
  description = "Subnets for brokers"
  type        = list(string)
}

variable "security_group_ids" {
  description = "Security groups"
  type        = list(string)
}

variable "kms_key_arn" {
  description = "KMS key arn for encryption at rest"
  type        = string
}
