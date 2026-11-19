from .base_page import BasePage


class TurnoPage(BasePage):
    def registrar_turno_sintetico(self, fixture):
        patient = self.field("S11_PATIENT_SELECTOR", ["paciente", "patient"])
        if patient:
            patient.clear(); patient.send_keys(fixture["paciente"])

        for env, labels, value in (
            ("S11_ASSESSMENT_SELECTOR", ["valoracion", "assessment"], fixture["valoracion"]),
            ("S11_BALANCE_SELECTOR", ["balance", "entrada"], fixture["balance"]),
            ("S11_CARE_SELECTOR", ["cuidado", "care"], fixture["cuidado"]),
        ):
            field = self.field(env, labels)
            if field is None:
                raise AssertionError(f"No se localizó el campo configurado para {env}")
            field.clear(); field.send_keys(str(value))
        self.click_text("Guardar", "Registrar", "Save")

    def contains_fixture(self, fixture):
        text = self.driver.page_source.lower()
        return all(str(fixture[key]).lower() in text for key in ("valoracion", "balance", "cuidado"))

