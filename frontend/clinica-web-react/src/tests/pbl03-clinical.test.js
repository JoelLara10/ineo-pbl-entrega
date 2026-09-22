import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const read = (path) => readFileSync(resolve(process.cwd(), path), 'utf8');

describe('PBL-03 flujo clínico', () => {
  it('mantiene las claves de estado existentes usadas por Joel', () => {
    const analysis = read('src/pages/spark/SparkAnalysisScreen.jsx');
    expect(analysis).toContain('spark.states.pending.action');
    expect(analysis).toContain('spark.states.empty.action');
    expect(analysis).toContain('spark.states.failed.action');
    expect(analysis).toContain('spark.states.processing.hint');
  });

  it('trata pending sin running como pendiente y no como procesando', () => {
    const analysis = read('src/pages/spark/SparkAnalysisScreen.jsx');
    expect(analysis).toContain("status.running || status.state === 'processing'");
    expect(analysis).toContain("status.state === 'idle' || status.state === 'pending'");
    expect(analysis).not.toMatch(
      /status\.running \|\| status\.state === 'pending' \|\| status\.state === 'processing'/,
    );
  });
});
