import AnalysisFilters, { blankFilters } from './AnalysisFilters';
import AnalysisInsights from './AnalysisInsights';
import AnalysisReview from './AnalysisReview';
import { downloadCsv } from '../../utils/analysisExport';
import { useCallback, useEffect, useId, useMemo, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FiArrowLeft, FiPlay, FiRefreshCw } from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';
import { sparkService } from '../../services/sparkService';
import { formatRegionalDate, formatRegionalNumber } from '../../i18n/regional';
import './Spark.css';
import AnalysisMetadata from './AnalysisMetadata';

const isSimple = (value) => value === null || ['string', 'number', 'boolean'].includes(typeof value);
const prettyKey = (key) => key.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
const hasContent = (value) => {
  if (value === null || value === undefined) return false;
  if (Array.isArray(value)) return value.length > 0;
  if (typeof value === 'object') return Object.keys(value).length > 0;
  return value !== '';
};

function DataValue({ value }) {
  const { t, i18n } = useTranslation();
  if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value)) {
    return <span>{formatRegionalDate(value, i18n.language)}</span>;
  }
  if (isSimple(value)) return <span>{value === null ? '—' : typeof value === 'number'
    ? formatRegionalNumber(value, i18n.language, { maximumFractionDigits: 4 })
    : t(`spark.values.${value}`, String(value))}</span>;
  if (Array.isArray(value)) {
    if (!value.length) return <span>—</span>;
    if (value.every(isSimple)) return <ul>{value.slice(0, 20).map((item, index) => <li key={index}><DataValue value={item} /></li>)}</ul>;
    return <div className="spark-array">{value.slice(0, 12).map((item, index) => <DataObject key={index} data={item} />)}</div>;
  }
  return <DataObject data={value} />;
}

export function DataObject({ data }) {
  const { t } = useTranslation();
  if (!data || typeof data !== 'object') return <DataValue value={data} />;
  return (
    <div className="spark-data-grid">
      {Object.entries(data).map(([key, value]) => (
        <div className={isSimple(value) ? 'spark-datum' : 'spark-nested'} key={key}>
          <strong>{t(`spark.fields.${key}`, prettyKey(key))}</strong>
          <DataValue value={value} />
        </div>
      ))}
    </div>
  );
}

function VisualGallery({ images }) {
  const [sources, setSources] = useState({});
  useEffect(() => {
    let active = true;
    const urls = [];
    Promise.all((images || []).map(async (image) => {
      const url = await sparkService.getImage(image.url);
      if (!active) {
        URL.revokeObjectURL(url);
        return null;
      }
      urls.push(url);
      return [image.filename, url];
    })).then((entries) => active && setSources(Object.fromEntries(entries))).catch(() => {});
    return () => { active = false; urls.forEach((url) => URL.revokeObjectURL(url)); };
  }, [images]);
  if (!images?.length) return null;
  return <div className="spark-gallery">{images.map((image) => sources[image.filename] && (
    <figure key={image.filename}><img src={sources[image.filename]} alt={image.name} /><figcaption>{image.name}</figcaption></figure>
  ))}</div>;
}

