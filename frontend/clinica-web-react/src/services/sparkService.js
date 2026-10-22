import api from './api';

const resultPaths = {
  analytics: '/spark/analytics',
  met: '/spark/met',
  clinical: '/spark/clinical',
  unsupervised: '/spark/unsupervised',
};

export const sparkService = {
  getOverview: async () => (await api.get('/spark/overview')).data,
  getResults: async (type) => (await api.get(resultPaths[type])).data,
  run: async (type, filters) => (filters ? await api.post(`/spark/run/${type}`, filters) : await api.post(`/spark/run/${type}`)).data,
  getOptions: async () => (await api.get('/spark/options')).data,
  getReview: async (type, timestamp) => (await api.get(`/spark/reviews/${type}`, { params: { result_timestamp: timestamp } })).data,
  saveReview: async (type, review) => (await api.post(`/spark/reviews/${type}`, review)).data,
  getStatus: async (type) => (await api.get(`/spark/status/${type}`)).data,
  getImage: async (path) => {
    const response = await api.get(path, { responseType: 'blob' });
    return URL.createObjectURL(response.data);
  },
};
