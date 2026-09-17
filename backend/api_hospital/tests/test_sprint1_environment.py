REQUIRED_ROLES = {"admin", "medico", "enfermeria", "estudios"}


def test_synthetic_environment_has_isolated_users_and_relations(synthetic_data):
    roles = {user["role"] for user in synthetic_data["users"]}
    patient_ids = {patient["id"] for patient in synthetic_data["patients"]}

    assert roles == REQUIRED_ROLES
    assert all("TEST" in user["id"] for user in synthetic_data["users"])
    assert all("TEST" in patient_id for patient_id in patient_ids)
    assert all(study["patient_id"] in patient_ids for study in synthetic_data["studies"])


def test_fixture_is_restored_for_every_test(synthetic_data):
    assert len(synthetic_data["users"]) == 4
    synthetic_data["users"].clear()


def test_fixture_cleanup_returns_original_data(synthetic_data):
    assert len(synthetic_data["users"]) == 4


def test_real_application_exposes_modules_used_by_synthetic_data(app):
    routes = {rule.rule for rule in app.url_map.iter_rules()}

    assert "/health" in routes
    assert any(route.startswith("/api/v1/auth") for route in routes)
    assert any("patient" in route for route in routes)
    assert any("stud" in route or "exam" in route for route in routes)