export default function SparkAnalysisScreen({ type, ResultsComponent }) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const formId = useId();
  const initialized = useRef(false);
  const [filters, setFilters] = useState(blankFilters);
  const [areas, setAreas] = useState([]);
  const [optionsError, setOptionsError] = useState(false);
  const [data, setData] = useState(null);
  const [status, setStatus] = useState({ state: 'idle', running: false });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [errorKind, setErrorKind] = useState('error');

  const load = useCallback(async () => {
    setLoading(true); setError(''); setErrorKind('error');
    try {
      const [results, currentStatus] = await Promise.all([
        sparkService.getResults(type), sparkService.getStatus(type),
      ]);
      setData(results); setStatus(currentStatus);
      if (!initialized.current) {
        setFilters({ ...blankFilters(), ...(currentStatus.running ? currentStatus.filters : results.metadata?.filters) });
        initialized.current = true;
      }
    } catch (requestError) {
      setErrorKind(requestError.response ? 'error' : 'offline');
      setError(requestError.response?.data?.error || t('spark.loadError'));
    } finally { setLoading(false); }
  }, [t, type]);

  useEffect(() => { load(); }, [load]);
  useEffect(() => {
    let active = true;
    if (!sparkService.getOptions) return undefined;
    sparkService.getOptions().then((response) => { if (active) setAreas(response?.areas || []); })
      .catch(() => { if (active) setOptionsError(true); });
    return () => { active = false; };
  }, [type]);
  useEffect(() => {
    if (!status.running) return undefined;
    let active = true;
    const timer = window.setInterval(async () => {
      try {
        const next = await sparkService.getStatus(type);
        if (!active) return;
        setStatus(next);
        if (!next.running) load();
      } catch (requestError) {
        if (!active) return;
        window.clearInterval(timer);
        setErrorKind(requestError.response ? 'error' : 'offline');
        setError(requestError.response?.data?.error || t('spark.loadError'));
      }
    }, 3000);
    return () => { active = false; window.clearInterval(timer); };
  }, [load, status.running, t, type]);

  const sections = useMemo(
    () => Object.entries(data || {}).filter(
      ([key, value]) =>
        !['available', 'timestamp', 'metadata', 'visualizations', 'contract_version'].includes(key) &&
        hasContent(value)
    ),
    [data]
  );

  const run = async (event) => {
    event?.preventDefault?.();
    setError(''); setErrorKind('error');
    if (!!filters.start_date !== !!filters.end_date || (filters.compare_previous && !filters.start_date) ||
        (filters.start_date && (filters.start_date > filters.end_date || (Date.parse(filters.end_date) - Date.parse(filters.start_date)) / 86400000 >= 1827))) {
      setError(t('analysisTools.filters.invalid')); return;
    }
    try { const activeFilters = Object.fromEntries(Object.entries(filters).filter(([, value]) => value !== '' && value !== false));
      const response = Object.keys(activeFilters).length ? await sparkService.run(type, activeFilters) : await sparkService.run(type);
      setStatus(response.status); }
    catch (requestError) {
      setErrorKind(requestError.response ? 'error' : 'offline');
      setError(requestError.response?.data?.error || t('spark.runError'));
    }
  };

  const applied = { ...blankFilters(), ...data?.metadata?.filters };
  const changed = Object.keys(applied).some((key) => filters[key] !== applied[key]);
  const exportData = () => {
    const rows = [[t(`spark.types.${type}.title`), data.timestamp],
      [t('analysisTools.filters.from'), data.metadata?.period?.start || ''],
      [t('analysisTools.filters.to'), data.metadata?.period?.end || ''],
      [t('analysisTools.filters.area'), data.metadata?.filters?.area || t('analysisTools.filters.allAreas')],
      [t('analysisDashboard.category'), t('analysisTools.export.value'), t('analysisTools.export.unit')]];
    for (const kpi of data.dashboard?.kpis || []) rows.push([t(`analysisDashboard.kpis.${kpi.key}`), kpi.value, t(`analysisDashboard.units.${kpi.unit}`)]);
    for (const chart of data.dashboard?.charts || []) {
      rows.push([], [t(`analysisDashboard.charts.${chart.key}.title`), t(`analysisDashboard.units.${chart.unit}`)]);
      for (const row of chart.rows || []) rows.push([chart.key === 'groups' || chart.key.startsWith('profile_') ? `${t('analysisDashboard.group')} ${Number(row.label) + 1}` : t(`analysisDashboard.labels.${row.label}`, row.label), row.value]);
      if (Number.isFinite(chart.reference_value)) rows.push([t('analysisTools.insights.referenceMean'), chart.reference_value]);
    }
    if (data.comparison) rows.push([], [t('analysisTools.comparison.current'), data.comparison.current], [t('analysisTools.comparison.previous'), data.comparison.previous], [t('analysisTools.comparison.change'), data.comparison.change, t('analysisDashboard.units.attentions')], [t('analysisTools.comparison.change') + ' (%)', data.comparison.change_percent ?? t('analysisTools.comparison.noBase'), '%'], [t('analysisTools.comparison.previous'), data.comparison.previous_period.start, data.comparison.previous_period.end]);
    if ((data.metrics || []).some((metric) => metric.measure)) rows.push([], [t('analysisTools.export.metric'), t('analysisTools.export.mean'), t('analysisTools.export.unit'), t('analysisTools.observations'), t('analysisTools.export.minimum'), t('analysisTools.export.maximum')]);
    for (const metric of data.metrics || []) if (metric.measure) rows.push([t(`analysisDashboard.labels.${metric.measure}`, metric.measure), metric.mean, t(`analysisDashboard.units.${metric.measure}`, ''), metric.count, metric.minimum, metric.maximum]);
    if ((data.trends || []).length) {
      rows.push([], [t('analysisDashboard.dateAxis'), t('analysisTools.export.metric'), t('analysisTools.export.mean'), t('analysisTools.export.unit'), t('analysisTools.observations')]);
      for (const row of data.trends) rows.push([row.day, t(`analysisDashboard.labels.${row.measure}`, row.measure), row.mean, t(`analysisDashboard.units.${row.measure}`, ''), row.count]);
    }
    downloadCsv(rows, `OftalCore-${type}-data.csv`);
  };

  return <main className="spark-page">
    <div className="spark-toolbar">
      <button onClick={() => navigate('/admin/spark')}><FiArrowLeft /> {t('common.back', 'Volver')}</button>
      <div>
        <button onClick={load} disabled={loading}><FiRefreshCw /> {t('spark.refresh')}</button>
        <button className="spark-primary" type="submit" form={formId} disabled={status.running || loading}><FiPlay /> {status.running ? t('spark.running') : t('spark.run')}</button>
      </div>
    </div>
    <header className="spark-header"><span>{t('spark.eyebrow')}</span><h1>{t(`spark.types.${type}.title`)}</h1><p>{t(`spark.types.${type}.description`)}</p></header>
    <AnalysisFilters formId={formId} type={type} value={filters} onChange={setFilters} onSubmit={run} areas={areas} busy={status.running || loading} changed={changed} />
    {optionsError && <p className="analysis-footnote">{t('analysisTools.filters.optionsError')}</p>}
    {data && <AnalysisMetadata data={data} />}
    {data?.timestamp && <p className="analysis-applied">{t('analysisTools.filters.applied')}: {data.metadata?.filters?.area || t('analysisTools.filters.allAreas')} · {t(data.metadata?.filters?.start_date ? 'analysisTools.filters.selectedPeriod' : 'analysisTools.filters.allHistory')}</p>}
    {data?.available && !loading && !status.running && <button className="analysis-download-all" onClick={exportData}>{t('analysisTools.export.all')}</button>}
    {error && <div className="spark-state spark-state-error" role="alert"><h2>{t(`spark.states.${errorKind}.title`)}</h2><p>{errorKind === 'offline' ? t('spark.states.offline.hint') : error}</p><button onClick={load}>{t('common.retry')}</button></div>}
    {!error && loading ? <div className="spark-state" role="status"><h2>{t('spark.states.loading.title')}</h2><p>{t('spark.states.loading.hint')}</p><button onClick={load}>{t('spark.refresh')}</button></div>
      : !error && (status.running || status.state === 'pending' || status.state === 'processing') ? <div className="spark-state spark-state-processing" role="status"><h2>{t('spark.states.processing.title')}</h2><p>{t('spark.states.processing.hint')}</p><button onClick={load}>{t('spark.refresh')}</button></div>
      : !error && status.state === 'failed' ? <div className="spark-state spark-state-error" role="alert"><h2>{t('spark.states.failed.title')}</h2><p>{status.error || t('spark.states.failed.hint')}</p><button onClick={run}>{t('spark.states.failed.action')}</button></div>
      : !error && !data?.available && status.state === 'idle' ? <div className="spark-state"><h2>{t('spark.states.notRun.title')}</h2><p>{t('spark.states.notRun.hint')}</p><button className="spark-primary" onClick={run}>{t('spark.states.notRun.action')}</button></div>
      : !error && !data?.available ? (
      <div className="spark-state"><h2>{t('spark.states.empty.title')}</h2><p>{t(type === 'unsupervised' && data?.quality?.reason === 'insufficient_complete_distinct_rows' ? 'analysisDashboard.insufficientPatterns' : 'spark.states.empty.hint')}</p><button onClick={load}>{t('spark.states.empty.action')}</button></div>
    ) : !error && (ResultsComponent ? <ResultsComponent data={data} /> : <>
      {sections.map(([key, value]) => <section className="spark-panel" key={key}><h2>{t(`spark.sections.${key}`, prettyKey(key))}</h2><DataValue value={value} /></section>)}
      <VisualGallery images={data?.visualizations} />
    </>)}
    {data && !loading && !status.running && <AnalysisInsights type={type} data={data} />}
    {data?.available && data.timestamp && !loading && !status.running && <AnalysisReview key={data.timestamp} type={type} data={data} />}
    {status.state === 'failed' && status.log && <details className="spark-log"><summary>{t('spark.executionFailed')}</summary><pre>{status.log}</pre></details>}
  </main>;
}
