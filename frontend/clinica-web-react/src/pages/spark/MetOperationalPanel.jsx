import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { formatRegionalDate, formatRegionalNumber } from '../../i18n/regional';
import { DataObject } from './SparkDataViews';
import './MetOperationalPanel.css';

/**
 * Presenta resultados MET en lenguaje operativo para el responsable del hospital.
 * Conserva acceso al detalle técnico en un bloque expandible.
 */
export default function MetOperationalPanel({ data }) {
  const { t, i18n } = useTranslation();
  const [showDetail, setShowDetail] = useState(false);

  const kpis = useMemo(() => {
    const metrics = Array.isArray(data?.metrics) ? data.metrics : [];
    const total = Number(data?.summary?.total) || 0;
    const activeDays = metrics.filter((row) => Number(row?.count) > 0).length;

    let peak = null;
    metrics.forEach((row) => {
      const count = Number(row?.count) || 0;
      if (!peak || count > peak.count) {
        peak = { day: row?.day, count };
      }
    });

    const dailyAverage = activeDays > 0 ? total / activeDays : 0;
    const excluded = Number(data?.quality?.excluded_rows) || 0;
    const sourceRows = Number(data?.quality?.source_rows) || 0;

    return { total, activeDays, peak, dailyAverage, excluded, sourceRows, metrics };
  }, [data]);

  const peakLabel = kpis.peak?.day
    ? formatRegionalDate(kpis.peak.day, i18n.language)
    : t('spark.met.noPeak');

  const decisionPeak = kpis.peak && kpis.peak.count > 0
    ? t('spark.met.decision.highLoad')
    : t('spark.met.decision.stableLoad');

  const decisionQuality = kpis.excluded > 0
    ? t('spark.met.decision.improveCapture')
    : null;

  return (
    <div className="spark-met-panel">
      <section className="spark-kpi-grid" aria-label={t('spark.met.kpiSection')}>
        <article className="spark-kpi-card">
          <h3>{t('spark.met.kpis.total.title')}</h3>
          <p className="spark-kpi-value">
            {formatRegionalNumber(kpis.total, i18n.language, { maximumFractionDigits: 0 })}
          </p>
          <p className="spark-decision">{t('spark.met.kpis.total.hint')}</p>
        </article>

        <article className="spark-kpi-card">
          <h3>{t('spark.met.kpis.activeDays.title')}</h3>
          <p className="spark-kpi-value">
            {formatRegionalNumber(kpis.activeDays, i18n.language, { maximumFractionDigits: 0 })}
          </p>
          <p className="spark-decision">{t('spark.met.kpis.activeDays.hint')}</p>
        </article>

        <article className="spark-kpi-card">
          <h3>{t('spark.met.kpis.peakDay.title')}</h3>
          <p className="spark-kpi-value">
            {peakLabel}
            {kpis.peak?.count != null && (
              <span className="spark-kpi-sub">
                {' · '}
                {formatRegionalNumber(kpis.peak.count, i18n.language, { maximumFractionDigits: 0 })}
                {' '}
                {t('spark.met.atenciones')}
              </span>
            )}
          </p>
          <p className="spark-decision">{decisionPeak}</p>
        </article>

        <article className="spark-kpi-card">
          <h3>{t('spark.met.kpis.dailyAverage.title')}</h3>
          <p className="spark-kpi-value">
            {formatRegionalNumber(kpis.dailyAverage, i18n.language, { maximumFractionDigits: 1 })}
          </p>
          <p className="spark-decision">{t('spark.met.kpis.dailyAverage.hint')}</p>
        </article>
      </section>

      {decisionQuality && (
        <p className="spark-decision spark-decision-banner" role="status">
          {decisionQuality}
        </p>
      )}

      <section className="spark-panel">
        <h2>{t('spark.met.activityByDay')}</h2>
        {kpis.metrics.length === 0 ? (
          <p>{t('spark.met.noActivity')}</p>
        ) : (
          <ul className="spark-met-day-list">
            {kpis.metrics.map((row) => (
              <li key={String(row.day)}>
                <strong>
                  {row.day
                    ? formatRegionalDate(row.day, i18n.language)
                    : t('spark.met.unknownDay')}
                </strong>
                <span>
                  {formatRegionalNumber(Number(row.count) || 0, i18n.language, {
                    maximumFractionDigits: 0,
                  })}
                  {' '}
                  {t('spark.met.atenciones')}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <details
        className="spark-met-detail"
        open={showDetail}
        onToggle={(event) => setShowDetail(event.target.open)}
      >
        <summary>{t('spark.met.detailTitle')}</summary>
        <DataObject data={data} />
      </details>
    </div>
  );
}
