import { useCallback, useEffect, useState } from 'react';
import { getAdminCache, setAdminCache } from '../../services/adminCache';

export default function useAdminData(cacheKey, loader, initialValue) {
  const [data, setData] = useState(initialValue);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [updatedAt, setUpdatedAt] = useState(null);

  const load = useCallback(async (force = false) => {
    const cached = getAdminCache(cacheKey);
    if (!force && cached) {
      setData(cached.data);
      setUpdatedAt(cached.timestamp);
      setLoading(false);
      if (cached.isFresh) return;
    }
    if (force) setRefreshing(true);
    else setLoading(!cached);
    try {
      const response = await loader();
      const saved = setAdminCache(cacheKey, response);
      setData(response);
      setUpdatedAt(saved.timestamp);
      setError('');
    } catch (requestError) {
      setError(requestError.response?.data?.error || requestError.message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [cacheKey, loader]);

  useEffect(() => { load(); }, [load]);
  return { data, setData, loading, refreshing, error, updatedAt, reload: () => load(true) };
}
