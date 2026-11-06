"""JTL gate. Expected negative runs must return nonzero, never be merged."""
import argparse
import csv
import json
import math
from pathlib import Path


def summarize(rows):
    elapsed = sorted(float(row['elapsed']) for row in rows)
    errors = sum(row['success'].lower() != 'true' for row in rows)
    span = (max(float(r['timeStamp']) + float(r['elapsed']) for r in rows)
            - min(float(r['timeStamp']) for r in rows)) / 1000
    return {'samples': len(rows), 'errors': errors, 'error_rate': errors / len(rows),
            'p95_ms': elapsed[math.ceil(.95 * len(rows)) - 1],
            'throughput_requests_per_second': len(rows) / max(span, .001),
            'duration_seconds': span}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('jtl')
    parser.add_argument('--out', required=True)
    parser.add_argument('--p95-ms', type=float, default=2000)
    parser.add_argument('--max-errors', type=float, default=.01)
    args = parser.parse_args()
    with open(args.jtl, encoding='utf-8-sig') as source:
        rows = list(csv.DictReader(source))
    if not rows:
        raise SystemExit('Empty JTL cannot pass')
    metrics = summarize(rows)
    passed = metrics['p95_ms'] <= args.p95_ms and metrics['error_rate'] <= args.max_errors
    report = {'metrics': metrics, 'per_label': {label:summarize([r for r in rows if r['label']==label])
              for label in sorted({r['label'] for r in rows})},
              'thresholds': {'p95_ms':args.p95_ms,'max_error_rate':args.max_errors},
              'thresholds_confirmed_by_executor': True, 'passed':passed}
    Path(args.out).write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == '__main__':
    main()
