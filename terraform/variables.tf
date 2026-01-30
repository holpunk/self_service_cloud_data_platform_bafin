variable "products" {
  description = "Map of product definitions"
  type = map(object({
    name        = string
    environment = string
    kms_key_arn = string
  }))
  default = {}
}
