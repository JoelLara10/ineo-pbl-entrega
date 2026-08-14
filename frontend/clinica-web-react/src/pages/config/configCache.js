export const CACHE_TTL = 5 * 60 * 1000;
export const CACHE_PREFIX = 'ineo_config_react_';

export function getCache(key) {
  try {
    const raw = localStorage.getItem(CACHE_PREFIX + key);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (Date.now() - parsed.timestamp > parsed.ttl) {
      localStorage.removeItem(CACHE_PREFIX + key);
      return null;
    }
    return parsed.data;
  } catch (error) {
    console.error('Error leyendo caché:', error);
    return null;
  }
}

export function setCache(key, data, ttl = CACHE_TTL) {
  try {
    localStorage.setItem(CACHE_PREFIX + key, JSON.stringify({ data, timestamp: Date.now(), ttl }));
  } catch (error) {
    console.error('Error guardando caché:', error);
  }
}

export function clearCache(key) {
  localStorage.removeItem(CACHE_PREFIX + key);
}

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
