import { getClinicalCache, setClinicalCache, invalidateClinicalPrefix } from './clinicalCache';
const PREFIX = '@ineo_admin_cache:';
export const getAdminCache = (key, maxAge = 300000) => {
  const value = getClinicalCache(PREFIX + key);
  return value ? { ...value, isFresh: Date.now() - value.timestamp < maxAge } : null;
};
export const setAdminCache = (key, data) => {
  const value = { data, timestamp: Date.now() };
  setClinicalCache(PREFIX + key, value, 300000);
  return value;
};
export const clearAdminCache = () => invalidateClinicalPrefix(PREFIX);
