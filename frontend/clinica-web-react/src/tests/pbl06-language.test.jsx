// @vitest-environment jsdom
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { I18nextProvider, useTranslation } from 'react-i18next';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createAppI18n, LANGUAGE_KEY } from '../i18n/setup';
import { formatRegionalDate, formatRegionalNumber } from '../i18n/regional';
import LoginScreen from '../pages/auth/LoginScreen';
import { AuthProvider, useAuth } from '../context/AuthContext';
import { DataObject } from '../pages/spark/SparkAnalysisScreen';

vi.mock('../services/api', () => ({ default: {
  defaults: { headers: {} }, get: vi.fn(), post: vi.fn(),
} }));

let root;
let host;
globalThis.IS_REACT_ACT_ENVIRONMENT = true;

function SessionAndCurrency() {
  const { logout } = useAuth();
  const { i18n } = useTranslation();
  return <><button onClick={logout}>Test logout</button>
    <output>{formatRegionalNumber(1234.5, i18n.language, { style: 'currency', currency: 'MXN' })}</output></>;
}

async function mount(instance) {
  host = document.createElement('div');
  document.body.append(host);
  root = createRoot(host);
  await act(async () => root.render(<I18nextProvider i18n={instance}><AuthProvider>
    <LoginScreen /><DataObject data={{ day: '2026-09-24', mean: 1234.5 }} /><SessionAndCurrency />
  </AuthProvider></I18nextProvider>));
}

async function click(label) {
  const button = [...host.querySelectorAll('button')].find((item) => item.textContent.trim() === label);
  expect(button).toBeDefined();
  await act(async () => button.click());
}

beforeEach(() => localStorage.clear());
afterEach(async () => {
  if (root) await act(async () => root.unmount());
  root = null;
  host?.remove();
  vi.restoreAllMocks();
});

describe('PBL-06-T1 — persistencia de idioma y formato regional', () => {
  it('cambia textos, fecha y moneda en la misma pantalla mediante los botones reales ES/EN', async () => {
    const instance = createAppI18n();
    await mount(instance);
    const originalInput = host.querySelector('input');
    const originalRoot = host.querySelector('.login-container');
    expect(host.textContent).toContain('Promedio');
    expect(host.textContent).toContain('24/09/2026');
    expect(host.querySelector('output').textContent).toBe('$1,234.50');
    await click('EN');
    expect(host.textContent).toContain('Mean');
    expect(host.textContent).toContain('09/24/2026');
    expect(host.querySelector('output').textContent).toBe('MX$1,234.50');
    expect(host.querySelector('.brand-subtitle').textContent).toBe(instance.t('login.brandSubtitle'));
    expect(host.querySelector('input')).toBe(originalInput);
    expect(host.querySelector('.login-container')).toBe(originalRoot);
    expect(localStorage.getItem(LANGUAGE_KEY)).toBe('en');
    expect(document.documentElement.lang).toBe('en');
    await click('ES');
    expect(host.textContent).toContain('Promedio');
    expect(host.textContent).toContain('24/09/2026');
    expect(document.documentElement.lang).toBe('es');
  });

  it('restaura inglés en una nueva sesión después de cerrar sesión y remontar la aplicación', async () => {
    localStorage.setItem('@ineo_token', 'synthetic-token');
    localStorage.setItem('@ineo_user', JSON.stringify({ role: 'admin', username: 'synthetic' }));
    await mount(createAppI18n());
    await click('EN');
    await click('Test logout');
    expect(localStorage.getItem('@ineo_token')).toBeNull();
    expect(localStorage.getItem('@ineo_user')).toBeNull();
    expect(localStorage.getItem(LANGUAGE_KEY)).toBe('en');
    await act(async () => root.unmount());
    root = null;
    host.remove();
    const nextSession = createAppI18n();
    await mount(nextSession);
    expect(nextSession.language).toBe('en');
    expect(host.textContent).toContain('Mean');
    expect(host.textContent).toContain('09/24/2026');
    expect(host.querySelector('.lang-btn-active').textContent.trim()).toBe('EN');
  });

  it('persiste también cambios de idioma hechos fuera del login', async () => {
    const instance = createAppI18n();
    await instance.changeLanguage('en');
    expect(createAppI18n().language).toBe('en');
  });

  it.each([['en-US', 'en'], ['es-MX', 'es'], ['incorrecto', 'es'], ['', 'es']])(
    'normaliza la preferencia almacenada %s a %s', (saved, expected) => {
      localStorage.setItem(LANGUAGE_KEY, saved);
      expect(createAppI18n().language).toBe(expected);
    }
  );

  it('continúa traduciendo si el navegador bloquea la lectura y escritura de almacenamiento', async () => {
    const blocked = { getItem: () => { throw new Error('blocked'); }, setItem: () => { throw new Error('blocked'); } };
    const instance = createAppI18n(blocked);
    expect(instance.language).toBe('es');
    await instance.changeLanguage('en');
    expect(instance.t('spark.fields.mean')).toBe('Mean');
  });

  it('conserva la fecha de calendario y utiliza el orden regional', () => {
    expect(formatRegionalDate('2026-09-24', 'es')).toBe('24/09/2026');
    expect(formatRegionalDate('2026-09-24', 'en')).toBe('09/24/2026');
    expect(formatRegionalDate('2026-02-30', 'es')).toBe('—');
    expect(formatRegionalDate('invalid', 'en')).toBe('—');
    expect(formatRegionalDate(null, 'es')).toBe('—');
  });

  it.each(['dateTime', 'long', 'longDateTime', 'short'])('localiza fechas y horas de estilo %s', (style) => {
    const value = '2026-09-24T15:30:00';
    const es = formatRegionalDate(value, 'es', style);
    const en = formatRegionalDate(value, 'en', style);
    expect(es).not.toBe(en);
    expect(en).not.toContain(' de ');
    expect(en).not.toContain(' a las ');
  });

  it('formatea cantidades en es-MX/en-US sin confundir México con España', () => {
    expect(formatRegionalNumber(1234.5, 'es', { minimumFractionDigits: 2 })).toBe('1,234.50');
    expect(formatRegionalNumber(1234.5, 'en', { minimumFractionDigits: 2 })).toBe('1,234.50');
    expect(formatRegionalNumber(0, 'es')).toBe('0');
    expect(formatRegionalNumber(Infinity, 'es')).toBe('—');
    expect(formatRegionalNumber(null, 'es')).toBe('—');
  });
});
