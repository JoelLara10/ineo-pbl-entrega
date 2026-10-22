"""Persistent Spark jobs; no patient identifiers leave the source projection."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from uuid import uuid4

from pymongo import ReturnDocument
from utils.database import get_collection
from services.analysis_resources import choose_engine, memory_pressure
from services.analysis_filters import normalize_filters, previous_filters, parse_time

TYPES = ('analytics', 'met', 'clinical', 'unsupervised')
VERSION = '1.0'
EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix='ineo-spark')
TIMEOUT = int(os.getenv('SPARK_TIMEOUT_SECONDS', '180'))
JOB_TTL = int(os.getenv('SPARK_JOB_TTL_SECONDS', str(TIMEOUT + 60)))
MAX_ROWS = 20000


class SparkRuntimeError(RuntimeError):
    """Safe, actionable runtime failure that may be returned to the UI."""


def runtime_error():
    if importlib.util.find_spec('pyspark') is None:
        return 'PySpark no está instalado en la API. Instala requirements-spark.txt y reinicia el servicio.'
    if not shutil.which('java'):
        return 'Java no está disponible en la API. Instala Java 17 y configura JAVA_HOME.'
    return None


def now():
    return datetime.now(timezone.utc)


def stamp(value):
    if value is None:
        return None
    # PyMongo defaults to naive UTC; aware values must preserve their instant.
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


def empty_result():
    return {'contract_version': VERSION, 'available': False, 'timestamp': None,
            'metadata': empty_metadata(),
            'visualizations': [], 'summary': {}, 'metrics': [], 'clusters': [],
            'pca': {}, 'quality': {}}


def empty_metadata():
    return {'generated_at': None, 'last_updated_at': None,
            'period': {'start': None, 'end': None}, 'undated_rows': 0,
            'timezone': 'UTC'}


def status_of(doc):
    doc = doc or {}
    state = doc.get('state', 'idle')
    return {'contract_version': VERSION, 'state': state,
            'running': state in ('pending', 'running'), 'job_id': doc.get('job_id'),
            'started_at': stamp(doc.get('started_at')),
            'finished_at': stamp(doc.get('finished_at')),
            'error': doc.get('error'), 'filters': doc.get('filters', {})}


def read_job(kind):
    collection = get_collection('spark_jobs')
    collection.update_one(
        {'_id': kind, 'state': {'$in': ['pending', 'running']}, 'expires_at': {'$lte': now()}},
        {'$set': {'state': 'failed', 'finished_at': now(),
                  'error': 'La ejecución fue interrumpida. Vuelve a ejecutarla.'}})
    return collection.find_one({'_id': kind})


def results(kind):
    doc = read_job(kind)
    result = dict((doc or {}).get('result') or empty_result())
    # Historical snapshots have no source-period evidence; expose that absence.
    result.setdefault('metadata', {**empty_metadata(), 'generated_at': result.get('timestamp')})
    return result


def collect_source(kind, with_metadata=False, filters=None):
    """Bounded projection; fail instead of silently truncating a dataset."""
    clinical = kind in ('clinical', 'unsupervised')
    filters = filters or {}
    fields = ('fc', 'fr', 'temp', 'spo2') if clinical else ('status', 'fecha_ing', 'area')
    query = {}
    if filters.get('area'):
        if clinical:
            attention_ids = [doc.get('id_atencion') for doc in get_collection('atencion').find(
                {'area': filters['area']}, {'_id': 0, 'id_atencion': 1}).limit(MAX_ROWS + 1)]
            if len(attention_ids) > MAX_ROWS:
                raise SparkRuntimeError('El área supera el límite de 20,000 atenciones para este análisis.')
            query['id_atencion'] = {'$in': [value for value in attention_ids if value is not None]}
        else:
            query['area'] = filters['area']
    date_field = 'fecha_registro' if clinical else 'fecha_ing'
    docs = list(get_collection('signos_vitales' if clinical else 'atencion').find(
        query, {'_id': 0, **{field: 1 for field in (*fields, date_field)}}).limit(MAX_ROWS + 1))
    if len(docs) > MAX_ROWS:
        raise ValueError('dataset_limit')
    excluded_undated = 0
    if filters.get('start_date'):
        selected = []
        for doc in docs:
            recorded = parse_time(doc.get(date_field))
            if recorded is None:
                excluded_undated += 1
            elif filters['start_date'] <= recorded.date().isoformat() <= filters['end_date']:
                selected.append(doc)
        docs = selected
    rows = []
    for doc in docs:
        if clinical:
            row = {}
            for field in fields:
                try:
                    value = float(doc.get(field))
                    row[field] = value if math.isfinite(value) and not isinstance(doc.get(field), bool) else None
                except (TypeError, ValueError):
                    row[field] = None
            # Calendar bucket only: never send patient identifiers to Spark.
            if kind == 'clinical':
                date = doc.get(date_field)
                if isinstance(date, str):
                    try:
                        date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                    except ValueError:
                        date = None
                if isinstance(date, datetime):
                    row['day'] = stamp(date)[:10]
        else:
            date = doc.get('fecha_ing')
            if isinstance(date, str):
                try:
                    date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                except ValueError:
                    date = None
            row = {'day': stamp(date)[:10] if isinstance(date, datetime) else None,
                   'status': doc.get('status') if doc.get('status') in ('ABIERTA', 'CERRADA') else 'OTRO'}
        if not clinical and doc.get('area') is not None:
            row['area'] = str(doc['area'])
        rows.append(row)
    if not with_metadata:
        return rows
    dates = []
    for doc in docs:
        value = doc.get(date_field)
        if isinstance(value, str):
            try:
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:
                value = None
        if isinstance(value, datetime):
            dates.append(stamp(value))
    metadata = empty_metadata()
    metadata.update(last_updated_at=max(dates) if dates else None,
                    period={'start': min(dates)[:10] if dates else None,
                            'end': max(dates)[:10] if dates else None},
                    undated_rows=len(docs) - len(dates))
    metadata['filters'] = filters
    metadata['excluded_undated_rows'] = excluded_undated
    if filters.get('start_date'):
        metadata['period'] = {'start': filters['start_date'], 'end': filters['end_date']}
    return rows, metadata


def stop_engine(process):
    """Kill the whole analysis group, including any JVM children."""
    try:
        if os.name != 'nt':
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
    except ProcessLookupError:
        pass
    process.communicate()


def run_engine(kind, rows):
    """Choose a safe engine, isolate it and monitor time/memory headroom."""
    try:
        engine = choose_engine()
    except ValueError as error:
        raise SparkRuntimeError(str(error)) from error
    if engine == 'spark':
        unavailable = runtime_error()
        if unavailable:
            raise SparkRuntimeError(unavailable)
    with tempfile.TemporaryDirectory(prefix='ineo-analysis-') as directory:
        source = Path(directory) / 'input.json'
        target = Path(directory) / 'output.json'
        source.write_text(json.dumps({'type': kind, 'rows': rows, 'engine': engine}), encoding='utf-8')
        env = os.environ.copy()
        # Bound native thread pools before importing NumPy in the child process.
        env.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
        if engine == 'spark':
            # Driver memory must be set before the gateway JVM is launched.
            env['PYSPARK_SUBMIT_ARGS'] = '--driver-memory 512m --conf spark.executor.memory=512m --conf spark.driver.maxResultSize=32m pyspark-shell'
        process = subprocess.Popen(
            [sys.executable, str(Path(__file__).with_name('spark_engine.py')), str(source), str(target)],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, env=env,
            start_new_session=os.name != 'nt')
        deadline = time.monotonic() + TIMEOUT
        try:
            while True:
                if memory_pressure():
                    raise SparkRuntimeError('El análisis se detuvo para proteger la memoria de la API. Se conserva el último resultado; vuelve a intentarlo cuando haya recursos disponibles.')
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise SparkRuntimeError(f'El análisis excedió el límite de {TIMEOUT} segundos. Inténtalo con menos datos.')
                try:
                    _, stderr = process.communicate(timeout=min(0.25, remaining))
                    break
                except subprocess.TimeoutExpired:
                    continue
        except BaseException:
            stop_engine(process)
            raise
        if process.returncode != 0 or not target.exists():
            # A Python driver can exit before its JVM; never leave it behind.
            stop_engine(process)
            lowered = (stderr or '').lower()
            if 'java_home' in lowered or 'java gateway' in lowered or 'java: not found' in lowered:
                raise SparkRuntimeError('Java 17 no está configurado correctamente para ejecutar Spark.')
            if 'no module named' in lowered and 'pyspark' in lowered:
                raise SparkRuntimeError('PySpark no está instalado en la API.')
            if process.returncode in (-9, 137) or 'outofmemory' in lowered or 'cannot allocate memory' in lowered:
                raise SparkRuntimeError('El servidor no tiene memoria suficiente para ejecutar el análisis.')
            raise SparkRuntimeError('El motor de análisis terminó inesperadamente. Revisa los logs del servicio.')
        return json.loads(target.read_text(encoding='utf-8'))


def execute(kind, job_id):
    collection = get_collection('spark_jobs')
    claimed = collection.update_one(
        {'_id': kind, 'job_id': job_id, 'state': 'pending', 'expires_at': {'$gt': now()}},
        {'$set': {'state': 'running', 'started_at': now()}})
    if not claimed.modified_count:
        return
    try:
        job = collection.find_one({'_id': kind, 'job_id': job_id}) or {}
        filters = job.get('filters') or {}
        rows, metadata = collect_source(kind, with_metadata=True, filters=filters)
        result = run_engine(kind, rows)
        if kind in ('analytics', 'met') and filters.get('start_date'):
            # A fully queried date interval with zero dated encounters is still a valid count.
            result['available'] = True
            result.setdefault('summary', {}).setdefault('total', 0)
        from services.analysis_dashboard import build_dashboard
        result['dashboard'] = build_dashboard(kind, rows, result, filters=filters)
        if filters.get('compare_previous'):
            previous = previous_filters(filters)
            prior_rows = collect_source(kind, filters=previous)
            prior_count = len(prior_rows) if kind == 'analytics' else sum(bool(row.get('day')) for row in prior_rows)
            current_count = result.get('summary', {}).get('total', 0)
            result['comparison'] = {
                'current': current_count, 'previous': prior_count, 'change': current_count - prior_count,
                'change_percent': (current_count - prior_count) / prior_count * 100 if prior_count else None,
                'previous_period': {'start': previous['start_date'], 'end': previous['end_date']},
                'current_period': metadata['period'], 'area': filters.get('area'),
            }
        generated_at = stamp(now())
        metadata['generated_at'] = generated_at
        result.update(contract_version=VERSION, timestamp=generated_at,
                      metadata=metadata, visualizations=[])
        update = {'state': 'completed', 'result': result, 'error': None}
    except SparkRuntimeError as error:
        update = {'state': 'failed', 'error': str(error)}
    except Exception:
        # Do not publish source rows, paths, credentials or raw JVM logs.
        update = {'state': 'failed', 'error': 'No se pudo completar el análisis. Revisa el motor Spark y la fuente de datos.'}
    update['finished_at'] = now()
    collection.update_one({'_id': kind, 'job_id': job_id, 'state': 'running'}, {'$set': update})


def start(kind, filters=None):
    filters = normalize_filters(filters, kind)
    collection = get_collection('spark_jobs')
    collection.update_one({'_id': kind}, {'$setOnInsert': {'state': 'idle'}}, upsert=True)
    read_job(kind)
    job_id = str(uuid4())
    doc = collection.find_one_and_update(
        {'_id': kind, 'state': {'$nin': ['pending', 'running']}},
        {'$set': {'job_id': job_id, 'state': 'pending', 'error': None,
                  'started_at': None, 'finished_at': None, 'filters': filters,
                  'expires_at': now() + timedelta(seconds=JOB_TTL)}},
        return_document=ReturnDocument.AFTER)
    if doc is None:
        current = read_job(kind)
        if (current or {}).get('filters', {}) != filters:
            raise SparkRuntimeError('Ya hay un análisis en curso con otros filtros. Espera a que termine y vuelve a ejecutar.')
        return status_of(current), False
    try:
        EXECUTOR.submit(execute, kind, job_id)
    except RuntimeError:
        collection.update_one({'_id': kind, 'job_id': job_id, 'state': 'pending'},
                              {'$set': {'state': 'failed', 'finished_at': now(),
                                        'error': 'Ejecutor no disponible.'}})
        raise
    return status_of(doc), True
