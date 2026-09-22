from datetime import datetime, timezone
import threading

from services.analytics_service import AnalyticsService
from utils.database import get_collection


class SparkJobConflict(Exception):
    """El análisis solicitado ya se está procesando."""


class SparkTypeError(ValueError):
    """Tipo de análisis ausente o no permitido."""


class SparkNotImplemented(ValueError):
    """Tipo válido pero fuera del alcance de PBL-03."""


class SparkService:
    ALLOWED_TYPES = ('analytics', 'met', 'clinical', 'unsupervised')
    IMPLEMENTED_TYPES = ('clinical',)
    COLLECTION = 'spark_jobs'
    JOB_TIMEOUT_SECONDS = 60
    _lock = threading.Lock()

    @classmethod
    def get_overview(cls):
        overview = {}
        for analysis_type in cls.ALLOWED_TYPES:
            status = cls.get_status(analysis_type)
            result = cls.get_result(analysis_type)
            overview[analysis_type] = {
                'available': bool(result.get('available')),
                'state': status['state'],
            }
        return overview

    @classmethod
    def get_status(cls, analysis_type):
        cls._assert_allowed(analysis_type)
        job = cls._read_job(analysis_type)
        return cls._status_payload(analysis_type, job)

    @classmethod
    def get_result(cls, analysis_type):
        cls._assert_allowed(analysis_type)
        job = cls._read_job(analysis_type)
        result = (job or {}).get('result')
        if result:
            return result
        return cls._empty_result(analysis_type)

    @classmethod
    def run(cls, analysis_type, requested_by=None, role=None):
        cls._assert_allowed(analysis_type)
        if analysis_type not in cls.IMPLEMENTED_TYPES:
            raise SparkNotImplemented('Tipo de análisis no implementado en PBL-03')

        with cls._lock:
            current = cls._read_job(analysis_type) or {}
            if current.get('running') or current.get('state') == 'processing':
                raise SparkJobConflict('El análisis clínico ya se está procesando')

            started_at = cls._now()
            job = {
                'type': analysis_type,
                'state': 'processing',
                'running': True,
                'started_at': started_at,
                'finished_at': None,
                'log': None,
                'result': current.get('result'),
                'requested_by': requested_by,
                'role': role,
            }
            cls._write_job(analysis_type, job)

        cls._launch(analysis_type)
        return {'status': cls._status_payload(analysis_type, job)}

    @classmethod
    def _launch(cls, analysis_type):
        thread = threading.Thread(
            target=cls._execute_clinical,
            args=(analysis_type,),
            daemon=True,
            name=f'spark-{analysis_type}',
        )
        thread.start()

    @classmethod
    def _execute_clinical(cls, analysis_type):
        box = {}

        def work():
            try:
                box['data'] = AnalyticsService.get_clinical_analytics()
            except Exception as error:
                box['error'] = error

        worker = threading.Thread(target=work, daemon=True, name=f'spark-{analysis_type}-work')
        worker.start()
        worker.join(cls.JOB_TIMEOUT_SECONDS)

        finished_at = cls._now()
        current = cls._read_job(analysis_type) or {'type': analysis_type}

        if worker.is_alive() or 'error' in box:
            log = 'Tiempo de espera agotado al ejecutar el análisis clínico'
            if 'error' in box:
                log = cls._safe_log(box['error'])
            current.update({
                'state': 'failed',
                'running': False,
                'finished_at': finished_at,
                'log': log,
                'result': cls._empty_result(analysis_type, timestamp=finished_at),
            })
            cls._write_job(analysis_type, current)
            return

        payload = box.get('data') or {}
        available = cls._has_clinical_content(payload)
        result = {
            'available': available,
            'timestamp': finished_at,
            'type': analysis_type,
            'top_diagnosis': payload.get('top_diagnosis') or [],
            'age_distribution': payload.get('age_distribution') or [],
            'average_stay_days': payload.get('average_stay_days', 0),
            'visualizations': [],
        }
        current.update({
            'state': 'completed',
            'running': False,
            'finished_at': finished_at,
            'log': None,
            'result': result,
        })
        cls._write_job(analysis_type, current)

    @classmethod
    def _assert_allowed(cls, analysis_type):
        if analysis_type not in cls.ALLOWED_TYPES:
            raise SparkTypeError('Tipo de análisis no válido')

    @classmethod
    def _read_job(cls, analysis_type):
        document = get_collection(cls.COLLECTION).find_one({'type': analysis_type})
        if not document:
            return None
        document.pop('_id', None)
        return document

    @classmethod
    def _write_job(cls, analysis_type, job):
        payload = dict(job)
        payload['type'] = analysis_type
        payload.pop('_id', None)
        get_collection(cls.COLLECTION).update_one(
            {'type': analysis_type},
            {'$set': payload},
            upsert=True,
        )

    @classmethod
    def _status_payload(cls, analysis_type, job):
        job = job or {}
        state = job.get('state') or 'pending'
        running = bool(job.get('running')) and state == 'processing'
        return {
            'state': state,
            'running': running,
            'type': analysis_type,
            'started_at': job.get('started_at'),
            'finished_at': job.get('finished_at'),
            'log': job.get('log'),
        }

    @classmethod
    def _empty_result(cls, analysis_type, timestamp=None):
        return {
            'available': False,
            'timestamp': timestamp,
            'type': analysis_type,
            'visualizations': [],
        }

    @staticmethod
    def _has_clinical_content(payload):
        if payload.get('top_diagnosis'):
            return True
        if payload.get('age_distribution'):
            return True
        stay = payload.get('average_stay_days')
        return isinstance(stay, (int, float)) and stay > 0

    @staticmethod
    def _now():
        return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

    @staticmethod
    def _safe_log(error):
        text = str(error) or error.__class__.__name__
        text = text.replace('\n', ' ').strip()
        if len(text) > 500:
            text = text[:500]
        return text
