// @vitest-environment jsdom
import '@testing-library/jest-dom/vitest';
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { I18nextProvider } from 'react-i18next';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createAppI18n } from '../i18n/setup';
import AnalysisMetadata from '../pages/spark/AnalysisMetadata';
import OfflineBoundary from '../components/OfflineBoundary';
import Sidebar from '../components/layout/Sidebar';
import LoginScreen from '../pages/auth/LoginScreen';
import { MemoryRouter } from 'react-router-dom';
import { clearOfflineQueue, flushLanguage, queueLanguage, readOfflineQueue, QUEUE_KEY } from '../services/offlineQueue';
import { clearClinicalCache, getClinicalCache, setClinicalCache, purgeLegacyClinicalStorage } from '../services/clinicalCache';
import api from '../services/api';

vi.mock('../services/api', () => ({ default: { put: vi.fn() } }));
vi.mock('../context/PatientContext', () => ({ usePatient: () => ({ selectedPatient: null }) }));
const account = { id: 'owner' };
vi.mock('../context/AuthContext', () => ({ useAuth: () => ({ user: account, logout: vi.fn() }) }));
const online = (value) => Object.defineProperty(navigator, 'onLine', { configurable: true, value });

beforeEach(() => {
  online(true); localStorage.clear(); sessionStorage.clear(); clearOfflineQueue(); clearClinicalCache();
  vi.clearAllMocks(); api.put.mockResolvedValue({ data: { language: 'en' } });
});
afterEach(() => { cleanup(); online(true); vi.useRealTimers(); });

describe('PBL-11', () => {
  it('shows generation, source freshness and calendar period in both languages', async () => {
    const instance = createAppI18n();
    const data = { metadata: { generated_at: '2026-10-20T18:00:00Z', last_updated_at: '2026-10-19T18:00:00Z', period: { start: '2026-10-12', end: '2026-10-19' }, undated_rows: 2 } };
    render(<I18nextProvider i18n={instance}><AnalysisMetadata data={data} /></I18nextProvider>);
    expect(screen.getByText('Fecha de generación')).toBeInTheDocument();
    expect(screen.getByText('12/10/2026 — 19/10/2026')).toBeInTheDocument();
    expect(screen.getByRole('status')).toHaveTextContent('Registros sin fecha: 2');
    await act(() => instance.changeLanguage('en'));
    expect(screen.getByText('Generated at')).toBeInTheDocument();
    expect(screen.getByText('10/12/2026 — 10/19/2026')).toBeInTheDocument();
    expect(screen.getByRole('status')).toHaveTextContent('Undated records: 2');
  });
  it('does not invent dates for historical or empty results', () => {
    render(<I18nextProvider i18n={createAppI18n()}><AnalysisMetadata data={{ available: false }} /></I18nextProvider>);
    expect(screen.getAllByText('No disponible').length).toBe(2);
    expect(screen.getByText('No disponible — No disponible')).toBeInTheDocument();
  });
});

