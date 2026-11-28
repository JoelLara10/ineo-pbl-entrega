// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest';
import { act, cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { useState } from 'react';
import ScreenBoundary from '../components/ScreenBoundary';
import OfflineBoundary from '../components/OfflineBoundary';

const stable = vi.hoisted(() => ({ pathname: '/enfermeria', t: key => key, user: { id: 'qa' } }));
vi.mock('react-router-dom', () => ({ useLocation: () => ({ pathname: stable.pathname }) }));
vi.mock('react-i18next', () => ({ useTranslation: () => ({ t: stable.t, i18n: {} }) }));
vi.mock('../context/AuthContext', () => ({ useAuth: () => ({ user: stable.user, logout() {} }) }));
vi.mock('../services/offlineQueue', () => ({ clearOfflineQueue() {}, flushLanguage: async () => {}, readOfflineQueue: () => null, queueLanguage() {} }));
afterEach(() => { cleanup(); vi.restoreAllMocks(); stable.pathname = '/enfermeria'; });

it('replaces a failed lazy screen with a safe notice and recovers on navigation', () => {
  vi.spyOn(console, 'error').mockImplementation(() => {});
  function Broken() { throw new Error('Failed to fetch dynamically imported module private token'); }
  const view = render(<ScreenBoundary><Broken /></ScreenBoundary>);
  expect(screen.getByRole('alert')).toHaveTextContent('common.screenLoadError');
  expect(screen.getByRole('button', { name: 'common.reloadPage' })).toBeVisible();
  expect(document.body.textContent).not.toMatch(/private token|dynamically imported/);
  stable.pathname = '/enfermeria/nota';
  view.rerender(<ScreenBoundary><p>Pantalla recuperada</p></ScreenBoundary>);
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  expect(screen.getByText('Pantalla recuperada')).toBeVisible();
});

it('hides clinical content while offline and restores the same unsent draft', async () => {
  let online = true;
  vi.spyOn(navigator, 'onLine', 'get').mockImplementation(() => online);
  function Draft() {
    const [value, setValue] = useState('');
    return <label>Borrador QA<input value={value} onChange={event => setValue(event.target.value)} /></label>;
  }
  render(<OfflineBoundary><Draft /></OfflineBoundary>);
  const draft = screen.getByLabelText('Borrador QA');
  fireEvent.change(draft, { target: { value: 'NO GUARDADO QA' } });
  online = false;
  await act(async () => window.dispatchEvent(new Event('offline')));
  expect(draft).not.toBeVisible();
  expect(screen.getByText('offline.title')).toBeVisible();
  online = true;
  await act(async () => window.dispatchEvent(new Event('online')));
  expect(draft).toBeVisible();
  expect(draft).toHaveValue('NO GUARDADO QA');
});
