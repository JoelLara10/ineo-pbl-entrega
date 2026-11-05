"""Gate coverage of changed executable product API lines, retain global metrics."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


def changed_lines(diff):
    current, result = None, {}
    for row in diff.splitlines():
        if row.startswith('+++ b/'):
            current = row[6:]
        match = re.match(r'@@ .* \+(\d+)(?:,(\d+))? @@', row)
        if match and current:
            start, count = int(match[1]), int(match[2] if match[2] is not None else 1)
            result.setdefault(current, set()).update(range(start, start + count))
    return result


def measure(diff, xml):
    changed = changed_lines(diff)
    measured = []
    for cls in xml.findall('.//class'):
        name = 'backend/api_hospital/' + cls.get('filename').replace('\\', '/')
        for line in cls.findall('./lines/line'):
            number = int(line.get('number'))
            if number in changed.get(name, set()):
                measured.append(dict(file=name, line=number, hit=int(line.get('hits')) > 0))
    # Missing coverage for a changed file is a failure, never silently N/A.
    known = {x['file'] for x in measured}
    classes = {'backend/api_hospital/' + x.get('filename').replace('\\', '/') for x in xml.findall('.//class')}
    missing = sorted(name for name, lines in changed.items() if lines and name not in classes)
    covered = sum(x['hit'] for x in measured)
    percent = covered / len(measured) * 100 if measured else 100
    return dict(executable_changed=len(measured), covered=covered, percent=percent,
                missing_files=missing, lines=measured, passed=not missing and percent >= 80,
                threshold=80, scope='changed executable production API lines; excludes tests and infrastructure runners')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--xml', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    base = subprocess.check_output(['git','merge-base','origin/develop','HEAD'],cwd=ROOT,text=True).strip()
    diff = subprocess.check_output(['git','diff',base,'HEAD','--unified=0','--','backend/api_hospital/*.py',
                                    ':(exclude)backend/api_hospital/tests/**',' :(exclude)backend/api_hospital/testing/**'.strip()],cwd=ROOT,text=True)
    result = measure(diff, ET.parse(args.xml).getroot())
    result['base'] = base
    Path(args.out).write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps(result))
    raise SystemExit(0 if result['passed'] else 1)


if __name__ == '__main__':
    main()
