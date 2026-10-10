import { beforeEach, describe, expect, it, vi } from 'vitest';
import api from '../services/api';
import adminService from '../services/adminService';

vi.mock('../services/api', () => ({ default: {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
} }));

beforeEach(() => {
  vi.clearAllMocks();
  api.get.mockResolvedValue({ data: {} });
  api.post.mockResolvedValue({ data: {} });
  api.put.mockResolvedValue({ data: {} });
});

describe('Administrative patient API flow', () => {
  it('loads, creates, and edits through the attention-aware administrative routes', async () => {
    const payload = { curp: 'QA-REACTIVACION', area: 'Consulta', motivo: 'Consulta' };

    await adminService.getPatient(204);
    await adminService.createPatient(payload);
    await adminService.updatePatient(204, payload);

    expect(api.get).toHaveBeenCalledWith('/gestion-pacientes/204');
    expect(api.post).toHaveBeenCalledWith('/gestion-pacientes', payload);
    expect(api.put).toHaveBeenCalledWith('/gestion-pacientes/204', payload);
  });

  it('searches existing records through the authenticated patient lookup route', async () => {
    await adminService.searchPatients('QA-REACTIVACION', 8);

    expect(api.get).toHaveBeenCalledWith('/patients/search', {
      params: { q: 'QA-REACTIVACION', limit: 8 },
    });
  });
});
