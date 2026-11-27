// These checks validate input structure; they do not interpret clinical findings.
const text = value => typeof value === 'string' ? value.trim() : '';
const invalid = error => ({ error });
const number = value => typeof value === 'boolean' || value === null || typeof value === 'object' ? NaN : Number(value);

export function nursingContextError(attention, patient) {
  return [attention, patient].every(value => ['string', 'number'].includes(typeof value) &&
    /^\d+$/.test(String(value)) && Number.isSafeInteger(Number(value)) && Number(value) > 0)
    ? '' : 'Selecciona un paciente con atención y expediente válidos.';
}

export function validateNursingInput(kind, form) {
  if (kind === 'vitals') {
    const data = {};
    if (text(form.ta)) {
      if (!/^[1-9]\d{0,2}\/[1-9]\d{0,2}$/.test(text(form.ta))) return invalid('La presión arterial debe usar el formato 120/80.');
      data.ta = text(form.ta);
    }
    for (const key of ['fc', 'fr', 'temp', 'spo2', 'peso', 'talla']) {
      if (form[key] == null || String(form[key]).trim() === '') continue;
      const value = number(form[key]);
      if (!Number.isFinite(value) || value < 0 || (key !== 'spo2' && value === 0) ||
        (key === 'spo2' && value > 100) || (['fc', 'fr'].includes(key) && !Number.isInteger(value))) {
        return invalid(`El campo ${key} debe contener un número válido${key === 'spo2' ? ' entre 0 y 100' : ''}.`);
      }
      data[key] = value;
    }
    return Object.keys(data).length ? { data } : invalid('Captura al menos un signo vital.');
  }
  if (kind === 'assessment' || kind === 'care') {
    const required = kind === 'assessment' ? ['estado_general', 'dolor', 'movilidad', 'riesgo_caidas', 'riesgo_upp'] :
      ['diagnostico_enfermeria', 'objetivos', 'intervenciones'];
    const fields = [...required, 'observaciones', ...(kind === 'care' ? ['evaluacion'] : [])];
    const data = Object.fromEntries(fields.map(key => [key, text(form[key])]));
    if (required.some(key => data[key].length < (kind === 'care' ? 3 : 1)) || fields.some(key => data[key].length > 1000)) {
      return invalid(kind === 'care' ? 'Completa diagnóstico, objetivos e intervenciones (3 a 1000 caracteres).' :
        'Completa estado general, dolor, movilidad y ambos riesgos (hasta 1000 caracteres).');
    }
    if (kind === 'assessment' && /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(data.dolor) &&
      !(Number(data.dolor) >= 0 && Number(data.dolor) <= 10)) return invalid('El dolor numérico debe estar entre 0 y 10.');
    if (kind === 'care') {
      data.estado = text(form.estado) || 'EN_PROCESO';
      if (!['EN_PROCESO', 'PENDIENTE', 'COMPLETADO'].includes(data.estado)) return invalid('El estado del cuidado no es válido.');
    }
    return { data };
  }
  if (kind === 'note') {
    const nota_enfermeria = text(form.nota_enfermeria);
    return nota_enfermeria && nota_enfermeria.length <= 5000 ? { data: { nota_enfermeria } } :
      invalid('La nota es obligatoria y admite hasta 5000 caracteres.');
  }
  if (kind === 'balance') {
    const data = {};
    for (const key of ['ingresos_orales', 'ingresos_iv', 'egresos_orina', 'egresos_drenajes']) {
      const value = form[key] === '' || form[key] === undefined ? 0 : number(form[key]);
      if (!Number.isFinite(value) || value < 0 || value > 100000) return invalid('Los volúmenes deben ser números entre 0 y 100000 ml.');
      data[key] = value;
    }
    if (!Object.values(data).some(value => value > 0)) return invalid('Captura al menos un ingreso o egreso mayor que cero.');
    data.observaciones = text(form.observaciones);
    return data.observaciones.length <= 1000 ? { data } : invalid('Las observaciones no pueden exceder 1000 caracteres.');
  }
  if (kind === 'medications') {
    if (!Array.isArray(form) || form.length < 1 || form.length > 10) return invalid('El registro debe contener entre 1 y 10 medicamentos.');
    const limits = { nombre: 120, dosis: 80, frecuencia: 120, via: 60, fecha_aplicacion: 10 };
    const medicamentos = [];
    for (const row of form) {
      const clean = Object.fromEntries(Object.keys(limits).map(key => [key, text(row?.[key])]));
      if (Object.keys(limits).some(key => !clean[key] || clean[key].length > limits[key])) return invalid('Completa medicamento, dosis, frecuencia, vía y fecha de aplicación.');
      const match = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(clean.fecha_aplicacion);
      const date = match && new Date(Number(match[3]), Number(match[2]) - 1, Number(match[1]));
      const today = new Date(); today.setHours(23, 59, 59, 999);
      if (!match || date.getFullYear() !== Number(match[3]) || date.getMonth() + 1 !== Number(match[2]) || date.getDate() !== Number(match[1]) || date > today) {
        return invalid('La fecha debe ser válida, usar DD/MM/AAAA y no estar en el futuro.');
      }
      medicamentos.push(clean);
    }
    return { data: { medicamentos } };
  }
  return invalid('Formulario desconocido.');
}
