import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const read = (path) => readFileSync(resolve(process.cwd(), path), 'utf8');

describe('Tareas de Joel del Sprint 1', () => {
  it('PBL-01-T2 registra el panel y los cuatro módulos Spark', () => {
    const router = read('src/router/AppRouter.jsx');
    [
      'admin/spark',
      'admin/spark/analytics',
      'admin/spark/met',
      'admin/spark/clinical',
      'admin/spark/unsupervised',
    ].forEach((route) => expect(router).toContain(`path="${route}"`));
  });

  it('PBL-04-T2 presenta estados con acciones de recuperación', () => {
    const analysis = read('src/pages/spark/SparkAnalysisScreen.jsx');
    const dashboard = read('src/pages/spark/SparkDashboard.jsx');
    expect(analysis).toContain('spark.states.pending.action');
    expect(analysis).toContain("spark.states.empty.action");
    expect(analysis).toContain("spark.states.failed.action");
    expect(analysis).toContain("spark.states.processing.hint");
    expect(analysis).toContain("common.retry");
    expect(dashboard).toContain("spark.states.offline.hint");
  });

  it('PBL-05-T3 mantiene las claves Spark equivalentes en ambos idiomas', () => {
    const es = JSON.parse(read('src/i18n/locales/es.json'));
    const en = JSON.parse(read('src/i18n/locales/en.json'));
    expect(es.spark).toBeDefined();
    expect(en.spark).toBeDefined();
    expect(Object.keys(es.spark)).toEqual(Object.keys(en.spark));
    expect(Object.keys(es.spark.types)).toEqual(Object.keys(en.spark.types));
    expect(Object.keys(es.spark.states)).toEqual(Object.keys(en.spark.states));
  });
});
