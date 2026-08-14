import { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { FiActivity, FiArrowLeft, FiDownload, FiPlus, FiShield, FiUser } from 'react-icons/fi';
import { usePatient } from '../../context/PatientContext';
import api from '../../services/api';
import moment from 'moment';
import 'moment/locale/es';
import { useTranslation } from 'react-i18next';

function openPdfForVitalSigns(idSignos) {
  const baseUrl = api.defaults.baseURL || '';
  const pdfUrl = `${baseUrl.replace('/api/v1', '')}/pdf/vital-signs/${idSignos}`;
  window.open(pdfUrl, '_blank', 'noopener,noreferrer');
}

function getPatientName(paciente) {
  if (!paciente) return 'Paciente';
  return [paciente.papell, paciente.sapell, paciente.nom_pac].filter(Boolean).join(' ') || 'Paciente';
}

export default function VitalSignsListScreen() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { selectedPatient } = usePatient();
  const idAtencion = selectedPatient?.id_atencion || location.state?.id_atencion;
  const idExp = selectedPatient?.Id_exp || location.state?.Id_exp;
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');
  const [patient, setPatient] = useState(null);
  const [history, setHistory] = useState([]);

  useEffect(() => {
    moment.locale(i18n.language === 'en' ? 'en' : 'es');
  }, [i18n.language]);

  const patientLabel = useMemo(() => `Exp: ${idExp || 'N/A'} | Atención: ${idAtencion || 'N/A'}`, [idAtencion, idExp]);

  useEffect(() => {
    if (!idAtencion || !idExp) {
      setErrorMessage(t('vitalSigns.selectPatientFirst'));
      setLoading(false);
      return;
    }

    setErrorMessage('');

    const loadData = async () => {
      setLoading(true);
      try {
        const [patientResponse, historyResponse] = await Promise.all([
          api.get(`/paciente/${idAtencion}/${idExp}`),
          api.get(`/appointments/${idAtencion}/vital-signs`),
        ]);
        setPatient(patientResponse.data?.paciente || null);
        setHistory(Array.isArray(historyResponse.data) ? historyResponse.data : []);
      } catch (error) {
        console.error('Error loading vital signs history:', error);
        setErrorMessage(t('vitalSigns.saveError'));
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [idAtencion, idExp]);

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <button type="button" onClick={() => navigate(-1)} style={styles.headerButton}><FiArrowLeft size={20} /></button>
        <div>
          <div style={styles.headerEyebrow}>MÉDICO</div>
          <h1 style={styles.headerTitle}>{t('vitalSigns.history')}</h1>
        </div>
        <div style={styles.headerSpacer} />
      </div>

      <section style={styles.patientCard}>
        <div style={styles.patientAvatar}><FiUser size={30} color="#fff" /></div>
        <div>
          <h2 style={styles.patientName}>{getPatientName(patient)}</h2>
          <p style={styles.patientMeta}>{patientLabel}</p>
        </div>
      </section>

      <section style={styles.actionsCard}>
        <button type="button" style={styles.primaryButton} onClick={() => navigate('/medico/signos-vitales', { state: { id_atencion: idAtencion, Id_exp: idExp } })}><FiPlus size={18} /> {t('vitalSigns.newRecord')}</button>
      </section>

      {loading ? <div style={styles.loadingCard}>{t('vitalSigns.loadingHistory')}</div> : errorMessage ? <div style={styles.errorCard}>{errorMessage}</div> : (
        <section style={styles.historyCard}>
          <div style={styles.historyHeader}><FiActivity size={18} /><strong>{t('vitalSigns.history')}</strong><span style={styles.historyCount}>{history.length} {t('vitalSigns.registros')}</span></div>
          <div style={styles.historyBody}>
            {history.length === 0 ? <div style={styles.statusBox}>{t('vitalSigns.noRecords')}</div> : history.map((item, index) => (
              <article key={item.id_signos || `${item.fecha_registro || 'signos'}-${index}`} style={styles.historyItem}>
                <div style={styles.historyItemHeader}>
                  <div>
                    <div style={styles.historyDate}>{moment(item.fecha_registro).format('DD/MM/YYYY HH:mm')}</div>
                    <div style={styles.historySubtitle}>Registro #{index + 1}</div>
                  </div>
                  <button type="button" style={styles.secondaryButton} onClick={() => openPdfForVitalSigns(item.id_signos)}><FiDownload size={16} /> PDF</button>
                </div>
                <div style={styles.metricsGrid}>
                  <div style={styles.metricCard}><span style={styles.metricLabel}>TA</span><strong>{item.ta || '—'}</strong></div>
                  <div style={styles.metricCard}><span style={styles.metricLabel}>FC</span><strong>{item.fc ?? '—'}</strong></div>
                  <div style={styles.metricCard}><span style={styles.metricLabel}>FR</span><strong>{item.fr ?? '—'}</strong></div>
                  <div style={styles.metricCard}><span style={styles.metricLabel}>Temp</span><strong>{item.temp ?? '—'}</strong></div>
                  <div style={styles.metricCard}><span style={styles.metricLabel}>SpO2</span><strong>{item.spo2 ?? '—'}</strong></div>
                  <div style={styles.metricCard}><span style={styles.metricLabel}>Peso</span><strong>{item.peso ?? '—'}</strong></div>
                  <div style={styles.metricCard}><span style={styles.metricLabel}>Talla</span><strong>{item.talla ?? '—'}</strong></div>
                </div>
              </article>
            ))}
          </div>
        </section>
      )}

      <footer style={styles.footer}><FiShield size={14} /><span>{t('vitalSigns.footer')}</span></footer>
    </div>
  );
}

const styles = {
  page: { minHeight: '100%', padding: '24px', background: 'linear-gradient(180deg, #eff6ff 0%, #dbeafe 100%)' },
  header: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px', padding: '20px 24px', borderRadius: '22px', background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)', color: '#fff', boxShadow: '0 18px 50px rgba(37, 99, 235, 0.22)' },
  headerButton: { width: '44px', height: '44px', border: '1px solid rgba(255,255,255,0.24)', borderRadius: '12px', background: 'rgba(255,255,255,0.12)', color: '#fff', display: 'grid', placeItems: 'center' },
  headerEyebrow: { fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.18em', opacity: 0.8, marginBottom: '4px' },
  headerTitle: { margin: 0, fontSize: '28px', fontWeight: 800 },
  headerSpacer: { width: '44px', height: '44px' },
  patientCard: { marginTop: '20px', padding: '18px 20px', borderRadius: '20px', backgroundColor: '#fff', display: 'flex', alignItems: 'center', gap: '16px', boxShadow: '0 12px 32px rgba(15, 23, 42, 0.08)', borderLeft: '5px solid #2563eb' },
  patientAvatar: { width: '56px', height: '56px', borderRadius: '16px', backgroundColor: '#2563eb', display: 'grid', placeItems: 'center' },
  patientName: { margin: 0, color: '#0f172a', fontSize: '18px' },
  patientMeta: { margin: '6px 0 0', color: '#64748b' },
  actionsCard: { marginTop: '18px', display: 'flex', justifyContent: 'flex-end' },
  primaryButton: { display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 18px', border: 'none', borderRadius: '14px', backgroundColor: '#dc2626', color: '#fff', fontWeight: 700 },
  secondaryButton: { display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 14px', borderRadius: '12px', border: '1px solid #bfdbfe', backgroundColor: '#fff', color: '#2563eb', fontWeight: 700 },
  loadingCard: { marginTop: '18px', padding: '30px', borderRadius: '20px', backgroundColor: '#fff', textAlign: 'center', boxShadow: '0 14px 36px rgba(15, 23, 42, 0.08)' },
  errorCard: { marginTop: '18px', padding: '16px', borderRadius: '16px', backgroundColor: '#fff7ed', border: '1px solid #fdba74', color: '#9a3412' },
  historyCard: { marginTop: '18px', borderRadius: '24px', overflow: 'hidden', backgroundColor: '#fff', boxShadow: '0 14px 36px rgba(15, 23, 42, 0.08)' },
  historyHeader: { display: 'flex', alignItems: 'center', gap: '10px', padding: '18px 22px', background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)', color: '#fff' },
  historyCount: { marginLeft: 'auto', padding: '4px 10px', borderRadius: '999px', backgroundColor: 'rgba(255,255,255,0.18)', fontSize: '12px' },
  historyBody: { padding: '18px' },
  statusBox: { padding: '28px', borderRadius: '18px', textAlign: 'center', backgroundColor: '#eff6ff', color: '#1d4ed8' },
  historyItem: { padding: '18px', borderRadius: '18px', backgroundColor: '#f8fafc', border: '1px solid #dbeafe', marginBottom: '14px' },
  historyItemHeader: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', marginBottom: '14px', flexWrap: 'wrap' },
  historyDate: { color: '#1e3a8a', fontWeight: 700 },
  historySubtitle: { marginTop: '4px', color: '#64748b', fontSize: '13px' },
  metricsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '10px' },
  metricCard: { padding: '14px', borderRadius: '14px', backgroundColor: '#fff', border: '1px solid #e2e8f0' },
  metricLabel: { display: 'block', fontSize: '12px', color: '#64748b', marginBottom: '6px' },
  footer: { marginTop: '26px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', color: '#1e3a8a', fontSize: '13px' },
};
