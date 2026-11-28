// Validaciones puras y reutilizables para datos clínicos de la Actividad 09.
const MAX_CLINICAL_TEXT = 2000;

function isPositiveInteger(value) {
  const numeric = Number(value);
  return Number.isInteger(numeric) && numeric > 0;
}

function cleanText(value) {
  return typeof value === 'string' ? value.trim() : '';
}

function validateClinicalContext(idAtencion, idExp) {
  if (!isPositiveInteger(idAtencion) || !isPositiveInteger(idExp)) {
    return { ok: false, error: 'La atención o el expediente no son válidos.' };
  }
  return { ok: true };
}

function validateClinicalHistory({ id_atencion, Id_exp, formData = {} }) {
  const context = validateClinicalContext(id_atencion, Id_exp);
  if (!context.ok) return context;

  const reason = cleanText(formData.motivo_consulta);
  if (reason.length < 3 || reason.length > 500) {
    return { ok: false, error: 'El motivo de consulta debe tener entre 3 y 500 caracteres.' };
  }

  const longFields = [
    'sintomatologia_otros', 'heredo_otros', 'nopat_otros',
    'pat_enfermedades', 'pat_medicamentos', 'pat_alergias',
    'pat_oculares', 'pat_cirugias',
  ];
  if (longFields.some((field) => cleanText(formData[field]).length > MAX_CLINICAL_TEXT)) {
    return { ok: false, error: 'Los campos clínicos no pueden exceder 2000 caracteres.' };
  }

  const asList = (value) => Array.isArray(value) ? value : [];
  return {
    ok: true,
    data: {
      ...formData,
      motivo_consulta: reason,
      sintomatologia: asList(formData.sintomatologia).join(','),
      heredo: asList(formData.heredo).join(','),
      nopat: asList(formData.nopat).join(','),
      ...Object.fromEntries(longFields.map((field) => [field, cleanText(formData[field])])),
    },
  };
}

function validatePrescription({ id_atencion, Id_exp, medications = [] }) {
  const context = validateClinicalContext(id_atencion, Id_exp);
  if (!context.ok) return context;
  if (!Array.isArray(medications) || medications.length < 1 || medications.length > 10) {
    return { ok: false, error: 'La receta debe contener entre 1 y 10 medicamentos.' };
  }

  const normalized = medications.map((med) => ({
    medicamento: cleanText(med?.medicamento),
    dosis: cleanText(med?.dosis),
    frecuencia: cleanText(med?.frecuencia),
    duracion: cleanText(med?.duracion),
    indicaciones: cleanText(med?.indicaciones),
  }));

  const incomplete = normalized.some((med) =>
    !med.medicamento || !med.dosis || !med.frecuencia || !med.duracion
  );
  if (incomplete) {
    return { ok: false, error: 'Cada medicamento requiere nombre, dosis, frecuencia y duración.' };
  }

  const excessive = normalized.some((med) =>
    med.medicamento.length > 120 ||
    med.dosis.length > 80 ||
    med.frecuencia.length > 120 ||
    med.duracion.length > 80 ||
    med.indicaciones.length > 1000
  );
  if (excessive) {
    return { ok: false, error: 'Uno o más datos de la receta exceden el límite permitido.' };
  }

  return { ok: true, data: normalized };
}

function isValidClinicalDate(value) {
  const match = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(cleanText(value));
  if (!match) return false;
  const [, dd, mm, yyyy] = match;
  const date = new Date(Number(yyyy), Number(mm) - 1, Number(dd));
  const today = new Date();
  today.setHours(23, 59, 59, 999);
  return date.getFullYear() === Number(yyyy) &&
    date.getMonth() === Number(mm) - 1 &&
    date.getDate() === Number(dd) &&
    date <= today;
}

function validateMedicationAdministration({ id_atencion, Id_exp, medications = [] }) {
  const context = validateClinicalContext(id_atencion, Id_exp);
  if (!context.ok) return context;
  if (!Array.isArray(medications) || medications.length < 1 || medications.length > 10) {
    return { ok: false, error: 'El registro debe contener entre 1 y 10 medicamentos.' };
  }

  const normalized = medications.map((med) => ({
    nombre: cleanText(med?.nombre),
    dosis: cleanText(med?.dosis),
    frecuencia: cleanText(med?.frecuencia),
    via: cleanText(med?.via),
    fecha_aplicacion: cleanText(med?.fecha_aplicacion),
  }));

  if (normalized.some((med) => !med.nombre || !med.dosis || !med.frecuencia || !med.via)) {
    return { ok: false, error: 'Cada administración requiere medicamento, dosis, frecuencia y vía.' };
  }
  if (normalized.some((med) => !isValidClinicalDate(med.fecha_aplicacion))) {
    return { ok: false, error: 'La fecha debe ser válida, usar DD/MM/AAAA y no estar en el futuro.' };
  }
  if (normalized.some((med) =>
    med.nombre.length > 120 || med.dosis.length > 80 ||
    med.frecuencia.length > 120 || med.via.length > 60
  )) {
    return { ok: false, error: 'Uno o más datos de administración exceden el límite permitido.' };
  }

  return { ok: true, data: normalized };
}


export { validateClinicalHistory, validatePrescription };
