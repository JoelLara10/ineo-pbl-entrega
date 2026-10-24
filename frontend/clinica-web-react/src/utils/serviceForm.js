export function normalizeServiceForm(form) {
  const code = form.serv_cve.trim().toUpperCase();
  const description = form.serv_desc.trim();
  if (!code || !description || String(form.serv_costo ?? '').trim() === '') {
    return { error: 'serviceRequired' };
  }
  if (code.length > 40 || description.length > 250) return { error: 'serviceInvalidData' };
  const data = { ...form, serv_cve: code, serv_desc: description };
  for (const key of ['serv_costo', ...Array.from({ length: 7 }, (_, i) => `serv_costo${i + 2}`)]) {
    const number = Number(form[key] ?? 0);
    if (!Number.isFinite(number) || number < 0) return { error: 'serviceInvalidData' };
    data[key] = number;
  }
  data.iva = form.iva === '' || form.iva == null ? 16 : Number(form.iva);
  data.tipo = Number(form.tipo);
  if (!Number.isFinite(data.iva) || data.iva < 0 || data.iva > 100 || ![1, 2, 3, 4, 5].includes(data.tipo)) {
    return { error: 'serviceInvalidData' };
  }
  return { data };
}

export function serviceErrorKey(error, fallback) {
  if (error.response?.status === 401) return 'serviceSessionExpired';
  if (error.response?.status === 403) return 'serviceForbidden';
  if (error.response?.status === 400 || error.response?.status === 422) return 'serviceInvalidData';
  if (!error.response) return 'serviceConnectionError';
  return fallback;
}
