import { getClinicalCache, setClinicalCache, clearClinicalCache } from '../../services/clinicalCache';
export const CACHE_TTL = 5 * 60 * 1000;
export const CACHE_PREFIX = 'ineo_config_react_';

export function getCache(key) { return getClinicalCache(CACHE_PREFIX + key); }
export function setCache(key, data, ttl = CACHE_TTL) { setClinicalCache(CACHE_PREFIX + key, data, ttl); }
export function clearCache() { clearClinicalCache(); }

export function readPermanent(key, fallback) {
  try {
    const raw = localStorage.getItem(CACHE_PREFIX + 'perm_' + key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

export function savePermanent(key, data) {
  localStorage.setItem(CACHE_PREFIX + 'perm_' + key, JSON.stringify(data));
  return data;
}

export function paginate(data, page, perPage) {
  const start = (page - 1) * perPage;
  return data.slice(start, start + perPage);
}

export function pages(data, perPage) {
  return Math.max(1, Math.ceil(data.length / perPage));
}
