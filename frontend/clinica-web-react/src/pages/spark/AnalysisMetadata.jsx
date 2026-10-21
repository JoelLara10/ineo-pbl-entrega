import { useTranslation } from 'react-i18next';
import { formatRegionalDate } from '../../i18n/regional';

export default function AnalysisMetadata({ data }) {
  const { t, i18n } = useTranslation();
  const metadata = data?.metadata;
  const date = (value, style = 'dateTime') => value
    ? formatRegionalDate(value, i18n.language, style) : t('analysisMetadata.unknown');
  return <section className="spark-panel" aria-label={t('analysisMetadata.title')}>
    <h2>{t('analysisMetadata.title')}</h2>
    <dl className="spark-data-grid">
      <div><dt>{t('analysisMetadata.generated')}</dt><dd>{date(metadata?.generated_at || data?.timestamp)}</dd></div>
      <div><dt>{t('analysisMetadata.updated')}</dt><dd>{date(metadata?.last_updated_at)}</dd></div>
      {data?.engine?.name && <div><dt>{t('analysisMetadata.engine')}</dt><dd>{t(`analysisMetadata.engines.${data.engine.name}`, data.engine.name)}</dd></div>}
      <div><dt>{t('analysisMetadata.period')}</dt><dd>{date(metadata?.period?.start, 'date')} — {date(metadata?.period?.end, 'date')}</dd></div>
    </dl>
    <p>{t('analysisMetadata.timezone')}</p>
    {!!metadata?.undated_rows && <p role="status">{t('analysisMetadata.undated', { count: metadata.undated_rows })}</p>}
  </section>;
}
