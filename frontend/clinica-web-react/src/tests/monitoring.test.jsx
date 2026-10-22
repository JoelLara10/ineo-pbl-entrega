// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, fireEvent, act, cleanup } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import api from '../services/api';
import { I18nextProvider } from 'react-i18next';
import { createAppI18n } from '../i18n/setup';
import { readingState, readingTime, readingValue, alertTitle } from '../services/monitoringService';
const i18n = createAppI18n({ getItem: () => 'es', setItem: () => {} });
import MonitoringScreen from '../pages/monitoring/MonitoringScreen';
import { monitoringService } from '../services/monitoringService';
vi.mock('../services/api', () => ({ default: { get: vi.fn(), patch: vi.fn(), post: vi.fn() } }));
vi.mock('../context/AuthContext', () => ({ useAuth: () => ({ user: { role: 'medico' } }) }));
const patient = {patient_id: 1, name: 'Paciente QA', device: {device_id:'ESP32-QA',online:true}, latest: {timestamp:'2026-10-12T00:00:00Z',heart_rate:null,spo2:null,finger_detected:false,temperature:24}, alerts:[{id:'fall-1',type:'fall',timestamp:'2026-10-12T00:00:00Z',acknowledged:false}],history:[]};
beforeEach(async () => { vi.clearAllMocks(); await i18n.changeLanguage('es'); });
afterEach(cleanup);
describe('monitoring API and screen', () => {
 it('uses the API data array without an extra patients wrapper', async () => {api.get.mockResolvedValue({data:{success:true,data:[patient]}});expect(await monitoringService.patients()).toEqual([patient]);expect(api.get).toHaveBeenCalledWith('/monitoring/patients');});
 it('shows a possible fall independently of missing vital readings and acknowledges it', async () => {
 api.get.mockResolvedValue({data:{success:true,data:patient}});api.patch.mockResolvedValue({data:{success:true,data:{}}});
 render(<I18nextProvider i18n={i18n}><MemoryRouter initialEntries={['/monitoreo/1']}><Routes><Route path="/monitoreo/:patientId" element={<MonitoringScreen />} /></Routes></MemoryRouter></I18nextProvider>);
 await screen.findByText('Posible caída detectada');expect(screen.getByText('Sin contacto con el sensor')).toBeTruthy();fireEvent.click(screen.getByText('Reconocer alerta'));await waitFor(() => expect(api.patch).toHaveBeenCalledWith('/monitoring/alerts/fall-1/acknowledge'));
 });
});

it('switches loaded monitoring and errors between ES and EN without reloading data', async () => {
 api.get.mockResolvedValue({data:{success:true,data:patient}});
 api.patch.mockRejectedValue(new Error('offline'));
 render(<I18nextProvider i18n={i18n}><MemoryRouter initialEntries={['/monitoreo/1']}><Routes><Route path="/monitoreo/:patientId" element={<MonitoringScreen />} /></Routes></MemoryRouter></I18nextProvider>);
 await screen.findByText('Posible caída detectada');
 fireEvent.click(screen.getByText('Reconocer alerta'));
 await screen.findByRole('alert');
 const calls = api.get.mock.calls.length;
 await act(() => i18n.changeLanguage('en'));
 expect(screen.getByRole('heading', {name:'Patient monitoring'})).toBeTruthy();
 expect(screen.getByText('Possible fall detected')).toBeTruthy();
 expect(screen.getByText('No sensor contact')).toBeTruthy();
 expect(screen.getByRole('alert').textContent).toContain('Could not acknowledge');
 expect(screen.getByRole('columnheader', {name:'Heart rate'})).toBeTruthy();
 expect(api.get.mock.calls.length).toBe(calls);
 await act(() => i18n.changeLanguage('es'));
 expect(screen.getByText('Posible caída detectada')).toBeTruthy();
 expect(screen.getByRole('alert').textContent).toContain('No se pudo reconocer');
});
it('translates all sensor states, units, dates and known API alerts', async () => {
 await i18n.changeLanguage('en'); const t = i18n.t.bind(i18n);
 expect(readingState({},t)).toBe('No device assigned');
 expect(readingState({device:{}},t)).toBe('No readings');
 expect(readingState({...patient,device:{online:false}},t)).toBe('Device disconnected');
 expect(readingState({...patient,latest:{stale:true}},t)).toBe('Outdated reading');
 expect(readingState({...patient,latest:{}},t)).toBe('Recent reading');
 expect(readingValue(null,'',t)).toBe('No reading');
 expect(readingTime(null,'en',t)).toBe('No date');
 expect(readingTime(patient.latest.timestamp,'en',t)).toBe(new Date(patient.latest.timestamp).toLocaleString('en-US'));
 for (const type of ['fall','low_heart_rate','high_heart_rate','low_spo2']) expect(alertTitle({type,message:'mensaje API'},t)).not.toBe('mensaje API');
 expect(alertTitle({},t)).toBe('Monitoring alert');
});
