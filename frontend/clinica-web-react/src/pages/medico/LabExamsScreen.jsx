import { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiChevronDown, FiChevronUp, FiClock, FiRefreshCw, FiSave, FiShield, FiUser } from 'react-icons/fi';
import { MdBiotech } from 'react-icons/md';
import { usePatient } from '../../context/PatientContext';
import api from '../../services/api';
import { useTranslation } from 'react-i18next';
import moment from 'moment';
import 'moment/locale/es';

const CATALOG_CACHE = 'ineo_web_cache_lab_catalog';
const HISTORY_PREFIX = 'ineo_web_cache_lab_history_';
const CACHE_TTL = 5 * 60 * 1000;
const HISTORY_TTL = 2 * 60 * 1000;

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
    console.error('Error reading lab exams cache:', error);
    return null;
  }
}

function setCachedValue(key, data, ttl) {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(key, JSON.stringify({ data, timestamp: Date.now(), ttl }));
  } catch (error) {
    console.error('Error saving lab exams cache:', error);
  }
}

export default function LabExamsScreen() {
  const { t, i18n } = useTranslation();
  moment.locale(i18n.language === 'en' ? 'en' : 'es');
  const navigate = useNavigate();
  const location = useLocation();
  const { selectedPatient } = usePatient();
  const idAtencion = selectedPatient?.id_atencion || location.state?.id_atencion;
  const idExp = selectedPatient?.Id_exp || location.state?.Id_exp;
  const [loading, setLoading] = useState(false);
  const [loadingCatalog, setLoadingCatalog] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [exams, setExams] = useState([]);
  const [selectedExams, setSelectedExams] = useState([]);
  const [observations, setObservations] = useState('');
  const [history, setHistory] = useState([]);
  const [errorMessage, setErrorMessage] = useState('');

  const patientLabel = useMemo(() => `Exp: ${idExp || 'N/A'} | Atención: ${idAtencion || 'N/A'}`, [idAtencion, idExp]);

  useEffect(() => {
    if (!idAtencion) {
      setErrorMessage(t('labExams.selectPatientFirst'));
      return;
    }

    setErrorMessage('');
    setSelectedExams([]);
    setObservations('');

    const loadCatalog = async () => {
      setLoadingCatalog(true);
      const cached = getCachedValue(CATALOG_CACHE);
      if (cached) {
        setExams(cached);
        setLoadingCatalog(false);
      }
      try {
        const response = await api.get('/exams/catalog?type=LABORATORIO');
        const nextCatalog = Array.isArray(response.data) ? response.data : [];
        setCachedValue(CATALOG_CACHE, nextCatalog, CACHE_TTL);
        setExams(nextCatalog);
      } catch (error) {
        console.error('Error loading lab catalog:', error);
        if (!cached) setExams([]);
      } finally {
        setLoadingCatalog(false);
      }
    };

    const loadHistory = async () => {
      setLoadingHistory(true);
      const cacheKey = `${HISTORY_PREFIX}${idAtencion}`;
      const cached = getCachedValue(cacheKey);
      if (cached) {
        setHistory(cached);
        setLoadingHistory(false);
      }
      try {
        const response = await api.get(`/exams/requested/${idAtencion}?type=LABORATORIO`);
        const nextHistory = Array.isArray(response.data) ? response.data : [];
        setCachedValue(cacheKey, nextHistory, HISTORY_TTL);
        setHistory(nextHistory);
      } catch (error) {
        console.error('Error loading lab history:', error);
        if (!cached) setHistory([]);
      } finally {
        setLoadingHistory(false);
      }
    };

    loadCatalog();
    loadHistory();
  }, [idAtencion]);

  const reloadHistory = async () => {
    if (!idAtencion) return;
    setLoadingHistory(true);
    try {
      const response = await api.get(`/exams/requested/${idAtencion}?type=LABORATORIO`);
      const nextHistory = Array.isArray(response.data) ? response.data : [];
      setCachedValue(`${HISTORY_PREFIX}${idAtencion}`, nextHistory, HISTORY_TTL);
      setHistory(nextHistory);
    } catch (error) {
      console.error('Error reloading lab history:', error);
    } finally {
      setLoadingHistory(false);
    }
  };

  const reloadData = async () => {
    if (!idAtencion) return;
    setLoadingCatalog(true);
    setLoadingHistory(true);
    try {
      const [catalogResponse, historyResponse] = await Promise.all([
        api.get('/exams/catalog?type=LABORATORIO'),
        api.get(`/exams/requested/${idAtencion}?type=LABORATORIO`),
      ]);
      const nextCatalog = Array.isArray(catalogResponse.data) ? catalogResponse.data : [];
      const nextHistory = Array.isArray(historyResponse.data) ? historyResponse.data : [];
      setCachedValue(CATALOG_CACHE, nextCatalog, CACHE_TTL);
      setCachedValue(`${HISTORY_PREFIX}${idAtencion}`, nextHistory, HISTORY_TTL);
      setExams(nextCatalog);
      setHistory(nextHistory);
    } catch (error) {
      console.error('Error reloading lab data:', error);
    } finally {
      setLoadingCatalog(false);
      setLoadingHistory(false);
    }
  };

  const toggleExam = (examId) => {
    setSelectedExams((current) => (current.includes(examId) ? current.filter((id) => id !== examId) : [...current, examId]));
  };

  const handleSubmit = async () => {
    if (selectedExams.length === 0) {
      window.alert(t('labExams.selectAtLeastOne'));
      return;
    }

    setLoading(true);
    try {
      await api.post('/exams/request', {
        id_atencion: parseInt(idAtencion, 10),
        exams: selectedExams.map((id) => parseInt(id, 10)),
        observations: observations || '',
        type: 'LABORATORIO',
      });
      setSelectedExams([]);
      setObservations('');
      setShowHistory(true);
      await reloadHistory();
    } catch (error) {
      console.error('Error requesting lab exams:', error);
      window.alert(error.response?.data?.error || t('labExams.requestError'));
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
          <h1 style={styles.headerTitle}>{t('labExams.title')}</h1>
        </div>
        <button type="button" onClick={reloadData} style={styles.headerActionButton} disabled={!idAtencion || loadingCatalog || loadingHistory}><FiRefreshCw size={18} /></button>
      </div>

      <section style={styles.patientCard}>
        <div style={styles.patientAvatar}><FiUser size={30} color="#fff" /></div>
        <div>
          <h2 style={styles.patientName}>{t('labExams.selectedPatient')}</h2>
          <p style={styles.patientMeta}>{patientLabel}</p>
        </div>
      </section>

      {errorMessage ? <div style={styles.errorCard}>{errorMessage}</div> : null}

      <section style={styles.mainCard}>
        <div style={styles.cardHeader}><MdBiotech size={22} /><strong>{t('labExams.newRequest')}</strong></div>
        <div style={styles.cardBody}>
          <div style={styles.sectionTop}>
            <strong style={styles.sectionTitle}>{t('labExams.catalog')}</strong>
            <span style={styles.sectionCount}>{t('labExams.selected', { count: selectedExams.length })}</span>
          </div>

          {loadingCatalog ? <div style={styles.statusBox}>{t('labExams.loadingCatalog')}</div> : exams.length === 0 ? <div style={styles.statusBox}>{t('labExams.noExamsAvailable')}</div> : (
            <div style={styles.examsGrid}>
              {exams.map((exam) => {
                const selected = selectedExams.includes(exam.id_catalogo);
                return (
                  <button key={exam.id_catalogo} type="button" onClick={() => toggleExam(exam.id_catalogo)} style={{ ...styles.examItem, ...(selected ? styles.examItemSelected : {}) }}>
                    <span style={{ ...styles.examBadge, ...(selected ? styles.examBadgeSelected : {}) }}>{selected ? '✓' : '+'}</span>
                    <span style={{ ...styles.examText, ...(selected ? styles.examTextSelected : {}) }}>{exam.nombre}</span>
                  </button>
                );
              })}
            </div>
          )}

          <label style={styles.fieldGroup}>
            <span style={styles.fieldLabel}>{t('labExams.observations')}</span>
            <textarea style={styles.textArea} rows={4} value={observations} placeholder={t('labExams.observationsPlaceholder')} onChange={(event) => setObservations(event.target.value)} />
          </label>

          <div style={styles.actionsRow}>
            <button type="button" style={styles.secondaryButton} onClick={() => navigate('/medico/resultados', { state: { id_atencion: idAtencion, Id_exp: idExp } })}>{t('labExams.viewResults')}</button>
            <button type="button" style={styles.primaryButton} onClick={handleSubmit} disabled={!idAtencion || loading}><FiSave size={18} /> {loading ? t('labExams.requesting') : t('labExams.request')}</button>
          </div>
        </div>
      </section>

      <section style={styles.historyCard}>
        <button type="button" style={styles.historyToggle} onClick={() => setShowHistory((current) => !current)}>
          <div style={styles.historyTitle}><FiClock size={18} /><strong>{t('labExams.history')}</strong><span style={styles.historyCount}>{history.length}</span></div>
          {showHistory ? <FiChevronUp size={18} /> : <FiChevronDown size={18} />}
        </button>
        {showHistory ? (
          <div style={styles.historyBody}>
            {loadingHistory ? <div style={styles.statusBox}>{t('labExams.loadingHistory')}</div> : history.length === 0 ? <div style={styles.statusBox}>{t('labExams.noRequests')}</div> : history.map((item, index) => (
              <article key={item.id_examen || `${item.fecha || 'lab'}-${index}`} style={styles.historyItem}>
                <div style={styles.historyDate}>{moment(item.fecha_solicitud || item.fecha).format('DD/MM/YYYY HH:mm')}</div>
                <div style={styles.historyDoctor}>Dr. {item.medico || item.medico_nombre || 'No especificado'}</div>
                <div style={styles.historyExams}>
                  {(Array.isArray(item.examenes) ? item.examenes : []).map((exam, examIndex) => <span key={`${exam}-${examIndex}`} style={styles.historyExamChip}>{exam}</span>)}
                </div>
              </article>
            ))}
          </div>
        ) : null}
      </section>

      <footer style={styles.footer}><FiShield size={14} /><span>{t('labExams.footer')}</span></footer>
    </div>
  );
}

const styles = {
  page: { minHeight: '100%', padding: '24px', background: 'linear-gradient(180deg, #f0f9ff 0%, #e0f2fe 100%)' },
  header: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px', padding: '20px 24px', borderRadius: '22px', background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)', color: '#fff' },
  headerButton: { width: '44px', height: '44px', border: '1px solid rgba(255,255,255,0.24)', borderRadius: '12px', background: 'rgba(255,255,255,0.12)', color: '#fff', display: 'grid', placeItems: 'center' },
  headerEyebrow: { fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.18em', opacity: 0.8, marginBottom: '4px' },
  headerTitle: { margin: 0, fontSize: '28px', fontWeight: 800 },
  headerSpacer: { width: '44px', height: '44px' },
  headerActionButton: { width: '44px', height: '44px', border: '1px solid rgba(255,255,255,0.24)', borderRadius: '12px', background: 'rgba(255,255,255,0.12)', color: '#fff', display: 'grid', placeItems: 'center' },
  patientCard: { marginTop: '20px', padding: '18px 20px', borderRadius: '20px', backgroundColor: '#fff', display: 'flex', alignItems: 'center', gap: '16px', borderLeft: '5px solid #0284c7' },
  patientAvatar: { width: '56px', height: '56px', borderRadius: '16px', backgroundColor: '#0284c7', display: 'grid', placeItems: 'center' },
  patientName: { margin: 0, color: '#0f172a', fontSize: '18px' },
  patientMeta: { margin: '6px 0 0', color: '#64748b' },
  errorCard: { marginTop: '18px', padding: '16px', borderRadius: '16px', backgroundColor: '#fff7ed', border: '1px solid #fdba74', color: '#9a3412' },
  mainCard: { marginTop: '18px', borderRadius: '24px', overflow: 'hidden', backgroundColor: '#fff' },
  cardHeader: { display: 'flex', alignItems: 'center', gap: '10px', padding: '18px 22px', background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)', color: '#fff' },
  cardBody: { padding: '20px' },
  sectionTop: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', marginBottom: '14px' },
  sectionTitle: { color: '#0c4a6e' },
  sectionCount: { padding: '6px 12px', borderRadius: '999px', backgroundColor: '#e0f2fe', color: '#0369a1', fontWeight: 700, fontSize: '13px' },
  statusBox: { padding: '20px', borderRadius: '14px', textAlign: 'center', backgroundColor: '#f0f9ff', color: '#0369a1' },
  examsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '10px', marginBottom: '14px' },
  examItem: { display: 'flex', alignItems: 'center', gap: '10px', padding: '12px', borderRadius: '12px', border: '1px solid #bae6fd', backgroundColor: '#fff', textAlign: 'left' },
  examItemSelected: { borderColor: '#0284c7', backgroundColor: '#e0f2fe' },
  examBadge: { width: '24px', height: '24px', borderRadius: '999px', display: 'grid', placeItems: 'center', backgroundColor: '#f0f9ff', color: '#0369a1', fontWeight: 700 },
  examBadgeSelected: { backgroundColor: '#0284c7', color: '#fff' },
  examText: { color: '#0f172a' },
  examTextSelected: { color: '#0c4a6e', fontWeight: 700 },
  fieldGroup: { display: 'flex', flexDirection: 'column', gap: '8px' },
  fieldLabel: { color: '#0c4a6e', fontWeight: 700 },
  textArea: { width: '100%', minHeight: '110px', padding: '12px 14px', borderRadius: '14px', border: '1px solid #7dd3fc', backgroundColor: '#fff', resize: 'vertical', font: 'inherit', color: '#0f172a' },
  actionsRow: { display: 'flex', gap: '12px', justifyContent: 'space-between', flexWrap: 'wrap', marginTop: '14px' },
  secondaryButton: { padding: '12px 18px', borderRadius: '14px', border: '1px solid #7dd3fc', backgroundColor: '#fff', color: '#0369a1', fontWeight: 700 },
  primaryButton: { display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 18px', border: 'none', borderRadius: '14px', backgroundColor: '#0369a1', color: '#fff', fontWeight: 700 },
  historyCard: { marginTop: '18px', borderRadius: '24px', overflow: 'hidden', backgroundColor: '#fff' },
  historyToggle: { width: '100%', border: 'none', padding: '18px 22px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)', color: '#fff' },
  historyTitle: { display: 'flex', alignItems: 'center', gap: '10px' },
  historyCount: { marginLeft: '8px', padding: '4px 10px', borderRadius: '999px', backgroundColor: 'rgba(255,255,255,0.18)', fontSize: '12px' },
  historyBody: { padding: '16px' },
  historyItem: { padding: '14px', borderRadius: '14px', backgroundColor: '#f8fdff', border: '1px solid #bae6fd', marginBottom: '10px' },
  historyDate: { color: '#0c4a6e', fontWeight: 700, marginBottom: '4px' },
  historyDoctor: { color: '#475569', marginBottom: '8px' },
  historyExams: { display: 'flex', flexWrap: 'wrap', gap: '8px' },
  historyExamChip: { padding: '6px 10px', borderRadius: '999px', backgroundColor: '#fff', border: '1px solid #e0f2fe', color: '#0c4a6e', fontSize: '12px' },
  footer: { marginTop: '26px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', color: '#0c4a6e', fontSize: '13px' },
};
