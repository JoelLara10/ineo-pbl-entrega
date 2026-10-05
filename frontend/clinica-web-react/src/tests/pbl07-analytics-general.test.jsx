// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest';
import { cleanup, render, screen } from '@testing-library/react';
import { I18nextProvider } from 'react-i18next';
import { afterEach, describe, expect, it } from 'vitest';
import { createAppI18n } from '../i18n/setup';
import AnalyticsGeneralPanel from '../pages/spark/AnalyticsGeneralPanel';

afterEach(cleanup);

describe('PBL-07 — Analytics general explicado', () => {
  it('presenta tarjetas y una gráfica con título, etiquetas, valores, unidad, periodo, leyenda y explicación', () => {
    const i18n = createAppI18n({ getItem: () => 'es', setItem: () => {} });
    render(<I18nextProvider i18n={i18n}><AnalyticsGeneralPanel data={{
      summary: { total: 24, active: 18 },
      period: { start: '2026-10-01', end: '2026-10-05' },
      trends: [{ day: '2026-10-01', count: 8 }, { day: '2026-10-02', count: 16 }],
    }} /></I18nextProvider>);

    expect(screen.getByText(i18n.t('spark.analyticsGeneral.summaryTitle'))).toBeInTheDocument();
    expect(screen.getByText(i18n.t('spark.analyticsGeneral.chartTitle'))).toBeInTheDocument();
    expect(screen.getByText(i18n.t('spark.analyticsGeneral.unit'))).toBeInTheDocument();
    expect(screen.getByText(i18n.t('spark.analyticsGeneral.legend'))).toBeInTheDocument();
    expect(screen.getByText(i18n.t('spark.analyticsGeneral.chartExplanation'))).toBeInTheDocument();
    expect(screen.getByRole('img')).toHaveAttribute('aria-label', i18n.t('spark.analyticsGeneral.chartAria'));
    expect(screen.getByText('16')).toBeInTheDocument();
  });
});
