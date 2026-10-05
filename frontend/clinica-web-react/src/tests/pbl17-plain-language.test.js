import { describe, expect, it } from 'vitest';
import es from '../i18n/locales/es.json';

describe('PBL-17 — lenguaje cotidiano', () => {
  it('presenta nombres comprensibles en navegación y análisis', () => {
    expect(es.sidebar.spark).toBe('Análisis de datos');
    expect(es.sidebar.dashboard).toBe('Inicio');
    expect(es.sidebar.configBackup).toBe('Copias de seguridad');
    expect(es.spark.title).toBe('Panel de análisis de datos');
    expect(es.spark.types.met.title).toBe('Actividad diaria');
    expect(es.spark.types.unsupervised.title).toBe(
      'Patrones en los datos'
    );
  });

  it('evita tecnicismos visibles sin explicación', () => {
    const visibleLabels = [
      es.sidebar.spark,
      es.sidebar.sparkSection,
      es.sidebar.dashboard,
      es.sidebar.medicalNote,
      es.sidebar.labRequests,
      es.sidebar.labResults,
      es.sidebar.configBackup,
      es.spark.eyebrow,
      es.spark.title,
      es.spark.types.met.title,
      es.spark.types.unsupervised.title,
      es.spark.sections.pca,
      es.spark.states.offline.title,
    ].join(' ');

    expect(visibleLabels).not.toMatch(
      /\b(?:Dashboard|Backup|SOAP|MET|PCA|Spark)\b/i
    );
  });
});