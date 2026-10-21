"""Run with RUN_SPARK_TESTS=1; these tests execute a real Java/PySpark JVM."""
import os
import pytest
from services import spark_service as service
from services.spark_engine import analyze

pytestmark = pytest.mark.skipif(os.getenv('RUN_SPARK_TESTS') != '1', reason='Enable real Spark with RUN_SPARK_TESTS=1')


@pytest.fixture(scope='module')
def spark():
    from pyspark.sql import SparkSession
    session = (SparkSession.builder.master('local[1]').appName('INEO-contract-tests')
               .config('spark.ui.enabled', 'false').config('spark.sql.shuffle.partitions', '2')
               .config('spark.driver.host', '127.0.0.1').getOrCreate())
    yield session
    session.stop()


@pytest.mark.parametrize('kind', service.TYPES)
def test_real_spark_outputs(spark, kind):
    result = analyze(spark, kind, service.collect_source(kind))
    from tests.test_spark_contract import validate
    # The worker adds these envelope fields before exposing the engine result.
    validate('spark_result', {**result, 'contract_version': service.VERSION,
                             'timestamp': service.stamp(service.now()), 'visualizations': []})
    assert result['available']
    assert result['summary']['total'] == 8
    if kind == 'analytics':
        assert result['metrics'] == [{'status': 'ABIERTA', 'count': 4}, {'status': 'CERRADA', 'count': 4}]
    elif kind == 'clinical':
        assert result['metrics'][0]['mean'] == 82.5
    elif kind == 'met':
        assert len(result['metrics']) == 8
    else:
        assert sum(row['count'] for row in result['clusters']) == 8
        assert sum(result['pca']['explained_variance']) == pytest.approx(1.0)


def test_real_spark_empty_partial_constant(spark):
    for kind in service.TYPES:
        assert not analyze(spark, kind, [])['available']
    rows = [{'fc': None, 'fr': None, 'temp': None, 'spo2': None}]
    assert not analyze(spark, 'clinical', rows)['available']
    rows = [{'fc': 80., 'fr': 18., 'temp': 36., 'spo2': 98.}] * 4
    assert not analyze(spark, 'unsupervised', rows)['available']


def test_real_subprocess():
    result = service.run_engine('analytics', service.collect_source('analytics'))
    assert result['summary']['total'] == 8


def test_http_to_background_worker_to_real_spark(client):
    import time
    from middleware.auth_middleware import generate_token
    auth = {'Authorization': 'Bearer ' + generate_token('000000000000000000000001', 'admin.test', 'admin')}
    response = client.post('/api/v1/spark/run/clinical', headers=auth)
    assert response.status_code == 202
    deadline = time.monotonic() + service.TIMEOUT + 10
    while time.monotonic() < deadline:
        state = client.get('/api/v1/spark/status/clinical', headers=auth).json
        if not state['running']:
            break
        time.sleep(0.2)
    assert state['state'] == 'completed', state
    result = client.get('/api/v1/spark/clinical', headers=auth).json
    from tests.test_spark_contract import validate
    validate('spark_result', result)
    assert result['available']
    assert result['summary']['total'] == 8
    assert result['metrics'][0]['mean'] == 82.5


def test_pbl09_clinical_dated_trends_use_real_daily_aggregates(spark):
    rows = [
        {'fc': 80., 'fr': None, 'temp': 37., 'spo2': None, 'day': '2026-10-12'},
        {'fc': 100., 'fr': None, 'temp': 39., 'spo2': None, 'day': '2026-10-12'},
        {'fc': 60., 'fr': None, 'temp': 36., 'spo2': None, 'day': '2026-10-15'},
        {'fc': 120., 'fr': None, 'temp': 40., 'spo2': None},
    ]
    result = analyze(spark, 'clinical', rows)
    assert [row for row in result['trends'] if row['measure'] == 'temp'] == [
        {'day': '2026-10-12', 'measure': 'temp', 'count': 2, 'mean': 38., 'minimum': 37., 'maximum': 39.},
        {'day': '2026-10-15', 'measure': 'temp', 'count': 1, 'mean': 36., 'minimum': 36., 'maximum': 36.},
    ]
    assert result['summary']['total'] == 4
    assert result['metrics'][2]['count'] == 4
    assert not any(row['measure'] == 'spo2' for row in result['trends'])


def test_dated_rows_without_any_vital_sign_are_excluded(spark):
    result = analyze(spark, 'clinical', [{'day': '2026-10-01', 'fc': None, 'fr': None, 'temp': None, 'spo2': None}])
    assert result['available'] is False
    assert result['quality']['used_rows'] == 0
    assert result['quality']['excluded_rows'] == 1
