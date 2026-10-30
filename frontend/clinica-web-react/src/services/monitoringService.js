import api from './api';
import { clearMonitoringCache } from './monitoringCache';
export const monitoringService = {
  async provision(device_id, patient_id) { return (await api.post('/monitoring/devices', { device_id, patient_id: Number(patient_id) })).data.data; },
  async patients(page = 1, q = '') { return (await api.get('/monitoring/patients', { params: { page, page_size: 10, q } })).data; },
  async patient(id, historyPage = 1, alertsPage = 1, before) { return (await api.get(`/monitoring/patients/${encodeURIComponent(id)}`, { params: { history_page: historyPage, alerts_page: alertsPage, page_size: 10, ...(before ? { history_before: before } : {}) } })).data.data; },
  async acknowledge(id) { const result = (await api.patch(`/monitoring/alerts/${encodeURIComponent(id)}/acknowledge`)).data.data; clearMonitoringCache(); return result; },
};
export const readingState = (patient, t) => t(`patientMonitoring.states.${!patient.device ? 'unassigned' : !patient.latest ? 'noReadings' : (!patient.device.online || (patient.device.last_seen && Date.now() - Date.parse(patient.device.last_seen) > 30000)) ? 'offline' : (patient.latest.stale || (patient.latest.timestamp && Date.now() - Date.parse(patient.latest.timestamp) > 30000)) ? 'stale' : patient.latest.finger_detected === false ? 'noContact' : 'recent'}`);
export const readingTime = (value, language, t) => value ? new Date(value).toLocaleString(language?.startsWith('en') ? 'en-US' : 'es-MX') : t('patientMonitoring.noDate');
export const readingValue = (value, unit = '', t) => value == null ? t('patientMonitoring.noReading') : `${value} ${unit}`.trim();
const knownAlertTypes = new Set(['fall', 'low_heart_rate', 'high_heart_rate', 'low_spo2']);
export const alertTitle = (alert, t) => knownAlertTypes.has(alert.type) ? t(`patientMonitoring.alertTypes.${alert.type}`) : alert.message || t('patientMonitoring.alertTypes.generic');
