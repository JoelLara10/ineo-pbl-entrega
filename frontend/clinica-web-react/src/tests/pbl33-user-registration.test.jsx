// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { I18nextProvider } from 'react-i18next';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createAppI18n } from '../i18n/setup';
import UsuariosConfigScreen from '../pages/config/UsuariosConfigScreen';
import api from '../services/api';

vi.mock('../services/api', () => ({ default: {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
} }));

async function mount() {
  const i18n = createAppI18n({ getItem: () => 'es', setItem: () => {} });
  await i18n.changeLanguage('es');
  return render(
    <I18nextProvider i18n={i18n}>
      <MemoryRouter><UsuariosConfigScreen /></MemoryRouter>
    </I18nextProvider>,
  );
}

beforeEach(() => {
  localStorage.clear();
  vi.clearAllMocks();
  api.get.mockResolvedValue({ data: { data: [] } });
});
afterEach(cleanup);

describe('Alta de usuarios', () => {
  it('recorta el usuario, guarda el rol y muestra el alta sin depender de otra consulta', async () => {
    api.post.mockResolvedValue({
      data: { id: 42, username: 'qa.medico', nombre: 'Usuario QA', role: 'medico', password: 'no-debe-guardarse' },
    });
    const user = userEvent.setup();
    await mount();

    const roleSelect = screen.getByRole('combobox');
    const availableRoles = Array.from(roleSelect.options).map((option) => option.value);
    expect(availableRoles).toContain('enfermero');
    expect(availableRoles).not.toContain('enfermeria');
    expect(document.querySelector('input[type="date"]')).toBeInTheDocument();

    await user.type(screen.getByPlaceholderText('Ingrese nombre(s)'), 'Usuario QA');
    await user.type(screen.getByPlaceholderText('Usuario'), '  qa.medico  ');
    await user.type(screen.getByPlaceholderText('Contraseña'), 'PruebaSegura-42');
    await user.selectOptions(screen.getByRole('combobox'), 'medico');
    await user.click(screen.getByRole('button', { name: 'Guardar usuario' }));

    expect(api.post).toHaveBeenCalledWith('/auth/users', expect.objectContaining({
      nombre: 'Usuario QA',
      username: 'qa.medico',
      role: 'medico',
    }));
    expect(await screen.findByText('Usuario guardado correctamente.')).toBeInTheDocument();
    expect(await screen.findByText(/qa.medico/)).toBeInTheDocument();
    expect(localStorage.getItem('ineo_config_react_usuarios')).not.toContain('no-debe-guardarse');
  });

  it('explica el límite de bcrypt antes de enviar una contraseña demasiado larga', async () => {
    const user = userEvent.setup();
    await mount();

    await user.type(screen.getByPlaceholderText('Ingrese nombre(s)'), 'Usuario QA');
    await user.type(screen.getByPlaceholderText('Usuario'), 'qa.medico');
    await user.type(screen.getByPlaceholderText('Contraseña'), 'x'.repeat(73));
    await user.selectOptions(screen.getByRole('combobox'), 'medico');
    await user.click(screen.getByRole('button', { name: 'Guardar usuario' }));

    expect(await screen.findByText('La contraseña no puede superar 72 bytes.')).toBeInTheDocument();
    expect(api.post).not.toHaveBeenCalled();
  });
});


describe('Edición de usuarios', () => {
  it('carga los datos, actualiza el usuario y conserva su contraseña si se deja vacía', async () => {
    api.get.mockResolvedValue({
      data: { data: [{
        id: 27, username: 'qa.medico', nombre: 'Nombre original',
        papell: 'Apellido', role: 'medico', fecnac: '1995-04-12',
        email: 'qa@example.com', activo: true,
      }] },
    });
    api.put.mockResolvedValue({ data: { message: 'Usuario actualizado correctamente' } });
    const user = userEvent.setup();
    await mount();

    await user.click(await screen.findByRole('button', { name: 'Editar' }));
    expect(screen.getByDisplayValue('Nombre original')).toBeInTheDocument();
    expect(screen.getByDisplayValue('1995-04-12')).toBeInTheDocument();
    expect(screen.queryByPlaceholderText('Dejar vacío para conservar la contraseña actual')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Cambiar contraseña' })).toBeInTheDocument();

    await user.clear(screen.getByDisplayValue('Nombre original'));
    await user.type(screen.getByPlaceholderText('Ingrese nombre(s)'), 'Nombre nuevo');
    await user.click(screen.getByRole('button', { name: 'Guardar cambios' }));

    expect(api.put).toHaveBeenCalledWith('/auth/users/27', expect.objectContaining({
      username: 'qa.medico',
      nombre: 'Nombre nuevo',
      role: 'medico',
      fecnac: '1995-04-12',
    }));
    expect(api.put.mock.calls[0][1]).not.toHaveProperty('password');
  });
});


describe('Cambio voluntario de contraseña', () => {
  it('solo incluye contraseña si se activa explícitamente el cambio', async () => {
    api.get.mockResolvedValue({
      data: { data: [{ id: 27, username: 'qa.medico', nombre: 'Usuario QA', role: 'medico', activo: true }] },
    });
    api.put.mockResolvedValue({ data: { message: 'Usuario actualizado correctamente' } });
    const user = userEvent.setup();
    await mount();
    await user.click(await screen.findByRole('button', { name: 'Editar' }));
    await user.click(screen.getByRole('button', { name: 'Cambiar contraseña' }));
    const input = screen.getByPlaceholderText('Dejar vacío para conservar la contraseña actual');
    await user.type(input, 'Nueva-segura-42!');
    await user.click(screen.getByRole('button', { name: 'Guardar cambios' }));

    expect(api.put).toHaveBeenCalledWith('/auth/users/27', expect.objectContaining({
      password: 'Nueva-segura-42!',
    }));
  });
});
