import { formatRegionalDate } from '../../i18n/regional';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiClock, FiRefreshCw, FiSave, FiShield, FiUser } from 'react-icons/fi';
import { usePatient } from '../../context/PatientContext';
import api from '../../services/api';
import { useTranslation } from 'react-i18next';
import './NursingCare.css';

const CARE_STATES = ['EN_PROCESO', 'PENDIENTE', 'COMPLETADO'];

export default function EnfermeriaCareScreen() {
  const { t, i18n } = useTranslation();

  const navigate = useNavigate();
  const location = useLocation();
  const { selectedPatient } = usePatient();
  const idAtencion = selectedPatient?.id_atencion || location.state?.id_atencion;
  const idExp = selectedPatient?.Id_exp || location.state?.Id_exp;
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [historyError, setHistoryError] = useState('');
  const [history, setHistory] = useState([]);
  const [formData, setFormData] = useState({
    diagnostico_enfermeria: '',
    objetivos: '',
    intervenciones: '',
    evaluacion: '',
    estado: 'EN_PROCESO',
    observaciones: '',
  });

  const patientLabel = useMemo(
    () => `Exp: ${idExp || 'N/A'} | Atención: ${idAtencion || 'N/A'}`,
    [idAtencion, idExp]
  );

  const loadHistory = useCallback(async () => {
    if (!idAtencion) return;
    setLoadingHistory(true);
    setHistoryError('');
    try {
      const response = await api.get(`/appointments/${idAtencion}/nursing-care`);
      setHistory(response.data || []);
    } catch (error) {
      console.error('Error loading nursing care history:', error);
      setHistoryError(t('nursingCare.historyError'));
    } finally {
      setLoadingHistory(false);
    }
  }, [idAtencion, t]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleChange = (field, value) => setFormData((current) => ({ ...current, [field]: value }));

  const handleSubmit = async () => {
    if (!idAtencion) return;
    setLoading(true);
    try {
      await api.post(`/appointments/${idAtencion}/nursing-care`, formData);
      setFormData({
        diagnostico_enfermeria: '',
        objetivos: '',
        intervenciones: '',
        evaluacion: '',
        estado: 'EN_PROCESO',
        observaciones: '',
      });
      await loadHistory();
      window.alert(t('nursingCare.saveSuccess'));
    } catch (error) {
      console.error('Error saving nursing care:', error);
      window.alert(error.response?.data?.error || t('nursingCare.saveError'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="nursing-care-page">
      <header className="nursing-care-header">
        <button type="button" onClick={() => navigate(-1)} className="nursing-care-back" aria-label={t('common.back')}>
          <FiArrowLeft size={20} />
        </button>
        <div>
          <div className="nursing-care-eyebrow">{t('nursingCare.eyebrow')}</div>
          <h1>{t('nursingCare.title')}</h1>
        </div>
        <div className="nursing-care-header-spacer" />
      </header>

      <section className="nursing-care-patient" aria-labelledby="nursing-care-patient-title">
        <div className="nursing-care-avatar"><FiUser size={30} color="#fff" /></div>
        <div>
          <h2 id="nursing-care-patient-title">{t('nursingCare.selectedPatient')}</h2>
          <p>{patientLabel}</p>
        </div>
      </section>

      <section className="nursing-care-card" aria-labelledby="nursing-care-form-title">
        <h2 id="nursing-care-form-title">{t('nursingCare.formTitle')}</h2>
        <div className="nursing-care-grid">
          <label>{t('nursingCare.nursingDiagnosisPlaceholder')}<textarea rows={3} value={formData.diagnostico_enfermeria} onChange={(e) => handleChange('diagnostico_enfermeria', e.target.value)} /></label>
          <label>{t('nursingCare.objectivesPlaceholder')}<textarea rows={3} value={formData.objetivos} onChange={(e) => handleChange('objetivos', e.target.value)} /></label>
          <label>{t('nursingCare.interventionsPlaceholder')}<textarea rows={3} value={formData.intervenciones} onChange={(e) => handleChange('intervenciones', e.target.value)} /></label>
          <label>{t('nursingCare.evaluationPlaceholder')}<textarea rows={3} value={formData.evaluacion} onChange={(e) => handleChange('evaluacion', e.target.value)} /></label>
        </div>
        <label className="nursing-care-field">{t('nursingCare.stateLabel')}
          <select value={formData.estado} onChange={(e) => handleChange('estado', e.target.value)}>
            {CARE_STATES.map((state) => <option key={state} value={state}>{t(`nursingCare.states.${state}`)}</option>)}
          </select>
        </label>
        <label className="nursing-care-field">{t('nursingCare.observationsPlaceholder')}
          <textarea rows={3} value={formData.observaciones} onChange={(e) => handleChange('observaciones', e.target.value)} />
        </label>
        <div className="nursing-care-actions">
          <button type="button" className="nursing-care-secondary" onClick={loadHistory} disabled={loadingHistory}>
            <FiRefreshCw size={16} /> {t('nursingCare.reload')}
          </button>
          <button type="button" className="nursing-care-primary" onClick={handleSubmit} disabled={!idAtencion || loading}>
            <FiSave size={16} /> {loading ? t('nursingCare.saving') : t('nursingCare.save')}
          </button>
        </div>
      </section>

      <section className="nursing-care-history" aria-labelledby="nursing-care-history-title">
        <div className="nursing-care-history-header">
          <FiClock size={16} />
          <h2 id="nursing-care-history-title">{t('nursingCare.history')}</h2>
          <span>{history.length}</span>
        </div>
        {loadingHistory ? <div className="nursing-care-status" role="status">{t('nursingCare.loading')}</div>
          : historyError ? <div className="nursing-care-status nursing-care-error" role="alert"><span>{historyError}</span><button type="button" onClick={loadHistory}>{t('common.retry')}</button></div>
          : history.length === 0 ? (
          <div className="nursing-care-status">{t('nursingCare.noRecords')}</div>
        ) : (
          history.map((item, index) => (
            <article key={item.id_cuidado || index} className="nursing-care-history-item">
              <div className="nursing-care-history-date">{formatRegionalDate(item.fecha_registro, i18n.language, 'dateTime')} - Enf. {item.enfermero_nombre || t('nursingCare.notSpecified')}</div>
              <div>{t('nursingCare.stateLabel')} {t(`nursingCare.states.${item.estado || 'EN_PROCESO'}`)}</div>
              <div>{t('nursingCare.diagnosisLabel')} {item.diagnostico_enfermeria || t('nursingCare.notSpecified')}</div>
              <div>{t('nursingCare.objectivesLabel')} {item.objetivos || t('nursingCare.notSpecified')}</div>
              <div>{t('nursingCare.interventionsLabel')} {item.intervenciones || t('nursingCare.notSpecified')}</div>
              <div>{t('nursingCare.evaluationLabel')} {item.evaluacion || t('nursingCare.notSpecified')}</div>
              <div>{t('nursingCare.observationsLabel')} {item.observaciones || t('nursingCare.noObservations')}</div>
            </article>
          ))
        )}
      </section>

      <footer className="nursing-care-footer">
        <FiShield size={14} />
        <span>{t('nursingCare.footer')}</span>
      </footer>
    </main>
  );
}
