"""Persistent Spark jobs; no patient identifiers leave the source projection.

Resolución de merge:
- Se conserva la interfaz de clase `SparkService` (usada por routes/spark.py).
- Se adopta el motor PySpark vía subprocess (`spark_engine.py`) de origin/main.
- Se añade expiración de jobs y manejo seguro de errores (no filtra rutas,
  credenciales ni logs crudos de la JVM).
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
from uuid import uuid4

from pymongo import ReturnDocument

from utils.database import get_collection


class SparkJobConflict(Exception):
    """El análisis solicitado ya se está procesando."""


class SparkTypeError(ValueError):
    """Tipo de análisis ausente o no permitido."""


class SparkNotImplemented(ValueError):
    """Tipo válido pero fuera del alcance de PBL-03."""


class SparkService:
    VERSION = '1.0'
    ALLOWED_TYPES = ('analytics', 'met', 'clinical', 'unsupervised')
    IMPLEMENTED_TYPES = ('clinical',)
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

        try:
            cls._executor.submit(cls._execute, analysis_type, job_id)
        except RuntimeError as error:
            collection.update_one(
                {'_id': analysis_type, 'job_id': job_id},
                {'$set': {'state': 'failed',
                          'error': 'Ejecutor no disponible.'}},
            )
            raise SparkNotImplemented('Ejecutor no disponible') from error

        return {
            'contract_version': cls.VERSION,
            'status': cls._status_payload(analysis_type, doc),
        }

    # --- Ejecución asíncrona ----------------------------------------------

    @classmethod
    def _execute(cls, analysis_type, job_id):
        collection = get_collection(cls.COLLECTION)
        claimed = collection.update_one(
            {'_id': analysis_type, 'job_id': job_id,
             'state': 'pending', 'expires_at': {'$gt': cls._now()}},
            {'$set': {'state': 'running', 'started_at': cls._now()}},
        )
        if not claimed.modified_count:
            return

        try:
            rows = cls._collect_source(analysis_type)
            result = cls._run_engine(analysis_type, rows)
            result.update(
                contract_version=cls.VERSION,
                timestamp=cls._stamp(cls._now()),
                visualizations=[],
            )
            update = {'state': 'completed', 'result': result,
                      'error': None, 'log': None}
        except Exception as error:
            # No publicar filas, rutas, credenciales ni logs crudos de la JVM.
            update = {
                'state': 'failed',
                'result': cls._empty_result(analysis_type),
                'error': 'No se pudo completar el análisis. '
                         'Revisa el motor Spark y la fuente de datos.',
                'log': cls._safe_log(error),
            }
        update['finished_at'] = cls._now()
        collection.update_one(
            {'_id': analysis_type, 'job_id': job_id, 'state': 'running'},
            {'$set': update},
        )

    @classmethod
    def _collect_source(cls, analysis_type):
        """Proyección acotada; falla si excede MAX_ROWS en lugar de truncar."""
        clinical = analysis_type in ('clinical', 'unsupervised')
        fields = ('fc', 'fr', 'temp', 'spo2') if clinical else ('status', 'fecha_ing')
        source = 'signos_vitales' if clinical else 'atencion'

        docs = list(
            get_collection(source)
            .find({}, {'_id': 0, **{f: 1 for f in fields}})
            .limit(cls.MAX_ROWS + 1)
        )
        if len(docs) > cls.MAX_ROWS:
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

    # --- Helpers -----------------------------------------------------------

    @classmethod
    def _assert_allowed(cls, analysis_type):
        if analysis_type not in cls.ALLOWED_TYPES:
            raise SparkTypeError('Tipo de análisis no válido')

    @classmethod
    def _read_job(cls, analysis_type):
        cls._expire_stale(analysis_type)
        document = get_collection(cls.COLLECTION).find_one({'_id': analysis_type})
        if not document:
            return None
        document.pop('_id', None)
        return document

    @classmethod
    def _expire_stale(cls, analysis_type):
        get_collection(cls.COLLECTION).update_one(
            {'_id': analysis_type,
             'state': {'$in': ['pending', 'running']},
             'expires_at': {'$lte': cls._now()}},
            {'$set': {
                'state': 'failed',
                'finished_at': cls._now(),
                'error': 'La ejecución fue interrumpida. Vuelve a ejecutarla.',
            }},
        )

    @classmethod
    def _status_payload(cls, analysis_type, job):
        job = job or {}
        state = job.get('state') or 'idle'
        return {
            'contract_version': cls.VERSION,
            'state': state,
            'running': state in ('pending', 'running'),
            'job_id': job.get('job_id'),
            'type': analysis_type,
            'started_at': cls._stamp(job.get('started_at')),
            'finished_at': cls._stamp(job.get('finished_at')),
            'log': job.get('log'),
            'error': job.get('error'),
        }

    @classmethod
    def _empty_result(cls, analysis_type):
        return {
            'contract_version': cls.VERSION,
            'available': False,
            'timestamp': None,
            'type': analysis_type,
            'visualizations': [],
            'summary': {},
            'metrics': [],
            'clusters': [],
            'pca': {},
            'quality': {},
        }

    @staticmethod
    def _now():
        return datetime.now(timezone.utc)

    @staticmethod
    def _stamp(value):
        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            return value.isoformat()
        return value

    @staticmethod
    def _safe_log(error):
        text = str(error) or error.__class__.__name__
        text = text.replace('\n', ' ').strip()
        return text[:500]