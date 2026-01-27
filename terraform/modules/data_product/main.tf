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

# --- AWS S3 Bucket for Raw Data ---
resource "aws_s3_bucket" "product_bucket" {
  bucket = "bafin-dp-${var.product_name}-${var.environment}"

  tags = {
    Name           = "bafin-dp-${var.product_name}-${var.environment}"
    Product        = var.product_name
    Classification = "Confidential"
  }
}

# Enforce Server-Side Encryption with CMK
resource "aws_s3_bucket_server_side_encryption_configuration" "bucket_encryption" {
  bucket = aws_s3_bucket.product_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = var.kms_key_arn
      sse_algorithm     = "aws:kms"
    }
  }
}

# Enable Versioning for Audit/Recovery
resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.product_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Block Public Access (Explicitly)
resource "aws_s3_bucket_public_access_block" "block_public" {
  bucket = aws_s3_bucket.product_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# --- Snowflake Database for Structured Data ---
resource "snowflake_database" "product_db" {
  name    = "${upper(var.product_name)}_DB_${upper(var.environment)}"
  comment = "Database for ${var.product_name}"
}

resource "snowflake_schema" "raw" {
  database = snowflake_database.product_db.name
  name     = "RAW"
  comment  = "Raw data ingestion schema"
}

resource "snowflake_schema" "curated" {
  database = snowflake_database.product_db.name
  name     = "CURATED"
  comment  = "Cleaned and modeled data"
}

# Access Roles specific to this product
resource "snowflake_role" "product_read" {
  name    = "${upper(var.product_name)}_READ_${upper(var.environment)}"
  comment = "Read access to ${var.product_name}"
}

resource "snowflake_role" "product_write" {
  name    = "${upper(var.product_name)}_WRITE_${upper(var.environment)}"
  comment = "Write access to ${var.product_name}"
}

# Grants (Simplified)
resource "snowflake_grant_privileges_to_account_role" "read_db" {
  privileges        = ["USAGE"]
  account_role_name = snowflake_role.product_read.name
  on_account_object {
    object_type = "DATABASE"
    object_name = snowflake_database.product_db.name
  }
}
