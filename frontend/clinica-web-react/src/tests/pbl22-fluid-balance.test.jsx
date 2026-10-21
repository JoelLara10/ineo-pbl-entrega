/* @vitest-environment jsdom */
import '@testing-library/jest-dom/vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import EnfermeriaFluidBalanceScreen from '../pages/enfermeria/EnfermeriaFluidBalanceScreen';

const apiGet = vi.fn();
const apiPost = vi.fn();

vi.mock('../services/api', () => ({
  default: { get: (...args) => apiGet(...args), post: (...args) => apiPost(...args) },
}));

vi.mock('../context/PatientContext', () => ({
  usePatient: () => ({ selectedPatient: { id_atencion: 25, Id_exp: 1001 } }),
}));

vi.mock('react-router-dom', () => ({
  useLocation: () => ({ state: {} }),
  useNavigate: () => vi.fn(),
}));

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    i18n: { language: 'es' },
    t: (key, fallback) => fallback || key,
  }),
}));

describe('PBL-22 - Balance hídrico', () => {
  afterEach(() => cleanup());

  beforeEach(() => {
    apiGet.mockReset();
    apiPost.mockReset();
    apiGet.mockResolvedValue({ data: [] });
    apiPost.mockResolvedValue({ data: { message: 'ok' } });
    vi.spyOn(window, 'alert').mockImplementation(() => {});
  });

  it('distingue visualmente entradas, salidas y balance neto', async () => {
    render(<EnfermeriaFluidBalanceScreen />);

    expect(screen.getAllByText('nursingFluidBalance.inputsLabel').length).toBeGreaterThan(0);
    expect(screen.getAllByText('nursingFluidBalance.outputsLabel').length).toBeGreaterThan(0);
    expect(screen.getByTestId('total-inputs')).toHaveTextContent('0 ml');
    expect(screen.getByTestId('total-outputs')).toHaveTextContent('0 ml');
    expect(screen.getByTestId('net-balance')).toHaveTextContent('0 ml');
    await waitFor(() => expect(apiGet).toHaveBeenCalled());
  });

  it('calcula los totales mientras se capturan los datos', () => {
    render(<EnfermeriaFluidBalanceScreen />);

    fireEvent.change(screen.getByLabelText('nursingFluidBalance.oralInputsPlaceholder'), { target: { value: '500' } });
    fireEvent.change(screen.getByLabelText('nursingFluidBalance.ivInputsPlaceholder'), { target: { value: '250' } });
    fireEvent.change(screen.getByLabelText('nursingFluidBalance.urineOutputsPlaceholder'), { target: { value: '300' } });
    fireEvent.change(screen.getByLabelText('nursingFluidBalance.drainageOutputsPlaceholder'), { target: { value: '50' } });

    expect(screen.getByTestId('total-inputs')).toHaveTextContent('750 ml');
    expect(screen.getByTestId('total-outputs')).toHaveTextContent('350 ml');
    expect(screen.getByTestId('net-balance')).toHaveTextContent('400 ml');
  });

  it('conserva el envío y la recarga del historial', async () => {
    render(<EnfermeriaFluidBalanceScreen />);

    fireEvent.change(screen.getByLabelText('nursingFluidBalance.oralInputsPlaceholder'), { target: { value: '100' } });
    fireEvent.click(screen.getByRole('button', { name: /nursingFluidBalance.save$/ }));

    await waitFor(() => expect(apiPost).toHaveBeenCalledWith(
      '/appointments/25/fluid-balance',
      expect.objectContaining({ ingresos_orales: '100' }),
    ));
    await waitFor(() => expect(apiGet).toHaveBeenCalledTimes(2));
  });
});
