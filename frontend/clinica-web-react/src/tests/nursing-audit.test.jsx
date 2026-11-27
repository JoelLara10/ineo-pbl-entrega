// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import Vitals from '../pages/enfermeria/EnfermeriaVitalSignsScreen';
import Notes from '../pages/enfermeria/EnfermeriaNoteScreen';
import Medications from '../pages/enfermeria/EnfermeriaMedicationsScreen';
import Assessment from '../pages/enfermeria/EnfermeriaAssessmentScreen';
import Balance from '../pages/enfermeria/EnfermeriaFluidBalanceScreen';
import Care from '../pages/enfermeria/EnfermeriaCareScreen';
import api from '../services/api';
import { clearClinicalCache } from '../services/clinicalCache';

const stable = vi.hoisted(() => ({ t: key => key, patient: { id_atencion: 1, Id_exp: 1 }, state: {} }));
vi.mock('../services/api', () => ({ default: { get: vi.fn(), post: vi.fn() } }));
vi.mock('react-router-dom', () => ({ useNavigate: () => vi.fn(), useLocation: () => ({ state: stable.state }) }));
vi.mock('../context/PatientContext', () => ({ usePatient: () => ({ selectedPatient: stable.patient }) }));
vi.mock('react-i18next', () => ({ useTranslation: () => ({ t: stable.t, i18n: { language: 'es' } }) }));

beforeEach(() => {
  stable.patient = { id_atencion: 1, Id_exp: 1 }; stable.state = {};
  clearClinicalCache(); api.get.mockReset().mockResolvedValue({ data: [] }); api.post.mockReset();
  vi.spyOn(window, 'alert').mockImplementation(() => {});
});
afterEach(() => { cleanup(); vi.restoreAllMocks(); });

const cases = [
  ['signos', Vitals, 'vitalSigns.save'], ['notas', Notes, 'nursingNote.save'],
  ['medicamentos', Medications, 'nursingMeds.registerAdmin'],
  ['valoración', Assessment, 'nursingAssessment.save'],
  ['balance', Balance, 'nursingFluidBalance.save'], ['cuidados', Care, 'nursingCare.save'],
];

it.each(cases)('%s: muestra fallo de consulta y permite recuperar el historial', async (_name, Component) => {
  api.get.mockRejectedValue(new Error('private mongodb token password'));
  render(<Component />);
  const alerts = await screen.findAllByRole('alert');
  expect(alerts.length).toBeGreaterThan(0);
  expect(document.body.textContent).not.toMatch(/private mongodb|password/);
  api.get.mockResolvedValue({ data: [] });
  fireEvent.click(screen.getByRole('button', { name: 'common.retry' }));
  await waitFor(() => expect(screen.queryByRole('alert')).not.toBeInTheDocument());
});

it.each(cases)('%s: formulario incompleto nunca hace POST', async (_name, Component, save) => {
  const view = render(<Component />);
  await waitFor(() => expect(api.get).toHaveBeenCalled());
  if (Component === Assessment) fireEvent.submit(view.container.querySelector('form'));
  else fireEvent.click(screen.getByRole('button', { name: save }));
  expect(api.post).not.toHaveBeenCalled();
});

it('signos vitales rechaza números parciales en lugar de truncarlos', async () => {
  render(<Vitals />);
  fireEvent.change(screen.getByPlaceholderText('lpm'), { target: { value: '72abc' } });
  fireEvent.click(screen.getByRole('button', { name: 'vitalSigns.save' }));
  expect(api.post).not.toHaveBeenCalled();
  expect(window.alert).toHaveBeenCalledWith(expect.stringMatching(/número válido/));
});

it('cuidados conserva el borrador si falla el envío y no duplica una petición pendiente', async () => {
  const view = render(<Care />);
  const fields = view.container.querySelectorAll('textarea');
  for (const field of Array.from(fields).slice(0, 3)) fireEvent.change(field, { target: { value: 'REGISTRO SINTETICO QA' } });
  let reject;
  api.post.mockImplementation(() => new Promise((_resolve, fail) => { reject = fail; }));
  const save = screen.getByRole('button', { name: 'nursingCare.save' });
  fireEvent.click(save); fireEvent.click(save);
  expect(api.post).toHaveBeenCalledTimes(1);
  reject(Object.assign(new Error('private token password'), { response: { status: 503 } }));
  await waitFor(() => expect(window.alert).toHaveBeenCalled());
  expect(fields[0]).toHaveValue('REGISTRO SINTETICO QA');
  expect(JSON.stringify(window.alert.mock.calls)).not.toMatch(/private token|password/);
});

it('una respuesta tardía de otro paciente no aparece bajo la atención nueva', async () => {
  let resolveOld;
  api.get.mockImplementationOnce(() => new Promise(resolve => { resolveOld = resolve; }))
    .mockResolvedValue({ data: [] });
  const view = render(<Notes />);
  stable.patient = { id_atencion: 3, Id_exp: 3 };
  view.rerender(<Notes />);
  resolveOld({ data: [{ id_nota: 777, nota: 'NO MOSTRAR PACIENTE ANTERIOR' }] });
  await waitFor(() => expect(api.get).toHaveBeenCalledWith('/appointments/3/nursing-notes'));
  expect(screen.queryByText('NO MOSTRAR PACIENTE ANTERIOR')).not.toBeInTheDocument();
});
