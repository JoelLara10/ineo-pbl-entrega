/** @vitest-environment jsdom */
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { cleanup, render, screen, within } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import ClinicalAnalyticsPanel from '../ClinicalAnalyticsPanel';

const locale = vi.hoisted(() => ({ language: 'es' }));
afterEach(cleanup);
beforeEach(() => { locale.language = 'es'; });

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ i18n: { resolvedLanguage: locale.language } }),
}));

describe('Sprint 9 - PBL-09', () => {
  it('muestra valor, unidad, nivel textual y contexto clínico accesible', () => {
    render(<ClinicalAnalyticsPanel data={{ metrics: [
      { measure: 'fc', mean: 130, minimum: 70, maximum: 140 },
      { measure: 'spo2', mean: 93, minimum: 89, maximum: 98 },
      { measure: 'temperatura', mean: 36.8, minimum: 36.2, maximum: 37.2 },
    ] }} />);

    expect(screen.getAllByText('Frecuencia cardiaca')).toHaveLength(2);
    expect(screen.getAllByText('Alto').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Medio').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Normal').length).toBeGreaterThan(0);
    expect(screen.getByLabelText('Contexto clínico').textContent).toContain('no sustituyen el diagnóstico');
  });
});

describe('Sprint 9 - PBL-16', () => {
  it('carga las vistas pesadas por demanda con un fallback visible', () => {
    const router = readFileSync(resolve(process.cwd(), 'src/router/AppRouter.jsx'), 'utf8');
    expect(router).toContain("import { lazy, Suspense } from 'react'");
    expect(router).toContain("lazy(() => import('../pages/spark/ClinicalAnalyticsScreen.jsx'))");
    expect(router).toContain('<Suspense fallback={<PageLoader />}>');
  });
});


describe('PBL-09 real API regressions', () => {
  it('recognizes temp and leaves unknown measures unclassified', () => {
    render(<ClinicalAnalyticsPanel data={{ metrics: [
      { measure: 'temp', mean: 39.5, minimum: 39, maximum: 40, count: 2 },
      { measure: 'unexpected', mean: 77, minimum: 70, maximum: 80, count: 2 },
    ] }} />);
    const temperature = screen.getByRole('heading', { name: 'Temperatura' }).closest('article');
    expect(within(temperature).getByText('Alto')).toBeTruthy();
    expect(within(temperature).getByText('°C')).toBeTruthy();
    expect(screen.getAllByText('Sin clasificación').length).toBeGreaterThan(0);
  });
  it('does not invent values for missing or zero-count metrics', () => {
    render(<ClinicalAnalyticsPanel data={{ metrics: [null,
      { measure: 'fc', mean: null, minimum: null, maximum: null, count: 0 },
      { measure: 'temp', mean: '', count: 1 }, { measure: 'spo2', mean: false, count: 1 },
    ] }} />);
    expect(screen.getByText(/No hay métricas clínicas/)).toBeTruthy();
    expect(screen.queryByRole('article')).toBeNull();
  });
  it('positions range markers using the observed values and preserves unknown dates', () => {
    render(<ClinicalAnalyticsPanel data={{ metrics: [
      { measure: 'fc', mean: 75, minimum: 60, maximum: 120, count: 4 },
      { measure: 'temp', mean: 37, minimum: 37, maximum: 37, count: 2 },
    ] }} />);
    const meters = screen.getAllByRole('meter');
    expect(meters[0].getAttribute('aria-valuenow')).toBe('75');
    expect(meters[0].firstElementChild.style.left).toBe('25%');
    expect(meters[1].firstElementChild.style.left).toBe('50%');
    expect(screen.getAllByText(/Periodo analizado: No disponible/)).toHaveLength(2);
    expect(screen.getByText(/No hay al menos dos días/)).toBeTruthy();
  });
  it('renders real chronological trends, units and selected-language dates', () => {
    const data = { metrics: [{ measure: 'temp', mean: 38, minimum: 37, maximum: 39, count: 3 }],
      metadata: { period: { start: '2026-10-12', end: '2026-10-15' } },
      trends: [{ day: '2026-10-15', measure: 'temp', mean: 39, count: 1 },
        { day: '2026-10-12', measure: 'temp', mean: 37.5, count: 2 }] };
    const view = render(<ClinicalAnalyticsPanel data={data} />);
    expect(screen.getByRole('img', { name: 'Temperatura: Tendencias por fecha (°C)' })).toBeTruthy();
    expect(screen.getAllByRole('row')[1].textContent).toContain('12/10/2026');
    expect(screen.getByRole('img').querySelector('polyline').getAttribute('points')).toBe('20,160 580,20');
    locale.language = 'en'; view.rerender(<ClinicalAnalyticsPanel data={data} />);
    expect(screen.getByRole('img', { name: 'Temperature: Trends over time (°C)' })).toBeTruthy();
    expect(screen.getAllByRole('row')[1].textContent).toContain('10/12/2026');
    expect(screen.getByRole('columnheader', { name: 'Average (°C)' })).toBeTruthy();
  });
});


describe('PBL-09 captured HTTP contract', () => {
  it('renders the synthetic response captured from authenticated API and real Spark', () => {
    const data = JSON.parse(readFileSync(resolve(process.cwd(), '../../evidence/sprint-9-joel-zahid/clinical-api-synthetic.json'), 'utf8'));
    render(<ClinicalAnalyticsPanel data={data} />);
    const temperature = screen.getByRole('heading', { name: 'Temperatura' }).closest('article');
    expect(within(temperature).getByText('Alto')).toBeTruthy();
    expect(screen.getAllByRole('img')).toHaveLength(4);
    expect(screen.getAllByRole('table')).toHaveLength(4);
    expect(screen.getAllByText('Periodo analizado: 11/10/2026 – 18/10/2026')).toHaveLength(2);
  });
});
