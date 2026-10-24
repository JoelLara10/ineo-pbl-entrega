// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { I18nextProvider } from 'react-i18next';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { createAppI18n } from '../i18n/setup';
import ServiciosConfigScreen from '../pages/config/ServiciosConfigScreen';
import { normalizeServiceForm } from '../utils/serviceForm';
import api from '../services/api';

vi.mock('../services/api', () => ({ default: { get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() } }));
beforeEach(() => { vi.clearAllMocks(); api.get.mockResolvedValue({ data: [] }); });
afterEach(cleanup);

async function mount() {
  const i18n = createAppI18n({ getItem: () => 'es', setItem: () => {} });
  await i18n.changeLanguage('es');
  render(<I18nextProvider i18n={i18n}><MemoryRouter><ServiciosConfigScreen /></MemoryRouter></I18nextProvider>);
  await waitFor(() => expect(api.get).toHaveBeenCalled());
  const user = userEvent.setup();
  await user.type(screen.getByLabelText('Clave'), 'web-qa');
  await user.type(screen.getByLabelText('Descripción'), 'Servicio QA');
  await user.type(screen.getByLabelText('Precio principal'), '0');
  return user;
}

it('normaliza el formulario web con siete precios opcionales vacíos', () => {
  const result = normalizeServiceForm({ serv_cve: ' qa ', serv_desc: ' Prueba ', serv_costo: '0', tipo: '1', iva: '' });
  expect(result.data).toMatchObject({ serv_cve: 'QA', serv_desc: 'Prueba', serv_costo: 0, serv_costo2: 0, serv_costo8: 0, iva: 16, tipo: 1 });
  expect(normalizeServiceForm({ ...result.data, serv_costo2: -1 }).error).toBe('serviceInvalidData');
});

it('registra costo cero y consulta nuevamente el catálogo sin campos numéricos vacíos', async () => {
  api.post.mockResolvedValue({ data: { id_serv: 90 } });
  const user = await mount();
  await user.click(screen.getByRole('button', { name: 'Guardar servicio' }));
  expect(api.post).toHaveBeenCalledWith('/catalog/services', expect.objectContaining({ serv_costo: 0, serv_costo2: 0, serv_costo8: 0, tipo: 1 }));
  expect(await screen.findByText('Servicio registrado correctamente.')).toBeInTheDocument();
  expect(api.get).toHaveBeenCalledTimes(2);
});

it('bloquea un segundo envío mientras espera al servidor', async () => {
  let finish;
  api.post.mockImplementation(() => new Promise((resolve) => { finish = resolve; }));
  const user = await mount();
  await user.click(screen.getByRole('button', { name: 'Guardar servicio' }));
  const pending = screen.getByRole('button', { name: 'Guardando servicio...' });
  expect(pending).toBeDisabled();
  await user.click(pending);
  expect(api.post).toHaveBeenCalledTimes(1);
  finish({ data: { id_serv: 91 } });
  expect(await screen.findByText('Servicio registrado correctamente.')).toBeInTheDocument();
});

it('muestra un error seguro y permite reintentar cuando falla el servidor', async () => {
  api.post.mockRejectedValue({ response: { status: 500, data: { error: 'MongoError password=secret' } } });
  const user = await mount();
  await user.click(screen.getByRole('button', { name: 'Guardar servicio' }));
  expect(await screen.findByRole('status')).not.toHaveTextContent(/Mongo|secret/);
  expect(screen.getByRole('button', { name: 'Guardar servicio' })).toBeEnabled();
  expect(screen.getByLabelText('Clave')).toHaveValue('WEB-QA');
});
