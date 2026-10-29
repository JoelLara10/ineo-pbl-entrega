import { describe, expect, it } from 'vitest';
import { formatRegionalDate } from '../i18n/regional';

describe('Clinical history uses Mexico time exactly once', () => {
  it.each(['2026-10-29T18:30:00', '2026-10-29T18:30:00Z', '2026-10-29T18:30:00+00:00', '2026-10-29T12:30:00-06:00'])(
    'renders %s as 12 30 in Mexico', (value) => {
      expect(formatRegionalDate(value, 'es', 'dateTime')).toContain('12:30');
      expect(formatRegionalDate(value, 'en', 'dateTime')).toContain('12:30');
    });
  it('keeps calendar-only dates and handles invalid values', () => {
    expect(formatRegionalDate('2026-10-29', 'es')).toBe('29/10/2026');
    expect(formatRegionalDate('not a date', 'es', 'dateTime')).toBe('—');
  });
});
