// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { I18nextProvider } from 'react-i18next';
import { afterEach, expect, it } from 'vitest';
import { createAppI18n } from '../i18n/setup';
import AnalysisDashboard from '../pages/spark/AnalysisCharts';
afterEach(cleanup);
function show(data, language = 'es') {
  const i18n = createAppI18n({ getItem: () => language, setItem: () => {} });
  return render(<I18nextProvider i18n={i18n}><AnalysisDashboard data={data} /></I18nextProvider>);
}
const chart = (key, rows, extra = {}) => ({ key, rows, unit: 'attentions', scope: 'history', mode: 'bar', source: 'atencion', ...extra });
const data = (charts, kpis = []) => ({ metadata: { period: { start: '2026-10-01', end: '2026-10-03' } }, dashboard: { charts, kpis } });
it('labels actual statuses and exposes every value in an accessible table', () => {
  show(data([chart('attentionStatus', [{ label: 'ABIERTA', value: 4 }, { label: 'CERRADA', value: 8 }])]));
  expect(screen.getByRole('heading', { name: 'Atenciones por estado' })).toBeInTheDocument();
  expect(screen.getAllByText('Abiertas')).toHaveLength(2);
  expect(screen.getByRole('img')).toHaveAccessibleName('Atenciones por estado (Atenciones)');
  fireEvent.click(screen.getByText('Ver tabla de datos'));
  expect(screen.getAllByRole('row')).toHaveLength(3);
  expect(screen.getByText(/Fuente: Atenciones/)).toBeInTheDocument();
});
it('plots all dates and zero days without truncating at twelve rows', () => {
  const rows = Array.from({ length: 20 }, (_, i) => ({ label: `2026-10-${String(i + 1).padStart(2, '0')}`, value: i === 1 ? 0 : 3 }));
  show(data([chart('daily', rows, { mode: 'line' })]));
  const svg = screen.getByRole('img');
  expect(svg.querySelectorAll('circle')).toHaveLength(20);
  expect(svg.querySelectorAll('circle')[1]).toHaveAttribute('cy', '225');
  fireEvent.click(screen.getByText('Ver tabla de datos'));
  expect(screen.getAllByRole('row')).toHaveLength(21);
  expect(screen.getByRole('columnheader', { name: 'Fecha' })).toBeInTheDocument();
});
it('uses group labels rather than bed labels and keeps profile units separate', () => {
  show(data([chart('groups', [{ label: '0', value: 5 }], { unit: 'observations' }), chart('profile_temp', [{ label: '0', value: 37 }], { unit: 'temp' })]));
  expect(screen.getAllByText('Grupo 1')).toHaveLength(4);
  expect(screen.queryByText('Libres')).not.toBeInTheDocument();
  expect(screen.getByRole('img', { name: /Promedio de temperatura por grupo \(°C\)/ })).toBeInTheDocument();
});
it('renders unknown occupancy without inventing zero and translates labels', () => {
  show(data([chart('beds', [{ label: '0', value: 2 }, { label: '1', value: 3 }], { unit: 'beds', scope: 'snapshot' })], [{ key: 'occupancy', value: null, unit: 'percent' }]), 'en');
  expect(screen.getByText('—')).toBeInTheDocument();
  expect(screen.getByRole('heading', { name: 'Bed availability' })).toBeInTheDocument();
  expect(screen.getAllByText('Available')).toHaveLength(2);
});
it('shows empty and migration states explicitly', () => {
  const view = show(data([chart('groups', [])]));
  expect(screen.getByRole('status')).toHaveTextContent('No hay registros suficientes');
  view.unmount(); show({});
  expect(screen.getByRole('status')).toHaveTextContent('Pulsa Ejecutar análisis');
});
