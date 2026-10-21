/* @vitest-environment jsdom */
import '@testing-library/jest-dom/vitest';
import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react';
import { I18nextProvider } from 'react-i18next';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { createAppI18n } from '../i18n/setup';
import Patients from '../pages/administrativo/PacientesScreen';
import Census from '../pages/administrativo/CensoScreen';
import Medical from '../pages/medico/MedicoScreen';
import Nursing from '../pages/enfermeria/EnfermeriaScreen';
import adminService from '../services/adminService';
import api from '../services/api';
import { clearClinicalCache, setClinicalCache } from '../services/clinicalCache';
import { setAdminCache } from '../services/adminCache';

vi.mock('../services/adminService', () => ({ default: { getPatients: vi.fn(), getCensus: vi.fn(), getAccounts: vi.fn(), getAccount: vi.fn(), getOptions: vi.fn() } }));
vi.mock('../services/api', () => ({ default: { get: vi.fn() } }));
vi.mock('../context/AuthContext', () => ({ useAuth: () => ({ user: { role: 'admin' } }) }));
vi.mock('../context/PatientContext', () => ({ usePatient: () => ({ selectPatient: vi.fn() }) }));

function mount(Screen) {
  return render(<I18nextProvider i18n={createAppI18n()}><MemoryRouter><Screen /></MemoryRouter></I18nextProvider>);
}
const rows = (prefix, count) => Array.from({ length: count }, (_, i) => ({ Id_exp: i + 1, id_atencion: i + 1, name: `${prefix} ${i + 1}`, patient: `${prefix} ${i + 1}`, record: `${prefix}-${i + 1}` }));
const response = () => ({ groups: [{ key: 'activos', patients: rows('Activo', 7) }, { key: 'expedientes', patients: rows('Expediente', 8) }, { key: 'altas', patients: rows('Alta', 1) }] });
beforeEach(() => {
  clearClinicalCache(); localStorage.clear(); vi.clearAllMocks();
  adminService.getPatients.mockResolvedValue(response());
  adminService.getCensus.mockResolvedValue({ sections: [] });
});
afterEach(cleanup);

it('moves all patient groups together and returns to page one after server search', async () => {
  mount(Patients);
  await screen.findByText('Activo 1');
  expect(screen.getAllByRole('button', { name: 'Siguiente' })).toHaveLength(1);
  fireEvent.click(screen.getByRole('button', { name: 'Siguiente' }));
  expect(screen.getByText('Activo 6')).toBeInTheDocument();
  expect(screen.getByText('Expediente 6')).toBeInTheDocument();
  expect(screen.queryByText('Activo 1')).not.toBeInTheDocument();
  const tables = screen.getAllByRole('table');
  const names = within(tables[0]).getAllByRole('row').slice(1).map(row => row.children[1].textContent);
  expect(names).toEqual(['Activo 6', 'Activo 7']);
  adminService.getPatients.mockResolvedValue({ groups: [{ key: 'activos', patients: rows('Encontrado', 1) }] });
  fireEvent.change(screen.getByPlaceholderText('Buscar por paciente, expediente o atención...'), { target: { value: 'Encontrado' } });
  await waitFor(() => expect(adminService.getPatients).toHaveBeenLastCalledWith('Encontrado'));
  await screen.findByText('Encontrado 1');
  expect(screen.getByText('1 / 1')).toBeInTheDocument();
});

it('revalidates a fresh cache on entry and after focus instead of keeping stale patients', async () => {
  setAdminCache('patients:all:complete', { groups: [{ key: 'activos', patients: rows('Antiguo', 1) }] });
  mount(Patients);
  await screen.findByText('Activo 1');
  expect(screen.queryByText('Antiguo 1')).not.toBeInTheDocument();
  adminService.getPatients.mockResolvedValue({ groups: [{ key: 'activos', patients: rows('Actualizado', 1) }] });
  act(() => window.dispatchEvent(new Event('focus')));
  await screen.findByText('Actualizado 1');
  expect(screen.queryByText('Activo 1')).not.toBeInTheDocument();
});

