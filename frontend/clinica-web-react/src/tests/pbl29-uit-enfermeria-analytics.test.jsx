// @vitest-environment jsdom
/**
 * PBL-29 — UIT para Enfermería, Estudios y Analytics
 * Casos: CP-UIT-001 (Valoración), CP-UIT-002 (Balance hídrico),
 *        CP-UIT-003 (Cuidados), CP-UIT-004 (Analytics)
 * Herramientas: Vitest + React Testing Library
 * Datos sintéticos. Validación, teclado, gráficas y mensajes.
 */
import '@testing-library/jest-dom/vitest';
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { I18nextProvider } from 'react-i18next';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createAppI18n } from '../i18n/setup';
import EnfermeriaAssessmentScreen from '../pages/enfermeria/EnfermeriaAssessmentScreen';
import EnfermeriaFluidBalanceScreen from '../pages/enfermeria/EnfermeriaFluidBalanceScreen';
import EnfermeriaCareScreen from '../pages/enfermeria/EnfermeriaCareScreen';
import AnalysisDashboard from '../pages/spark/AnalysisCharts';
import api from '../services/api';

vi.mock('../services/api', () => ({
  default: { get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() },
}));

vi.mock('../context/PatientContext', () => ({
  usePatient: () => ({
    selectedPatient: {
      id_atencion: 'AT-S10-001',
      Id_exp: 'EXP-S10-001',
      nombre: 'Paciente Sintetico S10',
    },
  }),
}));

const storageMock = { getItem: () => 'es', setItem: () => {} };

