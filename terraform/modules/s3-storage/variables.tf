variable "bucket_name" {
  description = "The name of the S3 bucket"
  type        = string
}

variable "force_destroy" {
  description = "Delete objects with bucket"
  type        = bool
  default     = false
}

variable "lifecycle_days" {
  description = "Days before objects expire"
  type        = number
  default     = 30
}
