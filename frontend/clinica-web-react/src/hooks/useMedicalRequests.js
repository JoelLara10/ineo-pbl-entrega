import { useEffect, useRef, useState } from 'react';
import api from '../services/api';
import { getClinicalCache, setClinicalCache } from '../services/clinicalCache';
const CacheService = { get: async key => getClinicalCache(key), set: async (key, value, ttl) => setClinicalCache(key, value, ttl) };
import { adminErrorMessage } from '../utils/medicalFeedback';

// Only the current screen may apply a response. Cache remains in memory.
export default function useMedicalRequests(context) {
  const active = useRef(context);
  const sequence = useRef({});
  const sources = useRef({});
  const visibleData = useRef({});
  const sending = useRef(false);
  const [connection, setConnection] = useState({ status: 'loading', message: '' });
  useEffect(() => {
    active.current = context;
    sources.current = {};
    visibleData.current = {};
    setConnection({ status: 'loading', message: '' });
    return () => { active.current = null; };
  }, [context]);
  const current = () => active.current === context;
  const update = (url, status, message = '') => {
    if (!current()) return;
    sources.current[url] = { status, message };
    const values = Object.values(sources.current);
    setConnection(values.find(value => value.status === 'error') ||
      values.find(value => value.status === 'cache') || { status: 'remote', message: '' });
  };
  const load = async (url, apply, shape = 'array') => {
    const generation = sequence.current[url] = (sequence.current[url] || 0) + 1;
    const fresh = () => current() && sequence.current[url] === generation;
    const valid = value => typeof shape === 'function' ? shape(value) : shape === 'array' ? Array.isArray(value) : value && typeof value === 'object' && !Array.isArray(value);
    try {
      const response = await api.get(url);
      if (!valid(response.data)) throw new Error('Invalid response');
      if (!fresh()) return;
      visibleData.current[url] = response.data;
      apply(response.data);
      await CacheService.set('medical_qa_' + url, response.data, 120000);
      if (!fresh()) return;
      update(url, 'remote');
    } catch (error) {
      if (!fresh()) return;
      const denied = [401, 403].includes(error?.response?.status);
      const cached = denied ? null : visibleData.current[url] ?? await CacheService.get('medical_qa_' + url);
      if (!fresh()) return;
      if (valid(cached)) {
        apply(cached);
        update(url, 'cache');
      } else {
        update(url, 'error', adminErrorMessage(error, 'No se pudo cargar la información. Revisa tu conexión y vuelve a intentar.'));
      }
    }
  };
  return { connection, load, current, sending };
}