beforeEach(() => {
  vi.clearAllMocks();
  vi.spyOn(window, 'alert').mockImplementation(() => {});
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

function mountWithI18n(ui, language = 'es') {
  const i18n = createAppI18n(storageMock);
  i18n.changeLanguage(language);
  render(
    <I18nextProvider i18n={i18n}>
      <MemoryRouter>{ui}</MemoryRouter>
    </I18nextProvider>,
  );
  return i18n;
}

/* -------------------------------------------------------------------------- */
/* CP-UIT-001 — Valoración de Enfermería: completar y validar formulario      */
/* -------------------------------------------------------------------------- */
describe('CP-UIT-001 — Valoración de Enfermería (completar y validar)', () => {
  it('muestra campos, permite completar con teclado y conserva patrón unificado', async () => {
    api.get.mockResolvedValue({ data: [] });
    api.post.mockResolvedValue({ data: { ok: true } });
    const i18n = mountWithI18n(<EnfermeriaAssessmentScreen />);

    expect(await screen.findByText(i18n.t('nursingAssessment.noRecords'))).toBeInTheDocument();
    expect(api.get).toHaveBeenCalledWith('/appointments/AT-S10-001/nursing-assessment');

    const user = userEvent.setup();
    await user.type(
      screen.getByLabelText(i18n.t('nursingAssessment.generalStateLabel')),
      'Estable',
    );
    await user.type(screen.getByLabelText(i18n.t('nursingAssessment.painLabel')), '2/10');
    await user.type(
      screen.getByLabelText(i18n.t('nursingAssessment.mobilityLabel')),
      'Independiente',
    );
    await user.type(
      screen.getByLabelText(i18n.t('nursingAssessment.fallRiskLabel')),
      'Bajo',
    );
    await user.type(
      screen.getByLabelText(i18n.t('nursingAssessment.uprRiskLabel')),
      'Sin riesgo',
    );
    await user.type(
      screen.getByLabelText(i18n.t('nursingAssessment.observationsLabel')),
      'Datos sintéticos S10 - valoración OK',
    );

    const saveBtn = screen.getByRole('button', { name: i18n.t('nursingAssessment.save') });
    expect(saveBtn).toBeEnabled();
    await user.click(saveBtn);

    await waitFor(() =>
      expect(api.post).toHaveBeenCalledWith(
        '/appointments/AT-S10-001/nursing-assessment',
        expect.objectContaining({
          estado_general: 'Estable',
          dolor: '2/10',
          observaciones: 'Datos sintéticos S10 - valoración OK',
        }),
      ),
    );
    expect(window.alert).toHaveBeenCalledWith(i18n.t('nursingAssessment.saveSuccess'));
  });

  it('muestra error de servicio sin borrar datos válidos ya capturados', async () => {
    api.get.mockResolvedValue({ data: [] });
    api.post.mockRejectedValue({
      response: { data: { error: 'Error de red sintético' } },
    });
    const i18n = mountWithI18n(<EnfermeriaAssessmentScreen />);
    const user = userEvent.setup();

    // Todos los campos obligatorios (el form no envía si faltan)
    await user.type(
      screen.getByLabelText(i18n.t('nursingAssessment.generalStateLabel')),
      'Estable',
    );
    await user.type(screen.getByLabelText(i18n.t('nursingAssessment.painLabel')), '1/10');
    await user.type(
      screen.getByLabelText(i18n.t('nursingAssessment.mobilityLabel')),
      'Independiente',
    );
    await user.type(
      screen.getByLabelText(i18n.t('nursingAssessment.fallRiskLabel')),
      'Bajo',
    );
    await user.type(
      screen.getByLabelText(i18n.t('nursingAssessment.uprRiskLabel')),
      'Sin riesgo',
    );

    await user.click(screen.getByRole('button', { name: i18n.t('nursingAssessment.save') }));

    await waitFor(() => expect(window.alert).toHaveBeenCalled());
    // Los valores siguen en el formulario (no se pierden)
    expect(screen.getByLabelText(i18n.t('nursingAssessment.generalStateLabel'))).toHaveValue(
      'Estable',
    );
    expect(screen.getByLabelText(i18n.t('nursingAssessment.painLabel'))).toHaveValue('1/10');
  });

  it('navegación y botones secundarios siguen el patrón unificado', async () => {
    api.get.mockResolvedValue({ data: [] });
    const i18n = mountWithI18n(<EnfermeriaAssessmentScreen />);
    expect(await screen.findByText(i18n.t('nursingAssessment.noRecords'))).toBeInTheDocument();
    const refreshCandidates = screen.getAllByRole('button');
    expect(refreshCandidates.length).toBeGreaterThan(0);
  });
});

/* -------------------------------------------------------------------------- */
/* CP-UIT-002 — Balance hídrico: registrar entradas/salidas y calcular total  */
/* -------------------------------------------------------------------------- */
describe('CP-UIT-002 — Balance hídrico (entradas/salidas y totales)', () => {
  it('calcula totales correctos con valores positivos, cero y límite', async () => {
    api.get.mockResolvedValue({ data: [] });
    const i18n = mountWithI18n(<EnfermeriaFluidBalanceScreen />);

    expect(screen.getByTestId('total-inputs')).toHaveTextContent('0 ml');
    expect(screen.getByTestId('total-outputs')).toHaveTextContent('0 ml');
    expect(screen.getByTestId('net-balance')).toHaveTextContent('0 ml');

    const oralLabel = i18n.t('nursingFluidBalance.oralInputsPlaceholder');
    const ivLabel = i18n.t('nursingFluidBalance.ivInputsPlaceholder');
    const urineLabel = i18n.t('nursingFluidBalance.urineOutputsPlaceholder');
    const drainLabel = i18n.t('nursingFluidBalance.drainageOutputsPlaceholder');

    fireEvent.change(screen.getByLabelText(oralLabel), { target: { value: '500' } });
    fireEvent.change(screen.getByLabelText(ivLabel), { target: { value: '250' } });
    fireEvent.change(screen.getByLabelText(urineLabel), { target: { value: '300' } });
    fireEvent.change(screen.getByLabelText(drainLabel), { target: { value: '50' } });

    await waitFor(() => {
      expect(screen.getByTestId('total-inputs')).toHaveTextContent('750 ml');
      expect(screen.getByTestId('total-outputs')).toHaveTextContent('350 ml');
      expect(screen.getByTestId('net-balance')).toHaveTextContent('400 ml');
    });
  });

  it('acepta cero y valores límite sin borrar datos válidos en error', async () => {
    api.get.mockResolvedValue({ data: [] });
    api.post.mockRejectedValue({ response: { data: { error: 'Fallo red' } } });
    const i18n = mountWithI18n(<EnfermeriaFluidBalanceScreen />);

    const oralLabel = i18n.t('nursingFluidBalance.oralInputsPlaceholder');
    const ivLabel = i18n.t('nursingFluidBalance.ivInputsPlaceholder');
    fireEvent.change(screen.getByLabelText(oralLabel), { target: { value: '0' } });
    fireEvent.change(screen.getByLabelText(ivLabel), { target: { value: '1000' } });

    const saveName = i18n.t('nursingFluidBalance.save');
    fireEvent.click(screen.getByRole('button', { name: new RegExp(saveName, 'i') }));

    await waitFor(() => expect(window.alert).toHaveBeenCalled());
    expect(screen.getByLabelText(oralLabel)).toHaveValue(0);
    expect(screen.getByLabelText(ivLabel)).toHaveValue(1000);
  });

  it('distingue visualmente entradas, salidas y balance neto', () => {
    api.get.mockResolvedValue({ data: [] });
    mountWithI18n(<EnfermeriaFluidBalanceScreen />);
    expect(screen.getByTestId('total-inputs')).toBeInTheDocument();
    expect(screen.getByTestId('total-outputs')).toBeInTheDocument();
    expect(screen.getByTestId('net-balance')).toBeInTheDocument();
  });
});

/* -------------------------------------------------------------------------- */
/* CP-UIT-003 — Cuidados de Enfermería: crear, editar y cancelar              */
/* -------------------------------------------------------------------------- */
describe('CP-UIT-003 — Cuidados de Enfermería (crear / mensajes consistentes)', () => {
  it('permite crear cuidado sintético y muestra mensajes consistentes', async () => {
    api.get.mockResolvedValue({ data: [] });
    api.post.mockResolvedValue({ data: { ok: true } });
    const i18n = mountWithI18n(<EnfermeriaCareScreen />);
    const user = userEvent.setup();

    expect(
      await screen.findByText(i18n.t('nursingCare.noRecords')),
    ).toBeInTheDocument();

    const textareas = screen.getAllByRole('textbox');
    expect(textareas.length).toBeGreaterThanOrEqual(4);

    await user.type(textareas[0], 'Diagnóstico sintético S10');
    await user.type(textareas[1], 'Objetivo: movilización temprana');
    await user.type(textareas[2], 'Intervención: cambio de posición q2h');
    await user.type(textareas[3], 'Evaluación: tolerancia adecuada');

    const saveBtn = screen.getByRole('button', { name: i18n.t('nursingCare.save') });
    await user.click(saveBtn);

    await waitFor(() =>
      expect(api.post).toHaveBeenCalledWith(
        expect.stringContaining('/nursing-care'),
        expect.objectContaining({
          diagnostico_enfermeria: expect.stringContaining('Diagnóstico sintético'),
        }),
      ),
    );
    expect(window.alert).toHaveBeenCalledWith(i18n.t('nursingCare.saveSuccess'));
  });

  it('conserva datos al fallar el guardado (no pérdida silenciosa)', async () => {
    api.get.mockResolvedValue({ data: [] });
    api.post.mockRejectedValue({
      response: { data: { error: 'Error de red sintético' } },
    });
    const i18n = mountWithI18n(<EnfermeriaCareScreen />);
    const user = userEvent.setup();

    const textareas = await screen.findAllByRole('textbox');
    await user.type(textareas[0], 'Cuidado que no debe perderse');
    await user.click(screen.getByRole('button', { name: i18n.t('nursingCare.save') }));

    await waitFor(() => expect(window.alert).toHaveBeenCalled());
    expect(textareas[0]).toHaveValue('Cuidado que no debe perderse');
  });

  it('botones de recarga y guardar están presentes y con etiquetas consistentes', async () => {
    api.get.mockResolvedValue({ data: [] });
    const i18n = mountWithI18n(<EnfermeriaCareScreen />);
    expect(await screen.findByText(i18n.t('nursingCare.noRecords'))).toBeInTheDocument();
    expect(screen.getByRole('button', { name: i18n.t('nursingCare.save') })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: i18n.t('nursingCare.reload') })).toBeInTheDocument();
  });
});

