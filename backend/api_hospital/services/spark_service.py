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
COLLECTION = 'spark_jobs'


class SparkRuntimeError(RuntimeError):
    """Fallo de runtime seguro y accionable para la UI."""


class SparkNotImplemented(ValueError):
    """Tipo válido pero fuera del alcance implementado."""


class SparkTypeError(ValueError):
    """Tipo de análisis ausente o no permitido."""


class SparkJobConflict(Exception):
    """El análisis solicitado ya se está procesando."""


def runtime_error():
    if importlib.util.find_spec('pyspark') is None:
        return (
            'PySpark no está instalado en la API. '
            'Instala requirements-spark.txt y reinicia el servicio.'
        )
    if not shutil.which('java'):
        return (
            'Java no está disponible en la API. '
            'Instala Java 17 y configura JAVA_HOME.'
        )
    return None


def now():
    return datetime.now(timezone.utc)


def stamp(value):
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def empty_result():
    return {
        'available': False,
        'summary': {},
        'metrics': [],
        'clusters': [],
        'pca': {},
        'quality': {'source_rows': 0, 'used_rows': 0, 'excluded_rows': 0},
        'contract_version': VERSION,
        'timestamp': None,
        'visualizations': [],
    }


def status_of(job):
    if not job:
        return {
            'contract_version': VERSION,
            'state': 'idle',
            'running': False,
            'job_id': None,
            'error': None,
            'started_at': None,
            'finished_at': None,
        }
    state = job.get('state') or 'idle'
    expires = job.get('expires_at')
    if state in ('pending', 'running') and expires is not None:
        exp = expires
        if isinstance(exp, str):
            try:
                exp = datetime.fromisoformat(exp.replace('Z', '+00:00'))
            except ValueError:
                exp = None
        if exp is not None:
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp < now():
                get_collection(COLLECTION).update_one(
                    {'_id': job.get('_id'), 'job_id': job.get('job_id')},
                    {'$set': {
                        'state': 'failed',
                        'error': 'El trabajo expiró antes de completarse.',
                        'finished_at': now(),
                    }},
                )
                state = 'failed'
    return {
        'contract_version': VERSION,
        'state': state,
        'running': state in ('pending', 'running'),
        'job_id': job.get('job_id'),
        'error': job.get('error'),
        'started_at': stamp(job.get('started_at')) if job.get('started_at') else None,
        'finished_at': stamp(job.get('finished_at')) if job.get('finished_at') else None,
        'type': job.get('type') or job.get('_id'),
    }


def read_job(kind):
    """Lee el job y marca como fallido si expiró."""
    collection = get_collection(COLLECTION)
    job = collection.find_one({'_id': kind})
    if not job:
        return None
    expires = job.get('expires_at')
    state = job.get('state')
    if state in ('pending', 'running') and expires is not None:
        exp = expires
        if isinstance(exp, str):
            try:
                exp = datetime.fromisoformat(exp.replace('Z', '+00:00'))
            except ValueError:
                exp = None
        if exp is not None:
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            if exp < now():
                collection.update_one(
                    {'_id': kind, 'job_id': job.get('job_id')},
                    {'$set': {
                        'state': 'failed',
                        'error': 'El trabajo expiró antes de completarse.',
                        'finished_at': now(),
                    }},
                )
                job = collection.find_one({'_id': kind})
    return job


def results(kind):
    job = read_job(kind)
    return (job or {}).get('result') or empty_result()


