variable "identifier" {
  description = "DB instance identifier"
  type        = string
}

variable "engine_version" {
  description = "Postgres engine version"
  type        = string
  default     = "15"
}

variable "instance_class" {
  description = "DB instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "allocated_storage" {
  description = "Storage in GB"
  type        = number
  default     = 20
}

variable "username" {
  description = "Master username"
  type        = string
}

variable "password" {
  description = "Master password"
  type        = string
  sensitive   = true
}

variable "subnet_group_name" {
  description = "DB subnet group name"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet ids"
  type        = list(string)
}

variable "security_group_ids" {
  description = "List of security group ids"
  type        = list(string)
}

variable "skip_final_snapshot" {
  description = "Skip final snapshot on destroy"
  type        = bool
  default     = true
}