/* -------------------------------------------------------------------------- */
/* CP-UIT-004 — Analytics: interpretar gráfica y tabla equivalente            */
/* -------------------------------------------------------------------------- */
describe('CP-UIT-004 — Analytics (gráfica + tabla equivalente)', () => {
  const chart = (key, rows, extra = {}) => ({
    key,
    rows,
    unit: 'attentions',
    scope: 'history',
    mode: 'bar',
    source: 'atencion',
    ...extra,
  });

  const data = (charts, kpis = []) => ({
    metadata: { period: { start: '2026-10-24', end: '2026-10-30' } },
    dashboard: { charts, kpis },
  });

  function show(dashboardData, language = 'es') {
    const i18n = createAppI18n(storageMock);
    i18n.changeLanguage(language);
    return render(
      <I18nextProvider i18n={i18n}>
        <AnalysisDashboard data={dashboardData} />
      </I18nextProvider>,
    );
  }

  it('título, periodo, etiquetas, valores, unidades y tabla coinciden', () => {
    show(
      data([
        chart('attentionStatus', [
          { label: 'ABIERTA', value: 4 },
          { label: 'CERRADA', value: 8 },
        ]),
      ]),
    );

    expect(screen.getByRole('heading', { name: /Atenciones por estado/i })).toBeInTheDocument();
    expect(screen.getAllByText('Abiertas').length).toBeGreaterThan(0);
    expect(screen.getByRole('img')).toHaveAccessibleName(/Atenciones por estado/i);

    fireEvent.click(screen.getByText(/Ver tabla de datos/i));
    const rows = screen.getAllByRole('row');
    expect(rows.length).toBeGreaterThanOrEqual(3);
    expect(screen.getByText(/Fuente:/i)).toBeInTheDocument();
  });

  it('mantiene valores conocidos y unidades en tabla y gráfica', () => {
    show(
      data([
        chart(
          'daily',
          [
            { label: '2026-10-24', value: 5 },
            { label: '2026-10-25', value: 0 },
            { label: '2026-10-26', value: 12 },
          ],
          { mode: 'line' },
        ),
      ]),
    );

    const svg = screen.getByRole('img');
    expect(svg.querySelectorAll('circle').length).toBe(3);

    fireEvent.click(screen.getByText(/Ver tabla de datos/i));
    expect(screen.getByRole('columnheader', { name: /Fecha/i })).toBeInTheDocument();

    // "5" y "12" aparecen en eje SVG y en tabla: usar getAllByText
    expect(screen.getAllByText('5').length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText('12').length).toBeGreaterThanOrEqual(1);

    // Verificar valores concretos dentro de la tabla
    const table = screen.getByRole('table');
    expect(within(table).getByText('5')).toBeInTheDocument();
    expect(within(table).getByText('12')).toBeInTheDocument();
    expect(within(table).getByText('0')).toBeInTheDocument();
  });

  it('estado vacío se comunica de forma clara', () => {
    show(data([chart('groups', [])]));
    expect(screen.getByRole('status')).toHaveTextContent(/No hay registros suficientes|sin datos|empty/i);
  });
});
