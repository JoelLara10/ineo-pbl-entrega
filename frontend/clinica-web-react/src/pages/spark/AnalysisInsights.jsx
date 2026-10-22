import { useTranslation } from 'react-i18next';
import { formatRegionalDate, formatRegionalNumber } from '../../i18n/regional';
export default function AnalysisInsights({ type, data }) {
  const { t, i18n } = useTranslation();
  if (!data?.timestamp) return null;
  const n = (value) => formatRegionalNumber(value, i18n.language, { maximumFractionDigits: 2 });
  const date = (value) => formatRegionalDate(value, i18n.language);
  const comparison = data.comparison;
  const quality = data.quality;
  const peaks = data.dashboard?.peak_days || [];
  return <aside className="analysis-insights spark-panel" aria-label={t('analysisTools.insights.title')}>
    <h2>{t('analysisTools.insights.title')}</h2>
    <p>{t(`analysisTools.insights.${type}`)}</p>
    {type === 'met' && peaks.length > 0 && <p><strong>{t('analysisTools.insights.peaks')}:</strong> {peaks.map((peak) => `${date(peak.day)} (${n(peak.count)} ${t('analysisDashboard.units.attentions')})`).join(' · ')}{data.dashboard.peak_ties > peaks.length && ` · ${t('analysisTools.insights.morePeaks', { count: data.dashboard.peak_ties })}`}</p>}
    {['clinical', 'unsupervised'].includes(type) && quality && <p>{t('analysisTools.insights.quality', { used: n(quality.used_rows || 0), total: n(quality.source_rows || 0), excluded: n(quality.excluded_rows || 0) })}</p>}
    {!!data.metadata?.excluded_undated_rows && <p>{t('analysisTools.insights.excludedDates', { count: data.metadata.excluded_undated_rows })}</p>}
    {comparison && <section className="analysis-comparison" aria-label={t('analysisTools.comparison.title')}>
      <h3>{t('analysisTools.comparison.title')}</h3>
      <dl><div><dt>{t('analysisTools.comparison.current')}</dt><dd><strong>{n(comparison.current)}</strong> {t('analysisDashboard.units.attentions')}<small>{date(comparison.current_period.start)} – {date(comparison.current_period.end)}</small></dd></div>
        <div><dt>{t('analysisTools.comparison.previous')}</dt><dd><strong>{n(comparison.previous)}</strong> {t('analysisDashboard.units.attentions')}<small>{date(comparison.previous_period.start)} – {date(comparison.previous_period.end)}</small></dd></div>
        <div><dt>{t('analysisTools.comparison.change')}</dt><dd><strong>{comparison.change > 0 ? '+' : ''}{n(comparison.change)}</strong><small>{comparison.change_percent === null ? t('analysisTools.comparison.noBase') : `${comparison.change_percent > 0 ? '+' : ''}${n(comparison.change_percent)} %`}</small></dd></div></dl>
      <p>{t(`analysisTools.comparison.${comparison.change > 0 ? 'rising' : comparison.change < 0 ? 'falling' : 'stable'}`)}</p>
    </section>}
    <p><strong>{t('analysisTools.insights.actionTitle')}:</strong> {t(`analysisTools.insights.action_${type}`)}</p>
    {type === 'unsupervised' && <div className="analysis-group-notes">{data.clusters?.map((group) => <article key={group.cluster}><h3>{t('analysisDashboard.group')} {group.cluster + 1} · {n(group.count)} {t('analysisDashboard.units.observations')}</h3><p>{t('analysisTools.insights.groupMeaning')}</p><ul>{Object.entries(group.means || {}).map(([key, value]) => <li key={key}>{t(`analysisDashboard.labels.${key}`, key)}: <strong>{n(value)} {t(`analysisDashboard.units.${key}`)}</strong></li>)}</ul></article>)}</div>}
  </aside>;
}
