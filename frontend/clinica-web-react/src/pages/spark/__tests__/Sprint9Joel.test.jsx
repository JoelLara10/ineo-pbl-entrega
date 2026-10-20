/** @vitest-environment jsdom */
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import ClinicalAnalyticsPanel from '../ClinicalAnalyticsPanel';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({ i18n: { resolvedLanguage: 'es' } }),
}));

describe('Sprint 9 - PBL-09', () => {
  it('muestra valor, unidad, nivel textual y contexto clínico accesible', () => {
    render(<ClinicalAnalyticsPanel data={{ metrics: [
      { measure: 'fc', mean: 130, minimum: 70, maximum: 140 },
      { measure: 'spo2', mean: 93, minimum: 89, maximum: 98 },
      { measure: 'temperatura', mean: 36.8, minimum: 36.2, maximum: 37.2 },
    ] }} />);

    expect(screen.getByText('Frecuencia cardiaca')).toBeInTheDocument();
    expect(screen.getAllByText('Alto').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Medio').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Normal').length).toBeGreaterThan(0);
    expect(screen.getByLabelText('Contexto clínico')).toHaveTextContent('no sustituyen el diagnóstico');
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
