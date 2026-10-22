"""Aggregate-only presentation data, persisted with the Spark snapshot."""
from collections import Counter
from datetime import date, timedelta
from utils.database import get_collection


def distribution(collection, field, query=None):
    # Keep missing values visible: they must never silently disappear from totals.
    grouped = get_collection(collection).aggregate([
        {'$match': query or {}},
        {'$group': {'_id': {'$ifNull': ['$' + field, 'UNKNOWN']}, 'count': {'$sum': 1}}},
        {'$sort': {'count': -1, '_id': 1}},
    ])
    combined = Counter()
    for row in grouped:
        combined[str(row['_id']) if row['_id'] != '' else 'UNKNOWN'] += row['count']
    rows = [{'label': label, 'value': value} for label, value in sorted(combined.items(), key=lambda item: (-item[1], item[0]))]
    # Explicit Other bucket keeps denominators correct for large catalogs.
    if len(rows) > 12:
        rows = rows[:11] + [{'label': 'OTHER', 'value': sum(row['value'] for row in rows[11:])}]
    return rows


def build_dashboard(kind, source_rows, result, filters=None):
    filters = filters or {}
    area_query = {'area': filters['area']} if filters.get('area') else {}
    dashboard = {'version': 1, 'charts': [], 'kpis': [], 'timezone': 'UTC'}

    def chart(key, rows, source, unit='records', scope='snapshot', mode='bar'):
        dashboard['charts'].append({'key': key, 'rows': rows, 'source': source,
                                    'unit': unit, 'scope': scope, 'mode': mode})

    if kind == 'analytics':
        patients = get_collection('pacientes').count_documents({})
        active = sum(row.get('status') == 'ABIERTA' for row in source_rows) if filters else get_collection('atencion').count_documents({'status': 'ABIERTA'})
        beds = distribution('camas', 'ocupada', area_query)
        total_beds = sum(row['value'] for row in beds)
        occupied = sum(row['value'] for row in beds if row['label'] == '1')
        dashboard['kpis'] = [
            {'key': 'patients', 'value': patients, 'unit': 'patients'},
            {'key': 'attentions', 'value': result.get('summary', {}).get('total', len(source_rows)), 'unit': 'attentions'},
            {'key': 'active', 'value': active, 'unit': 'attentions'},
            {'key': 'occupancy', 'value': occupied / total_beds * 100 if total_beds else None, 'unit': 'percent'},
        ]
        chart('attentionStatus', [{'label': row['status'], 'value': row['count']}
                                  for row in result.get('metrics', []) if 'status' in row], 'atencion', 'attentions', 'history')
        if filters:
            areas = Counter(row.get('area') or 'UNKNOWN' for row in source_rows if row.get('status') == 'ABIERTA')
            area_rows = [{'label': area, 'value': count} for area, count in sorted(areas.items(), key=lambda item: (-item[1], item[0]))]
            if len(area_rows) > 12:
                area_rows = area_rows[:11] + [{'label': 'OTHER', 'value': sum(row['value'] for row in area_rows[11:])}]
        else:
            area_rows = distribution('atencion', 'area', {'status': 'ABIERTA'})
        chart('activeArea', area_rows, 'atencion', 'attentions', 'history' if filters else 'snapshot')
        chart('beds', beds, 'camas', 'beds')
        exam_query = {}
        if filters.get('area'):
            ids = [row.get('id_atencion') for row in get_collection('atencion').find(area_query, {'_id': 0, 'id_atencion': 1}).limit(20001)]
            if len(ids) > 20000:
                raise ValueError('dataset_limit')
            exam_query['id_atencion'] = {'$in': [value for value in ids if value is not None]}
        chart('examStatus', distribution('examenes_det', 'estado', exam_query), 'examenes_det', 'exams')
    elif kind == 'met':
        counts = Counter(row['day'] for row in source_rows if row.get('day'))
        if counts or filters.get('start_date'):
            start, end = (date.fromisoformat(filters['start_date']), date.fromisoformat(filters['end_date'])) if filters.get('start_date') else (date.fromisoformat(min(counts)), date.fromisoformat(max(counts)))
            span = (end - start).days + 1
            # Daily for <=90 days, otherwise monthly: bound the chart without truncation.
            if span <= 90:
                rows = [{'label': (start + timedelta(days=i)).isoformat(),
                         'value': counts.get((start + timedelta(days=i)).isoformat(), 0)} for i in range(span)]
                key = 'daily'
            else:
                monthly = Counter()
                for day, count in counts.items():
                    monthly[day[:7]] += count
                month = start.replace(day=1)
                rows = []
                while month <= end:
                    label = month.strftime('%Y-%m')
                    rows.append({'label': label, 'value': monthly.get(label, 0)})
                    month = date(month.year + (month.month == 12), month.month % 12 + 1, 1)
                key = 'monthly'
            chart(key, rows, 'atencion.fecha_ing', 'attentions', 'history', 'line')
            weekday = Counter()
            for day, count in counts.items():
                weekday[date.fromisoformat(day).weekday()] += count
            chart('weekday', [{'label': 'weekday' + str(i), 'value': weekday[i]} for i in range(7)],
                  'atencion.fecha_ing', 'attentions', 'history')
            dated = sum(counts.values())
            peak = max(counts.values(), default=0)
            dashboard['peak_days'] = [{'day': day, 'count': count} for day, count in sorted(counts.items()) if count == peak][:10]
            dashboard['peak_ties'] = sum(count == peak for count in counts.values())
            dashboard['kpis'] = [{'key': 'dated', 'value': dated, 'unit': 'attentions'},
                                 {'key': 'calendarAverage', 'value': dated / span, 'unit': 'perDay'},
                                 {'key': 'calendarDays', 'value': span, 'unit': 'days'},
                                 {'key': 'undated', 'value': len(source_rows) - dated, 'unit': 'attentions'}]
    elif kind == 'clinical':
        dashboard['kpis'] = [{'key': 'observations', 'value': result.get('summary', {}).get('total', 0), 'unit': 'observations'},
                             {'key': 'excluded', 'value': result.get('quality', {}).get('excluded_rows', 0), 'unit': 'observations'}]
        # No comparison across incompatible units. Existing metrics retain each unit.
        chart('clinicalCoverage', [{'label': row['measure'], 'value': row['count']}
                                   for row in result.get('metrics', [])], 'signos_vitales', 'observations', 'history')
    elif kind == 'unsupervised':
        chart('groups', [{'label': str(row['cluster']), 'value': row['count']}
                          for row in result.get('clusters', [])], 'signos_vitales', 'observations', 'history')
        pca = result.get('pca', {})
        chart('variance', [{'label': 'PC' + str(i + 1), 'value': value * 100}
                           for i, value in enumerate(pca.get('explained_variance', []))],
              'signos_vitales', 'percent', 'history')
        for feature in ('fc', 'fr', 'temp', 'spo2'):
            chart('profile_' + feature,
                  [{'label': str(row['cluster']), 'value': row['means'][feature]}
                   for row in result.get('clusters', []) if feature in row.get('means', {})],
                  'signos_vitales', feature, 'history')
        total = sum(group['count'] for group in result.get('clusters', []))
        for entry in dashboard['charts']:
            if entry['key'].startswith('profile_') and total:
                feature = entry['key'][len('profile_'):]
                if all(feature in group.get('means', {}) for group in result.get('clusters', [])):
                    entry['reference_value'] = sum(group['count'] * group['means'][feature] for group in result.get('clusters', [])) / total
        dashboard['kpis'] = [{'key': 'observations', 'value': result.get('summary', {}).get('total', 0), 'unit': 'observations'},
                             {'key': 'groups', 'value': result.get('summary', {}).get('groups', 0), 'unit': 'groups'},
                             {'key': 'excluded', 'value': result.get('quality', {}).get('excluded_rows', 0), 'unit': 'observations'}]
    return dashboard
