# GLOBAL

variable "region" {
  description = "The AWS region to put all resources in."
  default     = "eu-west-2"
}

variable "SITE_URL" {
  description = "Your main site URL. E.g. 'https://mysite.com'"
}

variable "SITE_NAME" {
  description = "Your main site name. E.g. 'myfinances'. This is useful for multiple environments"
  default     = "myfinances"
}

locals {
  app_tags = {
    app = var.SITE_NAME
  }
}

# NETWORK

variable "vpc_cidr" {
  description = "IPv4 CIDR for main vpc"
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR Block for Public Subnet"
  default     = "10.0.1.0/24"
}

variable "public_subnet_az" {
  description = "Availability Zone for Public Subnet"
  default     = "eu-west-2a"
}

variable "private_subnet_cidr" {
  description = "CIDR Block for Private Subnet"
  default     = "10.0.2.0/24"
}

variable "private_subnet_az" {
  description = "Availability Zone for Private Subnet"
  default     = "eu-west-2a"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["eu-west-2a", "eu-west-2b", "eu-west-2c"]
}

# Step functions

variable "sfn_machine_name" {
  description = "Name for main step function"
  default     = "myfinances-invoicing-scheduler-fn"
}

# API Destination

variable "api_destination-api_key" {
  description = "Your django API key. Generate with 'py manage.py generate_aws_scheduler_apikey'"
}