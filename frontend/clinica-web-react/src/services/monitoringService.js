import api from './api';
export const monitoringService = {
  async provision(device_id, patient_id) { return (await api.post('/monitoring/devices', { device_id, patient_id: Number(patient_id) })).data.data; },
  async patients() { return (await api.get('/monitoring/patients')).data.data; },
  async patient(id) { return (await api.get(`/monitoring/patients/${encodeURIComponent(id)}`)).data.data; },
  async acknowledge(id) { return (await api.patch(`/monitoring/alerts/${encodeURIComponent(id)}/acknowledge`)).data.data; },
};
export const readingState = (patient) => !patient.device ? 'Sin dispositivo asignado' : !patient.latest ? 'Sin lecturas' : !patient.device.online ? 'Dispositivo desconectado' : patient.latest.stale ? 'Lectura desactualizada' : patient.latest.finger_detected === false ? 'Sin contacto con el sensor' : 'Lectura reciente';
export const readingTime = (value) => value ? new Date(value).toLocaleString() : 'Sin fecha';
export const readingValue = (value, unit = '') => value == null ? 'Sin lectura' : `${value} ${unit}`.trim();
export const alertTitle = (alert) => alert.type === 'fall' ? 'Posible caída detectada' : alert.message || 'Alerta de monitoreo';
