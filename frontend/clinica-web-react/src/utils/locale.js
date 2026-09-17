const LOCALES = { es: 'es-MX', en: 'en-US' };

export const getAppLocale = (language) => LOCALES[String(language || '').toLowerCase().split('-')[0]] || LOCALES.es;

export const formatLocalDate = (value, language, options = { dateStyle: 'short' }) => {
  if (!value) return '—';
  const date = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(date.getTime())) return '—';
  return new Intl.DateTimeFormat(getAppLocale(language), options).format(date);
};

export const formatLocalNumber = (value, language, options = {}) => {
  const number = Number(value);
  if (!Number.isFinite(number)) return '—';
  return new Intl.NumberFormat(getAppLocale(language), options).format(number);
};
