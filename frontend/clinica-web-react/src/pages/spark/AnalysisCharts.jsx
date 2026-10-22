import { downloadBlob, downloadCsv, makeChartSvg, downloadChartPng } from '../../utils/analysisExport';
import { useId, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { formatRegionalDate, formatRegionalNumber } from '../../i18n/regional';
import './AnalysisCharts.css';

export function AnalysisChart({ chart, period, filters, generatedAt }) {
  const { t, i18n } = useTranslation();
  const titleId = useId();
  const [exportError, setExportError] = useState(false);
  const [exporting, setExporting] = useState(false);
  const n = (value) => formatRegionalNumber(value, i18n.language, { maximumFractionDigits: 2 });
  const tr = (key) => t(`analysisDashboard.${key}`);
  const unit = tr(`units.${chart.unit}`);
  const isGroup = chart.key === 'groups' || chart.key.startsWith('profile_');
  const label = (raw) => {
    if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) return formatRegionalDate(raw, i18n.language);
    if (/^\d{4}-\d{2}$/.test(raw)) return raw;
    if (isGroup) return `${tr('group')} ${Number(raw) + 1}`;
    return t(`analysisDashboard.labels.${raw}`, raw);
  };
  const rows = (chart.rows || []).filter((row) => typeof row.value === 'number' && Number.isFinite(row.value));
  const min = Math.min(0, ...rows.map((row) => row.value));
  const reference = Number.isFinite(chart.reference_value) ? chart.reference_value : null;
  const max = Math.max(1, reference ?? 0, ...rows.map((row) => row.value));
  const hasCounts = rows.some((row) => Number.isFinite(row.count));
  const span = max - min;
  const zero = -min / span * 100;
  const color = chart.key === 'beds' ? '#047857' : chart.key === 'examStatus' || chart.key.startsWith('clinical_') ? '#7c3aed' : chart.key === 'groups' || chart.key.startsWith('profile_') ? '#0e7490' : '#2563eb';
  const steps = [0, 0.25, 0.5, 0.75, 1];
  const title = tr(`charts.${chart.key}.title`);
  const hint = tr(`charts.${chart.key}.hint`);
  const isLine = chart.mode === 'line' && rows.length > 1;
  // Date positions remain proportional to elapsed calendar time.
  const times = rows.map((row) => Date.parse(row.label.length === 7 ? row.label + '-01' : row.label));
  const first = times[0]; const last = times[times.length - 1];
  const x = (index) => 65 + (Number.isFinite(first) && last > first ? (times[index] - first) / (last - first) : index / Math.max(1, rows.length - 1)) * 670;
  const y = (value) => 225 - (value - min) / span * 190;
  const periodText = period?.start && period?.end ? `${formatRegionalDate(period.start, i18n.language)} – ${formatRegionalDate(period.end, i18n.language)}` : tr('unknownPeriod');
  const scope = (chart.scope === 'snapshot' ? tr('snapshot') : `${tr('period')}: ${periodText}`) + ` · ${t('analysisTools.filters.area')}: ${filters?.area || t('analysisTools.filters.allAreas')}`;
  const source = `${tr('source')}: ${t(`analysisDashboard.sources.${chart.source.replaceAll('.', '_')}`, chart.source)}` + (generatedAt ? ` · ${t('analysisMetadata.generated')}: ${formatRegionalDate(generatedAt, i18n.language, 'dateTime')}` : '');
  const exportChart = async (format) => {
    setExportError(false); setExporting(true);
    try {
      if (format === 'csv') {
        downloadCsv([[title], [scope], [source], ...(reference !== null ? [[t('analysisTools.insights.referenceMean'), reference, unit]] : []), [t('analysisDashboard.category'), unit, ...(hasCounts ? [t('analysisTools.observations')] : [])], ...rows.map((row) => [label(row.label), row.value, ...(hasCounts ? [Number.isFinite(row.count) ? row.count : ''] : [])])], `OftalCore-${chart.key}.csv`);
      } else {
        const svg = makeChartSvg({ title, hint, scope, source, unit, rows: rows.map((row) => ({ ...row, rawLabel: row.label, label: label(row.label) })), mode: chart.mode, color, reference, referenceLabel: t('analysisTools.insights.referenceMean'), format: n });
        if (format === 'svg') downloadBlob(new Blob([svg], { type: 'image/svg+xml;charset=utf-8' }), `OftalCore-${chart.key}.svg`);
        else await downloadChartPng(svg, `OftalCore-${chart.key}.png`);
      }
    } catch { setExportError(true); } finally { setExporting(false); }
  };
  return <figure className="analysis-chart" style={{ '--analysis-color': color }} aria-labelledby={titleId}>
    <header><div><h2 id={titleId}>{title}</h2><p>{hint}</p></div><span className="analysis-unit">{unit}</span></header>
    <p className="analysis-chart-scope">{scope} · {source}</p>
    {!rows.length ? <p className="analysis-no-data" role="status">{tr('empty')}</p> : <>
      {isLine ? <div className="analysis-plot"><svg className="analysis-line" viewBox="0 0 800 295" role="img" aria-label={`${title} (${unit})`}>
        <title>{title}</title><desc>{hint} · {unit}</desc>
        {steps.map((step) => <g key={step}><line x1="65" x2="735" y1={y(min + step * span)} y2={y(min + step * span)} className="analysis-gridline" /><text x="56" y={y(min + step * span) + 4} textAnchor="end">{n(min + step * span)}</text></g>)}
        <text x="65" y="18">{unit}</text>
        <polyline points={rows.map((row, i) => `${x(i)},${y(row.value)}`).join(' ')} fill="none" stroke={color} strokeWidth="3" />
        {rows.map((row, i) => <circle key={row.label} cx={x(i)} cy={y(row.value)} r="4" fill={color}><title>{label(row.label)}: {n(row.value)} {unit}</title></circle>)}
        {Array.from(new Set([0, Math.floor((rows.length - 1) / 2), rows.length - 1])).map((i) => <text key={i} x={x(i)} y="250" textAnchor={i === 0 ? 'start' : i === rows.length - 1 ? 'end' : 'middle'}>{label(rows[i].label)}</text>)}
        <text x="400" y="280" textAnchor="middle">{tr('dateAxis')} (UTC)</text>
      </svg></div> : <div className="analysis-bars" role="img" aria-label={`${title} (${unit})`}>
        <div className="analysis-bar-axis"><span>{tr('category')}</span><div>{[0, .5, 1].map((step) => <span key={step}>{n(min + span * step)}</span>)}</div><span>{unit}</span></div>
        {rows.map((row) => <div className="analysis-bar" key={row.label}><span>{label(row.label)}</span><div className="analysis-bar-track"><span className="analysis-zero" style={{ left: `${zero}%` }} />{reference !== null && <span className="analysis-reference-line" style={{ left: `${(reference - min) / span * 100}%` }} />}<i style={{ left: `${row.value < 0 ? (row.value - min) / span * 100 : zero}%`, width: `${Math.abs(row.value) / span * 100}%` }} /></div><strong>{n(row.value)}</strong></div>)}
      </div>}
      {reference !== null && <p className="analysis-reference-caption">{t('analysisTools.insights.referenceMean')}: <strong>{n(reference)} {unit}</strong></p>}
      <div className="analysis-export-actions">{['png', 'svg', 'csv'].map((format) => <button key={format} type="button" disabled={exporting} onClick={() => exportChart(format)} aria-label={`${t('analysisTools.export.download')} ${title} (${format.toUpperCase()})`}>{format.toUpperCase()}</button>)}</div>
      {exportError && <p role="alert">{t('analysisTools.export.error')}</p>}
      <figcaption><span className="analysis-legend"><i />{unit}</span> · {tr('zeroAxis')}</figcaption>
      <details className="analysis-data-table"><summary>{tr('table')}</summary><div><table><caption>{title} ({unit})</caption><thead><tr><th scope="col">{isLine ? tr('dateAxis') : tr('category')}</th><th scope="col">{unit}</th>{hasCounts && <th scope="col">{t('analysisTools.observations')}</th>}</tr></thead><tbody>{rows.map((row) => <tr key={row.label}><th scope="row">{label(row.label)}</th><td>{n(row.value)}</td>{hasCounts && <td>{Number.isFinite(row.count) ? n(row.count) : '—'}</td>}</tr>)}</tbody></table></div></details>
    </>}
  </figure>;
}

export default function AnalysisDashboard({ data }) {
  const { t, i18n } = useTranslation();
  const dashboard = data.dashboard;
  if (!dashboard) return <p className="analysis-update" role="status">{t('analysisDashboard.update')}</p>;
  return <div className="analysis-dashboard">
    {!!dashboard.kpis?.length && <section className="analysis-kpis" aria-label={t('analysisDashboard.summary')}>
      {dashboard.kpis.map((kpi) => <article key={kpi.key}><h2>{t(`analysisDashboard.kpis.${kpi.key}`)}</h2><strong>{kpi.value === null ? '—' : formatRegionalNumber(kpi.value, i18n.language, { maximumFractionDigits: 2 })}</strong><span>{t(`analysisDashboard.units.${kpi.unit}`)}</span></article>)}
    </section>}
    <div className="analysis-chart-grid">{dashboard.charts?.map((chart) => <AnalysisChart key={chart.key} chart={chart} period={data.metadata?.period} filters={data.metadata?.filters} generatedAt={data.timestamp} />)}</div>
    <p className="analysis-footnote">{t('analysisDashboard.aggregateHint')}</p>
  </div>;
}
