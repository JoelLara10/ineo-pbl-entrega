import { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiChevronDown, FiChevronUp, FiClock, FiFileText, FiRefreshCw, FiSave, FiShield, FiUser } from 'react-icons/fi';
import { usePatient } from '../../context/PatientContext';
import api from '../../services/api';
import moment from 'moment';
import 'moment/locale/es';
import { useTranslation } from 'react-i18next';

const CACHE_PREFIX = 'ineo_web_cache_medical_notes_';
const CACHE_TTL = 2 * 60 * 1000;

function getCachedValue(key) {
  if (typeof window === 'undefined') return null;
  try {
    const raw = window.localStorage.getItem(CACHE_PREFIX + key);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (Date.now() - parsed.timestamp > parsed.ttl) {
      window.localStorage.removeItem(CACHE_PREFIX + key);
      return null;
    }
    return parsed.data;
  } catch (error) {
    console.error('Error reading medical notes cache:', error);
    return null;
  }
}

function setCachedValue(key, data, ttl = CACHE_TTL) {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(CACHE_PREFIX + key, JSON.stringify({ data, timestamp: Date.now(), ttl }));
  } catch (error) {
    console.error('Error saving medical notes cache:', error);
  }
}

export default function MedicalNoteScreen() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { selectedPatient } = usePatient();
  const idAtencion = selectedPatient?.id_atencion || location.state?.id_atencion;
  const idExp = selectedPatient?.Id_exp || location.state?.Id_exp;
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState([]);
  const [errorMessage, setErrorMessage] = useState('');
  const [formData, setFormData] = useState({ subjetivo: '', objetivo: '', analisis: '', plan: '' });

  useEffect(() => {
    moment.locale(i18n.language === 'en' ? 'en' : 'es');
  }, [i18n.language]);

  const patientLabel = useMemo(() => `Exp: ${idExp || 'N/A'} | Atención: ${idAtencion || 'N/A'}`, [idAtencion, idExp]);

  useEffect(() => {
    if (!idAtencion) {
      setErrorMessage(t('medicalSoap.selectPatientFirst'));
      return;
    }
    setErrorMessage('');

    const loadHistory = async (forceRefresh = false) => {
      setLoadingHistory(true);
      const cacheKey = String(idAtencion);
      if (!forceRefresh) {
        const cachedData = getCachedValue(cacheKey);
        if (cachedData) {
          setHistory(cachedData);
          setLoadingHistory(false);
          return;
        }
      }

      try {
        const response = await api.get(`/appointments/${idAtencion}/medical-notes`);
        const nextHistory = response.data || [];
        setCachedValue(cacheKey, nextHistory);
        setHistory(nextHistory);
      } catch (error) {
        console.error('Error loading medical notes history:', error);
        const cachedData = getCachedValue(cacheKey);
        if (cachedData) setHistory(cachedData);
      } finally {
        setLoadingHistory(false);
      }
    };

    loadHistory();
  }, [idAtencion]);

  const reloadHistory = async () => {
    if (!idAtencion) return;
    setLoadingHistory(true);
    try {
      const response = await api.get(`/appointments/${idAtencion}/medical-notes`);
      const nextHistory = response.data || [];
      setCachedValue(String(idAtencion), nextHistory);
      setHistory(nextHistory);
    } catch (error) {
      console.error('Error reloading medical notes history:', error);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData((current) => ({ ...current, [field]: value }));
  };

  const handleSubmit = async () => {
    if (!formData.subjetivo.trim()) {
      window.alert(t('medicalSoap.subjectiveRequired'));
      return;
    }

    setLoading(true);
    try {
      const response = await api.post(`/appointments/${idAtencion}/medical-notes`, formData);
      if (response.data) {
        setFormData({ subjetivo: '', objetivo: '', analisis: '', plan: '' });
        setShowHistory(true);
        await reloadHistory();
      }
    } catch (error) {
      console.error('Error saving medical note:', error);
      window.alert(error.response?.data?.error || t('medicalSoap.saveError'));
    } finally {
      setLoading(false);
    }
  };

  const sections = [
    { key: 'subjetivo', label: t('medicalSoap.subjective'), badge: 'S', color: '#4299e1', placeholder: t('medicalSoap.subjectivePlaceholder') },
    { key: 'objetivo', label: t('medicalSoap.objective'), badge: 'O', color: '#48bb78', placeholder: t('medicalSoap.objectivePlaceholder') },
    { key: 'analisis', label: t('medicalSoap.analysis'), badge: 'A', color: '#ed8936', placeholder: t('medicalSoap.analysisPlaceholder') },
    { key: 'plan', label: t('medicalSoap.plan'), badge: 'P', color: '#9f7aea', placeholder: t('medicalSoap.planPlaceholder') },
  ];

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <button type="button" onClick={() => navigate(-1)} style={styles.headerButton}><FiArrowLeft size={20} /></button>
        <div>
          <div style={styles.headerEyebrow}>MÉDICO</div>
          <h1 style={styles.headerTitle}>{t('medicalSoap.title')}</h1>
        </div>
        <button type="button" onClick={reloadHistory} style={styles.headerActionButton} disabled={!idAtencion || loadingHistory}><FiRefreshCw size={18} /></button>
      </div>

      <section style={styles.patientCard}>
        <div style={styles.patientAvatar}><FiUser size={30} color="#fff" /></div>
        <div>
          <h2 style={styles.patientName}>{t('medicalSoap.selectedPatient')}</h2>
          <p style={styles.patientMeta}>{patientLabel}</p>
        </div>
      </section>

      {errorMessage ? <div style={styles.errorCard}>{errorMessage}</div> : null}

      <section style={styles.mainCard}>
        <div style={styles.cardHeader}><FiFileText size={20} /><strong>{t('medicalSoap.newNote')}</strong></div>
        <div style={styles.cardBody}>
          {sections.map((section) => (
            <div key={section.key} style={styles.soapSection}>
              <div style={styles.sectionHeader}>
                <div style={{ ...styles.sectionBadge, backgroundColor: section.color }}>{section.badge}</div>
                <strong style={styles.sectionTitle}>{section.label}</strong>
              </div>
              <textarea style={styles.textArea} placeholder={section.placeholder} value={formData[section.key]} onChange={(event) => handleChange(section.key, event.target.value)} rows={4} />
            </div>
          ))}
        </div>
        <div style={styles.cardFooter}>
          <button type="button" style={styles.saveButton} onClick={handleSubmit} disabled={!idAtencion || loading}><FiSave size={18} /><span>{loading ? t('medicalSoap.saving') : t('medicalSoap.save')}</span></button>
        </div>
      </section>

      <section style={styles.historyCard}>
        <button type="button" style={styles.historyToggle} onClick={() => setShowHistory((current) => !current)}>
          <div style={styles.historyTitleRow}><FiClock size={18} /><strong>{t('medicalSoap.history')}</strong><span style={styles.historyCount}>{history.length} {t('vitalSigns.registros')}</span></div>
          {showHistory ? <FiChevronUp size={18} /> : <FiChevronDown size={18} />}
        </button>
        {showHistory ? (
          <div style={styles.historyBody}>
            {loadingHistory ? <div style={styles.statusBox}>{t('medicalSoap.loadingHistory')}</div> : history.length === 0 ? <div style={styles.statusBox}>{t('medicalSoap.noNotes')}</div> : history.map((item, index) => (
              <article key={item.id_nota || `${item.fecha_registro || 'note'}-${index}`} style={styles.historyItem}>
                <div style={styles.historyHeader}><div style={styles.historyBadge}>{moment(item.fecha_registro).format('DD/MM')}</div><div><div style={styles.historyDate}>{moment(item.fecha_registro).format('dddd, D [de] MMMM [de] YYYY [a las] HH:mm')}</div><div style={styles.historyAuthor}>Dr. {item.id_medico || 'No especificado'}</div></div></div>
                {sections.map((section) => item[section.key] ? <div key={section.key} style={styles.historyFieldBlock}><div style={styles.historyFieldLabel}>{section.label}</div><p style={styles.historyFieldValue}>{item[section.key]}</p></div> : null)}
              </article>
            ))}
          </div>
        ) : null}
      </section>

      <footer style={styles.footer}><FiShield size={14} /><span>{t('medicalSoap.footer')}</span></footer>
    </div>
  );
}

