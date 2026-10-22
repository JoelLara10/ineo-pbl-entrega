// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest';
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { I18nextProvider } from 'react-i18next';
import { MemoryRouter } from 'react-router-dom';
import { createAppI18n } from '../i18n/setup';
import SparkAnalysisScreen from '../pages/spark/SparkAnalysisScreen';
import AnalysisDashboard from '../pages/spark/AnalysisCharts';
import AnalysisInsights from '../pages/spark/AnalysisInsights';
import AnalysisReview from '../pages/spark/AnalysisReview';
import { sparkService } from '../services/sparkService';
import { makeCsv, makeChartSvg } from '../utils/analysisExport';
vi.mock('../services/sparkService', () => ({ sparkService: {
  getResults: vi.fn(), getStatus: vi.fn(), getOptions: vi.fn(), getReview: vi.fn(), saveReview: vi.fn(), run: vi.fn(),
} }));
afterEach(cleanup);
beforeEach(() => {
  vi.clearAllMocks();
  sparkService.getOptions.mockResolvedValue({ areas: ['CONSULTA', 'RECUPERACION'] });
  sparkService.getReview.mockResolvedValue({ review: null });
  sparkService.getStatus.mockResolvedValue({ state: 'completed', running: false });
  sparkService.run.mockResolvedValue({ status: { state: 'pending', running: true } });
});
const snapshot = () => ({ available: true, timestamp: '2026-10-22T10:00:00Z',
  metadata: { period: { start: '2026-10-01', end: '2026-10-03' }, filters: {} },
  summary: { total: 4 }, dashboard: { kpis: [{ key: 'attentions', value: 4, unit: 'attentions' }], charts: [] } });
