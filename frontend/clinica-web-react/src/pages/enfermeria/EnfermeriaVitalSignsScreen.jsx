import { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { FiActivity, FiArrowLeft, FiHeart, FiSave, FiShield, FiUser } from 'react-icons/fi';
import { usePatient } from '../../context/PatientContext';
import api from '../../services/api';
import moment from 'moment';
import 'moment/locale/es';
import { useTranslation } from 'react-i18next';

moment.locale('es');

const CACHE_PREFIX = 'ineo_web_cache_enfermeria_vital_signs_';
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
    console.error('Error reading vital signs cache:', error);
    return null;
  }
}

function setCachedValue(key, data, ttl = CACHE_TTL) {
  if (typeof window === 'undefined') return;

  try {
    window.localStorage.setItem(
      CACHE_PREFIX + key,
      JSON.stringify({ data, timestamp: Date.now(), ttl })
    );
  } catch (error) {
    console.error('Error saving vital signs cache:', error);
  }
}

function parseNumericValue(value) {
  if (!value || value === '') return null;
  const parsed = parseFloat(value);
  return Number.isNaN(parsed) ? null : parsed;
}

export default function EnfermeriaVitalSignsScreen() {
  const { t, i18n } = useTranslation();
  moment.locale(i18n.language === 'en' ? 'en' : 'es');
  const navigate = useNavigate();
  const location = useLocation();
  const { selectedPatient } = usePatient();
  const idAtencion = selectedPatient?.id_atencion || location.state?.id_atencion;
  const idExp = selectedPatient?.Id_exp || location.state?.Id_exp;
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [history, setHistory] = useState([]);
  const [errorMessage, setErrorMessage] = useState('');
  const [formData, setFormData] = useState({
    ta: '',
    fc: '',
    fr: '',
    temp: '',
    spo2: '',
    peso: '',
    talla: '',
  });

  const patientLabel = useMemo(() => `Exp: ${idExp || 'N/A'} | Atención: ${idAtencion || 'N/A'}`, [idAtencion, idExp]);

  useEffect(() => {
    if (!idAtencion) {
      setErrorMessage(t('vitalSigns.selectPatientFirst'));
      return;
    }

    setErrorMessage('');

    const loadVitalSignsHistory = async (forceRefresh = false) => {
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
        const response = await api.get(`/appointments/${idAtencion}/vital-signs`);
        const nextHistory = response.data || [];
        setCachedValue(cacheKey, nextHistory);
        setHistory(nextHistory);
      } catch (error) {
        console.error('Error loading vital signs history:', error);
        const cachedData = getCachedValue(cacheKey);
        if (cachedData) {
          setHistory(cachedData);
        }
      } finally {
        setLoadingHistory(false);
      }
    };

    loadVitalSignsHistory();
  }, [idAtencion]);

  const reloadHistory = async () => {
    if (!idAtencion) return;
    setLoadingHistory(true);

    try {
      const response = await api.get(`/appointments/${idAtencion}/vital-signs`);
      const nextHistory = response.data || [];
      setCachedValue(String(idAtencion), nextHistory);
      setHistory(nextHistory);
    } catch (error) {
      console.error('Error reloading vital signs history:', error);
    } finally {
      setLoadingHistory(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData((current) => ({ ...current, [field]: value }));
  };

  const handleSubmit = async () => {
    const hasData = Object.values(formData).some((value) => value !== '');
    if (!hasData) {
      window.alert(t('vitalSigns.enterAtLeastOne'));
      return;
    }

    const dataToSend = {
      ta: formData.ta || '',
      fc: parseNumericValue(formData.fc),
      fr: parseNumericValue(formData.fr),
      temp: parseNumericValue(formData.temp),
      spo2: parseNumericValue(formData.spo2),
      peso: parseNumericValue(formData.peso),
      talla: parseNumericValue(formData.talla),
    };

    Object.keys(dataToSend).forEach((key) => {
      if (dataToSend[key] === null) delete dataToSend[key];
    });

    setLoading(true);
    try {
      const response = await api.post(`/appointments/${idAtencion}/vital-signs`, dataToSend);
      if (response.data) {
        setFormData({ ta: '', fc: '', fr: '', temp: '', spo2: '', peso: '', talla: '' });
        await reloadHistory();
      }
    } catch (error) {
      console.error('Error saving vital signs:', error);
      window.alert(error.response?.data?.error || t('vitalSigns.saveError'));
    } finally {
      setLoading(false);
    }
  };

  const fieldConfig = [
    { key: 'ta', label: t('vitalSigns.ta'), placeholder: '120/80', accent: '#ef4444' },
    { key: 'fc', label: t('vitalSigns.fc'), placeholder: 'lpm', accent: '#ef4444' },
    { key: 'fr', label: t('vitalSigns.fr'), placeholder: 'rpm', accent: '#f97316' },
    { key: 'temp', label: t('vitalSigns.temp'), placeholder: '36.5', accent: '#f97316' },
    { key: 'spo2', label: t('vitalSigns.spo2'), placeholder: '98', accent: '#0ea5e9' },
    { key: 'peso', label: t('vitalSigns.peso'), placeholder: '70', accent: '#16a34a' },
    { key: 'talla', label: t('vitalSigns.talla'), placeholder: '1.70', accent: '#7c3aed' },
  ];

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <button type="button" onClick={() => navigate(-1)} style={styles.headerButton}>
          <FiArrowLeft size={20} />
        </button>
        <div>
          <div style={styles.headerEyebrow}>{t('vitalSigns.eyebrow')}</div>
          <h1 style={styles.headerTitle}>{t('vitalSigns.title')}</h1>
        </div>
        <div style={styles.headerSpacer} />
      </div>

      <section style={styles.patientCard}>
        <div style={styles.patientAvatar}><FiUser size={30} color="#fff" /></div>
        <div>
          <h2 style={styles.patientName}>{t('vitalSigns.selectedPatient')}</h2>
          <p style={styles.patientMeta}>{patientLabel}</p>
        </div>
      </section>

      {errorMessage ? <div style={styles.errorCard}>{errorMessage}</div> : null}

      <section style={styles.mainCard}>
        <div style={styles.cardHeader}>
          <FiHeart size={20} />
          <strong>{t('vitalSigns.newRecord')}</strong>
        </div>

        <div style={styles.formGrid}>
          {fieldConfig.map((field) => (
            <label key={field.key} style={styles.fieldGroup}>
              <span style={styles.fieldLabel}>{field.label}</span>
              <input
                style={{ ...styles.fieldInput, borderColor: field.accent + '55' }}
                placeholder={field.placeholder}
                value={formData[field.key]}
                onChange={(event) => handleChange(field.key, event.target.value)}
                disabled={!idAtencion || loading}
              />
            </label>
          ))}
        </div>

        <div style={styles.cardFooter}>
          <button type="button" style={styles.cancelButton} onClick={() => navigate(-1)}>
            {t('vitalSigns.back')}
          </button>
          <button type="button" style={styles.saveButton} onClick={handleSubmit} disabled={!idAtencion || loading}>
            <FiSave size={18} />
            <span>{loading ? t('vitalSigns.saving') : t('vitalSigns.save')}</span>
          </button>
        </div>
      </section>

      <section style={styles.historyCard}>
        <div style={styles.historyHeader}>
          <FiActivity size={18} />
          <strong>{t('vitalSigns.history')}</strong>
          <span style={styles.historyCount}>{t('vitalSigns.records', { count: history.length })}</span>
        </div>

        <div style={styles.historyBody}>
          {loadingHistory ? (
            <div style={styles.statusBox}>{t('vitalSigns.loadingHistory')}</div>
          ) : history.length === 0 ? (
            <div style={styles.statusBox}>{t('vitalSigns.noRecords')}</div>
          ) : (
            history.map((item, index) => (
              <article key={item.id_signos || `${item.fecha_registro || 'sv'}-${index}`} style={styles.historyItem}>
                <div style={styles.historyDate}>{moment(item.fecha_registro).format('DD/MM/YYYY HH:mm')}</div>
                <div style={styles.historyGrid}>
                  {item.ta ? <div style={styles.metricCard}><span style={styles.metricLabel}>TA</span><strong>{item.ta}</strong></div> : null}
                  {item.fc !== undefined && item.fc !== null ? <div style={styles.metricCard}><span style={styles.metricLabel}>FC</span><strong>{item.fc}</strong></div> : null}
                  {item.fr !== undefined && item.fr !== null ? <div style={styles.metricCard}><span style={styles.metricLabel}>FR</span><strong>{item.fr}</strong></div> : null}
                  {item.temp !== undefined && item.temp !== null ? <div style={styles.metricCard}><span style={styles.metricLabel}>Temp</span><strong>{item.temp}°C</strong></div> : null}
                  {item.spo2 !== undefined && item.spo2 !== null ? <div style={styles.metricCard}><span style={styles.metricLabel}>SpO2</span><strong>{item.spo2}%</strong></div> : null}
                  {item.peso !== undefined && item.peso !== null ? <div style={styles.metricCard}><span style={styles.metricLabel}>Peso</span><strong>{item.peso} kg</strong></div> : null}
                  {item.talla !== undefined && item.talla !== null ? <div style={styles.metricCard}><span style={styles.metricLabel}>Talla</span><strong>{item.talla} m</strong></div> : null}
                </div>
              </article>
            ))
          )}
        </div>
      </section>

      <footer style={styles.footer}>
        <FiShield size={14} />
        <span>{t('vitalSigns.footer')}</span>
      </footer>
    </div>
  );
}

