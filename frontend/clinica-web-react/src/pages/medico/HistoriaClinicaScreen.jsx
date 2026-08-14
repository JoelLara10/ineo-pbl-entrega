import { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiCheckCircle, FiClipboard, FiRefreshCw, FiSave, FiShield, FiUser } from 'react-icons/fi';
import { usePatient } from '../../context/PatientContext';
import api from '../../services/api';
import { useTranslation } from 'react-i18next';

const CACHE_PREFIX = 'ineo_web_cache_historia_clinica_';
const CACHE_TTL = 5 * 60 * 1000;

const sintomasOptions = ['Dolor', 'Ojo rojo', 'Lagrimeo', 'Vision borrosa', 'Fotofobia', 'Prurito', 'Cuerpo extrano'];
const heredoOptions = ['Diabetes', 'Hipertension', 'Cancer', 'Glaucoma', 'Catarata'];
const nopatOptions = ['Tabaquismo', 'Alcohol', 'Sedentarismo', 'Vacunacion COVID'];

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
    console.error('Error reading historia clinica cache:', error);
    return null;
  }
}

function setCachedValue(key, data, ttl = CACHE_TTL) {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(CACHE_PREFIX + key, JSON.stringify({ data, timestamp: Date.now(), ttl }));
  } catch (error) {
    console.error('Error saving historia clinica cache:', error);
  }
}

