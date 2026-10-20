import { useTranslation } from 'react-i18next';
import { formatRegionalDate, formatRegionalNumber } from '../../i18n/regional';

const COPY = {
  es: {
    title: 'Resumen de riesgo clínico',
    subtitle: 'Los niveles combinan el valor promedio con rangos clínicos de referencia.',
    distribution: 'Distribución de indicadores por riesgo',
    distributionHint: 'Cantidad de indicadores según su promedio; no representa el número de pacientes ni de alertas individuales.',
    period: 'Periodo analizado',
    unknownPeriod: 'No disponible',
    range: 'Rangos observados',
    rangeHint: 'La marca indica la posición del promedio entre el mínimo y el máximo observados.',
    trendHint: 'Promedios diarios en orden cronológico. Cada gráfica usa la unidad del indicador.',
    noTrends: 'No hay al menos dos días con observaciones fechadas para mostrar una tendencia.',
    date: 'Fecha',
    count: 'Observaciones',
    unknown: 'Sin clasificación',
    trends: 'Tendencias por fecha',
    high: 'Alto',
    medium: 'Medio',
    normal: 'Normal',
    noData: 'No hay métricas clínicas suficientes para construir el panel.',
    context: 'Contexto clínico',
    disclaimer: 'Los indicadores son agregados y apoyan la priorización; no sustituyen el diagnóstico ni la valoración profesional.',
    minimum: 'Mínimo',
    average: 'Promedio',
    maximum: 'Máximo',
  },
  en: {
    title: 'Clinical risk summary',
    subtitle: 'Levels combine the average value with clinical reference ranges.',
    distribution: 'Indicators by risk level',
    distributionHint: 'Number of indicators classified by their average; this is not a patient or individual alert count.',
    period: 'Analysis period',
    unknownPeriod: 'Unavailable',
    range: 'Observed ranges',
    rangeHint: 'The marker locates the average between the observed minimum and maximum.',
    trendHint: 'Daily averages in chronological order. Each chart uses the indicator unit.',
    noTrends: 'At least two days with dated observations are needed to show a trend.',
    date: 'Date',
    count: 'Observations',
    unknown: 'Unclassified',
    trends: 'Trends over time',
    high: 'High',
    medium: 'Medium',
    normal: 'Normal',
    noData: 'There are not enough clinical metrics to build the dashboard.',
    context: 'Clinical context',
    disclaimer: 'These aggregate indicators support prioritization; they do not replace diagnosis or professional assessment.',
    minimum: 'Minimum',
    average: 'Average',
    maximum: 'Maximum',
  },
};

const NORMALIZED_NAMES = {
  fc: 'heartRate',
  heart_rate: 'heartRate',
  frecuencia_cardiaca: 'heartRate',
  fr: 'respiratoryRate',
  respiratory_rate: 'respiratoryRate',
  frecuencia_respiratoria: 'respiratoryRate',
  temp: 'temperature',
  temperatura: 'temperature',
  temperature: 'temperature',
  spo2: 'oxygen',
  oxygen_saturation: 'oxygen',
  saturacion_oxigeno: 'oxygen',
};

const METRIC_LABELS = {
  es: {
    heartRate: ['Frecuencia cardiaca', 'lpm'],
    respiratoryRate: ['Frecuencia respiratoria', 'rpm'],
    temperature: ['Temperatura', '°C'],
    oxygen: ['Saturación de oxígeno', '%'],
  },
  en: {
    heartRate: ['Heart rate', 'bpm'],
    respiratoryRate: ['Respiratory rate', 'rpm'],
    temperature: ['Temperature', '°C'],
    oxygen: ['Oxygen saturation', '%'],
  },
};

function riskFor(key, value) {
  if (!Number.isFinite(value)) return 'unknown';
  if (key === 'heartRate') return value < 50 || value > 120 ? 'high' : value < 60 || value > 100 ? 'medium' : 'normal';
  if (key === 'respiratoryRate') return value < 8 || value > 30 ? 'high' : value < 12 || value > 20 ? 'medium' : 'normal';
  if (key === 'temperature') return value < 35 || value >= 39 ? 'high' : value < 36 || value > 37.5 ? 'medium' : 'normal';
  if (key === 'oxygen') return value < 90 ? 'high' : value < 95 ? 'medium' : 'normal';
  return 'unknown';
}

function normalizeMetrics(data) {
  const source = Array.isArray(data?.metrics)
    ? data.metrics
    : Object.entries(data?.metrics || {}).map(([measure, values]) => ({ measure, ...values }));

  return source.filter((metric) => metric && typeof metric === 'object').map((metric) => {
    const rawName = String(metric.measure || metric.metric || metric.name || '').toLowerCase();
    const key = NORMALIZED_NAMES[rawName] || rawName;
    const numeric = (value) => value === null || value === undefined || value === '' || typeof value === 'boolean' ? NaN : Number(value);
    const average = numeric(metric.mean ?? metric.average ?? metric.avg ?? metric.value);
    return {
      key,
      average,
      minimum: numeric(metric.minimum ?? metric.min),
      maximum: numeric(metric.maximum ?? metric.max),
      count: numeric(metric.count ?? metric.total),
      day: metric.day,
    };
  }).filter((metric) => Number.isFinite(metric.average) && metric.count !== 0);
}

