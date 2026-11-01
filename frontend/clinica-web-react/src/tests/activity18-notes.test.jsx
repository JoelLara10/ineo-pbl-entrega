/* @vitest-environment jsdom */
import '@testing-library/jest-dom/vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import Notes from '../pages/enfermeria/EnfermeriaNoteScreen';
const { get, post } = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }));
vi.mock('../services/api', () => ({ default: { get, post } }));
vi.mock('../services/clinicalCache', () => ({ getClinicalCache: () => null, setClinicalCache: () => {} }));
vi.mock('../context/PatientContext', () => ({ usePatient: () => ({ selectedPatient: { id_atencion: 1, Id_exp: 1 } }) }));
vi.mock('react-router-dom', () => ({ useLocation: () => ({ state: {} }), useNavigate: () => vi.fn() }));
vi.mock('react-i18next', () => ({ useTranslation: () => ({ i18n: { language: 'es' }, t: key => key }) }));
afterEach(cleanup);
beforeEach(() => { get.mockReset(); post.mockReset(); get.mockResolvedValue({ data: [] }); vi.spyOn(window, 'alert').mockImplementation(() => {}); });
it('A18 web conserva contrato de POST y vuelve a consultar el historial', async () => {
 post.mockResolvedValue({ status: 201, data: { id_nota: 321, message: 'ok' } });
 render(<Notes />);
 await waitFor(() => expect(get).toHaveBeenCalledTimes(1));
 fireEvent.change(screen.getByRole('textbox'), { target: { value: 'A18 prueba web' } });
 fireEvent.click(screen.getByRole('button', { name: /nursingNote.save/ }));
 await waitFor(() => expect(post).toHaveBeenCalledWith('/appointments/1/nursing-notes', { nota_enfermeria: 'A18 prueba web' }));
 await waitFor(() => expect(get).toHaveBeenCalledTimes(2));
 expect(screen.getByRole('textbox')).toHaveValue('');
});
it('A18 web bloquea una nota vacía sin llamar al servidor', async () => {
 render(<Notes />);
 await waitFor(() => expect(get).toHaveBeenCalled());
 fireEvent.click(screen.getByRole('button', { name: /nursingNote.save/ }));
 expect(post).not.toHaveBeenCalled();
});
it('A18 web conserva el borrador si la API falla', async () => {
 post.mockRejectedValue({ response: { status: 500, data: { error: 'Error interno del servidor' } } });
 render(<Notes />);
 await waitFor(() => expect(get).toHaveBeenCalled());
 fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Borrador pendiente' } });
 fireEvent.click(screen.getByRole('button', { name: /nursingNote.save/ }));
 await waitFor(() => expect(window.alert).toHaveBeenCalled());
 expect(screen.getByRole('textbox')).toHaveValue('Borrador pendiente');
});
