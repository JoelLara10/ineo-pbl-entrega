// Session-only clinical cache. Never written to disk or browser storage.
const entries = new Map();
const requests = new Map();
let generation = 0;
export function clearMonitoringCache() { generation++; entries.clear(); requests.clear(); }
export function monitoringCacheKey(owner, patientId, page, historyPage, alertsPage, query, before) {
  return JSON.stringify([owner, patientId || null, page, historyPage, alertsPage, query, before || null]);
}
export function getMonitoringCache(key) {
  const entry = entries.get(key);
  if (!entry || Date.now() - entry.savedAt > 120000) { entries.delete(key); return null; }
  return entry;
}
export function loadMonitoringCache(key, fetcher) {
  if (requests.has(key)) return requests.get(key);
  const version = generation;
  const request = Promise.resolve().then(fetcher).then(data => {
    if (version !== generation) throw Object.assign(new Error('session_changed'), {code:'ERR_SESSION_CHANGED'});
    const entry = { data, savedAt: Date.now() };
    entries.delete(key); entries.set(key, entry);
    if (entries.size > 40) entries.delete(entries.keys().next().value);
    return entry;
  }).finally(() => { if (requests.get(key) === request) requests.delete(key); });
  requests.set(key, request);
  return request;
}
