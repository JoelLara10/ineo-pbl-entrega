/* @vitest-environment jsdom */
import '@testing-library/jest-dom/vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import Assessment from '../pages/enfermeria/EnfermeriaAssessmentScreen';
import Balance from '../pages/enfermeria/EnfermeriaFluidBalanceScreen';
import Care from '../pages/enfermeria/EnfermeriaCareScreen';
import Medications from '../pages/enfermeria/EnfermeriaMedicationsScreen';
import api from '../services/api';
import { clearClinicalCache } from '../services/clinicalCache';

vi.mock('../services/api', () => ({ default: { get: vi.fn(), post: vi.fn() } }));
vi.mock('../context/PatientContext', () => ({ usePatient: () => ({ selectedPatient: { id_atencion: 25, Id_exp: 1001 } }) }));
vi.mock('react-router-dom', () => ({ useLocation: () => ({ state: {} }), useNavigate: () => vi.fn() }));
const { translate } = vi.hoisted(() => ({ translate: (key) => key }));
vi.mock('react-i18next', () => ({ useTranslation: () => ({ t: translate, i18n: { language: 'es' } }) }));

beforeEach(() => {
  clearClinicalCache();
  vi.clearAllMocks();
  api.get.mockResolvedValue({ data: [] });
  api.post.mockResolvedValue({ data: { message: 'ok' } });
});
afterEach(cleanup);

it.each([{ Screen: Assessment, prefix: 'nursingAssessment' }, { Screen: Balance, prefix: 'nursingFluidBalance' }, { Screen: Care, prefix: 'nursingCare' }])(
  '$prefix keeps its history available and allows collapsing it without reloading', async ({ Screen, prefix }) => {
    render(<Screen />);
    const empty = await screen.findByText(`${prefix}.noRecords`);
    const toggle = screen.getByRole('button', { name: new RegExp(`${prefix}.history`) });
    expect(empty).toBeVisible();
    expect(toggle).toHaveAttribute('aria-expanded', 'true');
    fireEvent.click(toggle);
    expect(empty).not.toBeVisible();
    expect(toggle).toHaveAttribute('aria-expanded', 'false');
    fireEvent.click(toggle);
    expect(empty).toBeVisible();
    expect(api.get).toHaveBeenCalledTimes(1);
  },
);

it('selects a medication date with a calendar and preserves the existing API date format', async () => {
  render(<Medications />);
  const date = screen.getByLabelText('nursingMeds.applicationDate');
  expect(date).toHaveAttribute('type', 'date');
  fireEvent.change(date, { target: { value: '2026-10-21' } });
  expect(date).toHaveValue('2026-10-21');
  fireEvent.change(screen.getByLabelText('nursingMeds.medicationName'), { target: { value: 'Medicamento sintético' } });
  fireEvent.click(screen.getByRole('button', { name: 'nursingMeds.registerAdmin' }));
  await waitFor(() => expect(api.post).toHaveBeenCalledWith('/appointments/25/medications', {
    medicamentos: [expect.objectContaining({ nombre: 'Medicamento sintético', fecha_aplicacion: '21/10/2026' })],
  }));
  await waitFor(() => expect(date).toHaveValue(''));
});
