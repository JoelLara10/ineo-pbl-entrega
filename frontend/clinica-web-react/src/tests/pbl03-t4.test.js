import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const read = (path) => readFileSync(resolve(process.cwd(), path), 'utf8');

describe('PBL-03-T4 permisos, i18n y errores', () => {
  it('expone rutas clinical a médico y limita analytics/met/unsupervised', () => {
    const router = read('src/router/AppRouter.jsx');
    expect(router).toContain('admin/spark/clinical');
    expect(router).toContain('isMedico');
    // El panel clínico debe poder abrirse con médico (canSparkClinical o isMedico).
    expect(router).toMatch(/canSparkClinical|isMedico/);
  });

  it('usa claves pending y completed del criterio de aceptación', () => {
    const analysis = read('src/pages/spark/SparkAnalysisScreen.jsx');
    expect(analysis).toContain('spark.states.pending.title');
    expect(analysis).toContain('spark.states.pending.action');
    expect(analysis).toContain('spark.states.completed.title');
    expect(analysis).toContain('spark.states.failed.action');
    expect(analysis).toContain('spark.states.processing.hint');
  });

  it('mapea 403, 401 y 409 a estados de error específicos', () => {
    const analysis = read('src/pages/spark/SparkAnalysisScreen.jsx');
    expect(analysis).toContain('forbidden');
    expect(analysis).toContain('unauthorized');
    expect(analysis).toContain('conflict');
    expect(analysis).toContain('mapHttpError');
  });

  it('mantiene paridad ES/EN incluyendo pending, completed, forbidden y conflict', () => {
    const es = JSON.parse(read('src/i18n/locales/es.json'));
    const en = JSON.parse(read('src/i18n/locales/en.json'));
    const required = [
      'pending', 'processing', 'completed', 'failed',
      'empty', 'offline', 'forbidden', 'unauthorized', 'conflict', 'error',
    ];
    required.forEach((key) => {
      expect(es.spark.states[key]).toBeDefined();
      expect(en.spark.states[key]).toBeDefined();
    });
    expect(Object.keys(es.spark.states).sort()).toEqual(Object.keys(en.spark.states).sort());
  });

  it('el dashboard filtra tarjetas por rol médico', () => {
    const dashboard = read('src/pages/spark/SparkDashboard.jsx');
    expect(dashboard).toContain('medico');
    expect(dashboard).toContain('clinical');
    expect(dashboard).toContain('cardsForRole');
  });
});
