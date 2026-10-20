import { runInNewContext } from 'node:vm';
import { describe, expect, it, vi } from 'vitest';
import { workerSource } from '../../scripts/offline-shell.mjs';

describe('PBL-25 static shell', () => {
  it('never intercepts API, credentials, mutations, external or unknown assets', async () => {
    const handlers = {};
    const cached = { body: 'public-shell' };
    const cache = { match: vi.fn().mockResolvedValue(cached), addAll: vi.fn().mockResolvedValue() };
    const caches = { open: vi.fn().mockResolvedValue(cache) };
    runInNewContext(workerSource(['/index.html', '/assets/app.js'], 'test'), {
      self: { location: { origin: 'https://ineo.test' }, addEventListener: (name, callback) => { handlers[name] = callback; } },
      URL, caches, fetch: vi.fn().mockRejectedValue(new Error('offline')),
    });
    for (const request of [
      { method: 'GET', url: 'https://ineo.test/api/v1/patients', mode: 'navigate' },
      { method: 'POST', url: 'https://ineo.test/assets/app.js' },
      { method: 'GET', url: 'https://api.test/patients' },
      { method: 'GET', url: 'https://ineo.test/assets/unknown.js' },
      { method: 'GET', url: 'https://ineo.test/assets/app.js?token=secret' },
    ]) {
      const respondWith = vi.fn(); handlers.fetch({ request, respondWith }); expect(respondWith).not.toHaveBeenCalled();
    }
    let response;
    handlers.fetch({ request: { method: 'GET', url: 'https://ineo.test/medico', mode: 'navigate' }, respondWith: value => { response = value; } });
    expect(await response).toEqual(cached);
    expect(cache.match).toHaveBeenCalledWith('/index.html');
    let installation;
    handlers.install({ waitUntil: value => { installation = value; } }); await installation;
    expect(cache.addAll).toHaveBeenCalledWith(['/index.html', '/assets/app.js']);
  });
});
