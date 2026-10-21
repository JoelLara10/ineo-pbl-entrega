// Clinical responses live only in memory while online, never in browser storage.
const entries = new Map();
export function clearClinicalCache() { entries.clear(); }
export function removeClinicalCache(key) { entries.delete(key); }
export function invalidateClinicalPrefix(prefix) { for (const key of entries.keys()) if (key.startsWith(prefix)) entries.delete(key); }
export function getClinicalCache(key) {
  if (globalThis.navigator?.onLine === false) return null;
  const entry = entries.get(key);
  if (!entry || entry.expires <= Date.now()) { entries.delete(key); return null; }
  return entry.data;
}
export function setClinicalCache(key, data, ttl = 120000) {
  if (globalThis.navigator?.onLine !== false) entries.set(key, { data, expires: Date.now() + ttl });
}
export function purgeLegacyClinicalStorage() {
  try {
    for (const key of Object.keys(localStorage)) {
      if (key.startsWith('ineo_web_cache_') || (key.startsWith('ineo_config_react_') && !key.startsWith('ineo_config_react_perm_')) || key.startsWith('@ineo_admin_cache:')
          || key.startsWith('estudios_') || key.startsWith('examen_info_')
          || ['ineo_selected_patient', '@ineo_print_history'].includes(key)) localStorage.removeItem(key);
    }
  } catch { /* Storage can be disabled. */ }
  try { globalThis.indexedDB?.deleteDatabase('ineo_estudios_cache'); } catch { /* Legacy cache may be unavailable. */ }
}
if (typeof window !== 'undefined') window.addEventListener('offline', clearClinicalCache);