const styles = {
  page: {
    minHeight: '100%',
    padding: '24px',
    background: 'linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%)',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: '16px',
    padding: '20px 24px',
    borderRadius: '20px',
    background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
    color: '#fff',
    boxShadow: '0 18px 50px rgba(79, 70, 229, 0.22)',
  },
  headerButton: {
    width: '44px',
    height: '44px',
    border: '1px solid rgba(255,255,255,0.25)',
    borderRadius: '12px',
    background: 'rgba(255,255,255,0.12)',
    color: '#fff',
    display: 'grid',
    placeItems: 'center',
  },
  headerEyebrow: {
    fontSize: '12px',
    letterSpacing: '0.18em',
    textTransform: 'uppercase',
    opacity: 0.8,
    marginBottom: '4px',
  },
  headerTitle: { margin: 0, fontSize: '28px', fontWeight: 800 },
  headerSpacer: { width: '44px', height: '44px' },
  patientCard: {
    marginTop: '20px',
    padding: '18px 20px',
    backgroundColor: '#fff',
    borderRadius: '20px',
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    boxShadow: '0 12px 32px rgba(15, 23, 42, 0.08)',
    borderLeft: '5px solid #ef4444',
  },
  patientAvatar: {
    width: '56px',
    height: '56px',
    borderRadius: '16px',
    backgroundColor: '#ef4444',
    display: 'grid',
    placeItems: 'center',
    flexShrink: 0,
  },
  patientName: { margin: 0, fontSize: '18px', color: '#0f172a' },
  patientMeta: { margin: '6px 0 0', color: '#64748b' },
  errorCard: {
    marginTop: '18px',
    padding: '16px',
    borderRadius: '16px',
    backgroundColor: '#fff7ed',
    border: '1px solid #fdba74',
    color: '#9a3412',
  },
  mainCard: {
    marginTop: '18px',
    backgroundColor: '#fff',
    borderRadius: '24px',
    overflow: 'hidden',
    boxShadow: '0 14px 36px rgba(15, 23, 42, 0.08)',
  },
  cardHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '18px 22px',
    color: '#fff',
    background: 'linear-gradient(135deg, #f56565 0%, #ed8936 100%)',
  },
  formGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
    gap: '14px',
    padding: '22px',
  },
  fieldGroup: { display: 'flex', flexDirection: 'column', gap: '8px' },
  fieldLabel: { fontWeight: 700, color: '#1e293b' },
  fieldInput: {
    padding: '12px 14px',
    borderRadius: '14px',
    border: '1px solid #cbd5e1',
    backgroundColor: '#fff',
    font: 'inherit',
    color: '#0f172a',
  },
  cardFooter: {
    padding: '0 22px 22px',
    display: 'flex',
    gap: '12px',
    justifyContent: 'flex-end',
    flexWrap: 'wrap',
  },
  cancelButton: {
    padding: '12px 18px',
    borderRadius: '12px',
    border: '1px solid #cbd5e1',
    backgroundColor: '#fff',
    color: '#475569',
    fontWeight: 700,
  },
  saveButton: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '12px 18px',
    border: 'none',
    borderRadius: '12px',
    backgroundColor: '#16a34a',
    color: '#fff',
    fontWeight: 700,
  },
  historyCard: {
    marginTop: '18px',
    backgroundColor: '#fff',
    borderRadius: '24px',
    overflow: 'hidden',
    boxShadow: '0 14px 36px rgba(15, 23, 42, 0.08)',
  },
  historyHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '18px 22px',
    color: '#fff',
    background: 'linear-gradient(135deg, #4299e1 0%, #3182ce 100%)',
  },
  historyCount: {
    marginLeft: 'auto',
    padding: '4px 10px',
    borderRadius: '999px',
    backgroundColor: 'rgba(255,255,255,0.2)',
    fontSize: '12px',
  },
  historyBody: { padding: '18px' },
  statusBox: {
    padding: '28px',
    borderRadius: '18px',
    textAlign: 'center',
    backgroundColor: '#f8fafc',
    color: '#64748b',
  },
  historyItem: {
    padding: '16px',
    borderRadius: '18px',
    backgroundColor: '#f8fafc',
    marginBottom: '14px',
  },
  historyDate: { color: '#475569', fontSize: '13px', marginBottom: '12px' },
  historyGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
    gap: '10px',
  },
  metricCard: {
    padding: '12px',
    borderRadius: '14px',
    backgroundColor: '#fff',
    border: '1px solid #e2e8f0',
  },
  metricLabel: {
    display: 'block',
    fontSize: '12px',
    color: '#64748b',
    marginBottom: '4px',
  },
  footer: {
    marginTop: '26px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    color: '#64748b',
    fontSize: '13px',
  },
};