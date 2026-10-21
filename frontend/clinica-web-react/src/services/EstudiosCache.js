import { getClinicalCache, setClinicalCache, removeClinicalCache, invalidateClinicalPrefix } from './clinicalCache';
export const CACHE_TTL_MS = 5 * 60 * 1000;
export const CacheKeys = {
  counts: 'estudios_counts',
  estudiosAll: (type, status) => `estudios_all_${type}_${status}`,
  examenInfo: (id) => `examen_info_${id}`,
};
export const getCacheEntry = async (key) => {
  const entry = getClinicalCache(key);
  return entry ? { ...entry, isFresh: Date.now() - entry.savedAt <= entry.ttl } : null;
};
export const getCache = async (key) => (await getCacheEntry(key))?.data ?? null;
export const setCache = async (key, data, ttl = CACHE_TTL_MS) => {
  setClinicalCache(key, { data, savedAt: Date.now(), ttl }, ttl);
};
export const removeCache = async (key) => removeClinicalCache(key);
export const invalidateCachePrefix = async (prefix) => invalidateClinicalPrefix(prefix);
