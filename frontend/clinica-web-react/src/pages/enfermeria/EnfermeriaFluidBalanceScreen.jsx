import { NursingPatientCard, NursingFormCard, NursingHistoryCard } from '../../components/nursing/NursingSections';
import { formatRegionalDate } from '../../i18n/regional';
import { useCallback, useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiDroplet, FiRefreshCw, FiSave, FiShield } from 'react-icons/fi';
import { usePatient } from '../../context/PatientContext';
import api from '../../services/api';
import { useTranslation } from 'react-i18next';


export default function EnfermeriaFluidBalanceScreen() {
  const { t, i18n } = useTranslation();

  const navigate = useNavigate();
  const location = useLocation();
  const { selectedPatient } = usePatient();
  const idAtencion = selectedPatient?.id_atencion || location.state?.id_atencion;
  const idExp = selectedPatient?.Id_exp || location.state?.Id_exp;
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [history, setHistory] = useState([]);
  const [formData, setFormData] = useState({
    ingresos_orales: '',
    ingresos_iv: '',
    egresos_orina: '',
    egresos_drenajes: '',
    observaciones: '',
  });

  const patientLabel = useMemo(
    () => `Exp: ${idExp || 'N/A'} | Atención: ${idAtencion || 'N/A'}`,
    [idAtencion, idExp]
  );

  const totals = useMemo(() => {
    const numberValue = (value) => Number(value) || 0;
    const inputs = numberValue(formData.ingresos_orales) + numberValue(formData.ingresos_iv);
    const outputs = numberValue(formData.egresos_orina) + numberValue(formData.egresos_drenajes);

    return { inputs, outputs, balance: inputs - outputs };
  }, [formData]);

  const loadHistory = useCallback(async () => {
    if (!idAtencion) return;
    setLoadingHistory(true);
    try {
      const response = await api.get(`/appointments/${idAtencion}/fluid-balance`);
      setHistory(response.data || []);
    } catch (error) {
      console.error('Error loading fluid balance history:', error);
    } finally {
      setLoadingHistory(false);
    }
  }, [idAtencion]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleChange = (field, value) => setFormData((current) => ({ ...current, [field]: value }));

  const handleSubmit = async () => {
    if (!idAtencion) return;
    setLoading(true);
    try {
      await api.post(`/appointments/${idAtencion}/fluid-balance`, formData);
      setFormData({
        ingresos_orales: '',
        ingresos_iv: '',
        egresos_orina: '',
        egresos_drenajes: '',
        observaciones: '',
      });
      await loadHistory();
      window.alert(t('nursingFluidBalance.saveSuccess'));
    } catch (error) {
      console.error('Error saving fluid balance:', error);
      window.alert(error.response?.data?.error || t('nursingFluidBalance.saveError'));
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
          <div style={styles.headerEyebrow}>{t('nursingFluidBalance.eyebrow')}</div>
          <h1 style={styles.headerTitle}>{t('nursingFluidBalance.title')}</h1>
        </div>
        <div style={styles.headerSpacer} />
      </div>

      <NursingPatientCard theme="balance" title={t('nursingFluidBalance.selectedPatient')} label={patientLabel} />

      <NursingFormCard theme="balance" title={t('nursingFluidBalance.newRecord')} icon={<FiDroplet size={22} />}>
        <div style={styles.balanceColumns}>
          <fieldset style={{ ...styles.balanceSection, ...styles.inputSection }}>
            <legend style={{ ...styles.sectionLegend, ...styles.inputLegend }}>
              {t('nursingFluidBalance.inputsLabel')}
            </legend>
            {[
              ['ingresos_orales', t('nursingFluidBalance.oralInputsPlaceholder')],
              ['ingresos_iv', t('nursingFluidBalance.ivInputsPlaceholder')],
            ].map(([field, label]) => (
              <label key={field} style={styles.fieldGroup}>
                <span style={styles.fieldLabel}>{label}</span>
                <div style={styles.inputWithUnit}>
                  <input aria-label={label} style={styles.input} type="number" min="0" placeholder="0" value={formData[field]} onChange={(e) => handleChange(field, e.target.value)} />
                  <span style={styles.unit}>ml</span>
                </div>
              </label>
            ))}
          </fieldset>

          <fieldset style={{ ...styles.balanceSection, ...styles.outputSection }}>
            <legend style={{ ...styles.sectionLegend, ...styles.outputLegend }}>
              {t('nursingFluidBalance.outputsLabel')}
            </legend>
            {[
              ['egresos_orina', t('nursingFluidBalance.urineOutputsPlaceholder')],
              ['egresos_drenajes', t('nursingFluidBalance.drainageOutputsPlaceholder')],
            ].map(([field, label]) => (
              <label key={field} style={styles.fieldGroup}>
                <span style={styles.fieldLabel}>{label}</span>
                <div style={styles.inputWithUnit}>
                  <input aria-label={label} style={styles.input} type="number" min="0" placeholder="0" value={formData[field]} onChange={(e) => handleChange(field, e.target.value)} />
                  <span style={styles.unit}>ml</span>
                </div>
              </label>
            ))}
          </fieldset>
        </div>
        <div style={styles.totalsGrid} aria-live="polite">
          <div style={{ ...styles.totalCard, ...styles.inputTotal }}>
            <span>{t('nursingFluidBalance.inputsLabel')}</span>
            <strong data-testid="total-inputs">{totals.inputs} ml</strong>
          </div>
          <div style={{ ...styles.totalCard, ...styles.outputTotal }}>
            <span>{t('nursingFluidBalance.outputsLabel')}</span>
            <strong data-testid="total-outputs">{totals.outputs} ml</strong>
          </div>
          <div style={{ ...styles.totalCard, ...styles.netTotal }}>
            <span>{t('nursingFluidBalance.netBalance')}</span>
            <strong data-testid="net-balance">{totals.balance} ml</strong>
          </div>
        </div>
        <label style={styles.observationsGroup}>
          <span style={styles.fieldLabel}>{t('nursingFluidBalance.observationsLabel')}</span>
          <textarea
            style={styles.textArea}
            rows={3}
            placeholder={t('nursingFluidBalance.observationsPlaceholder')}
            value={formData.observaciones}
            onChange={(e) => handleChange('observaciones', e.target.value)}
          />
        </label>
        <div style={styles.buttonRow}>
          <button type="button" style={styles.secondaryButton} onClick={loadHistory} disabled={loadingHistory}>
            <FiRefreshCw size={16} /> {t('nursingFluidBalance.reload')}
          </button>
          <button type="button" style={styles.primaryButton} onClick={handleSubmit} disabled={!idAtencion || loading}>
            <FiSave size={16} /> {loading ? t('nursingFluidBalance.saving') : t('nursingFluidBalance.save')}
          </button>
        </div>
      </NursingFormCard>

      <NursingHistoryCard theme="balance" title={t('nursingFluidBalance.history')} count={history.length}>
        {loadingHistory ? <div className="nursing-history-status">{t('nursingFluidBalance.loading')}</div> : history.length === 0 ? (
          <div className="nursing-history-status">{t('nursingFluidBalance.noRecords')}</div>
        ) : (
          history.map((item, index) => (
            <article key={item.id_balance || index} style={styles.historyItem}>
              <div style={styles.historyDate}>{formatRegionalDate(item.fecha_registro, i18n.language, 'dateTime')} - Enf. {item.enfermero_nombre || t('nursingFluidBalance.notSpecified')}</div>
              <div style={styles.historyText}>{t('nursingFluidBalance.inputsLabel') + ' '}{item.total_ingresos || 0} ml</div>
              <div style={styles.historyText}>{t('nursingFluidBalance.outputsLabel') + ' '}{item.total_egresos || 0} ml</div>
              <div style={styles.historyText}>{t('nursingFluidBalance.netBalance') + ' '}{item.balance_neto || 0} ml</div>
              <div style={styles.historyText}>{t('nursingFluidBalance.observationsLabel') + ' '}{item.observaciones || t('nursingFluidBalance.noObservations')}</div>
            </article>
          ))
        )}
      </NursingHistoryCard>

      <footer style={styles.footer}>
        <FiShield size={14} />
        <span>{t('nursingFluidBalance.footer')}</span>
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
  balanceColumns: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16 },
  balanceSection: { margin: 0, padding: 18, borderRadius: 18, display: 'grid', gap: 14 },
  inputSection: { border: '2px solid #bae6fd', background: '#f0f9ff' },
  outputSection: { border: '2px solid #fecaca', background: '#fff7f7' },
  sectionLegend: { padding: '0 8px', fontWeight: 800, fontSize: 15 },
  inputLegend: { color: '#0369a1' },
  outputLegend: { color: '#b91c1c' },
  fieldGroup: { display: 'grid', gap: 7 },
  fieldLabel: { color: '#334155', fontSize: 14, fontWeight: 700 },
  observationsGroup: { display: 'grid', gap: 7, marginTop: 16 },
  inputWithUnit: { display: 'flex', alignItems: 'center', border: '1px solid #cbd5e1', borderRadius: 14, background: '#fff', overflow: 'hidden' },
  input: { width: '100%', border: 'none', padding: '12px 14px', fontSize: 14, background: 'transparent' },
  unit: { padding: '0 12px', color: '#64748b', fontWeight: 700, borderLeft: '1px solid #e2e8f0' },
  totalsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: 10, marginTop: 18 },
  totalCard: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 10, padding: '14px 16px', borderRadius: 14 },
  inputTotal: { color: '#075985', background: '#e0f2fe' },
  outputTotal: { color: '#991b1b', background: '#fee2e2' },
  netTotal: { color: '#4c1d95', background: '#ede9fe' },
  textArea: { width: '100%', border: '1px solid #cbd5e1', borderRadius: 14, padding: 14, fontSize: 14, resize: 'vertical', boxSizing: 'border-box', fontFamily: 'inherit' },
  buttonRow: { marginTop: 14, display: 'flex', justifyContent: 'space-between', gap: 10 },
  secondaryButton: { display: 'inline-flex', alignItems: 'center', gap: 6, border: '1px solid #cbd5e1', borderRadius: 10, padding: '10px 14px', background: '#f8fafc', cursor: 'pointer' },
  primaryButton: { display: 'inline-flex', alignItems: 'center', gap: 6, border: 'none', borderRadius: 14, padding: '12px 18px', background: '#16a34a', color: '#fff', cursor: 'pointer', fontWeight: 700 },
  historyItem: { marginTop: 12, border: '1px solid #e2e8f0', borderRadius: 12, padding: 12 },
  historyDate: { fontSize: 13, color: '#475569', marginBottom: 6 },
  historyText: { fontSize: 14, color: '#1e293b', margin: '2px 0' },
  footer: { marginTop: 18, display: 'flex', alignItems: 'center', gap: 8, color: '#64748b', fontSize: 12 },
};
