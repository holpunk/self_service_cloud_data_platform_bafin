terraform {
  required_providers {
    snowflake = {
      source  = "Snowflake-Labs/snowflake"
      version = "~> 0.87"
    }
  }
}

# Network Policy: Restrict access to only the AWS VPC
# This ensures data cannot be accessed from public internet
resource "snowflake_network_policy" "vpc_only" {
  name    = "VPCONLY_${upper(var.environment)}"
  comment = "Restrict access to AWS VPC only for BaFin compliance"

  allowed_ip_list = [var.vpc_cidr]
}

resource "snowflake_account_parameter" "network_policy" {
  key   = "NETWORK_POLICY"
  value = snowflake_network_policy.vpc_only.name
}

# Functional Roles (RBAC)
# Base roles that all users will map to
resource "snowflake_role" "data_engineer" {
  name    = "DATA_ENGINEER_${upper(var.environment)}"
  comment = "Role for data engineering tasks"
}

resource "snowflake_role" "data_analyst" {
  name    = "DATA_ANALYST_${upper(var.environment)}"
  comment = "Role for data analysis (read-only mostly)"
}

resource "snowflake_role" "governance_officer" {
  name    = "GOVERNANCE_OFFICER_${upper(var.environment)}"
  comment = "Role for compliance and auditing"
}
