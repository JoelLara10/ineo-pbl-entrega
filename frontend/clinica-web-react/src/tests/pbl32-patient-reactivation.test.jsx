// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { I18nextProvider } from 'react-i18next';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createAppI18n } from '../i18n/setup';
import NuevoPacienteScreen from '../pages/administrativo/NuevoPacienteScreen';
import adminService from '../services/adminService';

vi.mock('../services/adminService', () => ({ default: {
  getOptions: vi.fn(),
  getPatient: vi.fn(),
  searchPatients: vi.fn(),
  createPatient: vi.fn(),
  updatePatient: vi.fn(),
} }));

function Destination() {
  const location = useLocation();
  return <div data-testid="destination">{location.pathname}:{location.state?.reactivation ? 'reactivation' : ''}</div>;
}

async function mount() {
  const i18n = createAppI18n({ getItem: () => 'es', setItem: () => {} });
  await i18n.changeLanguage('es');
  return render(
    <I18nextProvider i18n={i18n}>
      <MemoryRouter initialEntries={['/nuevo-paciente']}>
        <Routes>
          <Route path="/nuevo-paciente" element={<NuevoPacienteScreen />} />
          <Route path="/pacientes/:id/editar" element={<Destination />} />
        </Routes>
      </MemoryRouter>
    </I18nextProvider>,
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  adminService.getOptions.mockResolvedValue({ areas: [], motivos: [], especialidades: [], camas: [], medicos: [] });
});
afterEach(cleanup);

describe('Registro y reactivación de pacientes existentes', () => {
  it('busca un expediente previo y abre su edición para crear una nueva atención', async () => {
    adminService.searchPatients.mockResolvedValue([{
      Id_exp: 204,
      record: 'INEO-000204',
      name: 'PACIENTE QA SINTETICO',
      hasActiveAttention: false,
    }]);
    const user = userEvent.setup();
    await mount();

    await user.type(screen.getByRole('textbox', { name: 'Buscar paciente atendido anteriormente' }), 'Paciente QA');
    const result = await screen.findByRole('button', {
      name: /PACIENTE QA SINTETICO.*INEO-000204.*Reactivar en una nueva atención/,
    });
    await user.click(result);

    expect(await screen.findByTestId('destination')).toHaveTextContent('/pacientes/204/editar:reactivation');
    expect(adminService.searchPatients).toHaveBeenCalledWith('Paciente QA', 8);
    expect(adminService.createPatient).not.toHaveBeenCalled();
  });

  it('impide iniciar otra atención desde el buscador si el paciente ya está activo', async () => {
    adminService.searchPatients.mockResolvedValue([{
      Id_exp: 204,
      record: 'INEO-000204',
      name: 'PACIENTE QA SINTETICO',
      hasActiveAttention: true,
    }]);
    const user = userEvent.setup();
    await mount();

    await user.type(screen.getByRole('textbox', { name: 'Buscar paciente atendido anteriormente' }), 'Paciente QA');
    const result = await screen.findByRole('button', {
      name: /PACIENTE QA SINTETICO.*INEO-000204.*Ya tiene una atención activa/,
    });
    expect(result).toBeDisabled();
    expect(adminService.createPatient).not.toHaveBeenCalled();
  });
});
