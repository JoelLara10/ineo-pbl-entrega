// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { I18nextProvider } from 'react-i18next';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createAppI18n } from '../i18n/setup';
import EnfermeriaAssessmentScreen from '../pages/enfermeria/EnfermeriaAssessmentScreen';
import api from '../services/api';

vi.mock('../services/api', () => ({ default: { get: vi.fn(), post: vi.fn() } }));
vi.mock('../context/PatientContext', () => ({
  usePatient: () => ({ selectedPatient: { id_atencion: 'AT-JAIME-8', Id_exp: 'EXP-JAIME-8' } }),
}));

beforeEach(() => {
  vi.clearAllMocks();
  vi.spyOn(window, 'alert').mockImplementation(() => {});
});
afterEach(() => { cleanup(); vi.restoreAllMocks(); });

const mount = () => {
  const i18n = createAppI18n({ getItem: () => 'es', setItem: () => {} });
  render(<I18nextProvider i18n={i18n}><MemoryRouter><EnfermeriaAssessmentScreen /></MemoryRouter></I18nextProvider>);
  return i18n;
};

describe('PBL-21 — Valoración de Enfermería unificada', () => {
  it('muestra los datos anidados que devuelve la API en el historial', async () => {
    api.get.mockResolvedValue({
      data: [{
        id_valoracion: 3,
        fecha_registro: '2026-10-10T19:38:00Z',
        valoracion: {
          estado_general: 'Estable',
          dolor: '2/10',
          movilidad: 'Independiente',
          riesgo_caidas: 'Bajo',
          riesgo_upp: 'Sin riesgo',
          observaciones: 'Paciente orientado',
        },
      }],
    });
    mount();

    expect(await screen.findByText('Estable')).toBeInTheDocument();
    expect(screen.getByText('2/10')).toBeInTheDocument();
    expect(screen.getByText('Independiente')).toBeInTheDocument();
    expect(screen.getByText('Paciente orientado')).toBeInTheDocument();
  });

  it('conserva consulta, campos, guardado e historial con textos del diseño común', async () => {
    api.get.mockResolvedValue({ data: [] });
    api.post.mockResolvedValue({ data: { ok: true } });
    const i18n = mount();

    expect(await screen.findByText(i18n.t('nursingAssessment.noRecords'))).toBeInTheDocument();
    expect(api.get).toHaveBeenCalledWith('/appointments/AT-JAIME-8/nursing-assessment');
    await userEvent.type(screen.getByLabelText(i18n.t('nursingAssessment.generalStateLabel')), 'Estable');
    await userEvent.type(screen.getByLabelText(i18n.t('nursingAssessment.painLabel')), '0');
    await userEvent.type(screen.getByLabelText(i18n.t('nursingAssessment.mobilityLabel')), 'Independiente');
    await userEvent.type(screen.getByLabelText(i18n.t('nursingAssessment.fallRiskLabel')), 'Bajo');
    await userEvent.type(screen.getByLabelText(i18n.t('nursingAssessment.uprRiskLabel')), 'Bajo');
    await userEvent.type(screen.getByLabelText(i18n.t('nursingAssessment.observationsLabel')), 'Paciente sin dolor');
    await userEvent.click(screen.getByRole('button', { name: i18n.t('nursingAssessment.save') }));

    await waitFor(() => expect(api.post).toHaveBeenCalledWith(
      '/appointments/AT-JAIME-8/nursing-assessment',
      expect.objectContaining({ estado_general: 'Estable', observaciones: 'Paciente sin dolor' })
    ));
    expect(window.alert).toHaveBeenCalledWith(i18n.t('nursingAssessment.saveSuccess'));
  });
});
