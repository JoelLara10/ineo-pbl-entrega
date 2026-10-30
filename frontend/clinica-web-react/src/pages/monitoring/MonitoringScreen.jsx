import { getMonitoringCache, loadMonitoringCache, monitoringCacheKey } from '../../services/monitoringCache';
import { useEffect, useState, useRef } from 'react';
import { Link, useParams } from 'react-router-dom';
import { FiActivity, FiRefreshCw, FiUser, FiHeart, FiDroplet, FiThermometer, FiArrowLeft, FiArrowRight, FiCpu, FiClock } from 'react-icons/fi';
import { monitoringService, readingState, readingTime, readingValue, alertTitle } from '../../services/monitoringService';
import { useAuth } from '../../context/AuthContext';
import { useTranslation } from 'react-i18next';
import './Monitoring.css';
export default function MonitoringScreen() {
  const { t, i18n } = useTranslation();
  const lang = i18n.resolvedLanguage || i18n.language;
  const { patientId } = useParams();
  const { user } = useAuth();
  const [deviceId, setDeviceId] = useState('');
  const [deviceToken, setDeviceToken] = useState(null);
  const [page, setPage] = useState(1);
  const [historyPage, setHistoryPage] = useState(1);
  const [alertsPage, setAlertsPage] = useState(1);
  const [search, setSearch] = useState('');
  const [query, setQuery] = useState('');
  const historyBefore = useRef(null);
  const [snapshot, setSnapshot] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [fromCache, setFromCache] = useState(false);
  const owner = user?.id || user?.username || 'session';
  const key = monitoringCacheKey(owner, patientId, page, historyPage, alertsPage, query, historyPage > 1 ? historyBefore.current : null);
  const data = snapshot?.key === key ? snapshot.data : null;
  useEffect(() => {
    setHistoryPage(1); setAlertsPage(1); historyBefore.current = null;
  }, [patientId]);
  useEffect(() => {
    const timer = setTimeout(() => { setQuery(search.trim()); setPage(1); }, 300);
    return () => clearTimeout(timer);
  }, [search]);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(null);
  const [revision, setRevision] = useState(0);
  useEffect(() => { setDeviceToken(null); setDeviceId(''); }, [patientId]);
  useEffect(() => {
    let active = true, pending = false;
    const cached = getMonitoringCache(key);
    setSnapshot(cached ? { ...cached, key } : null); setFromCache(!!cached); setError('');
    const load = async () => {
      if (document.hidden || pending) return;
      pending = true;
      if (active) setRefreshing(true);
      try {
        const next = await loadMonitoringCache(key, () => patientId
          ? monitoringService.patient(patientId, historyPage, alertsPage, historyPage > 1 ? historyBefore.current : undefined)
          : monitoringService.patients(page, query));
        if (active) {
          setSnapshot({ ...next, key }); setFromCache(false); setError('');
          if (patientId && historyPage === 1) historyBefore.current = next.data?.history_pagination?.as_of || null;
        }
      }
      catch (error) { if (active && error.code !== 'ERR_SESSION_CHANGED') setError('patientMonitoring.loadError'); }
      finally { pending = false; if (active) setRefreshing(false); }
    };
    load(); const timer = setInterval(load, 10000);
    document.addEventListener('visibilitychange', load);
    return () => { active = false; clearInterval(timer); document.removeEventListener('visibilitychange', load); };
  }, [patientId, revision, key]);
  async function provision(event) {
    event.preventDefault(); setBusy('device'); setDeviceToken(null);
    try { const result = await monitoringService.provision(deviceId.trim(), patientId); setDeviceToken(result.device_token); setRevision(v => v + 1); }
    catch { setError('patientMonitoring.provisionError'); }
    finally { setBusy(null); }
  }
  async function acknowledge(id) {
    setBusy(id);
    try { await monitoringService.acknowledge(id); setRevision(v => v + 1); }
    catch { setError('patientMonitoring.ackError'); }
    finally { setBusy(null); }
  }
  const patients = patientId ? (data ? [data] : []) : (Array.isArray(data) ? data : data?.data) || [];
  return <section className="monitoring">
    <header className="monitoring-header"><div><h1><FiActivity aria-hidden="true" /> {t('patientMonitoring.title')}</h1><p>{t('patientMonitoring.subtitle')}</p></div><button onClick={() => setRevision(v => v + 1)}><FiRefreshCw aria-hidden="true" /> {t('patientMonitoring.refresh')}</button></header>
    {!patientId && <label className="monitoring-search">{t('patientMonitoring.search')}<input type="search" value={search} onChange={event => setSearch(event.target.value)} /></label>}
    {(refreshing || snapshot) && <p role="status" className="monitoring-note">{refreshing ? t('patientMonitoring.refreshing') : fromCache ? t('patientMonitoring.cached') : t('patientMonitoring.updated', { time: readingTime(snapshot?.savedAt, lang, t) })}</p>}
    {!patientId && <MonitoringPager meta={data?.pagination} onChange={setPage} disabled={refreshing} t={t} label={t('patientMonitoring.patientsPages')} />}
    {patientId && <Link className="monitoring-back" to="/monitoreo"><FiArrowLeft aria-hidden="true" /> {t('patientMonitoring.allPatients')}</Link>}
    {error && <p role="alert" className="monitoring-error">{t(error)}</p>}
    {!data && !error && <p role="status" className="monitoring-empty">{t('patientMonitoring.loading')}</p>}
    {data && !patients.length && <p className="monitoring-empty">{t('patientMonitoring.empty')}</p>}
    {patients.map(patient => <article className="monitoring-patient" key={patient.patient_id}>
      <div className="monitoring-patient-heading"><h2><span className="monitoring-patient-icon"><FiUser aria-hidden="true" /></span>{patient.name}</h2><span className="monitoring-status">{readingState(patient, t)}</span></div>
      <div className="monitoring-meta"><p><FiCpu aria-hidden="true" /> {t('patientMonitoring.device')}: {patient.device?.device_id || t('patientMonitoring.unassigned')}</p><p><FiClock aria-hidden="true" /> {t('patientMonitoring.lastReading')}: {readingTime(patient.latest?.timestamp, lang, t)}</p></div>
      <dl className="monitoring-readings">{[[t('patientMonitoring.pulse'), patient.latest?.heart_rate, t('patientMonitoring.pulseUnit'), FiHeart], [t('patientMonitoring.oxygen'), patient.latest?.spo2, '%', FiDroplet], [t('patientMonitoring.movement'), patient.latest?.movement == null ? null : patient.latest.movement ? t('patientMonitoring.detected') : t('patientMonitoring.resting'), '', FiActivity], [t('patientMonitoring.sensorTemperature'), patient.latest?.temperature, '°C', FiThermometer]].map(([label,value,unit,Icon]) => <div key={label}><dt><Icon aria-hidden="true" />{label}</dt><dd>{readingValue(value,unit,t)}</dd></div>)}</dl>
      <p className="monitoring-note">{t('patientMonitoring.sensorNote')}</p>
      {!patientId ? <><p>{t('patientMonitoring.pendingCount', { count: patient.pending_alert_count ?? (patient.alerts || []).filter(a => !a.acknowledged).length })}</p><Link className="monitoring-link" to={`/monitoreo/${patient.patient_id}`}>{t('patientMonitoring.viewDetails')} <FiArrowRight aria-hidden="true" /></Link></> : <>
        {user?.role === 'admin' && <section className="monitoring-provision"><h3>{t('patientMonitoring.assignDevice')}</h3><p>{t('patientMonitoring.assignHelp')}</p><form onSubmit={provision}><label htmlFor="device-id">{t('patientMonitoring.deviceId')}</label><input id="device-id" value={deviceId} onChange={event => setDeviceId(event.target.value)} required maxLength={100} autoComplete="off" /><button disabled={busy !== null || !deviceId.trim()} type="submit">{t('patientMonitoring.generateCredential')}</button></form>{deviceToken && <div role="status"><p>{t('patientMonitoring.credentialHelp')}</p><code className="monitoring-token">{deviceToken}</code><button type="button" onClick={() => setDeviceToken(null)}>{t('patientMonitoring.hideCredential')}</button></div>}</section>}
        <h3>{t('patientMonitoring.alerts')}</h3><MonitoringPager meta={patient.alerts_pagination} onChange={setAlertsPage} disabled={refreshing} t={t} label={t('patientMonitoring.alerts')} />{!(patient.alerts || []).length && <p>{t('patientMonitoring.noAlerts')}</p>}
        {(patient.alerts || []).map(alert => <div className={`monitoring-alert${alert.acknowledged ? " monitoring-alert-acknowledged" : ""}`} key={alert.id}><div><strong>{alertTitle(alert, t)}</strong><p>{readingTime(alert.timestamp, lang, t)} · {alert.acknowledged ? t('patientMonitoring.acknowledged') : t('patientMonitoring.pendingReview')}</p></div>{!alert.acknowledged && <button disabled={busy !== null} onClick={() => acknowledge(alert.id)}>{busy === alert.id ? t('patientMonitoring.saving') : t('patientMonitoring.acknowledge')}</button>}</div>)}
        <h3>{t('patientMonitoring.history')}</h3><MonitoringPager meta={patient.history_pagination} onChange={setHistoryPage} disabled={refreshing} t={t} label={t('patientMonitoring.history')} />{!(patient.history || []).length && <p>{t('patientMonitoring.noHistory')}</p>}
        <div className="monitoring-table"><table><thead><tr><th>{t('patientMonitoring.date')}</th><th>{t('patientMonitoring.pulse')}</th><th>{t('patientMonitoring.oxygen')}</th><th>{t('patientMonitoring.movement')}</th></tr></thead><tbody>{(patient.history || []).map((reading,index) => <tr key={reading.id || index}><td>{readingTime(reading.timestamp, lang, t)}</td><td>{readingValue(reading.heart_rate,t('patientMonitoring.pulseUnit'),t)}</td><td>{readingValue(reading.spo2,'%',t)}</td><td>{reading.movement == null ? t('patientMonitoring.noReading') : reading.movement ? t('patientMonitoring.detected') : t('patientMonitoring.resting')}</td></tr>)}</tbody></table></div>
      </>}
    </article>)}
  </section>;
}

function MonitoringPager({ meta, onChange, disabled, t, label }) {
  if (!meta || meta.total_pages <= 1) return null;
  return <nav className="monitoring-pager" aria-label={label}>
    <button disabled={disabled || meta.page <= 1} onClick={() => onChange(meta.page - 1)}>{t('patientMonitoring.previous')}</button>
    <span>{t('patientMonitoring.page', { page: meta.page, pages: meta.total_pages, total: meta.total })}</span>
    <button disabled={disabled || meta.page >= meta.total_pages} onClick={() => onChange(meta.page + 1)}>{t('patientMonitoring.next')}</button>
  </nav>;
}
