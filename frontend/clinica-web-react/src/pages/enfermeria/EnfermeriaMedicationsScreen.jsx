import { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiChevronDown, FiChevronUp, FiClock, FiPlus, FiSave, FiShield, FiTrash2, FiUser } from 'react-icons/fi';
import { MdMedication } from 'react-icons/md';
import { usePatient } from '../../context/PatientContext';
import api from '../../services/api';
import moment from 'moment';
import 'moment/locale/es';
import { useTranslation } from 'react-i18next';

const CACHE_PREFIX = 'ineo_web_cache_enfermeria_medications_';
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
    console.error('Error reading medications cache:', error);
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
    console.error('Error saving medications cache:', error);
  }
}

function createMedicationItem(id) {
  return { id, nombre: '', dosis: '', frecuencia: '', via: '', fecha_aplicacion: '' };
}

export default function EnfermeriaMedicationsScreen() {
  const { t, i18n } = useTranslation();
  moment.locale(i18n.language === 'en' ? 'en' : 'es');

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
  const [medications, setMedications] = useState([createMedicationItem(0)]);

  const patientLabel = useMemo(() => `Exp: ${idExp || 'N/A'} | Atención: ${idAtencion || 'N/A'}`, [idAtencion, idExp]);

  useEffect(() => {
    if (!idAtencion) {
      setErrorMessage(t('nursingMeds.selectPatientFirst'));
      return;
    }

    setErrorMessage('');

    const loadMedicationsHistory = async (forceRefresh = false) => {
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
        const response = await api.get(`/appointments/${idAtencion}/medications`);
        const nextHistory = response.data || [];
        setCachedValue(cacheKey, nextHistory);
        setHistory(nextHistory);
      } catch (error) {
        console.error('Error loading medications history:', error);
        const cachedData = getCachedValue(cacheKey);
        if (cachedData) {
          setHistory(cachedData);
        }
      } finally {
        setLoadingHistory(false);
      }
    };

    loadMedicationsHistory();
  }, [idAtencion]);

  const reloadHistory = async () => {
    if (!idAtencion) return;
    setLoadingHistory(true);

    try {
      const response = await api.get(`/appointments/${idAtencion}/medications`);
      const nextHistory = response.data || [];
      setCachedValue(String(idAtencion), nextHistory);
      setHistory(nextHistory);
    } catch (error) {
      console.error('Error reloading medications history:', error);
    } finally {
      setLoadingHistory(false);
    }
  };

  const addMedication = () => {
    setMedications((current) => [...current, createMedicationItem(Date.now() + current.length)]);
  };

  const removeMedication = (id) => {
    if (medications.length === 1) {
      window.alert(t('nursingMeds.minOneMedicationAlert'));
      return;
    }

    setMedications((current) => current.filter((medication) => medication.id !== id));
  };

  const updateMedication = (id, field, value) => {
    setMedications((current) => current.map((medication) => (
      medication.id === id ? { ...medication, [field]: value } : medication
    )));
  };

  const handleSubmit = async () => {
    const validMedications = medications.filter((medication) => medication.nombre.trim() !== '');
    if (!validMedications.length) {
      window.alert(t('nursingMeds.minOneMedication'));
      return;
    }

    setLoading(true);
    try {
      const response = await api.post(`/appointments/${idAtencion}/medications`, {
        medicamentos: validMedications,
      });

      if (response.data) {
        setMedications([createMedicationItem(0)]);
        setShowHistory(true);
        await reloadHistory();
      }
    } catch (error) {
      console.error('Error saving medications:', error);
      window.alert(error.response?.data?.error || t('nursingMeds.saveError'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <button type="button" onClick={() => navigate(-1)} style={styles.headerButton}>
          <FiArrowLeft size={20} />
        </button>
        <div>
          <div style={styles.headerEyebrow}>{t('nursingMeds.eyebrow')}</div>
          <h1 style={styles.headerTitle}>{t('nursingMeds.title')}</h1>
        </div>
        <div style={styles.headerSpacer} />
      </div>

      <section style={styles.patientCard}>
        <div style={styles.patientAvatar}><FiUser size={30} color="#fff" /></div>
        <div>
          <h2 style={styles.patientName}>{t('nursingMeds.selectedPatient')}</h2>
          <p style={styles.patientMeta}>{patientLabel}</p>
        </div>
      </section>

      {errorMessage ? <div style={styles.errorCard}>{errorMessage}</div> : null}

      <section style={styles.mainCard}>
        <div style={styles.cardHeader}>
          <MdMedication size={22} />
          <strong>{t('nursingMeds.registerAdmin')}</strong>
        </div>

        <div style={styles.cardBody}>
          {medications.map((medication, index) => (
            <article key={medication.id} style={styles.medicationCard}>
              <div style={styles.medicationHeader}>
                <strong>{t('nursingMeds.medicationNumber', { num: index + 1 })}</strong>
                {medications.length > 1 ? (
                  <button type="button" style={styles.deleteButton} onClick={() => removeMedication(medication.id)}>
                    <FiTrash2 size={16} />
                    <span>{t('common.delete')}</span>
                  </button>
                ) : null}
              </div>

              <div style={styles.fieldStack}>
                <label style={styles.fieldGroup}>
                  <span style={styles.fieldLabel}>{t('nursingMeds.medicationName')}</span>
                  <input
                    style={styles.fieldInput}
                    placeholder={t('nursingMeds.medicationNamePlaceholder')}
                    value={medication.nombre}
                    onChange={(event) => updateMedication(medication.id, 'nombre', event.target.value)}
                  />
                </label>

                <div style={styles.twoColumnRow}>
                  <label style={styles.fieldGroup}>
                    <span style={styles.fieldLabel}>{t('nursingMeds.dose')}</span>
                    <input
                      style={styles.fieldInput}
                      placeholder={t('nursingMeds.dosePlaceholder')}
                      value={medication.dosis}
                      onChange={(event) => updateMedication(medication.id, 'dosis', event.target.value)}
                    />
                  </label>
                  <label style={styles.fieldGroup}>
                    <span style={styles.fieldLabel}>{t('nursingMeds.frequency')}</span>
                    <input
                      style={styles.fieldInput}
                      placeholder={t('nursingMeds.frequencyPlaceholder')}
                      value={medication.frecuencia}
                      onChange={(event) => updateMedication(medication.id, 'frecuencia', event.target.value)}
                    />
                  </label>
                </div>

                <div style={styles.twoColumnRow}>
                  <label style={styles.fieldGroup}>
                    <span style={styles.fieldLabel}>{t('nursingMeds.route')}</span>
                    <input
                      style={styles.fieldInput}
                      placeholder={t('nursingMeds.routePlaceholder')}
                      value={medication.via}
                      onChange={(event) => updateMedication(medication.id, 'via', event.target.value)}
                    />
                  </label>
                  <label style={styles.fieldGroup}>
                    <span style={styles.fieldLabel}>{t('nursingMeds.applicationDate')}</span>
                    <input
                      style={styles.fieldInput}
                      placeholder="DD/MM/YYYY"
                      value={medication.fecha_aplicacion}
                      onChange={(event) => updateMedication(medication.id, 'fecha_aplicacion', event.target.value)}
                    />
                  </label>
                </div>
              </div>
            </article>
          ))}

          <button type="button" style={styles.addButton} onClick={addMedication}>
            <FiPlus size={18} />
            <span>{t('nursingMeds.addAnother')}</span>
          </button>
        </div>

        <button type="button" style={styles.saveButton} onClick={handleSubmit} disabled={!idAtencion || loading}>
          <FiSave size={18} />
          <span>{loading ? t('nursingMeds.saving') : t('nursingMeds.registerAdmin')}</span>
        </button>
      </section>

      <section style={styles.historyCard}>
        <button type="button" style={styles.historyToggle} onClick={() => setShowHistory((current) => !current)}>
          <div style={styles.historyTitleRow}>
            <FiClock size={18} />
            <strong>{t('nursingMeds.history')}</strong>
            <span style={styles.historyCount}>{history.length} registros</span>
          </div>
          {showHistory ? <FiChevronUp size={18} /> : <FiChevronDown size={18} />}
        </button>

        {showHistory ? (
          <div style={styles.historyBody}>
            {loadingHistory ? (
              <div style={styles.statusBox}>{t('nursingMeds.loadingHistory')}</div>
            ) : history.length === 0 ? (
              <div style={styles.statusBox}>{t('nursingMeds.noAdministrations')}</div>
            ) : (
              history.map((item, index) => (
                <article key={item.id_registro || `${item.fecha_registro || 'med'}-${index}`} style={styles.historyItem}>
                  <div style={styles.historyHeaderRow}>
                    <div style={styles.historyBadge}>{moment(item.fecha_registro).format('DD/MM')}</div>
                    <div>
                      <div style={styles.historyDate}>{moment(item.fecha_registro).format('dddd, D [de] MMMM [de] YYYY [a las] HH:mm')}</div>
                      <div style={styles.historyAuthor}>Enf. {item.enfermero_nombre || 'No especificado'}</div>
                    </div>
                  </div>

                  <div style={styles.historyMedicationList}>
                    {(item.medicamentos || []).map((medication, medIndex) => (
                      <div key={`${medication.nombre || 'med'}-${medIndex}`} style={styles.historyMedicationCard}>
                        <strong style={styles.historyMedicationName}>{medication.nombre}</strong>
                        <div style={styles.historyMedicationMeta}>
                          {medication.dosis ? <span>{t('nursingMeds.dosisLabel')} {medication.dosis}</span> : null}
                          {medication.frecuencia ? <span>{t('nursingMeds.frecuenciaLabel')} {medication.frecuencia}</span> : null}
                          {medication.via ? <span>{t('nursingMeds.viaLabel')} {medication.via}</span> : null}
                          {medication.fecha_aplicacion ? <span>{t('nursingMeds.fechaLabel')} {medication.fecha_aplicacion}</span> : null}
                        </div>
                      </div>
                    ))}
                  </div>
                </article>
              ))
            )}
          </div>
        ) : null}
      </section>

      <footer style={styles.footer}>
        <FiShield size={14} />
        <span>{t('nursingMeds.footer')}</span>
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
    borderLeft: '5px solid #16a34a',
  },
  patientAvatar: {
    width: '56px',
    height: '56px',
    borderRadius: '16px',
    backgroundColor: '#16a34a',
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
    background: 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)',
  },
  cardBody: { padding: '22px' },
  medicationCard: {
    borderRadius: '18px',
    border: '1px solid #e2e8f0',
    overflow: 'hidden',
    marginBottom: '18px',
  },
  medicationHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: '12px',
    padding: '14px 16px',
    backgroundColor: '#f8fafc',
  },
  deleteButton: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    border: 'none',
    background: 'transparent',
    color: '#dc2626',
    fontWeight: 700,
  },
  fieldStack: {
    padding: '16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '14px',
  },
  twoColumnRow: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
    gap: '14px',
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
  addButton: {
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    padding: '13px 16px',
    borderRadius: '14px',
    border: '2px dashed #16a34a',
    backgroundColor: '#f0fdf4',
    color: '#16a34a',
    fontWeight: 700,
  },
  saveButton: {
    margin: '0 22px 22px',
    width: 'calc(100% - 44px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    padding: '14px 18px',
    border: 'none',
    borderRadius: '14px',
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
  historyToggle: {
    width: '100%',
    border: 'none',
    padding: '18px 22px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    color: '#fff',
    background: 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)',
  },
  historyTitleRow: { display: 'flex', alignItems: 'center', gap: '10px' },
  historyCount: {
    marginLeft: '8px',
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
    backgroundColor: '#f8fafc',
    borderRadius: '18px',
    padding: '16px',
    marginBottom: '14px',
  },
  historyHeaderRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '12px',
  },
  historyBadge: {
    minWidth: '52px',
    padding: '12px 10px',
    borderRadius: '14px',
    backgroundColor: '#16a34a',
    color: '#fff',
    fontWeight: 800,
    textAlign: 'center',
  },
  historyDate: { color: '#1e293b', fontWeight: 700, marginBottom: '4px' },
  historyAuthor: { color: '#64748b', fontSize: '13px' },
  historyMedicationList: { display: 'flex', flexDirection: 'column', gap: '10px' },
  historyMedicationCard: {
    padding: '12px',
    borderRadius: '14px',
    backgroundColor: '#fff',
    border: '1px solid #e2e8f0',
  },
  historyMedicationName: { display: 'block', color: '#0f172a', marginBottom: '6px' },
  historyMedicationMeta: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '10px',
    color: '#64748b',
    fontSize: '13px',
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
