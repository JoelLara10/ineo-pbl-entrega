import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const read = (path) => readFileSync(resolve(process.cwd(), path), 'utf8');

describe('Entrega corregida de Jaime para Sprint 7', () => {
  it('PBL-03-T3 conserva el flujo ejecutar, consultar estado y cargar resultado', () => {
    const screen = read('src/pages/spark/SparkAnalysisScreen.jsx');

    // Ejecutar, consultar estado y cargar resultado
    expect(screen).toContain('sparkService.run(type)');
    expect(screen).toContain('sparkService.getStatus(type)');
    expect(screen).toContain('sparkService.getResults(type)');

    // Cuando deja de procesar, vuelve a cargar resultados
    // (versión actual usa isProcessing; la antigua usaba next.running)
    const reloadsWhenDone =
      screen.includes('if (!next.running) load()') ||
      screen.includes('if (!isProcessing(next))') ||
      /if\s*\(\s*!isProcessing\s*\(\s*next\s*\)\s*\)/.test(screen);

    expect(reloadsWhenDone).toBe(true);
  });

  it('PBL-03-T4 integra pendiente, procesamiento, completado y fallo', () => {
    const screen = read('src/pages/spark/SparkAnalysisScreen.jsx');

    // Estados de job: pending / processing / failed
    // (pueden aparecer en comparaciones directas o dentro de isProcessing)
    const hasPending =
      screen.includes("status.state === 'pending'") ||
      screen.includes("'pending'") ||
      screen.includes('"pending"');
    const hasProcessing =
      screen.includes("status.state === 'processing'") ||
      screen.includes("'processing'") ||
      screen.includes('"processing"');
    const hasFailed =
      screen.includes("status.state === 'failed'") ||
      screen.includes("'failed'") ||
      screen.includes('"failed"');

    expect(hasPending).toBe(true);
    expect(hasProcessing).toBe(true);
    expect(hasFailed).toBe(true);

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
