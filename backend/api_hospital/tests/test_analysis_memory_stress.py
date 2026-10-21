"""Exercise maximum source size within a hard 256 MiB process address limit."""
import json
import os
from pathlib import Path
import subprocess
import sys
import pytest


@pytest.mark.skipif(sys.platform != 'linux', reason='Uses the Linux address-space limit')
@pytest.mark.parametrize('kind', ['clinical', 'unsupervised'])
def test_maximum_source_under_small_process_budget(tmp_path, kind):
    import resource
    source, target = tmp_path / 'source.json', tmp_path / 'result.json'
    rows = [{'fc': float(60 + i % 60), 'fr': float(12 + i % 12), 'temp': 36. + i % 30 / 10,
             'spo2': float(90 + i % 10), 'day': '2026-10-01'} for i in range(20000)]
    source.write_text(json.dumps({'type': kind, 'engine': 'lightweight', 'rows': rows}))
    runner = "import resource,runpy,sys; resource.setrlimit(resource.RLIMIT_AS,(256*1024*1024,256*1024*1024)); sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name='__main__')"
    env = {**os.environ, 'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1'}
    engine = Path(__file__).parents[1] / 'services' / 'spark_engine.py'
    # runpy does not add the script directory to sys.path like direct execution does.
    env['PYTHONPATH'] = str(engine.parent)
    completed = subprocess.run([sys.executable, '-c', runner, str(engine), str(source), str(target)],
                               env=env, capture_output=True, text=True, timeout=60)
    assert completed.returncode == 0, completed.stderr
    result = json.loads(target.read_text())
    assert result['engine']['name'] == 'lightweight'
    assert result['available']
    assert result['summary']['total'] == 20000
