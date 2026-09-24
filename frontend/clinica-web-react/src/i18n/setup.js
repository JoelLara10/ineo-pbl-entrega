import { createInstance } from 'i18next';
import { initReactI18next } from 'react-i18next';
import es from './locales/es.json';
import en from './locales/en.json';

export const LANGUAGE_KEY = '@ineo_lang';
export const normalizeLanguage = (language) => /^en(?:-|$)/i.test(language || '') ? 'en' : 'es';

export function createAppI18n(storage) {
  let saved = 'es';
  try {
    storage ??= globalThis.localStorage;
    saved = normalizeLanguage(storage?.getItem(LANGUAGE_KEY));
  } catch { /* Storage may be blocked; translation must still work. */ }
  const instance = createInstance();
  instance.on('languageChanged', (language) => {
    const selected = normalizeLanguage(language);
    try { storage?.setItem(LANGUAGE_KEY, selected); } catch { /* Session-only preference. */ }
    if (typeof document !== 'undefined') document.documentElement.lang = selected;
  });
  instance.use(initReactI18next).init({
    resources: { es: { translation: es }, en: { translation: en } },
    lng: saved, fallbackLng: 'es', supportedLngs: ['es', 'en'],
    load: 'languageOnly', initImmediate: false,
    interpolation: { escapeValue: false },
  });
  return instance;
}
