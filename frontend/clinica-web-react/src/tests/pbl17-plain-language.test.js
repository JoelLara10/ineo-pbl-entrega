import { describe, expect, it } from 'vitest';
import es from '../i18n/locales/es.json';
import en from '../i18n/locales/en.json';

const technicalTerms = /\b(?:Dashboard|SOAP|MET|PCA|Spark)\b/i;

function visibleNavigationAndAnalysis(locale) {
  return [
    locale.sidebar.spark,
    locale.sidebar.sparkSection,
    locale.sidebar.dashboard,
    locale.sidebar.medicalNote,
    locale.sidebar.labRequests,
    locale.sidebar.labResults,
    locale.sidebar.configBackup,
    locale.spark.eyebrow,
    locale.spark.title,
    locale.spark.types.met.title,
    locale.spark.types.unsupervised.title,
    locale.spark.sections.pca,
    locale.spark.states.offline.title,
  ].join(' ');
}

describe('PBL-17 — terminología comprensible', () => {
  it('presenta nombres cotidianos en español', () => {
    expect(es.sidebar.spark).toBe('Análisis de datos');
    expect(es.sidebar.dashboard).toBe('Inicio');
    expect(es.sidebar.configBackup).toBe('Copias de seguridad');
    expect(es.spark.title).toBe('Panel de análisis de datos');
    expect(es.spark.types.met.title).toBe('Actividad diaria');
    expect(es.spark.types.unsupervised.title).toBe('Patrones en los datos');
    expect(visibleNavigationAndAnalysis(es)).not.toMatch(technicalTerms);
    expect(visibleNavigationAndAnalysis(es)).not.toMatch(/\bBackup\b/i);
  });

  it('mantiene el mismo criterio de lenguaje claro en inglés', () => {
    expect(en.sidebar.spark).toBe('Data analysis');
    expect(en.sidebar.dashboard).toBe('Home');
    expect(en.spark.title).toBe('Data analysis panel');
    expect(visibleNavigationAndAnalysis(en)).not.toMatch(technicalTerms);
  });
});
