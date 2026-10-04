"""Persistent Spark jobs; no patient identifiers leave the source projection.

Resolución de merge:
- Se conserva la interfaz de clase `SparkService` (usada por routes/spark.py).
- Se adopta el motor PySpark vía subprocess (`spark_engine.py`) de origin/main.
- Se añade expiración de jobs y manejo seguro de errores (no filtra rutas,
  credenciales ni logs crudos de la JVM).
"""
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



class SparkNotImplemented(ValueError):
    """Tipo válido pero fuera del alcance de PBL-03."""


class SparkService:
    VERSION = '1.0'
    ALLOWED_TYPES = ('analytics', 'met', 'clinical', 'unsupervised')
    IMPLEMENTED_TYPES = ('clinical', 'met')
    COLLECTION = 'spark_jobs'
    JOB_TIMEOUT_SECONDS = 180
    MAX_ROWS = 20000

    _executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='ineo-spark')

    # --- API pública -------------------------------------------------------

    @classmethod
    def get_overview(cls):
        overview = {}
        for analysis_type in cls.ALLOWED_TYPES:
            job = cls._read_job(analysis_type)
            status = cls._status_payload(analysis_type, job)
            result = (job or {}).get('result') or cls._empty_result(analysis_type)
            overview[analysis_type] = {
                'contract_version': cls.VERSION,
                'available': bool(result.get('available')),
                'state': status['state'],
            }
        return overview

    @classmethod
    def get_status(cls, analysis_type):
        cls._assert_allowed(analysis_type)
        return cls._status_payload(analysis_type, cls._read_job(analysis_type))

    @classmethod
    def get_result(cls, analysis_type):
        cls._assert_allowed(analysis_type)
        job = cls._read_job(analysis_type)
        return (job or {}).get('result') or cls._empty_result(analysis_type)

    @classmethod
    def run(cls, analysis_type, requested_by=None, role=None):
        cls._assert_allowed(analysis_type)
        if analysis_type not in cls.IMPLEMENTED_TYPES:
            raise SparkNotImplemented('Tipo de análisis no implementado en PBL-03')

        collection = get_collection(cls.COLLECTION)
        collection.update_one(
            {'_id': analysis_type},
            {'$setOnInsert': {'state': 'idle'}},
            upsert=True,
        )
        cls._expire_stale(analysis_type)

        job_id = str(uuid4())
        doc = collection.find_one_and_update(
            {'_id': analysis_type, 'state': {'$nin': ['pending', 'running']}},
            {'$set': {
                'type': analysis_type,
                'job_id': job_id,
                'state': 'pending',
                'error': None,
                'log': None,
                'started_at': None,
                'finished_at': None,
                'requested_by': requested_by,
                'role': role,
                'expires_at': cls._now() + timedelta(
                    seconds=cls.JOB_TIMEOUT_SECONDS + 120
                ),
            }},
            return_document=ReturnDocument.AFTER,
        )
        if doc is None:
            raise SparkJobConflict('El análisis clínico ya se está procesando')


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


    @classmethod
    def _run_engine(cls, analysis_type, rows):
        """Aísla la JVM y mata el grupo de procesos al expirar (Linux)."""
        with tempfile.TemporaryDirectory(prefix='ineo-spark-') as directory:
            source = Path(directory) / 'input.json'
            target = Path(directory) / 'output.json'
            source.write_text(
                json.dumps({'type': analysis_type, 'rows': rows}),
                encoding='utf-8',
            )
            process = subprocess.Popen(
                [sys.executable,
                 str(Path(__file__).with_name('spark_engine.py')),
                 str(source), str(target)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=os.name != 'nt',
            )
            try:
                process.wait(timeout=cls.JOB_TIMEOUT_SECONDS)
            except subprocess.TimeoutExpired:
                if os.name != 'nt':
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
                process.wait()
                raise RuntimeError('spark_timeout')
            if process.returncode != 0 or not target.exists():
                raise RuntimeError('spark_execution_failed')
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


    @classmethod
    def _assert_allowed(cls, analysis_type):
        if analysis_type not in cls.ALLOWED_TYPES:
            raise SparkTypeError('Tipo de análisis no válido')


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

