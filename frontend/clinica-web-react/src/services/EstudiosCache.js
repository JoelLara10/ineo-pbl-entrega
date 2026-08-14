const CACHE_PREFIX = "estudios_";

export const CacheKeys = {
  counts: `${CACHE_PREFIX}counts`,
  estudiosAll: (type, status) => `${CACHE_PREFIX}all_${type}_${status}`,
  examenInfo: (id) => `examen_info_${id}`,
};

export const getCache = async (key) => {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
};

export const setCache = async (key, value) => {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (e) {
    console.warn("Error guardando caché:", e);
  }
};

export const removeCache = async (key) => {
  try {
    localStorage.removeItem(key);
  } catch {}
};

export const invalidateCachePrefix = async (prefix) => {
  try {
    const keys = Object.keys(localStorage);
    for (const key of keys) {
      if (key.startsWith(prefix)) {
        localStorage.removeItem(key);
      }
    }
  } catch {}
};
