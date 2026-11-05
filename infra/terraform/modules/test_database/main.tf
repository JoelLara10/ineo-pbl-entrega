terraform {
  required_providers {
    docker = {
      source = "kreuzwerker/docker"
    }
  }
}

variable "name" { type = string }
variable "port" { type = number }

resource "docker_image" "mongo" {
  name         = "mongo:7.0.16"
  keep_locally = true
}

resource "docker_volume" "synthetic" {
  name = "${var.name}-synthetic"
}

resource "docker_container" "mongo" {
  name  = var.name
  image = docker_image.mongo.image_id
  ports {
    internal = 27017
    external = var.port
    ip       = "127.0.0.1"
  }
  volumes {
    volume_name    = docker_volume.synthetic.name
    container_path = "/data/db"
  }
  healthcheck {
    test         = ["CMD", "mongosh", "--quiet", "--eval", "db.adminCommand('ping').ok"]
    interval     = "5s"
    timeout      = "5s"
    start_period = "10s"
    retries      = 20
  }
  wait         = true
  wait_timeout = 180
}

output "uri" {
  value = "mongodb://127.0.0.1:${var.port}/"
}