function show(node, language = 'es') {
  const i18n = createAppI18n({ getItem: () => language, setItem: () => {} });
  return render(<I18nextProvider i18n={i18n}><MemoryRouter>{node}</MemoryRouter></I18nextProvider>);
}
it('applies dates, area and equal-period comparison only after running', async () => {
  sparkService.getResults.mockResolvedValue(snapshot());
  show(<SparkAnalysisScreen type="analytics" ResultsComponent={AnalysisDashboard} />);
  await screen.findByRole('heading', { name: 'Atenciones registradas' });
  fireEvent.change(screen.getByLabelText('Desde'), { target: { value: '2026-10-01' } });
  fireEvent.change(screen.getByLabelText('Hasta'), { target: { value: '2026-10-03' } });
  fireEvent.change(screen.getByLabelText('Área'), { target: { value: 'CONSULTA' } });
  await userEvent.click(screen.getByLabelText('Comparar con el periodo anterior de igual duración'));
  expect(screen.getByText(/Hay filtros sin aplicar/)).toBeInTheDocument();
  expect(sparkService.run).not.toHaveBeenCalled();
  await userEvent.click(screen.getByRole('button', { name: 'Ejecutar análisis' }));
  expect(sparkService.run).toHaveBeenCalledWith('analytics', { start_date: '2026-10-01', end_date: '2026-10-03', area: 'CONSULTA', compare_previous: true });
});
it('rejects a partial date range without executing the analysis', async () => {
  sparkService.getResults.mockResolvedValue(snapshot());
  show(<SparkAnalysisScreen type="clinical" ResultsComponent={AnalysisDashboard} />);
  await screen.findByRole('heading', { name: 'Atenciones registradas' });
  fireEvent.change(screen.getByLabelText('Desde'), { target: { value: '2026-10-01' } });
  await userEvent.click(screen.getByRole('button', { name: 'Ejecutar análisis' }));
  expect(sparkService.run).not.toHaveBeenCalled();
});
it('clearly labels both periods, counts, units and a missing percentage baseline', () => {
  const data = { ...snapshot(), comparison: { current: 4, previous: 0, change: 4, change_percent: null,
    current_period: { start: '2026-10-01', end: '2026-10-03' }, previous_period: { start: '2026-09-28', end: '2026-09-30' } } };
  show(<AnalysisInsights type="analytics" data={data} />);
  const compare = screen.getByRole('region', { name: 'Comparación de atenciones' });
  expect(within(compare).getByText('Periodo anterior · referencia')).toBeInTheDocument();
  expect(within(compare).getByText(/Sin base porcentual/)).toBeInTheDocument();
  expect(within(compare).getAllByText(/Atenciones/i).length).toBeGreaterThan(0);
  expect(within(compare).getByText('28/09/2026 – 30/09/2026')).toBeInTheDocument();
});
it('records a human interpretation, action and qualitative clarity against the displayed snapshot', async () => {
  const data = snapshot();
  const review = { interpretation: 'En octubre hubo cuatro atenciones registradas.', decision: 'Revisar la programación del área con mayor carga.', clarity: 'acceptable', notes: '', result_timestamp: data.timestamp };
  sparkService.saveReview.mockResolvedValue({ saved: true, review });
  show(<AnalysisReview type="analytics" data={data} />);
  await waitFor(() => expect(screen.getByLabelText('¿Qué significa el indicador? Incluye el periodo y la unidad.')).not.toBeDisabled());
  expect(screen.getByRole('radio', { name: 'Clara' })).not.toBeChecked();
  await userEvent.type(screen.getByLabelText('¿Qué significa el indicador? Incluye el periodo y la unidad.'), review.interpretation);
  await userEvent.type(screen.getByLabelText('¿Qué conclusión o acción propones y en qué dato te basas?'), review.decision);
  await userEvent.click(screen.getByRole('radio', { name: 'Aceptable' }));
  await userEvent.click(screen.getByRole('button', { name: 'Guardar interpretación y evaluación' }));
  await screen.findByText('Interpretación y evaluación guardadas para este resultado.');
  expect(sparkService.saveReview).toHaveBeenCalledWith('analytics', review);
  expect(screen.getByRole('button', { name: 'Descargar evaluación (CSV)' })).toBeEnabled();
});
it('reports that a changed result requires refreshing before saving a review', async () => {
  sparkService.getReview.mockResolvedValue({ review: { interpretation: 'Un periodo con ocho atenciones.', decision: 'Revisar la programación de recursos.', clarity: 'clear', notes: '' } });
  sparkService.saveReview.mockRejectedValue({ response: { status: 409 } });
  show(<AnalysisReview type="analytics" data={snapshot()} />);
  await screen.findByDisplayValue('Un periodo con ocho atenciones.');
  await userEvent.click(screen.getByRole('button', { name: 'Guardar interpretación y evaluación' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('El resultado cambió');
});
it('exports CSV safely for Excel while retaining numeric negative changes', () => {
  const csv = makeCsv([['=HYPERLINK("x")', ' @SUM(1)', -2, 'Texto, con "comillas"']]);
  expect(csv).toContain('"\'=HYPERLINK(""x"")"');
  expect(csv).toContain('"\' @SUM(1)"');
  expect(csv).toContain('"-2"');
  expect(csv).toContain('"Texto, con ""comillas"""');
});
it('exports a standalone chart with labels, unit, period and weighted reference without markup injection', () => {
  const svg = makeChartSvg({ title: 'Temperatura por grupo', hint: 'Promedios observados', scope: '01/10/2026 – 03/10/2026 · Consulta', source: 'Signos vitales', unit: '°C',
    rows: [{ label: '<script>alert(1)</script>', value: 37 }], reference: 36.5, referenceLabel: 'Promedio general' });
  const doc = new DOMParser().parseFromString(svg, 'image/svg+xml');
  expect(doc.querySelector('parsererror')).toBeNull();
  expect(doc.querySelector('script')).toBeNull();
  expect(doc.documentElement.textContent).toContain('Promedio general: 36.5 °C');
  expect(doc.documentElement.textContent).toContain('01/10/2026 – 03/10/2026');
  expect(doc.querySelector('[stroke-dasharray]')).not.toBeNull();
});
