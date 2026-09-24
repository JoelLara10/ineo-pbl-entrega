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
