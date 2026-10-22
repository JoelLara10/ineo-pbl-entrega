import { useId } from 'react';
import { useTranslation } from 'react-i18next';
export const blankFilters = () => ({ start_date: '', end_date: '', area: '', compare_previous: false });
export default function AnalysisFilters({ value, onChange, onSubmit, formId, type, areas, busy, changed }) {
  const { t } = useTranslation();
  const id = useId();
  const set = (key, next) => onChange({ ...value, [key]: next });
  return <form id={formId} className="analysis-filters spark-panel" onSubmit={onSubmit}>
    <h2>{t('analysisTools.filters.title')}</h2>
    <div className="analysis-filter-fields">
      <div><label htmlFor={id + '-from'}>{t('analysisTools.filters.from')}</label><input id={id + '-from'} type="date" value={value.start_date} max={value.end_date || undefined} required={!!value.end_date || value.compare_previous} disabled={busy} onChange={(e) => set('start_date', e.target.value)} /></div>
      <div><label htmlFor={id + '-to'}>{t('analysisTools.filters.to')}</label><input id={id + '-to'} type="date" value={value.end_date} min={value.start_date || undefined} required={!!value.start_date || value.compare_previous} disabled={busy} onChange={(e) => set('end_date', e.target.value)} /></div>
      <div><label htmlFor={id + '-area'}>{t('analysisTools.filters.area')}</label><select id={id + '-area'} value={value.area} disabled={busy} onChange={(e) => set('area', e.target.value)}><option value="">{t('analysisTools.filters.allAreas')}</option>{[...new Set([...areas, ...(value.area ? [value.area] : [])])].map((area) => <option key={area} value={area}>{t(`analysisDashboard.labels.${area}`, area)}</option>)}</select></div>
    </div>
    <div className="analysis-filter-actions">
      {['analytics', 'met'].includes(type) && <label className="analysis-checkbox"><input type="checkbox" checked={value.compare_previous} disabled={busy} onChange={(e) => set('compare_previous', e.target.checked)} />{t('analysisTools.filters.compare')}</label>}
      <button type="button" disabled={busy} onClick={() => onChange(blankFilters())}>{t('analysisTools.filters.clear')}</button>
    </div>
    <p>{t('analysisTools.filters.hint')}</p>
    {type === 'analytics' && <p>{t('analysisTools.insights.snapshotScope')}</p>}
    {changed && <p className="analysis-draft-hint" role="status">{t('analysisTools.filters.changed')}</p>}
  </form>;
}
