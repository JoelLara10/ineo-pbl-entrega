import api from './api';

const clean = (params = {}) => Object.fromEntries(
  Object.entries(params).filter(([, value]) => value !== '' && value != null),
);
const data = (response) => response.data;

const withFallback = async (paths, config) => {
  let lastError;
  for (const path of paths) {
    try {
      return data(await api.get(path, config));
    } catch (error) {
      lastError = error;
      if (![404, 405].includes(error.response?.status)) throw error;
    }
  }
  throw lastError;
};

const adminService = {
  getOptions: (currentIdCama) => api.get('/options', {
    params: clean({ current_id_cama: currentIdCama, all: true }),
  }).then(data),
  getPatients: (search = '') => withFallback(
    ['/gestion-pacientes', '/admin-patients', '/patients-admin', '/patients'],
    { params: clean({ search, all: true }) },
  ),
  searchPatients: (q = '', limit = 10) => api.get('/patients/search', {
    params: clean({ q, limit }),
  }).then(data),
  getPatient: (idExp) => api.get(`/patients/${idExp}`).then(data),
  createPatient: (payload) => api.post('/patients', payload).then(data),
  updatePatient: (idExp, payload) => api.put(`/patients/${idExp}`, payload).then(data),
  getCensus: (search = '') => api.get('/censo', {
    params: clean({ search, all: true }),
  }).then(data),
  getCashCut: ({ date, search } = {}) => api.get('/corte-caja', {
    params: clean({ date, search, all: true }),
  }).then(data),
  getAccounts: (search = '') => api.get('/cuenta-pacientes', {
    params: clean({ search, all: true }),
  }).then(data),
  getAccount: (idAtencion) => api.get(`/cuenta-pacientes/${idAtencion}`).then(data),
  getAccountDocuments: (idAtencion) => api.get(`/accounts/${idAtencion}/documents`).then(data),
  addCharge: (idAtencion, payload) => api.post(`/accounts/${idAtencion}/charges`, payload).then(data),
  removeCharge: (idAtencion, chargeId) => api.delete(`/accounts/${idAtencion}/charges/${chargeId}`).then(data),
  registerPayment: (idAtencion, payload) => api.post(`/accounts/${idAtencion}/payments`, payload).then(data),
  closeAccount: (idAtencion) => api.post(`/accounts/${idAtencion}/close`).then(data),
  downloadDocument: async (file) => {
    if (!file?.endpoint) throw new Error('Document endpoint is missing.');
    const endpoint = file.endpoint.startsWith('/api/v1')
      ? file.endpoint.replace(/^\/api\/v1/, '')
      : file.endpoint;
    const response = await api.get(endpoint, { responseType: 'blob' });
    const url = URL.createObjectURL(response.data);
    const anchor = window.document.createElement('a');
    anchor.href = url;
    anchor.download = file.filename || `${file.key || 'document'}.pdf`;
    window.document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  },
};

export default adminService;
