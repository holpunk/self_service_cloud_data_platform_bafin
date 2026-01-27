variable "product_name" {
  description = "Name of the data product (e.g., 'customer_360')"
  type        = string
}

variable "environment" {
  type = string
}

variable "kms_key_arn" {
  description = "ARN of the KMS key for encryption"
  type        = string
}