def collect_source(kind):
    """Proyección acotada; falla si excede MAX_ROWS en lugar de truncar."""
    clinical = kind in ('clinical', 'unsupervised')
    fields = ('fc', 'fr', 'temp', 'spo2') if clinical else ('status', 'fecha_ing')
    source = 'signos_vitales' if clinical else 'atencion'

    docs = list(
        get_collection(source)
        .find({}, {'_id': 0, **{f: 1 for f in fields}})
        .limit(MAX_ROWS + 1)
    )
    if len(docs) > MAX_ROWS:
        raise ValueError('dataset_limit')

    rows = []
    for doc in docs:
        if clinical:
            row = {}
            for field in fields:
                raw = doc.get(field)
                try:
                    value = float(raw)
                    row[field] = (
                        value
                        if math.isfinite(value) and not isinstance(raw, bool)
                        else None
                    )
                except (TypeError, ValueError):
                    row[field] = None
            rows.append(row)
        else:
            date = doc.get('fecha_ing')
            if isinstance(date, str):
                try:
                    date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                except ValueError:
                    date = None
            rows.append({
                'day': date.date().isoformat()
                       if isinstance(date, datetime) else None,
                'status': doc.get('status')
                          if doc.get('status') in ('ABIERTA', 'CERRADA')
                          else 'OTRO',
            })
    return rows


