"""Low-memory execution must retain real results without launching Java."""
import json
from unittest.mock import Mock
import pytest
from services import analysis_resources as resources, spark_service as service
from services.analysis_lightweight import analyze, silhouette


def test_small_container_uses_lightweight_even_when_host_has_ram(monkeypatch):
    monkeypatch.setattr(resources, 'memory_snapshot', lambda: (512 * resources.MIB, 240 * resources.MIB))
    monkeypatch.delenv('ANALYSIS_ENGINE', raising=False)
    assert resources.choose_engine() == 'lightweight'
    monkeypatch.setenv('ANALYSIS_ENGINE', 'spark')
    with pytest.raises(ValueError, match='memoria suficiente'):
        resources.choose_engine()


def test_memory_limit_v2_is_respected(monkeypatch):
    def read(path):
        return {'/sys/fs/cgroup/memory.max': '536870912', '/sys/fs/cgroup/memory.current': '209715200'}[str(path)]
    monkeypatch.setattr(resources.Path, 'read_text', read)
    assert resources.memory_snapshot() == (512 * resources.MIB, 312 * resources.MIB)


def test_unknown_render_limit_fails_closed_for_spark(monkeypatch):
    monkeypatch.setattr(resources.Path, 'read_text', Mock(side_effect=OSError))
    monkeypatch.setenv('RENDER', 'true')
    monkeypatch.delenv('ANALYSIS_ENGINE', raising=False)
    assert resources.choose_engine() == 'lightweight'


def test_high_pressure_refuses_even_lightweight(monkeypatch):
    monkeypatch.setenv('ANALYSIS_ENGINE', 'lightweight')
    monkeypatch.setattr(resources, 'memory_snapshot', lambda: (512 * resources.MIB, 40 * resources.MIB))
    with pytest.raises(ValueError, match='poca memoria'):
        resources.choose_engine()
    assert resources.memory_pressure()


def test_clinical_counts_partial_and_undated_values_correctly():
    rows = [{'fc': 80., 'fr': None, 'temp': 37., 'spo2': None, 'day': '2026-10-01'},
            {'fc': 100., 'fr': None, 'temp': 39., 'spo2': None, 'day': '2026-10-01'},
            {'fc': 120., 'fr': None, 'temp': None, 'spo2': None},
            {'fc': None, 'fr': None, 'temp': None, 'spo2': None, 'day': '2026-10-02'}]
    result = analyze('clinical', rows)
    assert result['summary']['total'] == 3
    assert result['metrics'][0] == {'measure': 'fc', 'count': 3, 'mean': 100., 'minimum': 80., 'maximum': 120.}
    assert result['metrics'][1]['mean'] is None
    assert result['trends'][0] == {'day': '2026-10-01', 'measure': 'fc', 'count': 2, 'mean': 90., 'minimum': 80., 'maximum': 100.}
    assert result['quality'] == {'source_rows': 4, 'used_rows': 3, 'excluded_rows': 1}


@pytest.mark.parametrize('kind', service.TYPES)
def test_low_memory_subprocess_completes_without_spark(kind, monkeypatch):
    monkeypatch.setenv('ANALYSIS_ENGINE', 'lightweight')
    monkeypatch.setattr(service, 'runtime_error', Mock(side_effect=AssertionError('Must not launch Spark')))
    result = service.run_engine(kind, service.collect_source(kind))
    assert result['available']
    assert result['engine']['name'] == 'lightweight'
    assert result['summary']['total'] == 8
    from tests.test_spark_contract import validate
    validate('spark_result', {**result, 'contract_version': service.VERSION, 'timestamp': None, 'visualizations': []})
    if kind == 'unsupervised':
        assert sum(group['count'] for group in result['clusters']) == 8
        assert sum(result['pca']['explained_variance']) == pytest.approx(1)


def test_lightweight_patterns_repeatable_and_incomplete_excluded():
    rows = [{'fc': float(60 + i * 5), 'fr': float(12 + i), 'temp': 36. + i / 10, 'spo2': float(100 - i)} for i in range(8)]
    rows += [{'fc': None, 'fr': 18., 'temp': 37., 'spo2': 98.}]
    a, b = analyze('unsupervised', rows), analyze('unsupervised', list(reversed(rows)))
    assert a['clusters'] == b['clusters']
    assert a['quality']['excluded_rows'] == 1
    json.dumps(a, allow_nan=False)
    assert not analyze('unsupervised', [rows[0]] * 4)['available']


def test_moment_silhouette_matches_brute_force_without_pairwise_matrix():
    import numpy as np
    values = np.array([[0., 0.], [0., 1.], [5., 4.], [6., 5.], [20., 30.]])
    labels = np.array([0, 0, 1, 1, 2])
    expected = []
    for i, value in enumerate(values):
        own = [float(((value - other) ** 2).sum()) for j, other in enumerate(values) if labels[j] == labels[i] and i != j]
        if not own:
            expected.append(0.)
            continue
        a = sum(own) / len(own)
        b = min(np.mean([float(((value - other) ** 2).sum()) for j, other in enumerate(values) if labels[j] == group]) for group in set(labels) if group != labels[i])
        expected.append((b - a) / max(a, b))
    assert silhouette(values, labels, 3) == pytest.approx(sum(expected) / len(expected))


def test_pressure_kills_child(monkeypatch):
    monkeypatch.setattr(service, 'choose_engine', lambda: 'lightweight')
    monkeypatch.setattr(service, 'memory_pressure', lambda: True)
    process = Mock(pid=321, returncode=None)
    monkeypatch.setattr(service.subprocess, 'Popen', Mock(return_value=process))
    kill = Mock()
    monkeypatch.setattr(service.os, 'killpg', kill)
    with pytest.raises(service.SparkRuntimeError, match='proteger la memoria'):
        service.run_engine('clinical', [])
    kill.assert_called_once_with(321, service.signal.SIGKILL)
    process.communicate.assert_called_once()


def test_failed_guard_retains_last_saved_analysis(monkeypatch):
    monkeypatch.setattr(service.EXECUTOR, 'submit', lambda *_: None)
    previous = {**service.empty_result(), 'available': True, 'summary': {'total': 8}}
    monkeypatch.setattr(service, 'run_engine', lambda *_: previous.copy())
    first, _ = service.start('clinical')
    service.execute('clinical', first['job_id'])
    monkeypatch.setattr(service, 'run_engine', Mock(side_effect=service.SparkRuntimeError('Memoria insuficiente')))
    second, _ = service.start('clinical')
    service.execute('clinical', second['job_id'])
    assert service.read_job('clinical')['state'] == 'failed'
    assert service.results('clinical')['summary']['total'] == 8


def test_deadline_stops_the_whole_analysis_process(monkeypatch):
    monkeypatch.setattr(service, 'choose_engine', lambda: 'lightweight')
    monkeypatch.setattr(service, 'memory_pressure', lambda: False)
    clock = iter([0, 1, service.TIMEOUT + 1])
    monkeypatch.setattr(service.time, 'monotonic', lambda: next(clock))
    process = Mock(pid=456, returncode=None)
    process.communicate.side_effect = [service.subprocess.TimeoutExpired('analysis', .25), ('', '')]
    monkeypatch.setattr(service.subprocess, 'Popen', Mock(return_value=process))
    kill = Mock()
    monkeypatch.setattr(service.os, 'killpg', kill)
    with pytest.raises(service.SparkRuntimeError, match='excedió el límite'):
        service.run_engine('clinical', [])
    kill.assert_called_once_with(456, service.signal.SIGKILL)
