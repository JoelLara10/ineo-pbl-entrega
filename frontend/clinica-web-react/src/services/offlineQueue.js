export const QUEUE_KEY = '@ineo_offline_language_v1';
const TTL = 8 * 60 * 60 * 1000;
let memory = null;
let inFlight = null;
let generation = 0;

export function clearOfflineQueue() {
  memory = null;
  generation += 1;
  try { sessionStorage.removeItem(QUEUE_KEY); } catch { /* Memory-only fallback. */ }
}

export function readOfflineQueue(owner) {
  try { memory = JSON.parse(sessionStorage.getItem(QUEUE_KEY)) || memory; } catch { /* Memory-only fallback. */ }
  if (!memory) return null;
  if (!owner || memory.owner !== owner || !['es', 'en'].includes(memory.language)
      || !Number.isFinite(memory.createdAt) || Date.now() - memory.createdAt >= TTL
      || memory.createdAt > Date.now() || Object.keys(memory).sort().join(',') !== 'createdAt,language,owner') {
    clearOfflineQueue(); return null;
  }
  return { ...memory };
}

export function queueLanguage(owner, language) {
  if (!owner || typeof owner !== 'string' || !['es', 'en'].includes(language)) throw new Error('invalid_preference');
  // One coalesced absolute preference; no URLs, credentials or clinical payloads.
  memory = { owner, language, createdAt: Date.now() };
  try { sessionStorage.setItem(QUEUE_KEY, JSON.stringify(memory)); } catch { /* Memory-only fallback. */ }
}

export async function flushLanguage(owner, send, isCurrent = () => true) {
  if (inFlight) { await inFlight; return flushLanguage(owner, send, isCurrent); }
  const item = readOfflineQueue(owner);
  if (!item || navigator.onLine === false || !isCurrent()) return;
  const startedGeneration = generation;
  inFlight = (async () => {
    try {
      await send({ language: item.language });
      if (startedGeneration !== generation || !isCurrent()) return;
      const latest = readOfflineQueue(owner);
      if (latest?.language === item.language && latest?.createdAt === item.createdAt) clearOfflineQueue();
    } catch (error) {
      if ([400, 401, 403].includes(error.response?.status) && startedGeneration === generation) clearOfflineQueue();
      throw error;
    }
  })();
  try { await inFlight; } finally { inFlight = null; }
  if (startedGeneration === generation && readOfflineQueue(owner) && isCurrent()) return flushLanguage(owner, send, isCurrent);
}
