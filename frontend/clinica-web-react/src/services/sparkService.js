import api from './api';

const resultPaths = {
  analytics: '/spark/analytics',
  met: '/spark/met',
  clinical: '/spark/clinical',
  unsupervised: '/spark/unsupervised',
};

const RUNNING_STATES = new Set(['pending', 'queued', 'starting', 'processing', 'running']);
const COMPLETED_STATES = new Set(['completed', 'complete', 'success', 'succeeded', 'finished']);
const FAILED_STATES = new Set(['failed', 'error', 'cancelled', 'canceled']);

export const normalizeSparkStatus = (payload = {}) => {
  const source = payload?.status && typeof payload.status === 'object'
    ? payload.status
    : payload;
  const rawState = typeof source === 'string'
    ? source
    : source?.state ?? source?.status ?? source?.phase ?? 'idle';
  const normalized = String(rawState).toLowerCase();

  let state = normalized;
  if (RUNNING_STATES.has(normalized)) state = normalized === 'pending' ? 'pending' : 'processing';
  else if (COMPLETED_STATES.has(normalized)) state = 'completed';
  else if (FAILED_STATES.has(normalized)) state = 'failed';
  else if (!normalized || normalized === 'idle' || normalized === 'not_started') state = 'idle';

  return {
    ...(typeof source === 'object' && source !== null ? source : {}),
    state,
    running: typeof source?.running === 'boolean'
      ? source.running
      : state === 'pending' || state === 'processing',
    log: source?.log ?? source?.message ?? '',
  };
};

export const sparkService = {
  getOverview: async () => (await api.get('/spark/overview')).data,
  getResults: async (type) => (await api.get(resultPaths[type])).data,
  run: async (type) => normalizeSparkStatus((await api.post(`/spark/run/${type}`)).data),
  getStatus: async (type) => normalizeSparkStatus((await api.get(`/spark/status/${type}`)).data),
  getImage: async (path) => {
    const response = await api.get(path, { responseType: 'blob' });
    return URL.createObjectURL(response.data);
  },
};
