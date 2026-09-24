import { describe, expect, it, vi } from 'vitest';
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { createInstance } from 'i18next';
import { I18nextProvider } from 'react-i18next';
import { readFileSync } from 'node:fs';
import es from '../i18n/locales/es.json';
import en from '../i18n/locales/en.json';
import { DataObject } from '../pages/spark/SparkAnalysisScreen';
import { sparkService } from '../services/sparkService';
import api from '../services/api';

vi.mock('../services/api', () => ({ default: { get: vi.fn(), post: vi.fn() } }));

const leaves = (object, path = '') => Object.entries(object).flatMap(([key, value]) =>
  typeof value === 'object' ? leaves(value, `${path}${key}.`) : [`${path}${key}`]);

describe('Sprint 7 — Zahid: PBL-05-T5 y contrato consumidor Spark', () => {
  it('traduce todas las claves estáticas y dinámicas de Spark', () => {
    expect(leaves(es.spark).sort()).toEqual(leaves(en.spark).sort());
    for (const locale of [es, en]) {
      const get = (path) => path.split('.').reduce((obj, key) => obj?.[key], locale);
      for (const file of ['SparkAnalysisScreen.jsx', 'SparkDashboard.jsx']) {
        const code = readFileSync(new URL(`../pages/spark/${file}`, import.meta.url), 'utf8');
        for (const match of code.matchAll(/t\(['"](spark\.[^'"]+)['"]/g)) {
          expect(get(match[1]), match[1]).toBeTypeOf('string');
        }
      }
      for (const kind of ['analytics', 'met', 'clinical', 'unsupervised']) {
        expect(locale.spark.types[kind].title).toBeTruthy();
        expect(locale.spark.types[kind].description).toBeTruthy();
      }
      for (const state of ['error', 'offline', 'loading', 'processing', 'failed', 'notRun', 'empty']) {
        expect(locale.spark.states[state].title).toBeTruthy();
        if (state !== 'error') expect(locale.spark.states[state].hint).toBeTruthy();
      }
    }
  });

  it.each([['es', 'Promedio', 'Frecuencia cardíaca'], ['en', 'Mean', 'Heart rate']])(
    'renderiza etiquetas y medidas reales en %s', async (lang, average, measure) => {
      const i18n = createInstance();
      await i18n.init({ lng: lang, resources: { es: { translation: es }, en: { translation: en } } });
      const html = renderToStaticMarkup(createElement(I18nextProvider, { i18n },
        createElement(DataObject, { data: { mean: 82.5, features: ['fc'] } })));
      expect(html).toContain(average);
      expect(html).toContain(measure);
      expect(html).not.toContain('spark.');
    }
  );

  it.each(['analytics', 'met', 'clinical', 'unsupervised'])('consume las rutas y formatos de %s', async (kind) => {
    const result = { contract_version: '1.0', available: true, summary: { total: 8 }, visualizations: [] };
    api.get.mockResolvedValueOnce({ data: result });
    expect(await sparkService.getResults(kind)).toEqual(result);
    expect(api.get).toHaveBeenLastCalledWith(`/spark/${kind}`);
    const state = { state: 'pending', running: true, job_id: 'test-job' };
    api.post.mockResolvedValueOnce({ data: { status: state } });
    expect((await sparkService.run(kind)).status).toEqual(state);
    expect(api.post).toHaveBeenLastCalledWith(`/spark/run/${kind}`);
    api.get.mockResolvedValueOnce({ data: state });
    expect(await sparkService.getStatus(kind)).toEqual(state);
    expect(api.get).toHaveBeenLastCalledWith(`/spark/status/${kind}`);
  });

  it('propaga errores de API para que la pantalla permita reintentar', async () => {
    const error = { response: { status: 503, data: { error: 'No disponible' } } };
    api.get.mockRejectedValueOnce(error);
    await expect(sparkService.getOverview()).rejects.toEqual(error);
  });
});
