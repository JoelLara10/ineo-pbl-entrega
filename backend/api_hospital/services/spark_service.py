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
from uuid import uuid4

from pymongo import ReturnDocument
from utils.database import get_collection

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
    return value.replace(tzinfo=timezone.utc).isoformat() if value else None


def empty_result():
    return {'contract_version': VERSION, 'available': False, 'timestamp': None,
            'visualizations': [], 'summary': {}, 'metrics': [], 'clusters': [],
            'pca': {}, 'quality': {}}


def status_of(doc):
    doc = doc or {}
    state = doc.get('state', 'idle')
    return {'contract_version': VERSION, 'state': state,
            'running': state in ('pending', 'running'), 'job_id': doc.get('job_id'),
            'started_at': stamp(doc.get('started_at')),
            'finished_at': stamp(doc.get('finished_at')),
            'error': doc.get('error')}


def read_job(kind):
    collection = get_collection('spark_jobs')
    collection.update_one(
        {'_id': kind, 'state': {'$in': ['pending', 'running']}, 'expires_at': {'$lte': now()}},
        {'$set': {'state': 'failed', 'finished_at': now(),
                  'error': 'La ejecución fue interrumpida. Vuelve a ejecutarla.'}})
    return collection.find_one({'_id': kind})


def results(kind):
    doc = read_job(kind)
    return (doc or {}).get('result') or empty_result()


def collect_source(kind):
    """Bounded projection; fail instead of silently truncating a dataset."""
    clinical = kind in ('clinical', 'unsupervised')
    fields = ('fc', 'fr', 'temp', 'spo2') if clinical else ('status', 'fecha_ing')
    docs = list(get_collection('signos_vitales' if clinical else 'atencion').find(
        {}, {'_id': 0, **{field: 1 for field in fields}}).limit(MAX_ROWS + 1))
    if len(docs) > MAX_ROWS:
        raise ValueError('dataset_limit')
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
        else:
            date = doc.get('fecha_ing')
            if isinstance(date, str):
                try:
                    date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                except ValueError:
                    date = None
            row = {'day': date.date().isoformat() if isinstance(date, datetime) else None,
                   'status': doc.get('status') if doc.get('status') in ('ABIERTA', 'CERRADA') else 'OTRO'}
        rows.append(row)
    return rows


def run_engine(kind, rows):
    """Isolate the JVM and kill its process group on timeout (Linux deployment)."""
    unavailable = runtime_error()
    if unavailable:
        raise SparkRuntimeError(unavailable)
    with tempfile.TemporaryDirectory(prefix='ineo-spark-') as directory:
        source = Path(directory) / 'input.json'
        target = Path(directory) / 'output.json'
        source.write_text(json.dumps({'type': kind, 'rows': rows}), encoding='utf-8')
        process = subprocess.Popen(
            [sys.executable, str(Path(__file__).with_name('spark_engine.py')), str(source), str(target)],
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
            start_new_session=os.name != 'nt')
        try:
            _, stderr = process.communicate(timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            if os.name != 'nt':
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            process.communicate()
            raise SparkRuntimeError(
                f'El análisis excedió el límite de {TIMEOUT} segundos. Inténtalo con menos datos.'
            )
        if process.returncode != 0 or not target.exists():
            lowered = (stderr or '').lower()
            if 'java_home' in lowered or 'java gateway' in lowered or 'java: not found' in lowered:
                raise SparkRuntimeError('Java 17 no está configurado correctamente para ejecutar Spark.')
            if 'no module named' in lowered and 'pyspark' in lowered:
                raise SparkRuntimeError('PySpark no está instalado en la API.')
            if process.returncode in (-9, 137) or 'outofmemory' in lowered or 'cannot allocate memory' in lowered:
                raise SparkRuntimeError('El servidor no tiene memoria suficiente para ejecutar Spark.')
            raise SparkRuntimeError('El motor Spark terminó inesperadamente. Revisa los logs del servicio.')
        return json.loads(target.read_text(encoding='utf-8'))


def execute(kind, job_id):
    collection = get_collection('spark_jobs')
    claimed = collection.update_one(
        {'_id': kind, 'job_id': job_id, 'state': 'pending', 'expires_at': {'$gt': now()}},
        {'$set': {'state': 'running', 'started_at': now()}})
    if not claimed.modified_count:
        return
    try:
        result = run_engine(kind, collect_source(kind))
        result.update(contract_version=VERSION, timestamp=stamp(now()), visualizations=[])
        update = {'state': 'completed', 'result': result, 'error': None}
    except SparkRuntimeError as error:
        update = {'state': 'failed', 'error': str(error)}
    except Exception:
        # Do not publish source rows, paths, credentials or raw JVM logs.
        update = {'state': 'failed', 'error': 'No se pudo completar el análisis. Revisa el motor Spark y la fuente de datos.'}
    update['finished_at'] = now()
    collection.update_one({'_id': kind, 'job_id': job_id, 'state': 'running'}, {'$set': update})


def start(kind):
    collection = get_collection('spark_jobs')
    collection.update_one({'_id': kind}, {'$setOnInsert': {'state': 'idle'}}, upsert=True)
    read_job(kind)
    job_id = str(uuid4())
    doc = collection.find_one_and_update(
        {'_id': kind, 'state': {'$nin': ['pending', 'running']}},
        {'$set': {'job_id': job_id, 'state': 'pending', 'error': None,
                  'started_at': None, 'finished_at': None,
                  'expires_at': now() + timedelta(seconds=JOB_TTL)}},
        return_document=ReturnDocument.AFTER)
    if doc is None:
        return status_of(read_job(kind)), False
    try:
        EXECUTOR.submit(execute, kind, job_id)
    except RuntimeError:
        collection.update_one({'_id': kind, 'job_id': job_id},
                              {'$set': {'state': 'failed', 'error': 'Ejecutor no disponible.'}})
        raise
    return status_of(doc), True