export default function ClinicalAnalyticsPanel({ data }) {
  const { i18n } = useTranslation();
  const language = (i18n.resolvedLanguage || i18n.language)?.startsWith('en') ? 'en' : 'es';
  const copy = COPY[language];
  const formatValue = (value) => formatRegionalNumber(value, language, { maximumFractionDigits: 2 });
  const dated = normalizeMetrics({ metrics: data?.trends || [] }).filter((row) => /^\d{4}-\d{2}-\d{2}$/.test(row.day) && formatRegionalDate(row.day, language) !== '—').sort((a, b) => a.day.localeCompare(b.day));
  const series = Object.entries(METRIC_LABELS[language]).map(([key, labels]) => ({ key, labels, points: dated.filter((row) => row.key === key) })).filter((series) => new Set(series.points.map((row) => row.day)).size >= 2);
  const period = data?.metadata?.period || data?.period;
  const periodText = period?.start && period?.end ? `${formatRegionalDate(period.start, language)} – ${formatRegionalDate(period.end, language)}` : copy.unknownPeriod;
  const metrics = normalizeMetrics(data);
  const risks = metrics.map((metric) => ({ ...metric, risk: riskFor(metric.key, metric.average) }));
  const totals = risks.reduce((result, metric) => ({ ...result, [metric.risk]: result[metric.risk] + 1 }), {
    high: 0,
    medium: 0,
    normal: 0,
    unknown: 0,
  });

  if (!metrics.length) return <section className="spark-panel"><p>{copy.noData}</p></section>;

  return (
    <div className="clinical-dashboard">
      <section className="spark-panel" aria-labelledby="clinical-risk-title">
        <h2 id="clinical-risk-title">{copy.title}</h2>
        <p className="spark-chart-explanation">{copy.subtitle}</p>
        <p>{copy.period}: {periodText}</p>
        <div className="clinical-risk-grid">
          {risks.map((metric) => {
            const [label, unit] = METRIC_LABELS[language][metric.key] || [metric.key, ''];
            return (
              <article className={`clinical-risk-card risk-${metric.risk}`} key={metric.key}>
                <span className="clinical-risk-badge">{copy[metric.risk]}</span>
                <h3>{label}</h3>
                <p className="clinical-risk-value">{formatValue(metric.average)} <small>{unit}</small></p>
                <p>{copy.minimum}: {formatValue(metric.minimum)} · {copy.maximum}: {formatValue(metric.maximum)}</p>
              </article>
            );
          })}
        </div>
      </section>

      <section className="spark-panel" aria-labelledby="clinical-distribution-title">
        <h2 id="clinical-distribution-title">{copy.distribution}</h2>
        <p>{copy.distributionHint}</p>
        <div className="clinical-distribution">
          {['high', 'medium', 'normal', ...(totals.unknown ? ['unknown'] : [])].map((risk) => (
            <div className={`clinical-distribution-item risk-${risk}`} key={risk}>
              <strong>{totals[risk]}</strong><span>{copy[risk]}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="spark-panel" aria-labelledby="clinical-trends-title">
        <h2 id="clinical-trends-title">{copy.range}</h2>
        <p>{copy.rangeHint}</p>
        <div className="clinical-range-list">
          {risks.map((metric) => {
            const [label, unit] = METRIC_LABELS[language][metric.key] || [metric.key, ''];
            return (
              <div className="clinical-range-row" key={metric.key}>
                <strong>{label}</strong>
                {Number.isFinite(metric.minimum) && Number.isFinite(metric.maximum) && metric.minimum <= metric.average && metric.average <= metric.maximum ? <div className="clinical-range-track" role="meter" aria-label={`${label}: ${copy.average}`} aria-valuemin={metric.minimum} aria-valuemax={metric.maximum} aria-valuenow={metric.average} aria-valuetext={`${formatValue(metric.average)} ${unit}`}><span style={{ left: `${metric.maximum === metric.minimum ? 50 : (metric.average - metric.minimum) / (metric.maximum - metric.minimum) * 100}%` }} /></div> : <span>—</span>}
                <span>{copy.minimum} {formatValue(metric.minimum)} / {copy.average} {formatValue(metric.average)} / {copy.maximum} {formatValue(metric.maximum)} {unit}</span>
              </div>
            );
          })}
        </div>
      </section>

      <section className="spark-panel" aria-labelledby="clinical-daily-title">
        <h2 id="clinical-daily-title">{copy.trends}</h2>
        <p>{copy.trendHint}</p><p>{copy.period}: {periodText}</p>
        {!series.length && <p>{copy.noTrends}</p>}
        {series.map(({ key, labels: [label, unit], points }) => {
          const min = Math.min(...points.map((point) => point.average));
          const max = Math.max(...points.map((point) => point.average));
          const times = points.map((point) => Date.parse(point.day));
          const start = times[0]; const end = times[times.length - 1];
          const coords = points.map((point, index) => `${20 + (times[index] - start) / (end - start) * 560},${max === min ? 90 : 160 - (point.average - min) / (max - min) * 140}`).join(' ');
          return <figure className="clinical-trend" key={key}>
            <figcaption>{label} — {copy.average} ({unit})</figcaption>
            <svg viewBox="0 0 600 180" role="img" aria-label={`${label}: ${copy.trends} (${unit})`}><polyline points={coords} fill="none" stroke="currentColor" strokeWidth="3" />{coords.split(' ').map((pair, index) => { const [cx, cy] = pair.split(','); return <circle key={points[index].day} cx={cx} cy={cy} r="5"><title>{formatRegionalDate(points[index].day, language)}: {formatValue(points[index].average)} {unit}</title></circle>; })}</svg>
            <table><thead><tr><th scope="col">{copy.date}</th><th scope="col">{copy.average} ({unit})</th><th scope="col">{copy.count}</th></tr></thead><tbody>{points.map((point) => <tr key={point.day}><td>{formatRegionalDate(point.day, language)}</td><td>{formatValue(point.average)}</td><td>{formatValue(point.count)}</td></tr>)}</tbody></table>
          </figure>;
        })}
      </section>

      <aside className="clinical-context" aria-label={copy.context}>
        <strong>{copy.context}:</strong> {copy.disclaimer}
      </aside>
    </div>
  );
}
