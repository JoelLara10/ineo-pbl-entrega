// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import SparkAnalysisScreen from './SparkAnalysisScreen';

const { sparkServiceMock, navigateMock } = vi.hoisted(() => ({
  sparkServiceMock: {
    getResults: vi.fn(),
    getStatus: vi.fn(),
    run: vi.fn(),
    getImage: vi.fn(),
  },
  navigateMock: vi.fn(),
}));

vi.mock('../../services/sparkService', () => ({
  sparkService: sparkServiceMock,
}));

const translate = (key, fallback) => typeof fallback === 'string' ? fallback : key;
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: translate,
    i18n: { language: 'es' },
  }),
}));

vi.mock('react-router-dom', () => ({
  useNavigate: () => navigateMock,
}));

const emptyResults = { available: false };

function renderScreen() {
  return render(<SparkAnalysisScreen type="analytics" />);
}

async function showState(status, data = emptyResults) {
  sparkServiceMock.getResults.mockResolvedValue(data);
  sparkServiceMock.getStatus.mockResolvedValue(status);

  renderScreen();

  await waitFor(() => {
    expect(sparkServiceMock.getStatus).toHaveBeenCalled();
  });
}

describe('SparkAnalysisScreen — PBL-04', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    cleanup();
    vi.useRealTimers();
  });

  it('muestra el estado sin ejecutar y permite ejecutar', async () => {
    await showState({ state: 'idle', running: false });

    expect(
      await screen.findByText('spark.states.notRun.title')
    ).toBeTruthy();

    sparkServiceMock.run.mockResolvedValue({
      status: { state: 'pending', running: true },
    });

    fireEvent.click(
      screen.getByRole('button', {
        name: 'spark.states.notRun.action',
      })
    );

    await waitFor(() => {
      expect(sparkServiceMock.run).toHaveBeenCalledWith('analytics');
    });
  });

  it('muestra el estado sin datos cuando la ejecución terminó vacía', async () => {
    await showState(
      { state: 'completed', running: false },
      { available: false }
    );

    expect(
      await screen.findByText('spark.states.empty.title')
    ).toBeTruthy();

    expect(
      screen.getByRole('button', {
        name: 'spark.states.empty.action',
      })
    ).toBeTruthy();
  });

  it('muestra un mensaje de conexión cuando la API no responde', async () => {
    sparkServiceMock.getResults.mockRejectedValue(
      new Error('Network Error')
    );
    sparkServiceMock.getStatus.mockRejectedValue(
      new Error('Network Error')
    );

    renderScreen();

    expect(
      await screen.findByText('spark.states.offline.title')
    ).toBeTruthy();

    expect(
      screen.getByRole('button', { name: 'common.retry' })
    ).toBeTruthy();
  });

  it('muestra el estado de procesamiento', async () => {
    await showState(
      { state: 'running', running: true },
      { available: false }
    );

    expect(
      await screen.findByText('spark.states.processing.title')
    ).toBeTruthy();
  });

  it('muestra el fallo y permite volver a ejecutar', async () => {
    await showState(
      {
        state: 'failed',
        running: false,
        error: 'Error de prueba',
      },
      { available: false }
    );

    expect(
      await screen.findByText('spark.states.failed.title')
    ).toBeTruthy();

    expect(screen.getByText('Error de prueba')).toBeTruthy();

    sparkServiceMock.run.mockResolvedValue({
      status: { state: 'pending', running: true },
    });

    fireEvent.click(
      screen.getByRole('button', {
        name: 'spark.states.failed.action',
      })
    );

    await waitFor(() => {
      expect(sparkServiceMock.run).toHaveBeenCalledWith('analytics');
    });
  });

  it('muestra los resultados cuando existen datos', async () => {
    await showState(
      { state: 'completed', running: false },
      {
        available: true,
        summary: { total: 12 },
      }
    );

    expect(await screen.findByText('Total')).toBeTruthy();
    expect(screen.getByText('12')).toBeTruthy();
  });

  it('permite regresar al panel de Analytics', async () => {
    await showState(
      { state: 'idle', running: false },
      emptyResults
    );

    fireEvent.click(
      screen.getByRole('button', { name: /Volver/ })
    );

    expect(navigateMock).toHaveBeenCalledWith('/admin/spark');
  });

  it('bloquea ejecuciones duplicadas mientras el POST sigue pendiente', async () => {
    await showState({ state: 'idle', running: false });
    await screen.findByText('spark.states.notRun.title');
    let finish;
    sparkServiceMock.run.mockReturnValue(new Promise((resolve) => { finish = resolve; }));
    const run = screen.getByRole('button', { name: 'spark.states.notRun.action' });
    fireEvent.click(run);
    fireEvent.click(run);
    expect(sparkServiceMock.run).toHaveBeenCalledTimes(1);
    await act(async () => finish({ status: { state: 'pending', running: true } }));
  });

  it('consulta un trabajo pendiente incluso con running=false y carga su resultado al terminar', async () => {
    vi.useFakeTimers();
    sparkServiceMock.getResults.mockResolvedValue({ available: false });
    sparkServiceMock.getStatus.mockResolvedValue({ state: 'pending', running: false });
    await act(async () => { renderScreen(); });
    expect(screen.getByText('spark.states.processing.title')).toBeTruthy();
    sparkServiceMock.getStatus.mockResolvedValue({ state: 'completed', running: false });
    sparkServiceMock.getResults.mockResolvedValue({ available: true, summary: { total: 42 } });
    await act(async () => { await vi.advanceTimersByTimeAsync(3000); });
    expect(screen.getByText('42')).toBeTruthy();
    expect(screen.queryByText('spark.states.processing.title')).toBeNull();
  });
});
