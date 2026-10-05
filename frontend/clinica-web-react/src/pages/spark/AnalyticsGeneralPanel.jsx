import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { formatRegionalDate, formatRegionalNumber } from '../../i18n/regional';

const simpleEntries = (value) => Object.entries(value || {}).filter(([, item]) =>
  ['string', 'number'].includes(typeof item)
);
const labelOf = (row, index) => row.day || row.date || row.period || row.name || row.measure || `${index + 1}`;
const valueOf = (row) => Number(row.count ?? row.value ?? row.total ?? row.mean ?? 0);

export default function AnalyticsGeneralPanel({ data }) {
  const { t, i18n } = useTranslation();
  const cards = useMemo(() => simpleEntries(data?.summary).slice(0, 6), [data]);
  const series = useMemo(() => [data?.trends, data?.metrics].find(Array.isArray)
    ?.filter((row) => row && typeof row === 'object').slice(0, 12) || [], [data]);
  const max = Math.max(1, ...series.map(valueOf));
  const period = data?.period?.start && data?.period?.end
    ? `${formatRegionalDate(data.period.start, i18n.language)} – ${formatRegionalDate(data.period.end, i18n.language)}`
    : t('spark.analyticsGeneral.currentPeriod');

  return <div className="spark-analytics-general">
    <section aria-labelledby="analytics-summary-title">
      <h2 id="analytics-summary-title">{t('spark.analyticsGeneral.summaryTitle')}</h2>
      <div className="spark-kpi-grid">
        {(cards.length ? cards : [['status', t('spark.resultsReady')]]).map(([key, value]) => <article className="spark-kpi-card" key={key}>
          <h3>{t(`spark.fields.${key}`, key.replaceAll('_', ' '))}</h3>
          <p className="spark-kpi-value">{typeof value === 'number' ? formatRegionalNumber(value, i18n.language, { maximumFractionDigits: 2 }) : value}</p>
          <p className="spark-chart-explanation">{t('spark.analyticsGeneral.cardExplanation')}</p>
        </article>)}
      </div>
    </section>
    {series.length > 0 && <figure className="spark-explained-chart" aria-labelledby="analytics-chart-title">
      <header><div><h2 id="analytics-chart-title">{t('spark.analyticsGeneral.chartTitle')}</h2><p>{t('spark.analyticsGeneral.periodLabel')}: {period}</p></div><span className="spark-chart-unit">{t('spark.analyticsGeneral.unit')}</span></header>
      <div className="spark-bar-chart" role="img" aria-label={t('spark.analyticsGeneral.chartAria')}>
        {series.map((row, index) => <div className="spark-bar-row" key={`${labelOf(row, index)}-${index}`}><span className="spark-bar-label">{labelOf(row, index)}</span><span className="spark-bar-track"><span className="spark-bar-fill" style={{ width: `${(valueOf(row) / max) * 100}%` }} /></span><strong>{formatRegionalNumber(valueOf(row), i18n.language, { maximumFractionDigits: 2 })}</strong></div>)}
      </div>
      <figcaption><span className="spark-chart-legend"><i />{t('spark.analyticsGeneral.legend')}</span><p>{t('spark.analyticsGeneral.chartExplanation')}</p></figcaption>
    </figure>}
  </div>;
}
