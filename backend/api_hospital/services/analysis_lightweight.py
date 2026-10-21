"""Bounded local calculations for small API containers; never starts a JVM."""
from collections import Counter, defaultdict
import math

FEATURES = ('fc', 'fr', 'temp', 'spo2')


def stats(values):
    return {'count': len(values), 'mean': math.fsum(values) / len(values) if values else None,
            'minimum': min(values) if values else None, 'maximum': max(values) if values else None}


def analyze(kind, rows):
    result = {'available': False, 'summary': {}, 'metrics': [], 'clusters': [], 'pca': {},
              'engine': {'name': 'lightweight', 'method': 'aggregates'},
              'quality': {'source_rows': len(rows), 'used_rows': 0, 'excluded_rows': 0}}
    if not rows:
        return result
    if kind in ('analytics', 'met'):
        field = 'status' if kind == 'analytics' else 'day'
        counts = Counter(row.get(field) for row in rows if row.get(field) is not None)
        used = sum(counts.values())
        result['metrics'] = [{field: key, 'count': count} for key, count in sorted(counts.items())]
    elif kind == 'clinical':
        # Values are validated/projected by collect_source before reaching either engine.
        used = sum(any(row.get(name) is not None for name in FEATURES) for row in rows)
        result['metrics'] = [{'measure': name, **stats([row[name] for row in rows if row.get(name) is not None])}
                             for name in FEATURES]
        daily = defaultdict(lambda: defaultdict(list))
        for row in rows:
            if row.get('day'):
                for name in FEATURES:
                    if row.get(name) is not None:
                        daily[row['day']][name].append(row[name])
        result['trends'] = [{'day': day, 'measure': name, **stats(values[name])}
                            for day, values in sorted(daily.items()) for name in FEATURES if values[name]]
    elif kind == 'unsupervised':
        complete = [tuple(row[name] for name in FEATURES) for row in rows
                    if all(row.get(name) is not None for name in FEATURES)]
        used = len(complete)
        if used >= 4 and len(set(complete)) >= 3:
            grouped = cluster(complete)
            result['quality'].update(grouped.pop('quality', {}))
            result.update(grouped)
        else:
            result['quality']['reason'] = 'insufficient_complete_distinct_rows'
    else:
        raise ValueError('invalid_analysis_type')
    result['quality'].update(used_rows=used, excluded_rows=len(rows) - used)
    if kind != 'unsupervised':
        result['available'] = used > 0
        result['summary'] = {'total': used} if used else {}
    return result


def squared_distances(values, centers):
    # At most N x 4: never materialize an N x N pairwise matrix.
    import numpy as np
    return np.maximum((values * values).sum(axis=1)[:, None]
                      - 2 * values @ centers.T + (centers * centers).sum(axis=1), 0)


def silhouette(values, labels, k):
    """Exact squared-Euclidean silhouette from cluster moments, O(N*k*d)."""
    import numpy as np
    counts = np.bincount(labels, minlength=k)
    if np.any(counts == 0):
        return -1.0
    centers = np.vstack([values[labels == group].mean(axis=0) for group in range(k)])
    avg_norm = np.array([(values[labels == group] ** 2).sum(axis=1).mean() for group in range(k)])
    distance = np.maximum((values * values).sum(axis=1)[:, None] - 2 * values @ centers.T + avg_norm, 0)
    index = np.arange(len(values))
    size = counts[labels]
    intra = distance[index, labels] * size / np.maximum(size - 1, 1)
    distance[index, labels] = np.inf
    inter = distance.min(axis=1)
    denominator = np.maximum(intra, inter)
    score = np.divide(inter - intra, denominator, out=np.zeros_like(intra), where=denominator > 0)
    score[size == 1] = 0
    return float(score.mean())


def kmeans(values, k):
    import numpy as np
    rng = np.random.default_rng(7)
    best = None
    # Fixed restarts/iterations; memory stays proportional to the bounded source.
    for _ in range(4):
        centers = [values[rng.integers(len(values))].copy()]
        while len(centers) < k:
            nearest = squared_distances(values, np.array(centers)).min(axis=1)
            centers.append(values[rng.choice(len(values), p=nearest / nearest.sum())].copy())
        centers = np.array(centers)
        for _ in range(30):
            distances = squared_distances(values, centers)
            labels = distances.argmin(axis=1)
            if len(np.unique(labels)) != k:
                break
            updated = np.vstack([values[labels == group].mean(axis=0) for group in range(k)])
            if np.allclose(updated, centers, rtol=0, atol=1e-6):
                centers = updated
                break
            centers = updated
        distances = squared_distances(values, centers)
        labels = distances.argmin(axis=1)
        if len(np.unique(labels)) != k:
            continue
        inertia = float(distances[np.arange(len(values)), labels].sum())
        if best is None or inertia < best[0]:
            best = inertia, labels
    return best


def cluster(rows):
    import numpy as np
    raw = np.array(sorted(rows), dtype=float)
    deviation = raw.std(axis=0, ddof=1)
    scaled = (raw - raw.mean(axis=0)) / np.where(deviation > 0, deviation, 1)
    eigenvalues, components = np.linalg.eigh(np.cov(scaled, rowvar=False))
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = np.maximum(eigenvalues[order], 0)
    candidates = []
    best = None
    distinct = len(np.unique(raw, axis=0))
    for k in range(2, min(4, distinct - 1) + 1):
        fitted = kmeans(scaled, k)
        if fitted is None:
            continue
        inertia, labels = fitted
        score = silhouette(scaled, labels, k)
        candidates.append({'k': k, 'silhouette': score, 'inertia': inertia})
        if best is None or score > best[0]:
            best = score, k, labels
    if best is None:
        return {'quality': {'reason': 'no_stable_groups'}, 'available': False}
    _, k, labels = best
    return {'available': True, 'summary': {'total': len(rows), 'groups': k},
            'engine': {'name': 'lightweight', 'method': 'numpy_kmeans_pca'},
            'clusters': [{'cluster': group, 'count': int((labels == group).sum()),
                          'means': {name: float(raw[labels == group, index].mean()) for index, name in enumerate(FEATURES)}}
                         for group in range(k)],
            'pca': {'features': list(FEATURES), 'explained_variance': (eigenvalues[:2] / eigenvalues.sum()).tolist(),
                    'components': components[:, order[:2]].tolist(), 'seed': 7, 'standardized': True,
                    'candidates': candidates, 'selected_k': k}}
