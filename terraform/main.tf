provider "aws" {
  region = "eu-central-1"
}

provider "snowflake" {
  # Configuration parameters usually expected here (account, user, etc.)
  # For now assuming env vars or default profile
}

module "aws_foundation" {
  source      = "./modules/aws_foundation"
  environment = "prod" # Defaulting to prod for foundation, or could be var
  vpc_cidr    = "10.0.0.0/16"
}

module "data_product" {
  source   = "./modules/data_product"
  for_each = var.products

  product_name = each.value.name
  environment  = each.value.environment
  kms_key_arn  = each.value.kms_key_arn
}
