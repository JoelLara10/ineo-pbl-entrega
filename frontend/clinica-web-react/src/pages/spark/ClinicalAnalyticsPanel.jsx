import { useTranslation } from 'react-i18next';

const COPY = {
  es: {
    title: 'Resumen de riesgo clínico',
    subtitle: 'Los niveles combinan el valor promedio con rangos clínicos de referencia.',
    distribution: 'Distribución de alertas',
    trends: 'Tendencias y rangos',
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
    distribution: 'Alert distribution',
    trends: 'Trends and ranges',
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
  if (!Number.isFinite(value)) return 'normal';
  if (key === 'heartRate') return value < 50 || value > 120 ? 'high' : value < 60 || value > 100 ? 'medium' : 'normal';
  if (key === 'respiratoryRate') return value < 8 || value > 30 ? 'high' : value < 12 || value > 20 ? 'medium' : 'normal';
  if (key === 'temperature') return value < 35 || value >= 39 ? 'high' : value < 36 || value > 37.5 ? 'medium' : 'normal';
  if (key === 'oxygen') return value < 90 ? 'high' : value < 95 ? 'medium' : 'normal';
  return 'normal';
}

function normalizeMetrics(data) {
  const source = Array.isArray(data?.metrics)
    ? data.metrics
    : Object.entries(data?.metrics || {}).map(([measure, values]) => ({ measure, ...values }));

  return source.map((metric) => {
    const rawName = String(metric.measure || metric.metric || metric.name || '').toLowerCase();
    const key = NORMALIZED_NAMES[rawName] || rawName;
    const average = Number(metric.mean ?? metric.average ?? metric.avg ?? metric.value);
    return {
      key,
      average,
      minimum: Number(metric.minimum ?? metric.min),
      maximum: Number(metric.maximum ?? metric.max),
      count: Number(metric.count ?? metric.total),
    };
  }).filter((metric) => Number.isFinite(metric.average));
}

function formatValue(value) {
  return Number.isFinite(value) ? value.toLocaleString(undefined, { maximumFractionDigits: 2 }) : '—';
}

export default function ClinicalAnalyticsPanel({ data }) {
  const { i18n } = useTranslation();
  const language = i18n.resolvedLanguage?.startsWith('en') ? 'en' : 'es';
  const copy = COPY[language];
  const metrics = normalizeMetrics(data);
  const risks = metrics.map((metric) => ({ ...metric, risk: riskFor(metric.key, metric.average) }));
  const totals = risks.reduce((result, metric) => ({ ...result, [metric.risk]: result[metric.risk] + 1 }), {
    high: 0,
    medium: 0,
    normal: 0,
  });

  if (!metrics.length) return <section className="spark-panel"><p>{copy.noData}</p></section>;

  return (
    <div className="clinical-dashboard">
      <section className="spark-panel" aria-labelledby="clinical-risk-title">
        <h2 id="clinical-risk-title">{copy.title}</h2>
        <p className="spark-chart-explanation">{copy.subtitle}</p>
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
        <div className="clinical-distribution">
          {['high', 'medium', 'normal'].map((risk) => (
            <div className={`clinical-distribution-item risk-${risk}`} key={risk}>
              <strong>{totals[risk]}</strong><span>{copy[risk]}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="spark-panel" aria-labelledby="clinical-trends-title">
        <h2 id="clinical-trends-title">{copy.trends}</h2>
        <div className="clinical-range-list">
          {risks.map((metric) => {
            const [label, unit] = METRIC_LABELS[language][metric.key] || [metric.key, ''];
            return (
              <div className="clinical-range-row" key={metric.key}>
                <strong>{label}</strong>
                <div className="clinical-range-track" aria-hidden="true"><span /></div>
                <span>{copy.minimum} {formatValue(metric.minimum)} / {copy.average} {formatValue(metric.average)} / {copy.maximum} {formatValue(metric.maximum)} {unit}</span>
              </div>
            );
          })}
        </div>
      </section>

      <aside className="clinical-context" aria-label={copy.context}>
        <strong>{copy.context}:</strong> {copy.disclaimer}
      </aside>
    </div>
  );
}
