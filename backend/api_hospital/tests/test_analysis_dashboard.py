"""Chart totals, calendar denominators and snapshot integration use isolated data."""
from datetime import datetime, timezone, timedelta
from services.analysis_dashboard import build_dashboard, distribution
from services import spark_service


def by_key(dashboard, key):
    return next(chart for chart in dashboard['charts'] if chart['key'] == key)


def test_general_uses_real_collections_without_patient_identifiers(isolated_database):
    result = {'summary': {'total': 8}, 'metrics': [{'status': 'ABIERTA', 'count': 4}, {'status': 'CERRADA', 'count': 4}]}
    dashboard = build_dashboard('analytics', [], result)
    kpis = {row['key']: row['value'] for row in dashboard['kpis']}
    assert kpis == {'patients': 8, 'attentions': 8, 'active': 4, 'occupancy': 0}
    assert by_key(dashboard, 'activeArea')['rows'] == [{'label': 'PRUEBA', 'value': 4}]
    assert by_key(dashboard, 'examStatus')['rows'] == [{'label': 'PENDIENTE', 'value': 1}]
    assert 'Id_exp' not in str(dashboard) and 'SINTETICO' not in str(dashboard)
    isolated_database.camas.delete_many({})
    assert build_dashboard('analytics', [], result)['kpis'][-1]['value'] is None


def test_distribution_preserves_missing_and_other_totals(isolated_database):
    isolated_database.camas.delete_many({})
    isolated_database.camas.insert_many([{'area': str(i)} for i in range(20)] + [{}, {'area': ''}])
    rows = distribution('camas', 'area')
    assert len(rows) <= 12
    assert sum(row['value'] for row in rows) == 22
    assert rows[-1]['label'] == 'OTHER'
    assert len(set(row['label'] for row in rows)) == len(rows)


def test_daily_includes_zero_days_and_excludes_missing_dates():
    dashboard = build_dashboard('met', [{'day': '2026-10-01'}, {'day': '2026-10-03'}, {'day': None}], {})
    assert by_key(dashboard, 'daily')['rows'] == [
        {'label': '2026-10-01', 'value': 1}, {'label': '2026-10-02', 'value': 0}, {'label': '2026-10-03', 'value': 1}]
    values = {row['key']: row['value'] for row in dashboard['kpis']}
    assert values['calendarAverage'] == 2 / 3
    assert values['undated'] == 1
    assert sum(row['value'] for row in by_key(dashboard, 'weekday')['rows']) == 2


def test_monthly_aggregation_does_not_truncate_or_omit_empty_months():
    dashboard = build_dashboard('met', [{'day': '2026-01-01'}, {'day': '2026-05-01'}], {})
    rows = by_key(dashboard, 'monthly')['rows']
    assert len(rows) == 5
    assert [row['value'] for row in rows] == [1, 0, 0, 0, 1]


def test_patterns_preserve_group_totals_units_and_variance():
    result = {'clusters': [{'cluster': 0, 'count': 4, 'means': {'fc': 80, 'temp': 37}},
                           {'cluster': 1, 'count': 6, 'means': {'fc': 90, 'temp': 38}}],
              'summary': {'total': 10, 'groups': 2}, 'pca': {'explained_variance': [.7, .2]},
              'quality': {'excluded_rows': 3}}
    dashboard = build_dashboard('unsupervised', [], result)
    assert sum(row['value'] for row in by_key(dashboard, 'groups')['rows']) == 10
    assert by_key(dashboard, 'variance')['rows'][0]['value'] == 70
    assert by_key(dashboard, 'profile_temp')['unit'] == 'temp'
    assert by_key(dashboard, 'profile_fc')['rows'][1]['value'] == 90


def test_worker_persists_dashboard_with_result_and_keeps_privacy(monkeypatch):
    monkeypatch.setattr(spark_service.EXECUTOR, 'submit', lambda *_: None)
    monkeypatch.setattr(spark_service, 'run_engine', lambda *_: {
        **spark_service.empty_result(), 'available': True, 'summary': {'total': 8},
        'metrics': [{'status': 'ABIERTA', 'count': 4}, {'status': 'CERRADA', 'count': 4}]})
    state, _ = spark_service.start('analytics')
    spark_service.execute('analytics', state['job_id'])
    saved = spark_service.results('analytics')
    assert saved['dashboard']['version'] == 1
    assert saved['metadata']['generated_at'] == saved['timestamp']
    from tests.test_spark_contract import validate
    validate('spark_result', saved)


def test_calendar_dates_and_metadata_use_same_utc_bucket(isolated_database):
    isolated_database.atencion.delete_many({})
    isolated_database.atencion.insert_one({'fecha_ing': datetime(2026, 10, 1, 23, tzinfo=timezone(timedelta(hours=-6))), 'status': 'ABIERTA'})
    rows, metadata = spark_service.collect_source('met', with_metadata=True)
    assert rows[0]['day'] == metadata['period']['start'] == '2026-10-02'
