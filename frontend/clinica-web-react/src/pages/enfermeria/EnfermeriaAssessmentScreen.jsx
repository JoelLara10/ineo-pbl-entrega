import { formatRegionalDate } from '../../i18n/regional';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  FiArrowLeft,
  FiClipboard,
  FiRefreshCw,
  FiSave,
  FiShield,
  FiUser,
} from 'react-icons/fi';
import { usePatient } from '../../context/PatientContext';
import api from '../../services/api';
import { useTranslation } from 'react-i18next';

/**
 * PBL-21: Valoración de Enfermería unificada al patrón visual aprobado
 * (misma estructura que Signos Vitales / Nota de Enfermería).
 * Lógica, endpoints y validaciones sin cambio funcional.
 */
export default function EnfermeriaAssessmentScreen() {
  const { t, i18n } = useTranslation();
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

  const fieldConfig = useMemo(
    () => [
      {
        key: 'estado_general',
        label: t('nursingAssessment.generalStateLabel'),
        placeholder: t('nursingAssessment.generalStatePlaceholder'),
      },
      {
        key: 'dolor',
        label: t('nursingAssessment.painLabel'),
        placeholder: t('nursingAssessment.painPlaceholder'),
      },
      {
        key: 'movilidad',
        label: t('nursingAssessment.mobilityLabel'),
        placeholder: t('nursingAssessment.mobilityPlaceholder'),
      },
      {
        key: 'riesgo_caidas',
        label: t('nursingAssessment.fallRiskLabel'),
        placeholder: t('nursingAssessment.fallRiskPlaceholder'),
      },
      {
        key: 'riesgo_upp',
        label: t('nursingAssessment.uprRiskLabel'),
        placeholder: t('nursingAssessment.uprRiskPlaceholder'),
      },
    ],
    [t]
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
    if (!idAtencion) {
      setErrorMessage(t('nursingAssessment.selectPatientFirst', 'Selecciona un paciente primero'));
      return;
    }
    setErrorMessage('');
    loadHistory();
  }, [idAtencion, loadHistory, t]);

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
      <header style={styles.header}>
        <button type="button" onClick={() => navigate(-1)} style={styles.headerButton} aria-label={t('common.back', 'Volver')}>
          <FiArrowLeft size={20} />
        </button>
        <div>
          <div style={styles.headerEyebrow}>{t('nursingAssessment.eyebrow')}</div>
          <h1 style={styles.headerTitle}>{t('nursingAssessment.title')}</h1>
        </div>
        <div style={styles.headerSpacer} />
      </header>

      <section style={styles.patientCard}>
        <div style={styles.patientAvatar}>
          <FiUser size={28} color="#fff" />
        </div>
        <div>
          <h2 style={styles.patientName}>{t('nursingAssessment.selectedPatient')}</h2>
          <p style={styles.patientMeta}>{patientLabel}</p>
        </div>
      </section>

      {errorMessage ? <div style={styles.errorCard}>{errorMessage}</div> : null}

      <section style={styles.mainCard}>
        <div style={styles.cardHeader}>
          <FiClipboard size={20} />
          <strong>{t('nursingAssessment.newRecord', 'Nueva valoración')}</strong>
        </div>

        <div style={styles.formGrid}>
          {fieldConfig.map((field) => (
            <label key={field.key} style={styles.fieldGroup}>
              <span style={styles.fieldLabel}>{field.label}</span>
              <input
                style={styles.fieldInput}
                placeholder={field.placeholder}
                value={formData[field.key]}
                onChange={(event) => handleChange(field.key, event.target.value)}
                disabled={!idAtencion || loading}
              />
            </label>
          ))}
        </div>

        <label style={{ ...styles.fieldGroup, marginTop: 14 }}>
          <span style={styles.fieldLabel}>{t('nursingAssessment.observationsLabel')}</span>
          <textarea
            style={styles.textArea}
            rows={4}
            placeholder={t('nursingAssessment.observationsPlaceholder')}
            value={formData.observaciones}
            onChange={(event) => handleChange('observaciones', event.target.value)}
            disabled={!idAtencion || loading}
          />
        </label>

        <div style={styles.cardFooter}>
          <button type="button" style={styles.secondaryButton} onClick={loadHistory} disabled={!idAtencion || loadingHistory}>
            <FiRefreshCw size={16} />
            <span>{t('nursingAssessment.reload')}</span>
          </button>
          <button
            type="button"
            style={styles.primaryButton}
            onClick={handleSubmit}
            disabled={!idAtencion || loading}
          >
            <FiSave size={18} />
            <span>{loading ? t('nursingAssessment.saving') : t('nursingAssessment.save')}</span>
          </button>
        </div>
      </section>

      <section style={styles.historyCard}>
        <div style={styles.historyHeader}>
          <FiClipboard size={18} />
          <strong>{t('nursingAssessment.history')}</strong>
          <span style={styles.historyCount}>
            {t('nursingAssessment.records', { count: history.length, defaultValue: `${history.length} registro(s)` })}
          </span>
        </div>

        <div style={styles.historyBody}>
          {loadingHistory ? (
            <div style={styles.statusBox}>{t('nursingAssessment.loading')}</div>
          ) : history.length === 0 ? (
            <div style={styles.statusBox}>{t('nursingAssessment.noRecords')}</div>
          ) : (
            history.map((item, index) => (
              <article
                key={item.id_valoracion || `${item.fecha_registro || 'va'}-${index}`}
                style={styles.historyItem}
              >
                <div style={styles.historyDate}>
                  {formatRegionalDate(item.fecha_registro, i18n.language, 'dateTime')}
                </div>
                <div style={styles.historyGrid}>
                  <div style={styles.metricCard}>
                    <span style={styles.metricLabel}>{t('nursingAssessment.generalStateLabel')}</span>
                    <strong>{item.estado_general || t('nursingAssessment.notSpecified')}</strong>
                  </div>
                  <div style={styles.metricCard}>
                    <span style={styles.metricLabel}>{t('nursingAssessment.painLabel')}</span>
                    <strong>{item.dolor || t('nursingAssessment.notSpecified')}</strong>
                  </div>
                  <div style={styles.metricCard}>
                    <span style={styles.metricLabel}>{t('nursingAssessment.mobilityLabel')}</span>
                    <strong>{item.movilidad || t('nursingAssessment.notSpecified')}</strong>
                  </div>
                  <div style={styles.metricCard}>
                    <span style={styles.metricLabel}>{t('nursingAssessment.fallRiskLabel')}</span>
                    <strong>{item.riesgo_caidas || t('nursingAssessment.notSpecified')}</strong>
                  </div>
                  <div style={styles.metricCard}>
                    <span style={styles.metricLabel}>{t('nursingAssessment.uprRiskLabel')}</span>
                    <strong>{item.riesgo_upp || t('nursingAssessment.notSpecified')}</strong>
                  </div>
                </div>
                <p style={styles.historyText}>
                  <strong>{t('nursingAssessment.observationsLabel')}</strong>{' '}
                  {item.observaciones || t('nursingAssessment.noObservations')}
                </p>
              </article>
            ))
          )}
        </div>
      </section>

      <footer style={styles.footer}>
        <FiShield size={14} />
        <span>{t('nursingAssessment.footer')}</span>
      </footer>
    </div>
  );
}

