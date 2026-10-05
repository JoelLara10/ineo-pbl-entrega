import { describe, expect, it } from 'vitest';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const read = (path) => readFileSync(resolve(process.cwd(), path), 'utf8');

describe('PBL-08 vista MET operativa', () => {
  it('MetAnalyticsScreen sigue delegando en SparkAnalysisScreen con type met', () => {
    const screen = read('src/pages/spark/MetAnalyticsScreen.jsx');
    expect(screen).toContain('type="met"');
  });

  it('MetAnalyticsScreen integra el panel operativo sin afectar otros análisis', () => {
    const screen = read('src/pages/spark/MetAnalyticsScreen.jsx');
    expect(screen).toContain("import MetOperationalPanel from './MetOperationalPanel'");
    expect(screen).toContain('ResultsComponent={MetOperationalPanel}');
    expect(screen).toContain('type="met"');
  });

  it('MetOperationalPanel expone KPIs, pistas de decisión y detalle técnico', () => {
    const panel = read('src/pages/spark/MetOperationalPanel.jsx');
    expect(panel).toContain('spark.met.kpis.total.title');
    expect(panel).toContain('spark.met.kpis.peakDay.title');
    expect(panel).toContain('spark.met.kpis.dailyAverage.title');
    expect(panel).toContain('spark.met.decision.highLoad');
    expect(panel).toContain('spark.met.detailTitle');
    expect(panel).toContain('<details');
    expect(panel).toContain('DataObject');
  });

  it('i18n ES e EN incluyen claves operativas MET', () => {
    const es = JSON.parse(read('src/i18n/locales/es.json'));
    const en = JSON.parse(read('src/i18n/locales/en.json'));
    for (const locale of [es, en]) {
      expect(locale.spark.met.kpis.total.title).toBeTruthy();
      expect(locale.spark.met.decision.highLoad).toBeTruthy();
      expect(locale.spark.met.detailTitle).toBeTruthy();
      expect(locale.spark.types.met.description).toBeTruthy();
    }
  });

  it('backend registra MET dentro de los tipos Spark disponibles', () => {
    const service = read('../../backend/api_hospital/services/spark_service.py');
    expect(service).toMatch(/TYPES\s*=\s*\([^)]*'met'[^)]*\)/);
  });
});
