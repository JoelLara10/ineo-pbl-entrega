mock_provider "docker" {}

run "isolated_environment" {
  command = plan
  assert {
    condition     = output.mongo_uri == "mongodb://127.0.0.1:27029/"
    error_message = "Mongo debe permanecer en loopback y el puerto de prueba."
  }
}

run "reject_production_name" {
  command = plan
  variables { environment_name = "production" }
  expect_failures = [var.environment_name]
}

run "reject_invalid_port" {
  command = plan
  variables { mongo_port = 70000 }
  expect_failures = [var.mongo_port]
}