const styles = {
  page: {
    minHeight: '100%',
    padding: '24px',
    background: 'linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%)',
    boxSizing: 'border-box',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 16,
    padding: '20px 24px',
    borderRadius: 20,
    background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
    color: '#fff',
    boxShadow: '0 18px 50px rgba(79, 70, 229, 0.22)',
  },
  headerButton: {
    width: 44,
    height: 44,
    border: '1px solid rgba(255,255,255,0.25)',
    borderRadius: 12,
    background: 'rgba(255,255,255,0.12)',
    color: '#fff',
    display: 'grid',
    placeItems: 'center',
    cursor: 'pointer',
    flexShrink: 0,
  },
  headerEyebrow: {
    fontSize: 12,
    letterSpacing: '0.18em',
    textTransform: 'uppercase',
    opacity: 0.85,
    marginBottom: 4,
  },
  headerTitle: {
    margin: 0,
    fontSize: 26,
    fontWeight: 800,
    lineHeight: 1.2,
  },
  headerSpacer: { width: 44, height: 44, flexShrink: 0 },
  patientCard: {
    marginTop: 20,
    padding: '18px 20px',
    backgroundColor: '#fff',
    borderRadius: 18,
    display: 'flex',
    gap: 14,
    alignItems: 'center',
    boxShadow: '0 12px 24px rgba(15, 23, 42, 0.08)',
  },
  patientAvatar: {
    width: 52,
    height: 52,
    borderRadius: '50%',
    display: 'grid',
    placeItems: 'center',
    background: 'linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%)',
    flexShrink: 0,
  },
  patientName: { margin: 0, fontSize: 18, color: '#1f2937', fontWeight: 700 },
  patientMeta: { margin: '4px 0 0', color: '#64748b', fontSize: 14 },
  errorCard: {
    marginTop: 14,
    padding: '12px 16px',
    borderRadius: 12,
    background: '#fef2f2',
    border: '1px solid #fecaca',
    color: '#991b1b',
    fontSize: 14,
  },
  mainCard: {
    marginTop: 18,
    background: '#fff',
    borderRadius: 18,
    padding: 20,
    boxShadow: '0 12px 24px rgba(15, 23, 42, 0.08)',
  },
  cardHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    marginBottom: 16,
    color: '#1e293b',
    fontSize: 16,
  },
  formGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
    gap: 14,
  },
  fieldGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: 6,
  },
  fieldLabel: {
    fontSize: 13,
    fontWeight: 600,
    color: '#475569',
  },
  fieldInput: {
    border: '1px solid #cbd5e1',
    borderRadius: 10,
    padding: '11px 12px',
    fontSize: 14,
    width: '100%',
    boxSizing: 'border-box',
    background: '#f8fafc',
  },
  textArea: {
    width: '100%',
    border: '1px solid #cbd5e1',
    borderRadius: 10,
    padding: 12,
    fontSize: 14,
    resize: 'vertical',
    boxSizing: 'border-box',
    background: '#f8fafc',
    fontFamily: 'inherit',
  },
  cardFooter: {
    marginTop: 18,
    display: 'flex',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
    gap: 10,
  },
  secondaryButton: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 8,
    border: '1px solid #cbd5e1',
    borderRadius: 10,
    padding: '11px 16px',
    background: '#f8fafc',
    color: '#334155',
    cursor: 'pointer',
    fontSize: 14,
    fontWeight: 600,
  },
  primaryButton: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 8,
    border: 'none',
    borderRadius: 10,
    padding: '11px 18px',
    background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
    color: '#fff',
    cursor: 'pointer',
    fontSize: 14,
    fontWeight: 700,
    boxShadow: '0 8px 20px rgba(37, 99, 235, 0.25)',
  },
  historyCard: {
    marginTop: 18,
    background: '#fff',
    borderRadius: 18,
    padding: 20,
    boxShadow: '0 12px 24px rgba(15, 23, 42, 0.08)',
  },
  historyHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    color: '#1e293b',
    marginBottom: 12,
  },
  historyCount: {
    marginLeft: 'auto',
    fontSize: 12,
    color: '#64748b',
    background: '#f1f5f9',
    padding: '4px 10px',
    borderRadius: 999,
  },
  historyBody: { marginTop: 4 },
  statusBox: {
    padding: 16,
    borderRadius: 12,
    background: '#f8fafc',
    color: '#64748b',
    textAlign: 'center',
    fontSize: 14,
  },
  historyItem: {
    marginTop: 12,
    border: '1px solid #e2e8f0',
    borderRadius: 14,
    padding: 14,
    background: '#fafbff',
  },
  historyDate: {
    fontSize: 13,
    color: '#475569',
    marginBottom: 10,
    fontWeight: 600,
  },
  historyGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
    gap: 8,
  },
  metricCard: {
    background: '#fff',
    border: '1px solid #e2e8f0',
    borderRadius: 10,
    padding: '8px 10px',
  },
  metricLabel: {
    display: 'block',
    fontSize: 11,
    color: '#64748b',
    marginBottom: 2,
  },
  historyText: {
    margin: '12px 0 0',
    fontSize: 14,
    color: '#1e293b',
    lineHeight: 1.45,
  },
  footer: {
    marginTop: 20,
    display: 'flex',
    alignItems: 'center',
    gap: 8,
    color: '#64748b',
    fontSize: 12,
  },
};