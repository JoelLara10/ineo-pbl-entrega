import { readFileSync, statSync } from 'node:fs';
import { resolve } from 'node:path';
const root = resolve('dist');
const manifest = JSON.parse(readFileSync(resolve(root, '.vite/manifest.json'), 'utf8'));
const entry = Object.keys(manifest).find(key => manifest[key].isEntry);
const upfront = new Set();
function collect(key) {
  if (upfront.has(key)) return;
  upfront.add(key);
  for (const dependency of manifest[key].imports || []) collect(dependency);
}
if (!entry) throw new Error('Missing build entry');
collect(entry);
const screens = ['ClinicalAnalyticsScreen', 'MetAnalyticsScreen', 'AnalyticsScreen', 'UnsupervisedAnalyticsScreen'];
const checks = screens.map(name => {
  const key = Object.keys(manifest).find(key => key.endsWith('/' + name + '.jsx'));
  if (!key || upfront.has(key) || !manifest[key].isDynamicEntry) throw new Error(name + ' is not deferred');
  return { screen: name, file: manifest[key].file, bytes: statSync(resolve(root, manifest[key].file)).size };
});
const initialBytes = [...upfront].reduce((sum, key) => sum + statSync(resolve(root, manifest[key].file)).size, 0);
console.log(JSON.stringify({ initialJavaScriptBytes: initialBytes, deferredScreens: checks,
  note: 'Measured production entry plus static JS imports. Deferred screens are excluded from the initial dependency graph; this is not a historical before/after benchmark.' }, null, 2));
