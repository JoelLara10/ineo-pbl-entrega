"""User-authored interpretation and clarity feedback tied to a saved snapshot."""
from datetime import datetime, timezone
from hashlib import sha256
from utils.database import get_collection


def public_review(doc):
    if not doc:
        return None
    return {key: doc.get(key) for key in ('interpretation', 'decision', 'clarity', 'notes', 'result_timestamp')}


def read_review(user_id, kind, timestamp):
    return public_review(get_collection('analysis_reviews').find_one({
        'user_id': user_id, 'kind': kind, 'result_timestamp': timestamp}))


def save_review(user_id, kind, payload):
    allowed = {'interpretation', 'decision', 'clarity', 'notes', 'result_timestamp'}
    if not isinstance(payload, dict) or set(payload) - allowed:
        raise ValueError('La evaluación del análisis no es válida.')
    for key, minimum, maximum in (('interpretation', 10, 2000), ('decision', 10, 2000), ('notes', 0, 1000), ('result_timestamp', 1, 80)):
        value = payload.get(key, '')
        if not isinstance(value, str) or not minimum <= len(value.strip()) <= maximum:
            raise ValueError('Escribe una interpretación y una decisión entre 10 y 2000 caracteres; las observaciones admiten hasta 1000.')
    if payload.get('clarity') not in ('clear', 'acceptable', 'confusing'):
        raise ValueError('Selecciona una calificación de claridad válida.')
    job = get_collection('spark_jobs').find_one({'_id': kind}) or {}
    result = job.get('result') or {}
    if not result.get('available') or result.get('timestamp') != payload['result_timestamp']:
        raise LookupError('El resultado cambió. Actualiza el análisis antes de guardar tu interpretación.')
    review = {key: payload.get(key, '').strip() for key in allowed}
    # Minimal evidence stays with the review even after the next result replaces it.
    review.update(user_id=user_id, kind=kind, updated_at=datetime.now(timezone.utc),
                  evidence={'period': result.get('metadata', {}).get('period'),
                            'filters': result.get('metadata', {}).get('filters', {}),
                            'summary': result.get('summary', {}),
                            'comparison': result.get('comparison'),
                            'units': sorted({row.get('unit', '') for row in result.get('dashboard', {}).get('charts', [])}),
                            'clinical_metrics': result.get('metrics', []) if kind == 'clinical' else []})
    review_id = sha256(f"{user_id}\0{kind}\0{payload['result_timestamp']}".encode()).hexdigest()
    get_collection('analysis_reviews').update_one(
        {'_id': review_id},
        {'$set': review}, upsert=True)
    return public_review(review)