export default function HistoriaClinicaScreen() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { selectedPatient } = usePatient();
  const idAtencion = selectedPatient?.id_atencion || location.state?.id_atencion;
  const idExp = selectedPatient?.Id_exp || location.state?.Id_exp;
  const [loading, setLoading] = useState(false);
  const [loadingData, setLoadingData] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [formData, setFormData] = useState({
    motivo_consulta: '', sintomatologia: [], sintomatologia_otros: '', heredo: [], heredo_otros: '', nopat: [], nopat_otros: '', pat_enfermedades: '', pat_medicamentos: '', pat_alergias: '', pat_oculares: '', pat_cirugias: '',
  });

  const patientLabel = useMemo(() => `Paciente: ${idExp || 'N/A'}`, [idExp]);

  useEffect(() => {
    if (!idAtencion || !idExp) {
      setErrorMessage(t('historiaClinica.selectPatientFirst'));
      return;
    }
    setErrorMessage('');

    const loadExistingData = async () => {
      setLoadingData(true);
      const cacheKey = `${idAtencion}_${idExp}`;
      const cachedData = getCachedValue(cacheKey);
      if (cachedData) {
        setFormData(cachedData);
        setLoadingData(false);
        return;
      }
      try {
        const response = await api.get(`/historia-clinica/${idAtencion}/${idExp}`);
        if (response.data && Object.keys(response.data).length > 0) {
          const data = response.data;
          const parsedData = {
            motivo_consulta: data.motivo_consulta || '',
            sintomatologia: data.sintomatologia ? data.sintomatologia.split(',') : [],
            sintomatologia_otros: data.sintomatologia_otros || '',
            heredo: data.heredo ? data.heredo.split(',') : [],
            heredo_otros: data.heredo_otros || '',
            nopat: data.nopat ? data.nopat.split(',') : [],
            nopat_otros: data.nopat_otros || '',
            pat_enfermedades: data.pat_enfermedades || '',
            pat_medicamentos: data.pat_medicamentos || '',
            pat_alergias: data.pat_alergias || '',
            pat_oculares: data.pat_oculares || '',
            pat_cirugias: data.pat_cirugias || '',
          };
          setCachedValue(cacheKey, parsedData);
          setFormData(parsedData);
        }
      } catch (error) {
        console.error('Error loading historia clinica:', error);
        const fallback = getCachedValue(cacheKey);
        if (fallback) setFormData(fallback);
      } finally {
        setLoadingData(false);
      }
    };

    loadExistingData();
  }, [idAtencion, idExp]);

  const toggleCheckbox = (field, value) => {
    setFormData((current) => {
      const exists = current[field].includes(value);
      return { ...current, [field]: exists ? current[field].filter((item) => item !== value) : [...current[field], value] };
    });
  };

  const handleChange = (field, value) => {
    setFormData((current) => ({ ...current, [field]: value }));
  };

  const handleSubmit = async () => {
    if (!formData.motivo_consulta.trim()) {
      window.alert(t('historiaClinica.motivoRequired'));
      return;
    }
    setLoading(true);
    try {
      const dataToSend = {
        ...formData,
        sintomatologia: formData.sintomatologia.join(','),
        heredo: formData.heredo.join(','),
        nopat: formData.nopat.join(','),
      };

      const reloadData = async () => {
        if (!idAtencion || !idExp) return;
        setLoadingData(true);
        try {
          const response = await api.get(`/historia-clinica/${idAtencion}/${idExp}`);
          if (response.data && Object.keys(response.data).length > 0) {
            const data = response.data;
            const parsedData = {
              motivo_consulta: data.motivo_consulta || '',
              sintomatologia: data.sintomatologia ? data.sintomatologia.split(',') : [],
              sintomatologia_otros: data.sintomatologia_otros || '',
              heredo: data.heredo ? data.heredo.split(',') : [],
              heredo_otros: data.heredo_otros || '',
              nopat: data.nopat ? data.nopat.split(',') : [],
              nopat_otros: data.nopat_otros || '',
              pat_enfermedades: data.pat_enfermedades || '',
              pat_medicamentos: data.pat_medicamentos || '',
              pat_alergias: data.pat_alergias || '',
              pat_oculares: data.pat_oculares || '',
              pat_cirugias: data.pat_cirugias || '',
            };
            setCachedValue(`${idAtencion}_${idExp}`, parsedData);
            setFormData(parsedData);
          }
        } catch (error) {
          console.error('Error reloading historia clinica:', error);
        } finally {
          setLoadingData(false);
        }
      };
      const response = await api.post(`/historia-clinica/${idAtencion}/${idExp}`, dataToSend);
      if (response.data) {
        setCachedValue(`${idAtencion}_${idExp}`, formData);
        navigate(-1);
      }
    } catch (error) {
      console.error('Error saving historia clinica:', error);
      window.alert(error.response?.data?.error || t('historiaClinica.saveError'));
    } finally {
      setLoading(false);
    }
  };

  const renderCheckboxGroup = (title, options, field) => (
    <section style={styles.sectionBox}>
      <div style={styles.sectionHeader}><FiClipboard size={18} color="#667eea" /><strong>{title}</strong></div>
      <div style={styles.checkboxGroup}>
        {options.map((option) => {
          const selected = formData[field].includes(option);
          return (
            <button key={option} type="button" style={{ ...styles.checkboxItem, ...(selected ? styles.checkboxItemSelected : {}) }} onClick={() => toggleCheckbox(field, option)}>
              <FiCheckCircle size={16} color={selected ? '#667eea' : '#a0aec0'} />
              <span style={{ ...styles.checkboxLabel, ...(selected ? styles.checkboxLabelSelected : {}) }}>{option}</span>
            </button>
          );
        })}
      </div>
      <input style={styles.input} placeholder={`Otros ${title.toLowerCase()}...`} value={formData[`${field}_otros`]} onChange={(event) => handleChange(`${field}_otros`, event.target.value)} />
    </section>
  );

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <button type="button" onClick={() => navigate(-1)} style={styles.headerButton}><FiArrowLeft size={20} /></button>
        <div>
          <div style={styles.headerEyebrow}>MÉDICO</div>
          <h1 style={styles.headerTitle}>{t('historiaClinica.title')}</h1>
        </div>
        <button type="button" onClick={reloadData} style={styles.headerActionButton} disabled={!idAtencion || !idExp || loadingData}><FiRefreshCw size={18} /></button>
      </div>

      {errorMessage ? <div style={styles.errorCard}>{errorMessage}</div> : null}

      {loadingData ? <div style={styles.loadingCard}>{t('historiaClinica.loadingData')}</div> : (
        <section style={styles.mainCard}>
          <div style={styles.cardHeader}><FiUser size={20} /><strong>{patientLabel}</strong></div>
          <div style={styles.cardBody}>
            <section style={styles.sectionBox}>
              <div style={styles.sectionHeader}><FiClipboard size={18} color="#667eea" /><strong>{t('historiaClinica.motivoConsulta')}</strong></div>
              <textarea style={styles.textArea} placeholder={t('historiaClinica.motivoPlaceholder')} value={formData.motivo_consulta} onChange={(event) => handleChange('motivo_consulta', event.target.value)} rows={3} />
            </section>
            {renderCheckboxGroup(t('historiaClinica.sintomatologiaOcular'), sintomasOptions, 'sintomatologia')}
            {renderCheckboxGroup(t('historiaClinica.antecedentesHeredo'), heredoOptions, 'heredo')}
            {renderCheckboxGroup(t('historiaClinica.antecedentesNoPat'), nopatOptions, 'nopat')}
            <section style={styles.sectionBox}>
              <div style={styles.sectionHeader}><FiClipboard size={18} color="#667eea" /><strong>{t('historiaClinica.antecedentesPat')}</strong></div>
              <input style={styles.input} placeholder={t('historiaClinica.enfermedades')} value={formData.pat_enfermedades} onChange={(event) => handleChange('pat_enfermedades', event.target.value)} />
              <input style={styles.input} placeholder={t('historiaClinica.medicamentos')} value={formData.pat_medicamentos} onChange={(event) => handleChange('pat_medicamentos', event.target.value)} />
              <input style={styles.input} placeholder={t('historiaClinica.alergias')} value={formData.pat_alergias} onChange={(event) => handleChange('pat_alergias', event.target.value)} />
              <input style={styles.input} placeholder={t('historiaClinica.antecedentesOculares')} value={formData.pat_oculares} onChange={(event) => handleChange('pat_oculares', event.target.value)} />
              <input style={styles.input} placeholder={t('historiaClinica.cirugiasPrevias')} value={formData.pat_cirugias} onChange={(event) => handleChange('pat_cirugias', event.target.value)} />
            </section>
          </div>
          <div style={styles.cardFooter}><button type="button" style={styles.cancelButton} onClick={() => navigate(-1)}>{t('historiaClinica.cancel')}</button><button type="button" style={styles.saveButton} onClick={handleSubmit} disabled={!idAtencion || loading}><FiSave size={18} /><span>{loading ? t('historiaClinica.saving') : t('historiaClinica.save')}</span></button></div>
        </section>
      )}

      <footer style={styles.footer}><FiShield size={14} /><span>{t('historiaClinica.footer')}</span></footer>
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
  errorCard: { marginTop: '18px', padding: '16px', borderRadius: '16px', backgroundColor: '#fff7ed', border: '1px solid #fdba74', color: '#9a3412' },
  loadingCard: { marginTop: '20px', padding: '32px', textAlign: 'center', backgroundColor: '#fff', borderRadius: '20px', boxShadow: '0 12px 32px rgba(15, 23, 42, 0.08)' },
  mainCard: { marginTop: '18px', backgroundColor: '#fff', borderRadius: '24px', overflow: 'hidden', boxShadow: '0 14px 36px rgba(15, 23, 42, 0.08)' },
  cardHeader: { display: 'flex', alignItems: 'center', gap: '10px', padding: '18px 22px', color: '#fff', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
  cardBody: { padding: '20px' },
  sectionBox: { marginBottom: '22px' },
  sectionHeader: { display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px', paddingBottom: '8px', borderBottom: '2px solid #667eea', color: '#667eea' },
  input: { width: '100%', padding: '12px 14px', borderRadius: '14px', border: '1px solid #cbd5e1', backgroundColor: '#fff', font: 'inherit', color: '#0f172a', marginBottom: '12px' },
  textArea: { width: '100%', minHeight: '90px', padding: '12px 14px', borderRadius: '14px', border: '1px solid #cbd5e1', backgroundColor: '#fff', resize: 'vertical', font: 'inherit', color: '#0f172a' },
  checkboxGroup: { display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '12px' },
  checkboxItem: { display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 12px', borderRadius: '999px', border: '1px solid #e2e8f0', backgroundColor: '#fff', color: '#475569' },
  checkboxItemSelected: { backgroundColor: '#667eea20', borderColor: '#667eea' },
  checkboxLabel: { color: '#4a5568' },
  checkboxLabelSelected: { color: '#667eea' },
  cardFooter: { padding: '20px', borderTop: '1px solid #e2e8f0', backgroundColor: '#f8fafc', display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' },
  cancelButton: { padding: '12px 18px', borderRadius: '12px', border: '1px solid #cbd5e1', backgroundColor: '#fff', color: '#475569', fontWeight: 700 },
  saveButton: { display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 18px', border: 'none', borderRadius: '12px', backgroundColor: '#16a34a', color: '#fff', fontWeight: 700 },
  footer: { marginTop: '26px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', color: '#64748b', fontSize: '13px' },
};