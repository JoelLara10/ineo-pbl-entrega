import api from './api';
export const monitoringService = {
  async provision(device_id, patient_id) { return (await api.post('/monitoring/devices', { device_id, patient_id: Number(patient_id) })).data.data; },
  async patients() { return (await api.get('/monitoring/patients')).data.data; },
  async patient(id) { return (await api.get(`/monitoring/patients/${encodeURIComponent(id)}`)).data.data; },
  async acknowledge(id) { return (await api.patch(`/monitoring/alerts/${encodeURIComponent(id)}/acknowledge`)).data.data; },
};
export const readingState = (patient, t) => t(`patientMonitoring.states.${!patient.device ? 'unassigned' : !patient.latest ? 'noReadings' : !patient.device.online ? 'offline' : patient.latest.stale ? 'stale' : patient.latest.finger_detected === false ? 'noContact' : 'recent'}`);
export const readingTime = (value, language, t) => value ? new Date(value).toLocaleString(language?.startsWith('en') ? 'en-US' : 'es-MX') : t('patientMonitoring.noDate');
export const readingValue = (value, unit = '', t) => value == null ? t('patientMonitoring.noReading') : `${value} ${unit}`.trim();
const knownAlertTypes = new Set(['fall', 'low_heart_rate', 'high_heart_rate', 'low_spo2']);
export const alertTitle = (alert, t) => knownAlertTypes.has(alert.type) ? t(`patientMonitoring.alertTypes.${alert.type}`) : alert.message || t('patientMonitoring.alertTypes.generic');
