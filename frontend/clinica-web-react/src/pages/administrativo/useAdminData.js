import { useCallback, useEffect, useRef, useState } from 'react';
import { usePageRevalidation } from '../../hooks/usePageRevalidation';
import { getAdminCache, setAdminCache } from '../../services/adminCache';

export default function useAdminData(cacheKey, loader, initialValue) {
  const requestId = useRef(0);
  const initialData = useRef(initialValue);
  const currentKey = useRef(cacheKey);
  const [data, setData] = useState(initialValue);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [updatedAt, setUpdatedAt] = useState(null);

  const load = useCallback(async (force = false) => {
    const currentRequest = ++requestId.current;
    const cached = getAdminCache(cacheKey);
    if (currentKey.current !== cacheKey) {
      currentKey.current = cacheKey;
      setError('');
      if (!cached) { setData(initialData.current); setUpdatedAt(null); }
    }
    if (!force && cached) {
      setData(cached.data);
      setUpdatedAt(cached.timestamp);
      setLoading(false);
      // Show cached data immediately, then revalidate against the shared API.
    }
    if (force) setRefreshing(true);
    else setLoading(!cached);
    try {
      const response = await loader();
      if (currentRequest !== requestId.current) return;
      const saved = setAdminCache(cacheKey, response);
      setData(response);
      setUpdatedAt(saved.timestamp);
      setError('');
    } catch (requestError) {
      if (currentRequest !== requestId.current) return;
      setError(requestError.response?.data?.error || requestError.message);
    } finally {
      if (currentRequest === requestId.current) {
        setLoading(false);
        setRefreshing(false);
      }
    }
  }, [cacheKey, loader]);

  useEffect(() => { load(); return () => { requestId.current += 1; }; }, [load]);
  const refresh = useCallback(() => load(true), [load]);
  usePageRevalidation(refresh);
  return { data, setData, loading, refreshing, error, updatedAt, reload: () => load(true) };
}