def run_engine(kind, rows):
    """Aísla la JVM y mata el grupo de procesos al expirar (Linux)."""
    unavailable = runtime_error()
    if unavailable:
        raise SparkRuntimeError(unavailable)

    with tempfile.TemporaryDirectory(prefix='ineo-spark-') as directory:
        source = Path(directory) / 'input.json'
        target = Path(directory) / 'output.json'
        source.write_text(
            json.dumps({'type': kind, 'rows': rows}),
            encoding='utf-8',
        )
        process = subprocess.Popen(
            [
                sys.executable,
                str(Path(__file__).with_name('spark_engine.py')),
                str(source),
                str(target),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=os.name != 'nt',
        )
        try:
            _stdout, stderr = process.communicate(timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            if os.name != 'nt':
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            process.communicate()
            raise SparkRuntimeError(
                f'El análisis excedió el límite de {TIMEOUT} segundos. '
                'Inténtalo con menos datos.'
            )
        if process.returncode != 0 or not target.exists():
            lowered = (stderr or '').lower()
            if (
                'java_home' in lowered
                or 'java gateway' in lowered
                or 'java: not found' in lowered
            ):
                raise SparkRuntimeError(
                    'Java 17 no está configurado correctamente para ejecutar Spark.'
                )
            if 'no module named' in lowered and 'pyspark' in lowered:
                raise SparkRuntimeError('PySpark no está instalado en la API.')
            if (
                process.returncode in (-9, 137)
                or 'outofmemory' in lowered
                or 'cannot allocate memory' in lowered
            ):
                raise SparkRuntimeError(
                    'El servidor no tiene memoria suficiente para ejecutar Spark.'
                )
            raise SparkRuntimeError(
                'El motor Spark terminó inesperadamente. Revisa los logs del servicio.'
            )
        return json.loads(target.read_text(encoding='utf-8'))


def execute(kind, job_id):
    collection = get_collection(COLLECTION)
    claimed = collection.update_one(
        {
            '_id': kind,
            'job_id': job_id,
            'state': 'pending',
            'expires_at': {'$gt': now()},
        },
        {'$set': {'state': 'running', 'started_at': now()}},
    )
    if not claimed.modified_count:
        return
    try:
        result = run_engine(kind, collect_source(kind))
        result.update(
            contract_version=VERSION,
            timestamp=stamp(now()),
            visualizations=[],
        )
        update = {'state': 'completed', 'result': result, 'error': None}
    except SparkRuntimeError as error:
        update = {'state': 'failed', 'error': str(error)}
    except Exception:
        update = {
            'state': 'failed',
            'error': (
                'No se pudo completar el análisis. '
                'Revisa el motor Spark y la fuente de datos.'
            ),
        }
    update['finished_at'] = now()
    collection.update_one(
        {'_id': kind, 'job_id': job_id, 'state': 'running'},
        {'$set': update},
    )


def start(kind):
    if kind not in TYPES:
        raise SparkTypeError('Tipo de análisis no válido')
    collection = get_collection(COLLECTION)
    collection.update_one(
        {'_id': kind},
        {'$setOnInsert': {'state': 'idle'}},
        upsert=True,
    )
    read_job(kind)
    job_id = str(uuid4())
    doc = collection.find_one_and_update(
        {'_id': kind, 'state': {'$nin': ['pending', 'running']}},
        {'$set': {
            'type': kind,
            'job_id': job_id,
            'state': 'pending',
            'error': None,
            'started_at': None,
            'finished_at': None,
            'expires_at': now() + timedelta(seconds=JOB_TTL),
        }},
        return_document=ReturnDocument.AFTER,
    )
    if doc is None:
        return status_of(read_job(kind)), False
    try:
        EXECUTOR.submit(execute, kind, job_id)
    except RuntimeError:
        collection.update_one(
            {'_id': kind, 'job_id': job_id},
            {'$set': {'state': 'failed', 'error': 'Ejecutor no disponible.'}},
        )
        raise
    return status_of(doc), True


class SparkService:
    """Fachada orientada a rutas Flask (contrato v1)."""

    VERSION = VERSION
    ALLOWED_TYPES = TYPES
    IMPLEMENTED_TYPES = ('clinical', 'met', 'analytics', 'unsupervised')
    COLLECTION = COLLECTION
    JOB_TIMEOUT_SECONDS = TIMEOUT
    MAX_ROWS = MAX_ROWS

    _executor = EXECUTOR

    @classmethod
    def get_overview(cls):
        overview = {}
        for analysis_type in cls.ALLOWED_TYPES:
            job = read_job(analysis_type)
            result = (job or {}).get('result') or empty_result()
            overview[analysis_type] = {
                'available': bool(result.get('available')),
                'status': status_of(job),
            }
        return overview

    @classmethod
    def get_status(cls, analysis_type):
        cls._assert_allowed(analysis_type)
        job = read_job(analysis_type)
        payload = status_of(job)
        payload['type'] = analysis_type
        if job is None:
            payload['state'] = 'idle'
            payload['running'] = False
            payload['job_id'] = None
            payload['error'] = None
            payload['started_at'] = None
            payload['finished_at'] = None
        return payload

    @classmethod
    def get_result(cls, analysis_type):
        cls._assert_allowed(analysis_type)
        result = dict(results(analysis_type))
        result['type'] = analysis_type
        if 'contract_version' not in result:
            result['contract_version'] = cls.VERSION
        return result

    @classmethod
    def run(cls, analysis_type, requested_by=None, role=None):
        cls._assert_allowed(analysis_type)
        if analysis_type not in cls.IMPLEMENTED_TYPES:
            raise SparkNotImplemented(
                'Tipo de análisis no implementado en PBL-03'
            )
        status, created = start(analysis_type)
        if not created:
            raise SparkJobConflict('El análisis ya se está procesando')
        if requested_by or role:
            get_collection(cls.COLLECTION).update_one(
                {'_id': analysis_type, 'job_id': status.get('job_id')},
                {'$set': {
                    'requested_by': requested_by,
                    'role': role,
                }},
            )
        return {
            'contract_version': cls.VERSION,
            'status': status,
        }

    @classmethod
    def _assert_allowed(cls, analysis_type):
        if analysis_type not in cls.ALLOWED_TYPES:
            raise SparkTypeError('Tipo de análisis no válido')

    @classmethod
    def _now(cls):
        return now()

    @classmethod
    def _read_job(cls, analysis_type):
        return read_job(analysis_type)

    @classmethod
    def _status_payload(cls, analysis_type, job):
        payload = status_of(job)
        payload['type'] = analysis_type
        return payload

    @classmethod
    def _empty_result(cls, analysis_type=None):
        result = empty_result()
        if analysis_type:
            result['type'] = analysis_type
        return result

    @classmethod
    def _collect_source(cls, analysis_type):
        return collect_source(analysis_type)

    @classmethod
    def _run_engine(cls, analysis_type, rows):
        return run_engine(analysis_type, rows)

    @classmethod
    def _execute(cls, analysis_type, job_id):
        return execute(analysis_type, job_id)

    @classmethod
    def _execute_clinical(cls, analysis_type='clinical'):
        job = read_job(analysis_type)
        if not job or not job.get('job_id'):
            return
        return execute(analysis_type, job['job_id'])

    @classmethod
    def _launch(cls, analysis_type):
        return None