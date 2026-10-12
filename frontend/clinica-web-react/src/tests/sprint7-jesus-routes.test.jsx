// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { MemoryRouter, useLocation } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createAppI18n } from '../i18n/setup';
import { AuthProvider } from '../context/AuthContext';
import AppRouter from '../router/AppRouter';
import { getDashboardMenuOptions } from '../pages/dashboard/dashboardMenu';

vi.mock('../components/layout/MainLayout', () => ({ default: ({ children }) => <>{children}</> }));
vi.mock('../pages/dashboard/DashboardScreen', () => ({ default: () => <div>Dashboard</div> }));
vi.mock('../services/api', () => ({ default: { defaults: { headers: {} },
  get: vi.fn(), post: vi.fn(), interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
} }));
vi.mock('../services/sparkService', () => ({ sparkService: {
  getOverview: vi.fn(async () => ({})), getResults: vi.fn(async () => ({ available: false })),
  getStatus: vi.fn(async () => ({ state: 'idle', running: false })), run: vi.fn(),
} }));

let root;
let host;
globalThis.IS_REACT_ACT_ENVIRONMENT = true;
function Location() { const location = useLocation(); return <output data-testid="location">{location.pathname}</output>; }

async function open(path, role) {
  localStorage.clear();
  if (role) {
    localStorage.setItem('@ineo_token', 'test-token');
    localStorage.setItem('@ineo_user', JSON.stringify({ username: 'synthetic', role }));
  }
  host = document.createElement('div');
  document.body.append(host);
  root = createRoot(host);
  await act(async () => root.render(<I18nextProvider i18n={createAppI18n()}>
    <AuthProvider><MemoryRouter initialEntries={[path]}><Location /><AppRouter /></MemoryRouter></AuthProvider>
  </I18nextProvider>));
  await vi.waitFor(() => expect(host.querySelector('[data-testid="location"]')).toBeTruthy());
}

afterEach(async () => { if (root) await act(async () => root.unmount()); root = null; host?.remove(); });
beforeEach(() => localStorage.clear());

describe('PBL-01-T3 — rutas reales y control de acceso', () => {
  it.each(['/admin/spark', '/admin/spark/analytics', '/admin/spark/met',
    '/admin/spark/clinical', '/admin/spark/unsupervised'])(
    'admin abre directamente %s sin redirección', async (path) => {
      await open(path, 'admin');
      await vi.waitFor(() => expect(host.querySelector('.spark-page')).toBeTruthy());
      expect(host.querySelector('[data-testid="location"]').textContent).toBe(path);
      expect(host.textContent).not.toContain('spark.types.');
    });
  it('sin sesión envía al acceso', async () => {
    await open('/admin/spark/clinical');
    await vi.waitFor(() => expect(host.querySelector('[data-testid="location"]').textContent).toBe('/login'));
  });
  it('un médico no accede al módulo de administración', async () => {
    await open('/admin/spark/clinical', 'medico');
    await vi.waitFor(() => expect(host.querySelector('[data-testid="location"]').textContent).toBe('/'));
  });
});


describe('Módulos visibles por rol', () => {
  it('administrativo ve gestión administrativa y análisis, sin módulos clínicos ni configuración', () => {
    const modules = getDashboardMenuOptions('administrativo', (key) => key).map((item) => item.path);
    expect(modules).toEqual(['/admin', '/admin/spark']);
  });

  it('administrador conserva los módulos completos y análisis', () => {
    const modules = getDashboardMenuOptions('admin', (key) => key).map((item) => item.path);
    expect(modules).toContain('/enfermeria');
    expect(modules).toContain('/medico');
    expect(modules).toContain('/config');
    expect(modules).toContain('/admin/spark');
  });

  it('administrativo puede entrar a análisis, pero no a enfermería ni configuración', async () => {
    await open('/admin/spark/clinical', 'administrativo');
    await vi.waitFor(() => expect(host.querySelector('.spark-page')).toBeTruthy());
    await act(async () => root.unmount());
    root = null;
    host?.remove();

    await open('/enfermeria', 'administrativo');
    await vi.waitFor(() => expect(host.querySelector('[data-testid="location"]').textContent).toBe('/'));
    await act(async () => root.unmount());
    root = null;
    host?.remove();

    await open('/config/usuarios', 'administrativo');
    await vi.waitFor(() => expect(host.querySelector('[data-testid="location"]').textContent).toBe('/'));
  });
});
