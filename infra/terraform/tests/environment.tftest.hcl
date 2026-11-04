mock_provider "docker" {}

# Provider-backed test state is cleaned automatically after the test runs.
run "provisioning_lifecycle" {
  command = apply
  assert {
    condition     = output.mongo_uri == "mongodb://127.0.0.1:27029/"
    error_message = "El ambiente debe conservar su URI de prueba."
  }
}

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
