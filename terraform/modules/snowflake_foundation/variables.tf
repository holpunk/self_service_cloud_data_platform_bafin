variable "vpc_cidr" {
  description = "The CIDR block of the AWS VPC to allowlist"
  type        = string
}

variable "environment" {
  type = string
}
