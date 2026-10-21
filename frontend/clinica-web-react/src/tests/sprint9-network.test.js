// @vitest-environment jsdom
import { afterEach, expect, it, vi } from 'vitest';
import api from '../services/api';
import { clearClinicalCache } from '../services/clinicalCache';

afterEach(() => { Object.defineProperty(navigator, 'onLine', { configurable: true, value: true }); clearClinicalCache(); vi.restoreAllMocks(); });

it('PBL-25 rejects clinical writes before the adapter when offline', async () => {
  Object.defineProperty(navigator, 'onLine', { configurable: true, value: false });
  const adapter = vi.fn();
  await expect(api.post('/medico/signos-vitales', { synthetic: true }, { adapter })).rejects.toMatchObject({ code: 'ERR_OFFLINE' });
  expect(adapter).not.toHaveBeenCalled();
});

it('PBL-25 cannot synchronize the previous account preference with another account token', async () => {
  localStorage.setItem('@ineo_token', 'synthetic-other-account');
  localStorage.setItem('@ineo_user', JSON.stringify({ id: 'other' }));
  const adapter = vi.fn();
  await expect(api.put('/auth/preferences', { language: 'en' }, { adapter, preferenceOwner: 'original' })).rejects.toMatchObject({ code: 'ERR_SESSION_CHANGED' });
  expect(adapter).not.toHaveBeenCalled();
  localStorage.clear();
});

it('PBL-25 discards a clinical response that finishes after the session changes', async () => {
  localStorage.setItem('@ineo_token', 'first');
  let release;
  const pending = api.get('/patients', { adapter: config => new Promise(resolve => {
    release = () => resolve({ data: { synthetic: true }, status: 200, statusText: 'OK', headers: {}, config });
  }) });
  // Await the interceptor chain reaching the adapter before switching accounts.
  await vi.waitFor(() => expect(release).toBeTypeOf('function'));
  localStorage.setItem('@ineo_token', 'second');
  release();
  await expect(pending).rejects.toMatchObject({ code: 'ERR_SESSION_CHANGED' });
  localStorage.clear();
});

it('PBL-25 does not expire a new session when an older request returns 401', async () => {
  localStorage.setItem('@ineo_token', 'first');
  let release;
  const pending = api.get('/patients', { adapter: config => new Promise((_resolve, reject) => {
    release = () => reject({ response: { status: 401 }, config });
  }) });
  await vi.waitFor(() => expect(release).toBeTypeOf('function'));
  localStorage.setItem('@ineo_token', 'second');
  release();
  await expect(pending).rejects.toMatchObject({ code: 'ERR_SESSION_CHANGED' });
  expect(localStorage.getItem('@ineo_token')).toBe('second');
  localStorage.clear();
});