const styles = {
  page: { minHeight: '100%', padding: '24px', background: 'linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%)' },
  header: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px', padding: '20px 24px', borderRadius: '20px', background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)', color: '#fff', boxShadow: '0 18px 50px rgba(79, 70, 229, 0.22)' },
  headerButton: { width: '44px', height: '44px', border: '1px solid rgba(255,255,255,0.25)', borderRadius: '12px', background: 'rgba(255,255,255,0.12)', color: '#fff', display: 'grid', placeItems: 'center' },
  headerEyebrow: { fontSize: '12px', letterSpacing: '0.18em', textTransform: 'uppercase', opacity: 0.8, marginBottom: '4px' },
  headerTitle: { margin: 0, fontSize: '28px', fontWeight: 800 },
  headerSpacer: { width: '44px', height: '44px' },
  headerActionButton: { width: '44px', height: '44px', border: '1px solid rgba(255,255,255,0.25)', borderRadius: '12px', background: 'rgba(255,255,255,0.12)', color: '#fff', display: 'grid', placeItems: 'center' },
  patientCard: { marginTop: '20px', padding: '18px 20px', backgroundColor: '#fff', borderRadius: '20px', display: 'flex', alignItems: 'center', gap: '16px', boxShadow: '0 12px 32px rgba(15, 23, 42, 0.08)', borderLeft: '5px solid #2563eb' },
  patientAvatar: { width: '56px', height: '56px', borderRadius: '16px', backgroundColor: '#2563eb', display: 'grid', placeItems: 'center', flexShrink: 0 },
  patientName: { margin: 0, fontSize: '18px', color: '#0f172a' },
  patientMeta: { margin: '6px 0 0', color: '#64748b' },
  errorCard: { marginTop: '18px', padding: '16px', borderRadius: '16px', backgroundColor: '#fff7ed', border: '1px solid #fdba74', color: '#9a3412' },
  mainCard: { marginTop: '18px', backgroundColor: '#fff', borderRadius: '24px', boxShadow: '0 14px 36px rgba(15, 23, 42, 0.08)', overflow: 'hidden' },
  cardHeader: { display: 'flex', alignItems: 'center', gap: '10px', padding: '18px 22px', color: '#fff', background: 'linear-gradient(135deg, #4299e1 0%, #3182ce 100%)' },
  cardBody: { padding: '20px' },
  soapSection: { marginBottom: '20px', padding: '16px', backgroundColor: '#f8fafc', borderRadius: '16px' },
  sectionHeader: { display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' },
  sectionBadge: { width: '40px', height: '40px', borderRadius: '12px', color: '#fff', display: 'grid', placeItems: 'center', fontWeight: 800 },
  sectionTitle: { color: '#1e293b' },
  textArea: { width: '100%', minHeight: '110px', padding: '12px 14px', borderRadius: '14px', border: '1px solid #cbd5e1', backgroundColor: '#fff', resize: 'vertical', font: 'inherit', color: '#0f172a' },
  cardFooter: { padding: '20px', borderTop: '1px solid #e2e8f0', backgroundColor: '#f8fafc', display: 'flex', justifyContent: 'center' },
  saveButton: { display: 'flex', alignItems: 'center', gap: '8px', padding: '14px 28px', borderRadius: '14px', border: 'none', backgroundColor: '#16a34a', color: '#fff', fontWeight: 700 },
  historyCard: { marginTop: '18px', backgroundColor: '#fff', borderRadius: '24px', overflow: 'hidden', boxShadow: '0 14px 36px rgba(15, 23, 42, 0.08)' },
  historyToggle: { width: '100%', border: 'none', padding: '18px 22px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#fff', background: 'linear-gradient(135deg, #4299e1 0%, #3182ce 100%)' },
  historyTitleRow: { display: 'flex', alignItems: 'center', gap: '10px' },
  historyCount: { marginLeft: '8px', padding: '4px 10px', borderRadius: '999px', backgroundColor: 'rgba(255,255,255,0.2)', fontSize: '12px' },
  historyBody: { padding: '16px' },
  statusBox: { padding: '28px', borderRadius: '18px', textAlign: 'center', backgroundColor: '#f8fafc', color: '#64748b' },
  historyItem: { backgroundColor: '#f8fafc', borderRadius: '18px', padding: '16px', marginBottom: '14px' },
  historyHeader: { display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' },
  historyBadge: { minWidth: '52px', padding: '12px 10px', borderRadius: '14px', backgroundColor: '#4299e1', color: '#fff', fontWeight: 800, textAlign: 'center' },
  historyDate: { color: '#1e293b', fontWeight: 700, marginBottom: '4px' },
  historyAuthor: { color: '#64748b', fontSize: '13px' },
  historyFieldBlock: { marginTop: '10px' },
  historyFieldLabel: { color: '#334155', fontWeight: 700, marginBottom: '4px' },
  historyFieldValue: { margin: 0, color: '#475569', lineHeight: 1.6 },
  footer: { marginTop: '26px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', color: '#64748b', fontSize: '13px' },
};
