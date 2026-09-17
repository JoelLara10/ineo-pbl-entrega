import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { normalizeSparkStatus } from '../services/sparkService';
import { formatLocalDate, formatLocalNumber, getAppLocale } from '../utils/locale';

const source = (path) => readFileSync(resolve(process.cwd(), path), 'utf8');

describe('Sprint 1 de Joel', () => {
  it('PBL-01 registra el panel y los cuatro análisis Spark', () => {
    const router = source('src/router/AppRouter.jsx');
    [
      'admin/spark',
      'admin/spark/analytics',
      'admin/spark/met',
      'admin/spark/clinical',
      'admin/spark/unsupervised',
    ].forEach((path) => expect(router).toContain(`path="${path}"`));
    expect(router).toContain('{isAdminOrAdministrativo && (');
  });

  it('PBL-03 normaliza los estados del contrato Spark', () => {
    expect(normalizeSparkStatus({ status: 'queued' })).toMatchObject({ state: 'processing', running: true });
    expect(normalizeSparkStatus({ status: { state: 'completed' } })).toMatchObject({ state: 'completed', running: false });
    expect(normalizeSparkStatus({ state: 'error', message: 'falló' })).toMatchObject({ state: 'failed', running: false, log: 'falló' });
  });

  it('PBL-06 usa formatos locales consistentes', () => {
    expect(getAppLocale('es-MX')).toBe('es-MX');
    expect(getAppLocale('en-US')).toBe('en-US');
    expect(formatLocalNumber(1234.5, 'es')).not.toBe('—');
    expect(formatLocalNumber(1234.5, 'en')).not.toBe('—');
    expect(formatLocalDate('2026-09-17T12:00:00Z', 'es')).not.toBe('—');
    expect(formatLocalDate('2026-09-17T12:00:00Z', 'en')).not.toBe('—');
  });
});
