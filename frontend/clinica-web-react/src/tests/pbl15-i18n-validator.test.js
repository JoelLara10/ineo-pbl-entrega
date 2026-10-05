import { afterEach, describe, expect, it } from 'vitest';
import { mkdtemp, mkdir, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { validateTranslations } from '../../scripts/check-i18n-keys.mjs';

let directory;
afterEach(async () => { if (directory) await rm(directory, { recursive: true, force: true }); });

describe('PBL-15 — validador de traducciones', () => {
  it('reporta archivo, clave e idioma cuando falta una traducción', async () => {
    directory = await mkdtemp(path.join(tmpdir(), 'ineo-i18n-'));
    const sourceRoot = path.join(directory, 'src');
    await mkdir(sourceRoot);
    await writeFile(path.join(sourceRoot, 'Example.jsx'), "export const Example = ({t}) => t('demo.missing');");
    await writeFile(path.join(directory, 'es.json'), JSON.stringify({ demo: { missing: 'Existe' } }));
    await writeFile(path.join(directory, 'en.json'), JSON.stringify({ demo: {} }));

    const issues = await validateTranslations({ sourceRoot, esFile: path.join(directory, 'es.json'), enFile: path.join(directory, 'en.json') });
    expect(issues).toEqual([expect.objectContaining({ key: 'demo.missing', language: 'en' })]);
    expect(issues[0].file).toContain('Example.jsx');
  });
});
