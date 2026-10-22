"""Validated calendar scopes. No database identifiers are exposed in results."""
from datetime import date, datetime, timedelta, timezone
import re

MAX_PERIOD_DAYS = 1827


def normalize_filters(payload, kind):
    if payload is None:
        return {}
    if not isinstance(payload, dict) or set(payload) - {'start_date', 'end_date', 'area', 'compare_previous'}:
        raise ValueError('Los filtros de análisis no son válidos.')
    result = {}
    start, end = payload.get('start_date'), payload.get('end_date')
    if any(value is not None and not isinstance(value, str) for value in (start, end)):
        raise ValueError('Las fechas deben ser texto con formato AAAA-MM-DD.')
    if bool(start) != bool(end):
        raise ValueError('Selecciona las fechas de inicio y fin.')
    if start or end:
        for value in (start, end):
            if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                raise ValueError('Usa fechas válidas con formato AAAA-MM-DD.')
        try:
            first, last = date.fromisoformat(start), date.fromisoformat(end)
        except ValueError as error:
            raise ValueError('Las fechas del análisis no son válidas.') from error
        if first > last or (last - first).days >= MAX_PERIOD_DAYS:
            raise ValueError('El periodo debe estar en orden y no superar cinco años.')
        result.update(start_date=start, end_date=end)
    area = payload.get('area', '')
    if not isinstance(area, str) or len(area) > 100 or any(ord(char) < 32 for char in area):
        raise ValueError('El área seleccionada no es válida.')
    if area.strip():
        result['area'] = area.strip()
    compare = payload.get('compare_previous', False)
    if not isinstance(compare, bool):
        raise ValueError('La opción de comparar debe ser verdadera o falsa.')
    if compare:
        if kind not in ('analytics', 'met') or not start:
            raise ValueError('La comparación requiere fechas y está disponible en analítica general y actividad diaria.')
        span = (last - first).days + 1
        if first.toordinal() <= span:
            raise ValueError('No hay un periodo anterior válido para esas fechas.')
        result['compare_previous'] = True
    return result


def previous_filters(filters):
    first = date.fromisoformat(filters['start_date'])
    last = date.fromisoformat(filters['end_date'])
    length = (last - first).days + 1
    return {**{key: value for key, value in filters.items() if key not in ('start_date', 'end_date', 'compare_previous')},
            'start_date': (first - timedelta(days=length)).isoformat(),
            'end_date': (first - timedelta(days=1)).isoformat()}


def parse_time(value):
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            return None
    if not isinstance(value, datetime):
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
