import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const read = (path) => readFileSync(resolve(process.cwd(), path), 'utf8');

describe('Entrega corregida de Jaime para Sprint 7', () => {
  it('PBL-03-T3 conserva el flujo ejecutar, consultar estado y cargar resultado', () => {
    const screen = read('src/pages/spark/SparkAnalysisScreen.jsx');
    expect(screen).toContain('sparkService.run(type)');
    expect(screen).toContain('sparkService.getStatus(type)');
    expect(screen).toContain('sparkService.getResults(type)');
    expect(screen).toContain('if (!next.running) load()');
  });

  it('PBL-03-T4 integra pendiente, procesamiento, completado y fallo', () => {
    const screen = read('src/pages/spark/SparkAnalysisScreen.jsx');
    expect(screen).toContain("status.state === 'pending'");
    expect(screen).toContain("status.state === 'processing'");
    expect(screen).toContain("status.state === 'failed'");
    expect(screen).toContain('status.error');
    expect(screen).toContain('data?.available');
  });

  it('PBL-04-T1 mantiene acciones para estados vacíos, sin conexión y fallo', () => {
    const screen = read('src/pages/spark/SparkAnalysisScreen.jsx');
    ['notRun', 'empty', 'offline', 'failed', 'processing'].forEach((state) => {
      expect(screen).toContain(`spark.states.${state}`);
    });
    expect(screen).toContain('common.retry');
    expect(screen).toContain('spark.states.failed.action');
  });
});
