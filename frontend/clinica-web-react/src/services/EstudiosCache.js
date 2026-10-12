const CACHE_PREFIX = 'estudios_';
const CACHE_DB_NAME = 'ineo_estudios_cache';
const CACHE_DB_VERSION = 1;
const CACHE_STORE = 'entries';
export const CACHE_TTL_MS = 5 * 60 * 1000;

export const CacheKeys = {
  counts: `${CACHE_PREFIX}counts`,
  estudiosAll: (type, status) => `${CACHE_PREFIX}all_${type}_${status}`,
  examenInfo: (id) => `examen_info_${id}`,
};

let databasePromise;

function openDatabase() {
  if (typeof indexedDB === 'undefined') return Promise.reject(new Error('IndexedDB is unavailable'));
  if (databasePromise) return databasePromise;

  databasePromise = new Promise((resolve, reject) => {
    const request = indexedDB.open(CACHE_DB_NAME, CACHE_DB_VERSION);
    request.onupgradeneeded = () => {
      const database = request.result;
      if (!database.objectStoreNames.contains(CACHE_STORE)) {
        database.createObjectStore(CACHE_STORE, { keyPath: 'key' });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => {
      databasePromise = null;
      reject(request.error);
    };
  });
  return databasePromise;
}

function readEntryFromDatabase(database, key) {
  return new Promise((resolve, reject) => {
    const request = database.transaction(CACHE_STORE, 'readonly').objectStore(CACHE_STORE).get(key);
    request.onsuccess = () => resolve(request.result || null);
    request.onerror = () => reject(request.error);
  });
}

function writeEntryToDatabase(database, entry) {
  return new Promise((resolve, reject) => {
    const transaction = database.transaction(CACHE_STORE, 'readwrite');
    transaction.objectStore(CACHE_STORE).put(entry);
    transaction.oncomplete = () => resolve();
    transaction.onerror = () => reject(transaction.error);
    transaction.onabort = () => reject(transaction.error);
  });
}

function deleteEntryFromDatabase(database, key) {
  return new Promise((resolve, reject) => {
    const request = database.transaction(CACHE_STORE, 'readwrite').objectStore(CACHE_STORE).delete(key);
    request.onsuccess = () => resolve();
    request.onerror = () => reject(request.error);
  });
}

export const getCacheEntry = async (key) => {
  let entry = null;
  try {
    const database = await openDatabase();
    entry = await readEntryFromDatabase(database, key);
  } catch {
    // localStorage below keeps the cache usable in browsers without IndexedDB.
  }

  if (entry) {
    const ttl = Number(entry.ttl) || CACHE_TTL_MS;
    return {
      data: entry.data,
      savedAt: entry.savedAt || 0,
      isFresh: Date.now() - (entry.savedAt || 0) <= ttl,
    };
  }

  try {
    const raw = localStorage.getItem(key);
    if (!raw) return null;
    const parsed = JSON.parse(raw);

    // Read the previous raw-array cache format and migrate it on the next write.
    if (!parsed || typeof parsed !== 'object' || !Object.prototype.hasOwnProperty.call(parsed, 'data')) {
      return { data: parsed, savedAt: 0, isFresh: false };
    }

    const ttl = Number(parsed.ttl) || CACHE_TTL_MS;
    return {
      data: parsed.data,
      savedAt: Number(parsed.savedAt || parsed.timestamp) || 0,
      isFresh: Date.now() - (Number(parsed.savedAt || parsed.timestamp) || 0) <= ttl,
    };
  } catch {
    return null;
  }
};

export const getCache = async (key) => {
  const entry = await getCacheEntry(key);
  return entry ? entry.data : null;
};

export const setCache = async (key, value, ttl = CACHE_TTL_MS) => {
  const entry = { key, data: value, savedAt: Date.now(), ttl };
  try {
    const database = await openDatabase();
    await writeEntryToDatabase(database, entry);
    try { localStorage.removeItem(key); } catch {}
    return;
  } catch {
    try {
      localStorage.setItem(key, JSON.stringify(entry));
    } catch (error) {
      console.warn('Error guardando caché de estudios:', error);
    }
  }
};

export const removeCache = async (key) => {
  try {
    const database = await openDatabase();
    await deleteEntryFromDatabase(database, key);
  } catch {}
  try { localStorage.removeItem(key); } catch {}
};

export const invalidateCachePrefix = async (prefix) => {
  try {
    const database = await openDatabase();
    const keys = await new Promise((resolve, reject) => {
      const request = database.transaction(CACHE_STORE, 'readonly').objectStore(CACHE_STORE).getAllKeys();
      request.onsuccess = () => resolve(request.result || []);
      request.onerror = () => reject(request.error);
    });
    await Promise.all(keys.filter((key) => String(key).startsWith(prefix)).map((key) => deleteEntryFromDatabase(database, key)));
  } catch {}

  try {
    for (const key of Object.keys(localStorage)) {
      if (key.startsWith(prefix)) localStorage.removeItem(key);
    }
  } catch {}
};
