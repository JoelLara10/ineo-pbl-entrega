import { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiChevronDown, FiChevronUp, FiClipboard, FiClock, FiRefreshCw, FiSave, FiShield, FiUser } from 'react-icons/fi';
import { usePatient } from '../../context/PatientContext';
import api from '../../services/api';
import moment from 'moment';
import 'moment/locale/es';
import { useTranslation } from 'react-i18next';

const CACHE_CURRENT = 'ineo_web_cache_medico_diagnosis_current_';
const CACHE_HISTORY = 'ineo_web_cache_medico_diagnosis_history_';
const CACHE_TTL = 2 * 60 * 1000;

function getCachedValue(key) {
  if (typeof window === 'undefined') return null;
  try {
    const raw = window.localStorage.getItem(key);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (Date.now() - parsed.timestamp > parsed.ttl) {
      window.localStorage.removeItem(key);
      return null;
    }
    return parsed.data;
  } catch (error) {
    console.error('Error reading diagnosis cache:', error);
    return null;
  }
}

function setCachedValue(key, data, ttl = CACHE_TTL) {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(key, JSON.stringify({ data, timestamp: Date.now(), ttl }));
  } catch (error) {
    console.error('Error saving diagnosis cache:', error);
  }
}

export default function DiagnosisScreen() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { selectedPatient } = usePatient();
  const idAtencion = selectedPatient?.id_atencion || location.state?.id_atencion;
  const idExp = selectedPatient?.Id_exp || location.state?.Id_exp;
  const [loading, setLoading] = useState(false);
  const [loadingData, setLoadingData] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [currentDiagnosis, setCurrentDiagnosis] = useState(null);
  const [history, setHistory] = useState([]);
  const [errorMessage, setErrorMessage] = useState('');
  const [formData, setFormData] = useState({ diagnostico_principal: '', diagnosticos_secundarios: '', observaciones: '' });

  useEffect(() => {
    moment.locale(i18n.language === 'en' ? 'en' : 'es');
  }, [i18n.language]);

  const patientLabel = useMemo(() => `Exp: ${idExp || 'N/A'} | Atención: ${idAtencion || 'N/A'}`, [idAtencion, idExp]);

  useEffect(() => {
    if (!idAtencion) {
      setErrorMessage(t('medicalDiagnosis.selectPatientFirst'));
      return;
    }
    setErrorMessage('');

    const loadCurrentDiagnosis = async (forceRefresh = false) => {
      setLoadingData(true);
      const cacheKey = `${CACHE_CURRENT}${idAtencion}`;
      if (!forceRefresh) {
        const cachedData = getCachedValue(cacheKey);
        if (cachedData) {
          setCurrentDiagnosis(cachedData);
          setFormData({
            diagnostico_principal: cachedData.diagnostico_principal || '',
            diagnosticos_secundarios: cachedData.diagnosticos_secundarios || '',
            observaciones: cachedData.observaciones || '',
          });
          setLoadingData(false);
          return;
        }
      }
      try {
        const response = await api.get(`/appointments/${idAtencion}/diagnosis`);
        if (response.data) {
          setCachedValue(cacheKey, response.data);
          setCurrentDiagnosis(response.data);
          setFormData({
            diagnostico_principal: response.data.diagnostico_principal || '',
            diagnosticos_secundarios: response.data.diagnosticos_secundarios || '',
            observaciones: response.data.observaciones || '',
          });
        }
      } catch (error) {
        console.error('Error loading current diagnosis:', error);
        const cachedData = getCachedValue(cacheKey);
        if (cachedData) {
          setCurrentDiagnosis(cachedData);
          setFormData({
            diagnostico_principal: cachedData.diagnostico_principal || '',
            diagnosticos_secundarios: cachedData.diagnosticos_secundarios || '',
            observaciones: cachedData.observaciones || '',
          });
        }
      } finally {
        setLoadingData(false);
      }
    };

    const loadHistory = async (forceRefresh = false) => {
      setLoadingHistory(true);
      const cacheKey = `${CACHE_HISTORY}${idAtencion}`;
      if (!forceRefresh) {
        const cachedData = getCachedValue(cacheKey);
        if (cachedData) {
          setHistory(cachedData);
          setLoadingHistory(false);
          return;
        }
      }
      try {
        const response = await api.get(`/appointments/${idAtencion}/diagnosis/history`);
        const nextHistory = Array.isArray(response.data) ? response.data : [];
        setCachedValue(cacheKey, nextHistory);
        setHistory(nextHistory);
      } catch (error) {
        console.error('Error loading diagnosis history:', error);
        const cachedData = getCachedValue(cacheKey);
        setHistory(cachedData || []);
      } finally {
        setLoadingHistory(false);
      }
    };

    loadCurrentDiagnosis();
    loadHistory();
  }, [idAtencion]);

  const reloadAll = async () => {
    if (!idAtencion) return;
    setLoadingData(true);
    setLoadingHistory(true);
    try {
      const [currentResponse, historyResponse] = await Promise.all([
        api.get(`/appointments/${idAtencion}/diagnosis`),
        api.get(`/appointments/${idAtencion}/diagnosis/history`),
      ]);
      if (currentResponse.data) {
        setCachedValue(`${CACHE_CURRENT}${idAtencion}`, currentResponse.data);
        setCurrentDiagnosis(currentResponse.data);
        setFormData({
          diagnostico_principal: currentResponse.data.diagnostico_principal || '',
          diagnosticos_secundarios: currentResponse.data.diagnosticos_secundarios || '',
          observaciones: currentResponse.data.observaciones || '',
        });
      }
      const nextHistory = Array.isArray(historyResponse.data) ? historyResponse.data : [];
      setCachedValue(`${CACHE_HISTORY}${idAtencion}`, nextHistory);
      setHistory(nextHistory);
    } catch (error) {
      console.error('Error reloading diagnosis data:', error);
    } finally {
      setLoadingData(false);
      setLoadingHistory(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData((current) => ({ ...current, [field]: value }));
  };

  const handleSubmit = async () => {
    if (!formData.diagnostico_principal.trim()) {
      window.alert(t('medicalDiagnosis.principalRequired'));
      return;
    }

    setLoading(true);
    try {
      await api.post(`/appointments/${idAtencion}/diagnosis`, formData);
      setShowHistory(true);
      await reloadAll();
    } catch (error) {
      console.error('Error saving diagnosis:', error);
      window.alert(error.response?.data?.error || t('medicalDiagnosis.saveError'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <button type="button" onClick={() => navigate(-1)} style={styles.headerButton}><FiArrowLeft size={20} /></button>
        <div>
          <div style={styles.headerEyebrow}>MÉDICO</div>
          <h1 style={styles.headerTitle}>{t('medicalDiagnosis.title')}</h1>
        </div>
        <button type="button" onClick={reloadAll} style={styles.headerActionButton} disabled={!idAtencion || loadingData || loadingHistory}><FiRefreshCw size={18} /></button>
      </div>

      <section style={styles.patientCard}>
        <div style={styles.patientAvatar}><FiUser size={30} color="#fff" /></div>
        <div>
          <h2 style={styles.patientName}>{t('medicalDiagnosis.selectedPatient')}</h2>
          <p style={styles.patientMeta}>{patientLabel}</p>
        </div>
      </section>

      {errorMessage ? <div style={styles.errorCard}>{errorMessage}</div> : null}

      {loadingData ? <div style={styles.loadingCard}>{t('medicalDiagnosis.loadingData')}</div> : (
        <>
          <section style={styles.mainCard}>
            <div style={styles.cardHeader}><FiClipboard size={20} /><strong>{currentDiagnosis ? t('medicalDiagnosis.editDiagnosis') : t('medicalDiagnosis.newDiagnosis')}</strong></div>
            <div style={styles.cardBody}>
              <div style={styles.sectionBox}><div style={styles.sectionRow}><div style={styles.sectionBadge}>1</div><strong>{t('medicalDiagnosis.principalDiagnosis')}</strong></div><input style={styles.input} placeholder={t('medicalDiagnosis.principalDiagnosisPlaceholder')} value={formData.diagnostico_principal} onChange={(event) => handleChange('diagnostico_principal', event.target.value)} /></div>
              <div style={styles.sectionBox}><div style={styles.sectionRow}><div style={styles.sectionBadge}>2</div><strong>{t('medicalDiagnosis.secondaryDiagnoses')}</strong></div><textarea style={styles.textArea} placeholder={t('medicalDiagnosis.secondaryPlaceholder')} value={formData.diagnosticos_secundarios} onChange={(event) => handleChange('diagnosticos_secundarios', event.target.value)} rows={4} /></div>
              <div style={styles.sectionBox}><div style={styles.sectionRow}><div style={styles.sectionBadge}>3</div><strong>{t('medicalDiagnosis.observations')}</strong></div><textarea style={styles.textArea} placeholder={t('medicalDiagnosis.observationsPlaceholder')} value={formData.observaciones} onChange={(event) => handleChange('observaciones', event.target.value)} rows={4} /></div>
            </div>
            <div style={styles.cardFooter}><button type="button" style={styles.cancelButton} onClick={() => navigate(-1)}>{t('common.cancel')}</button><button type="button" style={styles.saveButton} onClick={handleSubmit} disabled={!idAtencion || loading}><FiSave size={18} /><span>{loading ? t('medicalDiagnosis.saving') : currentDiagnosis ? t('medicalDiagnosis.update') : t('medicalDiagnosis.save')}</span></button></div>
          </section>

          <section style={styles.historyCard}>
            <button type="button" style={styles.historyToggle} onClick={() => setShowHistory((current) => !current)}>
              <div style={styles.historyTitleRow}><FiClock size={18} /><strong>{t('medicalDiagnosis.history')}</strong><span style={styles.historyCount}>{history.length} {t('vitalSigns.registros')}</span></div>
              {showHistory ? <FiChevronUp size={18} /> : <FiChevronDown size={18} />}
            </button>
            {showHistory ? <div style={styles.historyBody}>{loadingHistory ? <div style={styles.statusBox}>{t('medicalDiagnosis.loadingHistory')}</div> : history.length === 0 ? <div style={styles.statusBox}>{t('medicalDiagnosis.noDiagnoses')}</div> : history.map((item, index) => <article key={`diag_${item.id_diagnostico || 'no-id'}_${index}`} style={styles.historyItem}><div style={styles.historyHeader}><div style={styles.historyBadge}>{moment(item.fecha_registro).format('DD/MM')}</div><div><div style={styles.historyDate}>{moment(item.fecha_registro).format('dddd, D [de] MMMM [de] YYYY [a las] HH:mm')}</div><div style={styles.historyAuthor}>Dr. {item.medico_nombre || 'No especificado'}</div></div></div><div style={styles.historyFieldLabel}>{t('medicalDiagnosis.principalLabel')}</div><p style={styles.historyFieldValue}>{item.diagnostico_principal}</p>{item.diagnosticos_secundarios ? <><div style={styles.historyFieldLabel}>{t('medicalDiagnosis.secondaryLabel')}</div><p style={styles.historyFieldValue}>{item.diagnosticos_secundarios}</p></> : null}{item.observaciones ? <><div style={styles.historyFieldLabel}>{t('medicalDiagnosis.observationsLabel')}</div><p style={styles.historyFieldValue}>{item.observaciones}</p></> : null}</article>)}</div> : null}
          </section>
        </>
      )}

      <footer style={styles.footer}><FiShield size={14} /><span>{t('medicalDiagnosis.footer')}</span></footer>
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
  patientCard: { marginTop: '20px', padding: '18px 20px', backgroundColor: '#fff', borderRadius: '20px', display: 'flex', alignItems: 'center', gap: '16px', boxShadow: '0 12px 32px rgba(15, 23, 42, 0.08)', borderLeft: '5px solid #667eea' },
  patientAvatar: { width: '56px', height: '56px', borderRadius: '16px', backgroundColor: '#667eea', display: 'grid', placeItems: 'center', flexShrink: 0 },
  patientName: { margin: 0, fontSize: '18px', color: '#0f172a' },
  patientMeta: { margin: '6px 0 0', color: '#64748b' },
  errorCard: { marginTop: '18px', padding: '16px', borderRadius: '16px', backgroundColor: '#fff7ed', border: '1px solid #fdba74', color: '#9a3412' },
  loadingCard: { marginTop: '20px', padding: '32px', textAlign: 'center', backgroundColor: '#fff', borderRadius: '20px', boxShadow: '0 12px 32px rgba(15, 23, 42, 0.08)' },
  mainCard: { marginTop: '18px', backgroundColor: '#fff', borderRadius: '24px', overflow: 'hidden', boxShadow: '0 14px 36px rgba(15, 23, 42, 0.08)' },
  cardHeader: { display: 'flex', alignItems: 'center', gap: '10px', padding: '18px 22px', color: '#fff', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
  cardBody: { padding: '20px' },
  sectionBox: { marginBottom: '20px', padding: '16px', backgroundColor: '#f8fafc', borderRadius: '16px' },
  sectionRow: { display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' },
  sectionBadge: { width: '30px', height: '30px', borderRadius: '8px', backgroundColor: '#667eea', color: '#fff', display: 'grid', placeItems: 'center', fontWeight: 800 },
  input: { width: '100%', padding: '12px 14px', borderRadius: '14px', border: '1px solid #cbd5e1', backgroundColor: '#fff', font: 'inherit', color: '#0f172a' },
  textArea: { width: '100%', minHeight: '90px', padding: '12px 14px', borderRadius: '14px', border: '1px solid #cbd5e1', backgroundColor: '#fff', resize: 'vertical', font: 'inherit', color: '#0f172a' },
  cardFooter: { padding: '20px', borderTop: '1px solid #e2e8f0', backgroundColor: '#f8fafc', display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' },
  cancelButton: { padding: '12px 18px', borderRadius: '12px', border: '1px solid #cbd5e1', backgroundColor: '#fff', color: '#475569', fontWeight: 700 },
  saveButton: { display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 18px', border: 'none', borderRadius: '12px', backgroundColor: '#16a34a', color: '#fff', fontWeight: 700 },
  historyCard: { marginTop: '18px', backgroundColor: '#fff', borderRadius: '24px', overflow: 'hidden', boxShadow: '0 14px 36px rgba(15, 23, 42, 0.08)' },
  historyToggle: { width: '100%', border: 'none', padding: '18px 22px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#fff', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
  historyTitleRow: { display: 'flex', alignItems: 'center', gap: '10px' },
  historyCount: { marginLeft: '8px', padding: '4px 10px', borderRadius: '999px', backgroundColor: 'rgba(255,255,255,0.2)', fontSize: '12px' },
  historyBody: { padding: '16px' },
  statusBox: { padding: '28px', borderRadius: '18px', textAlign: 'center', backgroundColor: '#f8fafc', color: '#64748b' },
  historyItem: { backgroundColor: '#f8fafc', borderRadius: '18px', padding: '16px', marginBottom: '14px' },
  historyHeader: { display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' },
  historyBadge: { minWidth: '52px', padding: '12px 10px', borderRadius: '14px', backgroundColor: '#667eea', color: '#fff', fontWeight: 800, textAlign: 'center' },
  historyDate: { color: '#1e293b', fontWeight: 700, marginBottom: '4px' },
  historyAuthor: { color: '#64748b', fontSize: '13px' },
  historyFieldLabel: { color: '#334155', fontWeight: 700, marginTop: '10px', marginBottom: '4px' },
  historyFieldValue: { margin: 0, color: '#475569', lineHeight: 1.6 },
  footer: { marginTop: '26px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', color: '#64748b', fontSize: '13px' },
};
