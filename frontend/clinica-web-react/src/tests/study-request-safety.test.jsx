// @vitest-environment jsdom
import React from 'react';
import { cleanup, render, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import ViewResultForm from '../components/ViewResultForm';
import EditResultForm from '../components/EditResultForm';
import UploadResultForm from '../components/UploadResultForm';
import api from '../services/api';

const { t } = vi.hoisted(() => ({ t: (key) => key }));
vi.mock('react-i18next', () => ({ useTranslation: () => ({ t }) }));
vi.mock('../services/api', () => ({ default: { get: vi.fn(), post: vi.fn(), put: vi.fn() } }));
vi.mock('../services/EstudiosCache', () => ({
  getCache: vi.fn(), setCache: vi.fn(), invalidateCachePrefix: vi.fn(), removeCache: vi.fn(),
}));
beforeEach(() => {
  vi.clearAllMocks();
  api.get.mockResolvedValue({ data: [] });
});
afterEach(cleanup);

describe.each([
  ['view', ViewResultForm, '/exams/123/files'],
  ['edit', EditResultForm, '/exams/123/edit-info?type=LABORATORIO'],
  ['upload', UploadResultForm, '/exams/123/info'],
])('Study request safety for %s', (_name, Form, endpoint) => {
  it.each(['../../auth/logout', '//other.example/path', '1?type=GABINETE', '-1', '0'])(
    'does not send an authenticated request for invalid exam ID %s', async (id) => {
      render(<MemoryRouter initialEntries={['/form?id_examen=' + encodeURIComponent(id)]}>
        <Form />
      </MemoryRouter>);
      await waitFor(() => expect(document.body.textContent).toContain('studies.missingExamId'));
      expect(api.get).not.toHaveBeenCalled();
      expect(api.post).not.toHaveBeenCalled();
      expect(api.put).not.toHaveBeenCalled();
    });
  it('continues loading the same endpoint for a valid numeric exam', async () => {
    render(<MemoryRouter initialEntries={['/form?id_examen=123']}><Form /></MemoryRouter>);
    await waitFor(() => expect(api.get).toHaveBeenCalled());
    expect(api.get.mock.calls[0][0]).toBe(endpoint);
  });
});
