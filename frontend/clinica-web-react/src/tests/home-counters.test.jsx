// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import Dashboard from '../pages/dashboard/DashboardScreen';
import api from '../services/api';

vi.mock('../services/api', () => ({ default: { get: vi.fn() } }));
vi.mock('react-router-dom', () => ({ useNavigate: () => vi.fn() }));
vi.mock('../context/AuthContext', () => ({ useAuth: () => ({ user: { role: 'admin' }, logout: vi.fn() }) }));
vi.mock('react-i18next', () => ({ useTranslation: () => ({ t: key => key, i18n: { language: 'es' } }) }));
afterEach(() => { cleanup(); vi.clearAllMocks(); });

const stats = { active_patients: { total: 927 }, bed_occupancy: { occupied: 46 } };
it('shows real counts and preserves them with a visible notice after a failed refresh', async () => {
  api.get.mockImplementation(async path => ({ data: path.includes('analytics') ? stats : { total: 12 } }));
  render(<Dashboard />);
  expect(await screen.findByText('927')).toBeVisible();
  expect(screen.getByText('46')).toBeVisible();
  api.get.mockRejectedValue(new Error('secret internal detail'));
  fireEvent.click(screen.getByTitle('dashboard.refresh'));
  expect(await screen.findByRole('alert')).toHaveTextContent('dashboard.loadError');
  expect(screen.getByText('927')).toBeVisible();
  expect(screen.getByText('46')).toBeVisible();
  expect(screen.queryByText(/secret/)).not.toBeInTheDocument();
});

it('never invents zeros when the initial response fails or has an invalid shape', async () => {
  api.get.mockResolvedValue({ data: {} });
  render(<Dashboard />);
  await screen.findByRole('alert');
  expect(screen.getAllByText('—')).toHaveLength(3);
  expect(screen.queryByText('0')).not.toBeInTheDocument();
  api.get.mockImplementation(async path => ({ data: path.includes('analytics') ?
    { active_patients: { total: 0 }, bed_occupancy: { occupied: 0 } } : { total: 0 } }));
  fireEvent.click(screen.getByTitle('dashboard.refresh'));
  await waitFor(() => expect(screen.queryByRole('alert')).not.toBeInTheDocument());
  expect(screen.getAllByText('0')).toHaveLength(3);
});

it('keeps successful statistics when only the studies request fails', async () => {
  api.get.mockImplementation(async path => {
    if (!path.includes('analytics')) throw new Error('offline');
    return { data: stats };
  });
  render(<Dashboard />);
  expect(await screen.findByText('927')).toBeVisible();
  expect(screen.getByText('46')).toBeVisible();
  expect(screen.getByRole('alert')).toBeVisible();
  expect(screen.getByText('—')).toBeVisible();
});
