terraform {
  required_version = ">= 1.6.0, < 2.0.0"
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "4.2.0"
    }
  }
}

provider "docker" {}

variable "run_id" {
  type = string
  validation {
    condition     = can(regex("^s10-[a-z0-9-]{1,32}$", var.run_id))
    error_message = "Only disposable sprint 10 resource names are accepted."
  }
}

resource "docker_image" "mongo" {
  name         = "mongo:7.0.16"
  keep_locally = true
}

resource "docker_container" "mongo" {
  name  = "ineo-${var.run_id}-mongo"
  image = docker_image.mongo.image_id
  labels {
    label = "ineo.qa.run"
    value = var.run_id
  }
  ports {
    internal = 27017
    external = 0
    ip       = "127.0.0.1"
  }
}

output "mongo_port" {
  value = docker_container.mongo.ports[0].external
}

