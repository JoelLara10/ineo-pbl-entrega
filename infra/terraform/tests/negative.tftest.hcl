mock_provider "docker" {}

run "empty_environment_rejected" {
  command = plan
  variables { environment_name = "" }
  expect_failures = [var.environment_name]
}

run "out_of_range_port_rejected" {
  command = plan
  variables { mongo_port = 70000 }
  expect_failures = [var.mongo_port]
}

run "privileged_port_rejected" {
  command = plan
  variables { mongo_port = 80 }
  expect_failures = [var.mongo_port]
}
