variable "environment" {
  description = "Deployment environment (e.g., dev, prod)"
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name        = "bafin-platform-vpc-${var.environment}"
    Compliance  = "BaFin-High"
    Description = "Isolated VPC for Data Platform"
  }
}

# Compliance Requirement: No Public Internet Access for Data Processing
# We only create Private Subnets.
resource "aws_subnet" "private" {
  count             = 3
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone = element(["eu-central-1a", "eu-central-1b", "eu-central-1c"], count.index)

  tags = {
    Name = "private-subnet-${count.index + 1}-${var.environment}"
    Type = "Private"
  }
}

# VPC Endpoints for S3 (Gateway) to keep traffic within AWS network
resource "aws_vpc_endpoint" "s3" {
  vpc_id          = aws_vpc.main.id
  service_name    = "com.amazonaws.eu-central-1.s3"
  route_table_ids = [aws_route_table.private.id]
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "private-route-table-${var.environment}"
  }
}

resource "aws_route_table_association" "private" {
  count          = 3
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

# Security Group restricting all inbound traffic by default
resource "aws_security_group" "default_deny" {
  name        = "default-deny-sg"
  description = "Deny all inbound traffic by default"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [] # No inbound access
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"] # Allow outbound for updates/services if needed via NAT/Endpoints
  }
}

output "vpc_id" {
  value = aws_vpc.main.id
}

output "private_subnets" {
  value = aws_subnet.private[*].id
}
