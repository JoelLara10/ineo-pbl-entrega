"""Build a release gate from versioned requirements and real JUnit evidence."""
import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def read_results(paths):
    results = {}
    evidence = []
    for path in sorted(map(Path, paths), key=lambda item: item.stat().st_mtime):
        raw = path.read_bytes()
        if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():
            raise ValueError('DTD y entidades no permitidas en evidencia JUnit.')
        tree = ET.fromstring(raw)
        reference = str(path.resolve().relative_to(ROOT)) if path.resolve().is_relative_to(ROOT) else path.name
        evidence.append({'file': reference, 'sha256': hashlib.sha256(raw).hexdigest()})
        for case in tree.iter('testcase'):
            key = case.get('classname', '') + '::' + case.get('name', '')
            outcome = ('failed' if case.find('failure') is not None or case.find('error') is not None
                       else 'skipped' if case.find('skipped') is not None else 'passed')
            results[key] = {'case': key, 'result': outcome, 'evidence': reference}
    return results, evidence


def build_report(manifest, paths):
    results, evidence = read_results(paths)
    regressions = {state: sum(item['result'] == state for item in results.values())
                   for state in ('passed', 'failed', 'skipped')}
    regression_passed = bool(results) and not regressions['failed'] and not regressions['skipped']
    stories = []
    for story in manifest['stories']:
        selectors = story.get('cases', [])
        cases = []
        for selector in selectors:
            matched = [value for key, value in results.items() if selector in key]
            cases.extend(matched or [{'case': selector, 'result': 'not_run', 'evidence': None}])
        cases = list({case['case']: case for case in cases}.values())
        defects = story.get('defects', [])
        approval = story.get('approval', {})
        approval_evidence = approval.get('evidence')
        approval_path = (ROOT / approval_evidence).resolve() if isinstance(approval_evidence, str) else None
        approved = bool(approval.get('by') and approval.get('at') and approval_path
                        and approval_path.is_relative_to(ROOT) and approval_path.is_file()
                        and approval_path.read_text(encoding='utf-8').strip())
        eligible = bool(cases) and all(case['result'] == 'passed' and case['evidence'] for case in cases)
        eligible = eligible and regression_passed and not any(defect.get('status') != 'closed' for defect in defects) and approved
        stories.append({**story, 'cases': cases, 'approval_verified': approved,
                        'acceptance': 'ready_for_acceptance' if eligible else 'pending',
                        'latest_result': 'failed' if any(c['result'] == 'failed' for c in cases)
                        else 'passed' if cases and all(c['result'] == 'passed' for c in cases)
                        else 'pending'})
    return {'generated_at': datetime.now(timezone.utc).isoformat(),
            'sprint': manifest['sprint'], 'stories': stories, 'evidence': evidence,
            'regression_summary': regressions,
            'ready_for_acceptance': bool(stories) and all(s['acceptance'] == 'ready_for_acceptance' for s in stories)}


def render_html(report):
    esc = lambda value: html.escape(str(value))
    sections = []
    for story in report['stories']:
        rows = ''.join('<tr><td>' + '</td><td>'.join(esc(case.get(key) or '—') for key in ('case', 'result', 'evidence')) + '</td></tr>' for case in story['cases'])
        defects = ', '.join(esc(d.get('id', '')) + ': ' + esc(d.get('status', 'open')) for d in story.get('defects', [])) or 'Sin defectos registrados; no acredita ausencia de defectos.'
        sections.append(f"<section><h2>{esc(story['id'])} — {esc(story['title'])}</h2>"
                        f"<p>Requisitos: {esc(', '.join(story['requirements']))} · Resultado: {esc(story['latest_result'])} · Aceptación: {esc(story['acceptance'])}</p>"
                        f"<p>Aprobación documentada: {'Sí' if story['approval_verified'] else 'Pendiente'} · Tipo: {esc(story.get('approval', {}).get('kind', 'sin registrar'))} · {defects}</p>"
                        f"<table><thead><tr><th>Caso</th><th>Último resultado</th><th>Evidencia</th></tr></thead><tbody>{rows or '<tr><td colspan=3>Sin casos vinculados; pendiente de evidencia del responsable.</td></tr>'}</tbody></table></section>")
    return ('<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
            '<title>Reporte de trazabilidad — Sprint 9</title><style>body{font:16px system-ui;max-width:1100px;margin:2rem auto;padding:1rem;color:#183744}section{border:1px solid #ccdce3;padding:1rem;margin:1rem 0}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccdce3;padding:.5rem;text-align:left;overflow-wrap:anywhere}th{background:#edf5f7}</style>'
            f"<h1>{esc(report['sprint'])} — Trazabilidad</h1><p>Generado: {esc(report['generated_at'])}</p><p>Regresión: {esc(report['regression_summary'])}</p><p>La aprobación de tipo technical corresponde a revisión técnica automatizada; no es aceptación UAT ni firma del PO. Las pruebas técnicas no sustituyen QA, UAT ni aprobación humana. Este reporte no modifica Azure DevOps.</p>"
            + ''.join(sections) + '<h2>Integridad de evidencias</h2><pre>' + esc(json.dumps(report['evidence'], ensure_ascii=False, indent=2)) + '</pre></html>')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', type=Path, default=ROOT / 'docs/sprints/sprint-9/traceability.json')
    parser.add_argument('--junit', type=Path, nargs='+', required=True)
    parser.add_argument('--output', type=Path, default=ROOT / 'evidence/sprint-9-joel-zahid/traceability')
    parser.add_argument('--strict', action='store_true', help='Fallar si faltan pruebas, evidencia o aprobación.')
    parser.add_argument('--story', action='append', help='Evaluar únicamente estas historias; repetible, sin ocultar el reporte general.')
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
    if args.story:
        known = {story['id'] for story in manifest['stories']}
        if set(args.story) - known:
            parser.error('Historia desconocida: ' + ', '.join(sorted(set(args.story) - known)))
        manifest['stories'] = [story for story in manifest['stories'] if story['id'] in args.story]
    report = build_report(manifest, args.junit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.with_suffix('.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    args.output.with_suffix('.html').write_text(render_html(report), encoding='utf-8')
    print(f"Reporte generado: {args.output.with_suffix('.html')}")
    if args.strict and not report['ready_for_acceptance']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
