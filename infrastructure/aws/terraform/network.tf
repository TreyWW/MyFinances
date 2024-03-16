# Main VPC
resource "aws_vpc" "main-vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags                 = {
    "Name" = "main vpc"
  }
}

# Public Subnets

resource "aws_subnet" "public-subnet" {
  vpc_id                  = aws_vpc.main-vpc.id
  cidr_block              = var.public_subnet_cidr
  availability_zone       = var.public_subnet_az
  map_public_ip_on_launch = true

  tags = {
    "Name" = "main_subnet"
  }
}

#resource "aws_subnet" "public-subnet-2" {
#  vpc_id = aws_vpc.main-vpc.id
#  cidr_block = var.public_subnet_cidr
#  availability_zone = var.availability_zones[1]
#}

# Private Subnets

resource "aws_subnet" "private-subnet" {
  vpc_id            = aws_vpc.main-vpc.id
  cidr_block        = var.private_subnet_cidr
  availability_zone = var.private_subnet_az
  tags              = {
    "Name" = "private-subnet"
  }
}

#resource "aws_subnet" "private-subnet-2" {
#  vpc_id = aws_vpc.main-vpc.id
#  cidr_block = var.private_subnet_cidr
#  availability_zone = var.availability_zones[1]
#}

## Route Tables (coming soon)