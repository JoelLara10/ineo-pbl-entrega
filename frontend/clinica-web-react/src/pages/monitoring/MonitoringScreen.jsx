import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { FiActivity, FiRefreshCw } from 'react-icons/fi';
import { monitoringService, readingState, readingTime, readingValue, alertTitle } from '../../services/monitoringService';
import { useAuth } from '../../context/AuthContext';
import './Monitoring.css';
export default function MonitoringScreen() {
  const { patientId } = useParams();
  const { user } = useAuth();
  const [deviceId, setDeviceId] = useState('');
  const [deviceToken, setDeviceToken] = useState(null);
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(null);
  const [revision, setRevision] = useState(0);
  useEffect(() => { setDeviceToken(null); setDeviceId(''); }, [patientId]);
  useEffect(() => {
    let active = true, pending = false;
    setData(null); setError('');
    const load = async () => {
      if (document.hidden || pending) return;
      pending = true;
      try { const next = await (patientId ? monitoringService.patient(patientId) : monitoringService.patients()); if (active) { setData(next); setError(''); } }
      catch { if (active) setError('No se pudo actualizar el monitoreo. Los datos mostrados pueden estar desactualizados.'); }
      finally { pending = false; }
    };
    load(); const timer = setInterval(load, 10000);
    document.addEventListener('visibilitychange', load);
    return () => { active = false; clearInterval(timer); document.removeEventListener('visibilitychange', load); };
  }, [patientId, revision]);
  async function provision(event) {
    event.preventDefault(); setBusy('device'); setDeviceToken(null);
    try { const result = await monitoringService.provision(deviceId.trim(), patientId); setDeviceToken(result.device_token); setRevision(v => v + 1); }
    catch { setError('No se pudo asociar el dispositivo. Revisa el identificador y que no esté asignado a otro paciente.'); }
    finally { setBusy(null); }
  }
  async function acknowledge(id) {
    setBusy(id);
    try { await monitoringService.acknowledge(id); setRevision(v => v + 1); }
    catch { setError('No se pudo reconocer la alerta. Intenta nuevamente.'); }
    finally { setBusy(null); }
  }
  const patients = patientId ? (data ? [data] : []) : data || [];
  return <section className="monitoring">
    <header className="monitoring-header"><div><h1><FiActivity aria-hidden="true" /> Monitoreo de pacientes</h1><p>Lecturas del ESP32 y alertas pendientes · actualización cada 10 segundos</p></div><button onClick={() => setRevision(v => v + 1)}><FiRefreshCw aria-hidden="true" /> Actualizar</button></header>
    {patientId && <Link to="/monitoreo">← Todos los pacientes</Link>}
    {error && <p role="alert" className="monitoring-error">{error}</p>}
    {!data && !error && <p role="status">Cargando monitoreo…</p>}
    {data && !patients.length && <p>No hay pacientes disponibles para monitoreo.</p>}
    {patients.map(patient => <article className="monitoring-patient" key={patient.patient_id}>
      <div className="monitoring-patient-heading"><h2>{patient.name}</h2><span className="monitoring-status">{readingState(patient)}</span></div>
      <p>Dispositivo: {patient.device?.device_id || 'Sin asignar'} · Última lectura: {readingTime(patient.latest?.timestamp)}</p>
      <dl className="monitoring-readings">{[['Pulso', patient.latest?.heart_rate, 'lpm'], ['SpO₂', patient.latest?.spo2, '%'], ['Movimiento', patient.latest?.movement == null ? null : patient.latest.movement ? 'Detectado' : 'En reposo', ''], ['Temperatura del sensor', patient.latest?.temperature, '°C']].map(([label,value,unit]) => <div key={label}><dt>{label}</dt><dd>{readingValue(value,unit)}</dd></div>)}</dl>
      <p className="monitoring-note">La temperatura corresponde al sensor, no a la temperatura corporal.</p>
      {!patientId ? <><p>{(patient.alerts || []).filter(a => !a.acknowledged).length} alertas pendientes</p><Link className="monitoring-link" to={`/monitoreo/${patient.patient_id}`}>Ver lecturas y alertas →</Link></> : <>
        {user?.role === 'admin' && <section className="monitoring-provision"><h3>Asociar ESP32</h3><p>El identificador debe coincidir con el firmware. Si ya está asociado a este paciente, se renueva la credencial y debes actualizarla en el ESP32.</p><form onSubmit={provision}><label htmlFor="device-id">Identificador del dispositivo</label><input id="device-id" value={deviceId} onChange={event => setDeviceId(event.target.value)} required maxLength={100} autoComplete="off" /><button disabled={busy !== null || !deviceId.trim()} type="submit">Asociar y generar credencial</button></form>{deviceToken && <div role="status"><p>Guarda esta credencial para configurar el ESP32. Solo se muestra tras generarla.</p><code className="monitoring-token">{deviceToken}</code><button type="button" onClick={() => setDeviceToken(null)}>Ocultar credencial</button></div>}</section>}
        <h3>Alertas</h3>{!(patient.alerts || []).length && <p>Sin alertas registradas.</p>}
        {(patient.alerts || []).map(alert => <div className="monitoring-alert" key={alert.id}><div><strong>{alertTitle(alert)}</strong><p>{readingTime(alert.timestamp)} · {alert.acknowledged ? 'Reconocida' : 'Pendiente de revisión'}</p></div>{!alert.acknowledged && <button disabled={busy !== null} onClick={() => acknowledge(alert.id)}>{busy === alert.id ? 'Guardando…' : 'Reconocer alerta'}</button>}</div>)}
        <h3>Historial reciente</h3>{!(patient.history || []).length && <p>Sin mediciones registradas.</p>}
        <div className="monitoring-table"><table><thead><tr><th>Fecha</th><th>Pulso</th><th>SpO₂</th><th>Movimiento</th></tr></thead><tbody>{(patient.history || []).map((reading,index) => <tr key={reading.id || index}><td>{readingTime(reading.timestamp)}</td><td>{readingValue(reading.heart_rate,'lpm')}</td><td>{readingValue(reading.spo2,'%')}</td><td>{reading.movement == null ? 'Sin lectura' : reading.movement ? 'Detectado' : 'En reposo'}</td></tr>)}</tbody></table></div>
      </>}
    </article>)}
  </section>;
}
