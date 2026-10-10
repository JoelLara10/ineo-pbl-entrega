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
