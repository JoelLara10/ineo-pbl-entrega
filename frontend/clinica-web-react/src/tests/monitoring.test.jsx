// @vitest-environment jsdom
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import api from '../services/api';
import MonitoringScreen from '../pages/monitoring/MonitoringScreen';
import { monitoringService } from '../services/monitoringService';
vi.mock('../services/api', () => ({ default: { get: vi.fn(), patch: vi.fn(), post: vi.fn() } }));
vi.mock('../context/AuthContext', () => ({ useAuth: () => ({ user: { role: 'medico' } }) }));
const patient = {patient_id: 1, name: 'Paciente QA', device: {device_id:'ESP32-QA',online:true}, latest: {timestamp:'2026-10-12T00:00:00Z',heart_rate:null,spo2:null,finger_detected:false,temperature:24}, alerts:[{id:'fall-1',type:'fall',timestamp:'2026-10-12T00:00:00Z',acknowledged:false}],history:[]};
beforeEach(() => vi.clearAllMocks());
describe('monitoring API and screen', () => {
 it('uses the API data array without an extra patients wrapper', async () => {api.get.mockResolvedValue({data:{success:true,data:[patient]}});expect(await monitoringService.patients()).toEqual([patient]);expect(api.get).toHaveBeenCalledWith('/monitoring/patients');});
 it('shows a possible fall independently of missing vital readings and acknowledges it', async () => {
 api.get.mockResolvedValue({data:{success:true,data:patient}});api.patch.mockResolvedValue({data:{success:true,data:{}}});
 render(<MemoryRouter initialEntries={['/monitoreo/1']}><Routes><Route path="/monitoreo/:patientId" element={<MonitoringScreen />} /></Routes></MemoryRouter>);
 await screen.findByText('Posible caída detectada');expect(screen.getByText('Sin contacto con el sensor')).toBeTruthy();fireEvent.click(screen.getByText('Reconocer alerta'));await waitFor(() => expect(api.patch).toHaveBeenCalledWith('/monitoring/alerts/fall-1/acknowledge'));
 });
});
