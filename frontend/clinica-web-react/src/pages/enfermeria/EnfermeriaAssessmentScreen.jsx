import { useCallback, useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiClock, FiRefreshCw, FiSave, FiShield, FiUser } from 'react-icons/fi';
import { usePatient } from '../../context/PatientContext';
import api from '../../services/api';
import moment from 'moment';
import 'moment/locale/es';
import { useTranslation } from 'react-i18next';

export default function EnfermeriaAssessmentScreen() {
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
  const [formData, setFormData] = useState({
    estado_general: '',
    dolor: '',
    movilidad: '',
    riesgo_caidas: '',
    riesgo_upp: '',
    observaciones: '',
  });

  const patientLabel = useMemo(
    () => `Exp: ${idExp || 'N/A'} | Atención: ${idAtencion || 'N/A'}`,
    [idAtencion, idExp]
  );

  const loadHistory = useCallback(async () => {
    if (!idAtencion) return;
    setLoadingHistory(true);
    try {
      const response = await api.get(`/appointments/${idAtencion}/nursing-assessment`);
      setHistory(response.data || []);
    } catch (error) {
      console.error('Error loading nursing assessment history:', error);
    } finally {
      setLoadingHistory(false);
    }
  }, [idAtencion]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleChange = (field, value) => {
    setFormData((current) => ({ ...current, [field]: value }));
  };

  const handleSubmit = async () => {
    if (!idAtencion) return;
    setLoading(true);
    try {
      await api.post(`/appointments/${idAtencion}/nursing-assessment`, formData);
      setFormData({
        estado_general: '',
        dolor: '',
        movilidad: '',
        riesgo_caidas: '',
        riesgo_upp: '',
        observaciones: '',
      });
      await loadHistory();
      window.alert(t('nursingAssessment.saveSuccess'));
    } catch (error) {
      console.error('Error saving nursing assessment:', error);
      window.alert(error.response?.data?.error || t('nursingAssessment.saveError'));
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
          <div style={styles.headerEyebrow}>{t('nursingAssessment.eyebrow')}</div>
          <h1 style={styles.headerTitle}>{t('nursingAssessment.title')}</h1>
        </div>
        <div style={styles.headerSpacer} />
      </div>

      <section style={styles.patientCard}>
        <div style={styles.patientAvatar}><FiUser size={30} color="#fff" /></div>
        <div>
          <h2 style={styles.patientName}>{t('nursingAssessment.selectedPatient')}</h2>
          <p style={styles.patientMeta}>{patientLabel}</p>
        </div>
      </section>

      <section style={styles.mainCard}>
        <div style={styles.formGrid}>
          <input style={styles.input} placeholder={t('nursingAssessment.generalStatePlaceholder')} value={formData.estado_general} onChange={(e) => handleChange('estado_general', e.target.value)} />
          <input style={styles.input} placeholder={t('nursingAssessment.painPlaceholder')} value={formData.dolor} onChange={(e) => handleChange('dolor', e.target.value)} />
          <input style={styles.input} placeholder={t('nursingAssessment.mobilityPlaceholder')} value={formData.movilidad} onChange={(e) => handleChange('movilidad', e.target.value)} />
          <input style={styles.input} placeholder={t('nursingAssessment.fallRiskPlaceholder')} value={formData.riesgo_caidas} onChange={(e) => handleChange('riesgo_caidas', e.target.value)} />
          <input style={styles.input} placeholder={t('nursingAssessment.uprRiskPlaceholder')} value={formData.riesgo_upp} onChange={(e) => handleChange('riesgo_upp', e.target.value)} />
        </div>
        <textarea
          style={styles.textArea}
          rows={4}
          placeholder={t('nursingAssessment.observationsPlaceholder')}
          value={formData.observaciones}
          onChange={(e) => handleChange('observaciones', e.target.value)}
        />
        <div style={styles.buttonRow}>
          <button type="button" style={styles.secondaryButton} onClick={loadHistory} disabled={loadingHistory}>
            <FiRefreshCw size={16} /> {t('nursingAssessment.reload')}
          </button>
          <button type="button" style={styles.primaryButton} onClick={handleSubmit} disabled={!idAtencion || loading}>
            <FiSave size={16} /> {loading ? t('nursingAssessment.saving') : t('nursingAssessment.save')}
          </button>
        </div>
      </section>

      <section style={styles.historyCard}>
        <div style={styles.historyHeader}>
          <FiClock size={16} />
          <strong>{t('nursingAssessment.history')}</strong>
          <span style={styles.count}>{history.length}</span>
        </div>
        {loadingHistory ? <div style={styles.status}>{t('nursingAssessment.loading')}</div> : history.length === 0 ? (
          <div style={styles.status}>{t('nursingAssessment.noRecords')}</div>
        ) : (
          history.map((item, index) => (
            <article key={item.id_valoracion || index} style={styles.historyItem}>
              <div style={styles.historyDate}>{moment(item.fecha_registro).format('DD/MM/YYYY HH:mm')} - Enf. {item.enfermero_nombre || 'No especificado'}</div>
              <div style={styles.historyText}>{t('nursingAssessment.generalStateLabel')} {item.valoracion?.estado_general || 'N/A'}</div>
              <div style={styles.historyText}>{t('nursingAssessment.painLabel')} {item.valoracion?.dolor || 'N/A'}</div>
              <div style={styles.historyText}>{t('nursingAssessment.mobilityLabel')} {item.valoracion?.movilidad || 'N/A'}</div>
              <div style={styles.historyText}>{t('nursingAssessment.fallRiskLabel')} {item.valoracion?.riesgo_caidas || 'N/A'}</div>
              <div style={styles.historyText}>{t('nursingAssessment.uprRiskLabel')} {item.valoracion?.riesgo_upp || 'N/A'}</div>
              <div style={styles.historyText}>{t('nursingAssessment.observationsLabel')} {item.valoracion?.observaciones || t('nursingAssessment.noObservations')}</div>
            </article>
          ))
        )}
      </section>

      <footer style={styles.footer}>
        <FiShield size={14} />
        <span>{t('nursingAssessment.footer')}</span>
      </footer>
    </div>
  );
}

const styles = {
  page: { minHeight: '100%', padding: '24px', background: 'linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%)' },
  header: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px', padding: '20px 24px', borderRadius: '20px', background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)', color: '#fff' },
  headerButton: { width: 44, height: 44, borderRadius: 12, border: '1px solid rgba(255,255,255,0.25)', background: 'rgba(255,255,255,0.12)', color: '#fff', display: 'grid', placeItems: 'center', cursor: 'pointer' },
  headerEyebrow: { fontSize: 12, letterSpacing: 1.2, opacity: 0.85 },
  headerTitle: { margin: '6px 0 0', fontSize: 26 },
  headerSpacer: { width: 44, height: 44 },
  patientCard: { marginTop: 18, background: '#fff', borderRadius: 18, padding: 18, display: 'flex', gap: 12, alignItems: 'center', boxShadow: '0 12px 24px rgba(15, 23, 42, 0.08)' },
  patientAvatar: { width: 52, height: 52, borderRadius: '50%', display: 'grid', placeItems: 'center', background: 'linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%)' },
  patientName: { margin: 0, fontSize: 18, color: '#1f2937' },
  patientMeta: { margin: '4px 0 0', color: '#64748b' },
  mainCard: { marginTop: 18, background: '#fff', borderRadius: 18, padding: 18, boxShadow: '0 12px 24px rgba(15, 23, 42, 0.08)' },
  formGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12 },
  input: { border: '1px solid #cbd5e1', borderRadius: 10, padding: '10px 12px', fontSize: 14 },
  textArea: { marginTop: 12, width: '100%', border: '1px solid #cbd5e1', borderRadius: 10, padding: 12, fontSize: 14, resize: 'vertical' },
  buttonRow: { marginTop: 14, display: 'flex', justifyContent: 'space-between', gap: 10 },
  secondaryButton: { display: 'inline-flex', alignItems: 'center', gap: 6, border: '1px solid #cbd5e1', borderRadius: 10, padding: '10px 14px', background: '#f8fafc', cursor: 'pointer' },
  primaryButton: { display: 'inline-flex', alignItems: 'center', gap: 6, border: 'none', borderRadius: 10, padding: '10px 14px', background: '#2563eb', color: '#fff', cursor: 'pointer' },
  historyCard: { marginTop: 18, background: '#fff', borderRadius: 18, padding: 18, boxShadow: '0 12px 24px rgba(15, 23, 42, 0.08)' },
  historyHeader: { display: 'flex', alignItems: 'center', gap: 8, color: '#334155' },
  count: { marginLeft: 'auto', fontSize: 12, color: '#64748b' },
  status: { marginTop: 12, color: '#64748b' },
  historyItem: { marginTop: 12, border: '1px solid #e2e8f0', borderRadius: 12, padding: 12 },
  historyDate: { fontSize: 13, color: '#475569', marginBottom: 6 },
  historyText: { fontSize: 14, color: '#1e293b', margin: '2px 0' },
  footer: { marginTop: 18, display: 'flex', alignItems: 'center', gap: 8, color: '#64748b', fontSize: 12 },
};
