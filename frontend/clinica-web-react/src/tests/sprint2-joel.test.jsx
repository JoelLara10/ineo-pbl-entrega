// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { I18nextProvider } from 'react-i18next';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createAppI18n } from '../i18n/setup';
import EnfermeriaCareScreen from '../pages/enfermeria/EnfermeriaCareScreen';
import SparkAnalysisScreen from '../pages/spark/SparkAnalysisScreen';
import api from '../services/api';
import { sparkService } from '../services/sparkService';

vi.mock('../services/api', () => ({ default: { get: vi.fn(), post: vi.fn() } }));
vi.mock('../services/sparkService', () => ({ sparkService: {
  getResults: vi.fn(), getStatus: vi.fn(), run: vi.fn(), getImage: vi.fn(),
} }));
vi.mock('../context/PatientContext', () => ({
  usePatient: () => ({ selectedPatient: { id_atencion: 'AT-7', Id_exp: 'EXP-7' } }),
}));

globalThis.IS_REACT_ACT_ENVIRONMENT = true;
let root;
let host;
let i18n;

async function render(component) {
  host = document.createElement('div');
  document.body.append(host);
  root = createRoot(host);
  i18n = createAppI18n({ getItem: () => 'es', setItem: () => {} });
  await act(async () => root.render(
    <I18nextProvider i18n={i18n}><MemoryRouter>{component}</MemoryRouter></I18nextProvider>
  ));
  await act(async () => Promise.resolve());
}

async function click(text) {
  const button = [...host.querySelectorAll('button')].find((item) => item.textContent.includes(text));
  expect(button).toBeDefined();
  await act(async () => button.click());
}

function fill(control, value) {
  const setter = Object.getOwnPropertyDescriptor(control.constructor.prototype, 'value').set;
  setter.call(control, value);
  control.dispatchEvent(new Event('input', { bubbles: true }));
  control.dispatchEvent(new Event('change', { bubbles: true }));
}

beforeEach(() => {
  vi.clearAllMocks();
  vi.spyOn(window, 'alert').mockImplementation(() => {});
  URL.revokeObjectURL = vi.fn();
});

afterEach(async () => {
  if (root) await act(async () => root.unmount());
  root = null;
  host?.remove();
  vi.restoreAllMocks();
});

describe('PBL-03 — flujo clínico Spark', () => {
  it('muestra resultados reales al completar el análisis', async () => {
    sparkService.getResults.mockResolvedValue({
      available: true,
      summary: { total_patients: 24 },
      metrics: { heart_rate: { mean: 78 } },
      visualizations: [],
    });
    sparkService.getStatus.mockResolvedValue({ state: 'completed', running: false });
    await render(<SparkAnalysisScreen type="clinical" />);

    expect(host.querySelector('h1').textContent).toBe(i18n.t('spark.types.clinical.title'));
    expect(host.textContent).toContain('24');
    expect(host.textContent).toContain('78');
    expect(sparkService.getResults).toHaveBeenCalledWith('clinical');
  });

  it('permite ejecutar y comunica pendiente o procesamiento', async () => {
    sparkService.getResults.mockResolvedValue({ available: false });
    sparkService.getStatus.mockResolvedValue({ state: 'idle', running: false });
    sparkService.run.mockResolvedValue({ status: { state: 'pending', running: true } });
    await render(<SparkAnalysisScreen type="clinical" />);

    await click(i18n.t('spark.states.notRun.action'));
    expect(sparkService.run).toHaveBeenCalledWith('clinical');
    expect(host.textContent).toContain(i18n.t('spark.states.processing.title'));
  });

  it('presenta un fallo previo y permite volver a ejecutar', async () => {
    sparkService.getResults.mockResolvedValue({ available: false });
    sparkService.getStatus.mockResolvedValue({ state: 'failed', running: false, error: 'Datos clínicos inválidos' });
    sparkService.run.mockResolvedValue({ status: { state: 'processing', running: true } });
    await render(<SparkAnalysisScreen type="clinical" />);

    expect(host.querySelector('[role="alert"]').textContent).toContain('Datos clínicos inválidos');
    await click(i18n.t('spark.states.failed.action'));
    expect(sparkService.run).toHaveBeenCalledWith('clinical');
  });
});

describe('PBL-23 — diseño de Cuidados de Enfermería', () => {
  it('conserva consulta, captura, estados y guardado con componentes responsivos', async () => {
    api.get.mockResolvedValue({ data: [] });
    api.post.mockResolvedValue({ data: { ok: true } });
    await render(<EnfermeriaCareScreen />);

    expect(api.get).toHaveBeenCalledWith('/appointments/AT-7/nursing-care');
    expect(host.querySelector('.nursing-care-grid')).not.toBeNull();
    expect(host.textContent).toContain(i18n.t('nursingCare.noRecords'));
    expect([...host.querySelectorAll('option')].map((item) => item.textContent)).toEqual([
      'En proceso', 'Pendiente', 'Completado',
    ]);

    fill(host.querySelectorAll('textarea')[0], 'Riesgo de caída');
    await click(i18n.t('nursingCare.save'));
    expect(api.post).toHaveBeenCalledWith('/appointments/AT-7/nursing-care', expect.objectContaining({
      diagnostico_enfermeria: 'Riesgo de caída', estado: 'EN_PROCESO',
    }));
  });

  it('muestra un error recuperable cuando falla el historial', async () => {
    api.get.mockRejectedValueOnce(new Error('offline')).mockResolvedValueOnce({ data: [] });
    await render(<EnfermeriaCareScreen />);

    expect(host.querySelector('[role="alert"]').textContent).toContain(i18n.t('nursingCare.historyError'));
    await click(i18n.t('common.retry'));
    expect(api.get).toHaveBeenCalledTimes(2);
    expect(host.textContent).toContain(i18n.t('nursingCare.noRecords'));
  });
});
