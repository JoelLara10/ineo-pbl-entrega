// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthProvider, useAuth } from '../context/AuthContext';
import api from '../services/api';

vi.mock('../services/api', () => ({ default: {
  defaults: { headers: {} },
  post: vi.fn(),
} }));

function SessionProbe() {
  const { user, login, logout } = useAuth();
  return (
    <>
      <output>{user?.username || 'signed-out'}</output>
      <button onClick={() => login('admin.test', 'password-a')}>login admin</button>
      <button onClick={() => login('staff.test', 'password-b')}>login staff</button>
      <button onClick={logout}>logout</button>
    </>
  );
}

beforeEach(() => {
  localStorage.clear();
  vi.clearAllMocks();
  api.defaults.headers = {};
});
afterEach(cleanup);

describe('Cambio de cuenta', () => {
  it('limpia la sesión anterior y acepta el inicio de sesión de otra cuenta', async () => {
    api.post
      .mockResolvedValueOnce({ data: { token: 'token-admin', user: { username: 'admin.test' } } })
      .mockResolvedValueOnce({ data: { message: 'Sesión cerrada' } })
      .mockResolvedValueOnce({ data: { token: 'token-staff', user: { username: 'staff.test' } } });
    const user = userEvent.setup();
    render(<AuthProvider><SessionProbe /></AuthProvider>);

    await user.click(screen.getByRole('button', { name: 'login admin' }));
    expect(await screen.findByText('admin.test')).toBeInTheDocument();
    expect(localStorage.getItem('@ineo_token')).toBe('token-admin');

    await user.click(screen.getByRole('button', { name: 'logout' }));
    expect(await screen.findByText('signed-out')).toBeInTheDocument();
    expect(localStorage.getItem('@ineo_token')).toBeNull();

    await user.click(screen.getByRole('button', { name: 'login staff' }));
    expect(await screen.findByText('staff.test')).toBeInTheDocument();
    expect(localStorage.getItem('@ineo_token')).toBe('token-staff');
    expect(api.defaults.headers.Authorization).toBe('Bearer token-staff');
    expect(api.post).toHaveBeenNthCalledWith(3, '/auth/login', {
      username: 'staff.test',
      password: 'password-b',
    });
  });
});
