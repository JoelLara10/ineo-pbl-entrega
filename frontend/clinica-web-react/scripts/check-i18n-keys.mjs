import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const SOURCE_EXTENSIONS = new Set(['.js', '.jsx', '.ts', '.tsx']);
const KEY_PATTERN = /\b(?:i18n\.)?t\s*\(\s*['"]([^'"]+)['"]/g;

async function sourceFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const nested = await Promise.all(entries.map(async (entry) => {
    const target = path.join(directory, entry.name);
    if (entry.isDirectory() && entry.name === 'tests') return [];
    if (entry.isDirectory()) return sourceFiles(target);
    return SOURCE_EXTENSIONS.has(path.extname(entry.name)) ? [target] : [];
  }));
  return nested.flat();
}

const hasKey = (dictionary, key) => key.split('.').every((part, index, parts) => {
  dictionary = dictionary?.[part];
  return index < parts.length - 1 ? dictionary && typeof dictionary === 'object' : dictionary !== undefined;
});

export async function validateTranslations({ sourceRoot, esFile, enFile }) {
  const [es, en, files] = await Promise.all([
    readFile(esFile, 'utf8').then(JSON.parse),
    readFile(enFile, 'utf8').then(JSON.parse),
    sourceFiles(sourceRoot),
  ]);
  const issues = [];
  for (const file of files) {
    const content = await readFile(file, 'utf8');
    for (const match of content.matchAll(KEY_PATTERN)) {
      for (const [language, dictionary] of [['es', es], ['en', en]]) {
        if (!hasKey(dictionary, match[1])) issues.push({ file, key: match[1], language });
      }
    }
  }
  return issues;
}

async function main() {
  const projectRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
  const issues = await validateTranslations({
    sourceRoot: path.join(projectRoot, 'src'),
    esFile: path.join(projectRoot, 'src/i18n/locales/es.json'),
    enFile: path.join(projectRoot, 'src/i18n/locales/en.json'),
  });
  if (issues.length) {
    issues.forEach(({ file, key, language }) => console.error(`${path.relative(projectRoot, file)}: falta "${key}" en ${language}.json`));
    process.exitCode = 1;
  } else {
    console.log('i18n OK: todas las claves estáticas usadas existen en es.json y en.json.');
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) await main();
