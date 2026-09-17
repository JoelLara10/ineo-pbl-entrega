import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import es from './locales/es.json';
import en from './locales/en.json';

export const SUPPORTED_LANGUAGES = ['es', 'en'];
export const normalizeLanguage = (language) => {
  const normalized = String(language || '').toLowerCase().split('-')[0];
  return SUPPORTED_LANGUAGES.includes(normalized) ? normalized : 'es';
};

const savedLang = normalizeLanguage(localStorage.getItem('@ineo_lang'));

i18n.use(initReactI18next).init({
  resources: {
    es: { translation: es },
    en: { translation: en },
  },
  lng: savedLang,
  fallbackLng: 'es',
  interpolation: {
    escapeValue: false,
  },
});

i18n.on('languageChanged', (language) => {
  const normalized = normalizeLanguage(language);
  localStorage.setItem('@ineo_lang', normalized);
  document.documentElement.lang = normalized;
});

document.documentElement.lang = savedLang;

export default i18n;
