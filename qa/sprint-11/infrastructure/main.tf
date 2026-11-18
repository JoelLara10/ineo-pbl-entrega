terraform {
  required_version = ">= 1.7, < 2.0"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.6"
    }
  }
}
provider "docker" {}
variable "environment_name" {
  type = string
  validation {
    condition     = can(regex("^ineo-test-s11-qa-[ab]$", var.environment_name))
    error_message = "Solo se permiten los ambientes QA exclusivos del Sprint 11."
  }
}
variable "mongo_port" {
  type = number
  validation {
    condition     = contains([27111, 27112], var.mongo_port)
    error_message = "Use 27111 o 27112; nunca un puerto de producción."
  }
}
module "test_database" {
  source = "../../../infra/terraform/modules/test_database"
  name   = var.environment_name
  port   = var.mongo_port
}
output "mongo_uri" { value = module.test_database.uri }
