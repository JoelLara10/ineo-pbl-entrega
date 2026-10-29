export const regionalLocale = (language) => /^en(?:-|$)/i.test(language || '') ? 'en-US' : 'es-MX';

const dateStyles = {
  date: { year: 'numeric', month: '2-digit', day: '2-digit' },
  short: { month: '2-digit', day: '2-digit' },
  long: { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' },
  dateTime: { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' },
  longDateTime: { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' },
};

export function formatRegionalDate(value, language, style = 'date') {
  if (value === null || value === undefined || value === '') return '—';
  // Calendar-only API values must not move to the previous day in Mexico.
  const calendar = typeof value === 'string' && /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  const timed = style === 'dateTime' || style === 'longDateTime';
  // Legacy clinical API timestamps without an offset came from Mongo UTC.
  // Calendar-only fields and explicit offsets must keep their own semantics.
  const naiveUtc = timed && typeof value === 'string'
    && /^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?$/.test(value);
  const instant = naiveUtc ? value.replace(' ', 'T') + 'Z' : value;
  const date = calendar
    ? new Date(Number(calendar[1]), Number(calendar[2]) - 1, Number(calendar[3]))
    : new Date(instant);
  if (Number.isNaN(date.getTime()) || (calendar && (
    date.getFullYear() !== Number(calendar[1]) || date.getMonth() !== Number(calendar[2]) - 1
    || date.getDate() !== Number(calendar[3])))) return '—';
  const options = { ...(dateStyles[style] || dateStyles.date) };
  if (timed && !calendar) options.timeZone = 'America/Mexico_City';
  return new Intl.DateTimeFormat(regionalLocale(language), options).format(date);
}

export function formatRegionalNumber(value, language, options = {}) {
  if (value === null || value === undefined || value === '' || typeof value === 'boolean') return '—';
  const number = Number(value);
  return Number.isFinite(number) ? new Intl.NumberFormat(regionalLocale(language), options).format(number) : '—';
}
