// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest';
import { act, cleanup, render, renderHook, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { I18nextProvider } from 'react-i18next';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createAppI18n } from '../i18n/setup';
import { clearAdminCache, setAdminCache } from '../services/adminCache';
import useAdminData from '../pages/administrativo/useAdminData';
import PacientesScreen from '../pages/administrativo/PacientesScreen';
import NuevoPacienteScreen from '../pages/administrativo/NuevoPacienteScreen';
import PacienteDetailScreen from '../pages/administrativo/PacienteDetailScreen';
import adminService from '../services/adminService';

vi.mock('../services/adminService', () => ({ default: {
  getPatients: vi.fn(), getOptions: vi.fn(), getPatient: vi.fn(), createPatient: vi.fn(),
  getAccounts: vi.fn(), getAccount: vi.fn(), searchPatients: vi.fn(), addCharge: vi.fn(),
} }));
let i18n;
function Wrapper({ children }) {
  return <I18nextProvider i18n={i18n}><MemoryRouter>{children}</MemoryRouter></I18nextProvider>;
}
beforeEach(async () => {
  vi.clearAllMocks(); clearAdminCache();
  i18n = createAppI18n({ getItem: () => 'es', setItem: () => {} });
  await i18n.changeLanguage('es');
  adminService.getOptions.mockResolvedValue({ areas: ['Consulta'], motivos: ['Consulta'], especialidades: ['Oftalmologia'], medicos: [] });
});
afterEach(cleanup);

describe('Administración: errores y recuperación', () => {
  it('explica un timeout sin filtrar el mensaje técnico y permite recuperar datos', async () => {
    const loader = vi.fn().mockRejectedValueOnce(Object.assign(new Error('timeout of 30000ms exceeded'), { code: 'ECONNABORTED' })).mockResolvedValue({ total: 7 });
    const { result } = renderHook(() => useAdminData('audit', loader, {}), { wrapper: Wrapper });
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.error).toMatch(/tiempo de espera/i);
    expect(result.current.error).not.toContain('30000');
    await act(async () => result.current.reload());
    expect(result.current.error).toBe('');
    expect(result.current.data).toEqual({ total: 7 });
  });
  it('conserva los datos anteriores al fallar una recarga', async () => {
    setAdminCache('audit', { total: 7 });
    const loader = vi.fn().mockRejectedValue(Object.assign(new Error('Network Error'), { code: 'ERR_NETWORK' }));
    const { result } = renderHook(() => useAdminData('audit', loader, {}), { wrapper: Wrapper });
    await waitFor(() => expect(result.current.error).not.toBe(''));
    expect(result.current.data).toEqual({ total: 7 });
    expect(result.current.updatedAt).toBeTruthy();
    expect(result.current.error).toMatch(/conexión/i);
  });
  it('no muestra ceros como resultados válidos cuando la primera consulta falla', async () => {
    adminService.getPatients.mockRejectedValue(Object.assign(new Error('Network Error'), { code: 'ERR_NETWORK' }));
    render(<PacientesScreen />, { wrapper: Wrapper });
    expect(await screen.findByRole('alert')).toHaveTextContent(/conexión/i);
    expect([...document.querySelectorAll('.adm-stat strong')].map(el => el.textContent)).toEqual(['—', '—', '—']);
  });
  it('hace visible el fallo al cargar la lista de cuentas', async () => {
    adminService.getAccounts.mockRejectedValue(Object.assign(new Error('Network Error'), { code: 'ERR_NETWORK' }));
    render(<PacienteDetailScreen />, { wrapper: Wrapper });
    expect(await screen.findByRole('alert')).toHaveTextContent(/conexión/i);
  });
  it('asocia etiquetas al formulario y conserva los datos cuando falla el envío', async () => {
    adminService.createPatient.mockRejectedValue(Object.assign(new Error('Network Error'), { code: 'ERR_NETWORK' }));
    render(<NuevoPacienteScreen />, { wrapper: Wrapper });
    const user = userEvent.setup();
    await user.type(await screen.findByLabelText('CURP'), 'QAAD000101HMCXXX01');
    await user.type(screen.getByLabelText('Primer apellido'), 'PRUEBA');
    await user.type(screen.getByLabelText('Nombre(s)'), 'QA SINTETICO');
    await user.type(screen.getByLabelText('Fecha de nacimiento'), '2000-01-01');
    await user.click(screen.getByRole('button', { name: 'Guardar', exact: true }));
    expect(await screen.findByRole('alert')).toHaveTextContent(/conexión/i);
    expect(screen.getByLabelText('CURP')).toHaveValue('QAAD000101HMCXXX01');
    expect(screen.getByRole('button', { name: 'Guardar', exact: true })).toBeEnabled();
  });
  it('consume los campos reales de catálogos y cargos de la API y envía el servicio correcto', async () => {
    const account = { account: 'A-1', id_atencion: 1, total: 100, charges: [{ charge_id: '7', descripcion: 'CARGO SINTETICO', cantidad: 2, precio: 50, subtotal: 100 }] };
    adminService.getAccounts.mockResolvedValue([{ id_atencion: 1, patient: 'PACIENTE SINTETICO' }]);
    adminService.getAccount.mockResolvedValue(account);
    adminService.getOptions.mockResolvedValue({ servicios: [{ id: 'mongo-service', id_serv: 9, serv_desc: 'CONSULTA SINTETICA', serv_costo: 50 }], medicamentos: [{ id: 'mongo-item', item_id: 45, item_name: 'MEDICAMENTO SINTETICO', item_price: 25 }] });
    adminService.addCharge.mockResolvedValue(account);
    render(<PacienteDetailScreen />, { wrapper: Wrapper });
    const user = userEvent.setup();
    await user.click(await screen.findByRole('button', { name: 'Abrir cuenta', exact: true }));
    expect(await screen.findByText('CARGO SINTETICO')).toBeVisible();
    await user.selectOptions(screen.getByLabelText('Elemento'), '9');
    await user.clear(screen.getByLabelText('Cantidad'));
    await user.type(screen.getByLabelText('Cantidad'), '2');
    await user.click(screen.getByRole('button', { name: 'Agregar', exact: true }));
    await waitFor(() => expect(adminService.addCharge).toHaveBeenCalledWith(1, expect.objectContaining({ id_serv: '9', quantity: 2 })));
    expect(adminService.addCharge.mock.calls[0][1]).not.toHaveProperty('item_id');
    expect(screen.getByText('CARGO SINTETICO')).toBeVisible();
    await user.selectOptions(screen.getByLabelText('Tipo de cargo'), 'medicine');
    await user.selectOptions(screen.getByLabelText('Elemento'), '45');
    await user.click(screen.getByRole('button', { name: 'Agregar', exact: true }));
    await waitFor(() => expect(adminService.addCharge).toHaveBeenLastCalledWith(1, expect.objectContaining({ item_id: '45', quantity: 1 })));
  });
});