describe('PBL-25', () => {
  it('coalesces language only, keeps no clinical payload and synchronizes after reconnection', async () => {
    online(false);
    queueLanguage('owner', 'es'); queueLanguage('owner', 'en');
    const send = vi.fn().mockResolvedValue({});
    await flushLanguage('owner', send);
    expect(send).not.toHaveBeenCalled();
    expect(Object.keys(JSON.parse(sessionStorage.getItem(QUEUE_KEY))).sort()).toEqual(['createdAt', 'language', 'owner']);
    online(true); await flushLanguage('owner', send);
    expect(send).toHaveBeenCalledExactlyOnceWith({ language: 'en' });
    expect(readOfflineQueue('owner')).toBeNull();
  });
  it('retains failed network operations for an explicit safe retry', async () => {
    queueLanguage('owner', 'en');
    await expect(flushLanguage('owner', vi.fn().mockRejectedValue(new Error('network')))).rejects.toThrow('network');
    expect(readOfflineQueue('owner')?.language).toBe('en');
    await flushLanguage('owner', vi.fn().mockResolvedValue({}));
    expect(readOfflineQueue('owner')).toBeNull();
  });
  it('expires, rejects tampering, isolates accounts and clears unauthorized work', async () => {
    queueLanguage('owner', 'en'); expect(readOfflineQueue('other')).toBeNull();
    expect(() => queueLanguage('owner', 'clinical')).toThrow();
    sessionStorage.setItem(QUEUE_KEY, JSON.stringify({ owner: 'owner', language: 'en', createdAt: Date.now(), patient: 1 }));
    expect(readOfflineQueue('owner')).toBeNull();
    vi.useFakeTimers(); queueLanguage('owner', 'en'); vi.advanceTimersByTime(8 * 3600000);
    expect(readOfflineQueue('owner')).toBeNull(); vi.useRealTimers();
    queueLanguage('owner', 'en');
    await expect(flushLanguage('owner', vi.fn().mockRejectedValue({ response: { status: 401 } }))).rejects.toBeDefined();
    expect(readOfflineQueue('owner')).toBeNull();
  });
  it('serializes concurrent synchronization and preserves a newer preference', async () => {
    queueLanguage('owner', 'en');
    let release;
    const send = vi.fn().mockImplementationOnce(() => new Promise(resolve => { release = resolve; })).mockResolvedValue({});
    const first = flushLanguage('owner', send);
    queueLanguage('owner', 'es');
    const second = flushLanguage('owner', send);
    release({}); await Promise.all([first, second]);
    expect(send.mock.calls.map(call => call[0].language)).toEqual(['en', 'es']);
    expect(readOfflineQueue('owner')).toBeNull();
  });
  it('uses online memory only and removes legacy persistent clinical entries', () => {
    localStorage.setItem('ineo_web_cache_medico_patient_detail_1', 'PRIVATE');
    localStorage.setItem('ineo_selected_patient', 'PRIVATE');
    localStorage.setItem('@ineo_print_history', 'PRIVATE');
    localStorage.setItem('@ineo_lang', 'es');
    setClinicalCache('patient', { synthetic: true });
    expect(getClinicalCache('patient')).toEqual({ synthetic: true });
    purgeLegacyClinicalStorage();
    expect(Object.values(localStorage)).not.toContain('PRIVATE');
    expect(localStorage.getItem('@ineo_lang')).toBe('es');
    online(false); window.dispatchEvent(new Event('offline'));
    expect(getClinicalCache('patient')).toBeNull();
    online(true); expect(getClinicalCache('patient')).toBeNull();
  });
  it('hides clinical children offline and lets the user queue a translated preference', async () => {
    const instance = createAppI18n();
    render(<I18nextProvider i18n={instance}><OfflineBoundary><div>CLINICAL</div></OfflineBoundary></I18nextProvider>);
    expect(screen.getByText('CLINICAL')).toBeInTheDocument();
    online(false); act(() => window.dispatchEvent(new Event('offline')));
    expect(screen.queryByText('CLINICAL')).not.toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Operación offline limitada' })).toBeInTheDocument();
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'en' } });
    await waitFor(() => expect(readOfflineQueue('owner')?.language).toBe('en'));
    expect(api.put).not.toHaveBeenCalled();
    online(true); act(() => window.dispatchEvent(new Event('online')));
    await waitFor(() => expect(api.put).toHaveBeenCalledWith('/auth/preferences', { language: 'en' }, { preferenceOwner: 'owner' }));
    expect(screen.getByText('CLINICAL')).toBeInTheDocument();
  });
});


describe('Language selector placement', () => {
  it('keeps only ES / EN on the online login without the global toolbar', async () => {
    render(<I18nextProvider i18n={createAppI18n()}><OfflineBoundary><LoginScreen /></OfflineBoundary></I18nextProvider>);
    expect(screen.queryByRole('combobox')).not.toBeInTheDocument();
    expect(screen.queryByRole('complementary')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: 'EN' }));
    await waitFor(() => expect(document.documentElement.lang).toBe('en'));
    expect(screen.getByRole('button', { name: 'ES' })).toBeInTheDocument();
  });

  it('changes and synchronizes the language from the sidebar', async () => {
    render(<I18nextProvider i18n={createAppI18n()}><OfflineBoundary><MemoryRouter><Sidebar isOpen /></MemoryRouter></OfflineBoundary></I18nextProvider>);
    expect(screen.queryByRole('combobox')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Español' })).toHaveAttribute('aria-pressed', 'true');
    fireEvent.click(screen.getByRole('button', { name: 'English' }));
    await waitFor(() => expect(api.put).toHaveBeenCalledWith('/auth/preferences', { language: 'en' }, { preferenceOwner: 'owner' }));
    expect(screen.getByRole('button', { name: 'English' })).toHaveAttribute('aria-pressed', 'true');
    expect(localStorage.getItem('@ineo_lang')).toBe('en');
  });
});
