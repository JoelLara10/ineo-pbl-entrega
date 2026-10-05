import { useTranslation } from 'react-i18next';
import { formatRegionalDate, formatRegionalNumber } from '../../i18n/regional';

export const isSimple = (value) => value === null || ['string', 'number', 'boolean'].includes(typeof value);
export const prettyKey = (key) => key.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
export const hasContent = (value) => {
  if (value === null || value === undefined) return false;
  if (Array.isArray(value)) return value.length > 0;
  if (typeof value === 'object') return Object.keys(value).length > 0;
  return value !== '';
};

export function DataValue({ value }) {
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