// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { MemoryRouter } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createAppI18n } from '../i18n/setup';
import SparkAnalysisScreen from '../pages/spark/SparkAnalysisScreen';
import { sparkService } from '../services/sparkService';

vi.mock('../services/sparkService', () => ({ sparkService: {
  getResults: vi.fn(), getStatus: vi.fn(), run: vi.fn(), getImage: vi.fn(),
} }));

globalThis.IS_REACT_ACT_ENVIRONMENT = true;
let root;
let host;
let i18n;

async function mount(result, state) {
  sparkService.getResults.mockResolvedValue(result);
  sparkService.getStatus.mockResolvedValue(state);
  host = document.createElement('div');
  document.body.append(host);
  root = createRoot(host);
  i18n = createAppI18n({ getItem: () => 'es', setItem: () => {} });
  await act(async () => root.render(<I18nextProvider i18n={i18n}>
    <MemoryRouter><SparkAnalysisScreen type="clinical" /></MemoryRouter>
  </I18nextProvider>));
}

async function click(label) {
  const button = [...host.querySelectorAll('button')].find((item) => item.textContent.trim() === label);
  expect(button, `Botón ${label}`).toBeDefined();
  await act(async () => button.click());
}

beforeEach(() => {
  vi.clearAllMocks();
  URL.revokeObjectURL = vi.fn();
});
afterEach(async () => {
  if (root) await act(async () => root.unmount());
  root = null;
  host?.remove();
});

describe('PBL-04-T3 — estados y acciones visibles de Spark', () => {
  it('sin ejecutar permite iniciar el trabajo y muestra procesamiento', async () => {
    await mount({ available: false }, { state: 'idle', running: false });
    expect(host.textContent).toContain(i18n.t('spark.states.notRun.title'));
    sparkService.run.mockResolvedValue({ status: { state: 'pending', running: true } });
    await click(i18n.t('spark.states.notRun.action'));
    expect(sparkService.run).toHaveBeenCalledWith('clinical');
    expect(host.textContent).toContain(i18n.t('spark.states.processing.title'));
    expect(host.textContent).toContain(i18n.t('spark.refresh'));
  });

  it('un resultado vacío ofrece actualizar y vuelve a consultar la API', async () => {
    await mount({ available: false }, { state: 'completed', running: false });
    expect(host.textContent).toContain(i18n.t('spark.states.empty.title'));
    const previous = sparkService.getResults.mock.calls.length;
    await click(i18n.t('spark.states.empty.action'));
    expect(sparkService.getResults.mock.calls.length).toBe(previous + 1);
  });

  it('sin conexión muestra una acción de reintento que recupera la vista', async () => {
    sparkService.getResults.mockRejectedValueOnce(new Error('offline'));
    await mount({ available: false }, { state: 'idle', running: false });
    expect(host.querySelector('[role="alert"]').textContent).toContain(i18n.t('spark.states.offline.title'));
    await click(i18n.t('common.retry'));
    expect(host.textContent).toContain(i18n.t('spark.states.notRun.title'));
  });

  it('un trabajo fallido permite ejecutarlo de nuevo', async () => {
    await mount({ available: false }, { state: 'failed', running: false });
    expect(host.querySelector('[role="alert"]').textContent).toContain(i18n.t('spark.states.failed.title'));
    sparkService.run.mockResolvedValue({ status: { state: 'pending', running: true } });
    await click(i18n.t('spark.states.failed.action'));
    expect(sparkService.run).toHaveBeenCalledWith('clinical');
  });

  it('un trabajo en ejecución muestra progreso y botón para actualizar', async () => {
    await mount({ available: false }, { state: 'running', running: true });
    expect(host.querySelector('[role="status"]').textContent).toContain(i18n.t('spark.states.processing.title'));
    const previous = sparkService.getStatus.mock.calls.length;
    await click(i18n.t('spark.refresh'));
    expect(sparkService.getStatus.mock.calls.length).toBe(previous + 1);
  });
});

describe('PBL-05-T4 — pantalla Spark completa en español e inglés', () => {
  it('traduce título, botones, mensajes, secciones y etiquetas dinámicas sin claves técnicas', async () => {
    await mount({ available: true, summary: { total: 8 }, metrics: { fc: { mean: 82.5 } },
      visualizations: [] }, { state: 'completed', running: false });
    for (const lang of ['es', 'en']) {
      await act(async () => i18n.changeLanguage(lang));
      expect(host.querySelector('h1').textContent).toBe(i18n.t('spark.types.clinical.title'));
      expect(host.textContent).toContain(i18n.t('spark.refresh'));
      expect(host.textContent).toContain(i18n.t('spark.run'));
      expect(host.textContent).toContain(i18n.t('spark.sections.metrics'));
      expect(host.textContent).toContain(i18n.t('spark.fields.fc'));
      expect(host.textContent).toContain(i18n.t('spark.fields.mean'));
      expect(i18n.t('sidebar.spark')).toBe('Spark');
      expect(i18n.t('sidebar.sparkSection')).not.toBe('sidebar.sparkSection');
      expect(host.textContent).not.toMatch(/spark\.(states|sections|fields|types)\./);
    }
  });

  it('traduce los mensajes de estado y sus acciones al cambiar de idioma', async () => {
    await mount({ available: false }, { state: 'idle', running: false });
    await act(async () => i18n.changeLanguage('en'));
    expect(host.textContent).toContain(i18n.t('spark.states.notRun.title'));
    expect(host.textContent).toContain(i18n.t('spark.states.notRun.action'));
    expect(host.textContent).not.toContain('spark.states.');
  });
});

describe('PBL-13-T5 — imagen sintética del contrato', () => {
  it('descarga y representa una imagen autenticada mediante sparkService', async () => {
    const image = { filename: 'chart.png', name: 'Gráfica sintética', url: '/spark/images/chart.png' };
    sparkService.getImage.mockResolvedValue('blob:synthetic-chart');
    await mount({ available: true, visualizations: [image] }, { state: 'completed', running: false });
    expect(sparkService.getImage).toHaveBeenCalledWith(image.url);
    const figure = host.querySelector('.spark-gallery figure');
    expect(figure.querySelector('img').getAttribute('src')).toBe('blob:synthetic-chart');
    expect(figure.querySelector('img').getAttribute('alt')).toBe(image.name);
  });
});
