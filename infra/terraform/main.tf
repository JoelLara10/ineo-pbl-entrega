module "test_database" {
  source = "./modules/test_database"
  name   = var.environment_name
  port   = var.mongo_port
}

variable "environment_name" {
  type    = string
  default = "ineo-test-sprint10"
  validation {
    condition     = can(regex("^ineo-test-[a-z0-9-]+$", var.environment_name))
    error_message = "Use un nombre exclusivo de pruebas con prefijo ineo-test-."
  }
}

variable "mongo_port" {
  type    = number
  default = 27029
  validation {
    condition     = var.mongo_port >= 1024 && var.mongo_port <= 65535 && floor(var.mongo_port) == var.mongo_port
    error_message = "El puerto debe ser un entero entre 1024 y 65535."
  }
}

output "mongo_uri" {
  value = module.test_database.uri
}