it('keeps census searches separate by area and resets the filtered area page', async () => {
  adminService.getCensus.mockResolvedValue({ sections: [{ key: 'consulta', title: 'Consulta', data: rows('Consulta', 7) }, { key: 'preparacion', title: 'Preparación', data: rows('Preparación', 2) }] });
  mount(Census);
  await screen.findByText('Consulta 1');
  const inputs = screen.getAllByPlaceholderText('Buscar en el censo...');
  fireEvent.change(inputs[0], { target: { value: 'Consulta 7' } });
  expect(screen.getByText('Consulta 7')).toBeInTheDocument();
  expect(screen.queryByText('Consulta 1')).not.toBeInTheDocument();
  expect(screen.getByText('Preparación 1')).toBeInTheDocument();
});

it.each([{ Screen: Medical, cache: 'ineo_web_cache_medico_' }, { Screen: Nursing, cache: 'ineo_web_cache_enfermeria_' }])(
  'clinical lists discard stale snapshots and preserve shared API order ($cache)', async ({ Screen, cache }) => {
    const stale = { estatus: 'OCUPADA', tiene_atencion: true, id_atencion: 1, Id_exp: 1, nom_pac: 'Antiguo' };
    for (const key of ['consulta', 'urgencias', 'hospitalizados']) setClinicalCache(cache + key, key === 'consulta' ? [stale] : [], 300000);
    api.get.mockResolvedValue({ data: { beds_consulta: [{ ...stale, id_atencion: 9, nom_pac: 'Primero' }, { ...stale, id_atencion: 3, nom_pac: 'Segundo' }], beds_preparacion: [], beds_recuperacion: [] } });
    mount(Screen);
    await screen.findByText('Primero');
    expect(screen.queryByText('Antiguo')).not.toBeInTheDocument();
    const names = screen.getAllByText(/^(Primero|Segundo)$/).map(el => el.textContent);
    expect(names).toEqual(['Primero', 'Segundo']);
    expect(api.get).toHaveBeenCalledWith('/medico');
  },
);

it('ignores a late response from a previous patient search', async () => {
  const pending = {};
  adminService.getPatients.mockImplementation(query => query
    ? new Promise(resolve => { pending[query] = resolve; })
    : Promise.resolve(response()));
  mount(Patients);
  await screen.findByText('Activo 1');
  const search = screen.getByPlaceholderText('Buscar por paciente, expediente o atención...');
  fireEvent.change(search, { target: { value: 'anterior' } });
  await waitFor(() => expect(pending.anterior).toBeDefined());
  fireEvent.change(search, { target: { value: 'actual' } });
  await waitFor(() => expect(pending.actual).toBeDefined());
  await act(async () => pending.actual({ groups: [{ key: 'activos', patients: rows('Actual', 1) }] }));
  await screen.findByText('Actual 1');
  await act(async () => pending.anterior({ groups: [{ key: 'activos', patients: rows('Anterior', 1) }] }));
  expect(screen.getByText('Actual 1')).toBeInTheDocument();
  expect(screen.queryByText('Anterior 1')).not.toBeInTheDocument();
});

it('keeps the complete patient row when the account API returns patient as a name string', async () => {
  const module = await import('../pages/administrativo/PacienteDetailScreen');
  const account = { id_atencion: 77, Id_exp: 42, name: 'Paciente cuenta sintético', patient: 'Paciente cuenta sintético', record: 'INEO-000042', attention: 'A-77', area: 'Consulta', total: 0, charges: [] };
  adminService.getAccounts.mockResolvedValue([account]);
  adminService.getAccount.mockResolvedValue(account);
  adminService.getOptions.mockResolvedValue({ servicios: [], medicamentos: [] });
  mount(module.default);
  fireEvent.click(await screen.findByRole('button', { name: 'Abrir cuenta' }));
  await waitFor(() => expect(adminService.getAccount).toHaveBeenCalledWith(77));
  await waitFor(() => expect(screen.getAllByText('Paciente cuenta sintético').length).toBeGreaterThan(1));
  expect(screen.getByText('INEO-000042')).toBeInTheDocument();
});
