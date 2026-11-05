// @vitest-environment jsdom
import { beforeAll, describe, expect, it } from 'vitest';
import api from '../services/api';
import { sparkService } from '../services/sparkService';

// Opt-in: requires the dedicated synthetic server, never a shared environment.
describe.skipIf(process.env.RUN_CONTRACT_SIT !== '1')('PBL-30 SIT React client - Flask - MongoDB', () => {
  beforeAll(() => {
    api.defaults.baseURL = 'http://127.0.0.1:5029/api/v1';
    api.defaults.adapter = 'fetch';
    localStorage.clear();
  });

  it('logs in and consumes patients, studies, Analytics and all Spark types', async () => {
    const login = await api.post('/auth/login', {
      username: 'admin.test', password: 'Prueba-Sprint7!',
    });
    expect(login.status).toBe(200);
    expect(login.data.token).toBeTypeOf('string');
    localStorage.setItem('@ineo_token', login.data.token);
    const patients = await api.get('/patients');
    expect(patients.status).toBe(200);
    expect(patients.data.groups).toBeInstanceOf(Array);
    expect(patients.data.pagination).toBeTypeOf('object');
    for (const path of ['/studies/counts', '/analytics/dashboard']) {
      const response = await api.get(path);
      expect(response.status).toBe(200);
      expect(response.data).toBeTypeOf('object');
    }
    const overview = await sparkService.getOverview();
    for (const kind of ['analytics', 'met', 'clinical', 'unsupervised']) {
      expect(overview).toHaveProperty(kind);
      const result = await sparkService.getResults(kind);
      expect(result.contract_version).toBe('1.0');
      expect(result.available).toBeTypeOf('boolean');
      expect(result.visualizations).toBeInstanceOf(Array);
      const state = await sparkService.getStatus(kind);
      expect(state.running).toBeTypeOf('boolean');
    }
    localStorage.clear();
    await expect(api.get('/patients')).rejects.toMatchObject({ response: { status: 401 } });
    await expect(sparkService.getOverview()).rejects.toMatchObject({ response: { status: 401 } });
  });
});
