import { useEffect, useId, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { sparkService } from '../../services/sparkService';
import { downloadCsv } from '../../utils/analysisExport';
const empty = () => ({ interpretation: '', decision: '', clarity: '', notes: '' });
export default function AnalysisReview({ type, data }) {
  const { t } = useTranslation();
  const group = useId();
  const [fields, setFields] = useState(empty);
  const [saved, setSaved] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    setFields(empty()); setSaved(null); setError('');
    if (!sparkService.getReview) return undefined;
    setLoading(true);
    sparkService.getReview(type, data.timestamp).then((response) => {
      if (active && response.review) { setFields(response.review); setSaved(response.review); }
    }).catch(() => { if (active) setError('analysisTools.review.loadError'); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [type, data.timestamp]);
  const set = (key, value) => { setFields({ ...fields, [key]: value }); setSaved(null); };
  const submit = async (event) => {
    event.preventDefault(); setSaving(true); setError('');
    try {
      const response = await sparkService.saveReview(type, { ...fields, result_timestamp: data.timestamp });
      setSaved(response.review);
    } catch (failure) { setError(failure.response?.status === 409 ? 'analysisTools.review.stale' : 'analysisTools.review.saveError'); }
    finally { setSaving(false); }
  };
  const exportReview = () => downloadCsv([
    [t('analysisTools.review.title'), t(`spark.types.${type}.title`)],
    [t('analysisTools.filters.from'), data.metadata?.period?.start || ''],
    [t('analysisTools.filters.to'), data.metadata?.period?.end || ''],
    [t('analysisTools.filters.area'), data.metadata?.filters?.area || t('analysisTools.filters.allAreas')],
    [t('analysisTools.export.unit'), [...new Set((data.dashboard?.charts || []).map((chart) => t(`analysisDashboard.units.${chart.unit}`)))].join(' · ')],
    ...(data.comparison ? [[t('analysisTools.comparison.current'), data.comparison.current], [t('analysisTools.comparison.previous'), data.comparison.previous], [t('analysisTools.comparison.previous'), data.comparison.previous_period.start, data.comparison.previous_period.end]] : []),
    [t('analysisTools.review.interpretation'), saved.interpretation],
    [t('analysisTools.review.decision'), saved.decision],
    [t('analysisTools.review.clarity'), t(`analysisTools.review.${saved.clarity}`)],
    [t('analysisTools.review.notes'), saved.notes],
  ], `OftalCore-${type}-evaluation.csv`);
  return <section className="analysis-review spark-panel" aria-label={t('analysisTools.review.title')}>
    <h2>{t('analysisTools.review.title')}</h2><p>{t('analysisTools.review.hint')}</p>
    <form onSubmit={submit}>
      <label>{t('analysisTools.review.interpretation')}<textarea required minLength={10} maxLength={2000} rows={3} disabled={loading || saving} value={fields.interpretation} onChange={(e) => set('interpretation', e.target.value)} /></label>
      <label>{t('analysisTools.review.decision')}<textarea required minLength={10} maxLength={2000} rows={3} disabled={loading || saving} value={fields.decision} onChange={(e) => set('decision', e.target.value)} /></label>
      <fieldset disabled={loading || saving}><legend>{t('analysisTools.review.clarity')}</legend>{['clear', 'acceptable', 'confusing'].map((value) => <label key={value}><input type="radio" name={group} required value={value} checked={fields.clarity === value} onChange={() => set('clarity', value)} />{t(`analysisTools.review.${value}`)}</label>)}</fieldset>
      <label>{t('analysisTools.review.notes')}<textarea maxLength={1000} rows={2} disabled={loading || saving} value={fields.notes} onChange={(e) => set('notes', e.target.value)} /></label>
      <div className="analysis-review-actions"><button type="submit" disabled={loading || saving}>{t(saving ? 'analysisTools.review.saving' : 'analysisTools.review.save')}</button><button type="button" disabled={!saved || saving} onClick={exportReview}>{t('analysisTools.review.export')}</button></div>
    </form>
    {loading && <p role="status">{t('analysisTools.review.loading')}</p>}
    {error && <p role="alert">{t(error)}</p>}{saved && <p role="status">{t('analysisTools.review.saved')}</p>}
  </section>;
}
