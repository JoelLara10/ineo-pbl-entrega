// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { I18nextProvider } from 'react-i18next';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createAppI18n } from '../i18n/setup';
import SparkAnalysisScreen from '../pages/spark/SparkAnalysisScreen';
import { sparkService } from '../services/sparkService';

vi.mock('../services/sparkService', () => ({ sparkService: {
  getResults: vi.fn(), getStatus: vi.fn(), run: vi.fn(), getImage: vi.fn(),
} }));

const mount = async (language = 'es') => {
  const i18n = createAppI18n({ getItem: () => language, setItem: () => {} });
  await i18n.changeLanguage(language);
  render(<I18nextProvider i18n={i18n}><MemoryRouter><SparkAnalysisScreen type="analytics" /></MemoryRouter></I18nextProvider>);
  return i18n;
};

beforeEach(() => vi.clearAllMocks());
afterEach(cleanup);

describe('PBL-28 — componentes, eventos, servicios simulados e i18n con RTL', () => {
  it('muestra el estado de carga', async () => {
    sparkService.getResults.mockReturnValue(new Promise(() => {}));
    sparkService.getStatus.mockReturnValue(new Promise(() => {}));
    const i18n = await mount();
    expect(screen.getByRole('status')).toHaveTextContent(i18n.t('spark.states.loading.title'));
  });

  it('representa un resultado exitoso', async () => {
    sparkService.getResults.mockResolvedValue({ available: true, summary: { total: 12 }, visualizations: [] });
    sparkService.getStatus.mockResolvedValue({ state: 'completed', running: false });
    await mount();
    expect(await screen.findByText('12')).toBeInTheDocument();
  });

  it('muestra el estado vacío y permite actualizar', async () => {
    sparkService.getResults.mockResolvedValue({ available: false });
    sparkService.getStatus.mockResolvedValue({ state: 'completed', running: false });
    const i18n = await mount();
    const action = await screen.findByRole('button', { name: i18n.t('spark.states.empty.action') });
    await userEvent.click(action);
    await waitFor(() => expect(sparkService.getResults).toHaveBeenCalledTimes(2));
  });

  it('muestra un error accionable y permite reintentar', async () => {
    sparkService.getResults.mockRejectedValueOnce(new Error('offline')).mockResolvedValue({ available: false });
    sparkService.getStatus.mockResolvedValue({ state: 'idle', running: false });
    const i18n = await mount();
    expect(await screen.findByRole('alert')).toHaveTextContent(i18n.t('spark.states.offline.title'));
    await userEvent.click(screen.getByRole('button', { name: i18n.t('common.retry') }));
    await waitFor(() => expect(sparkService.getResults).toHaveBeenCalledTimes(2));
  });

  it.each(['es', 'en'])('traduce la interfaz en %s sin mostrar claves técnicas', async (language) => {
    sparkService.getResults.mockResolvedValue({ available: false });
    sparkService.getStatus.mockResolvedValue({ state: 'idle', running: false });
    const i18n = await mount(language);
    expect(await screen.findByRole('heading', { level: 1 })).toHaveTextContent(i18n.t('spark.types.analytics.title'));
    expect(document.body.textContent).not.toMatch(/spark\.(types|states|sections)\./);
  });
});
