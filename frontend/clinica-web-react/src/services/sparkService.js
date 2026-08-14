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
  run: async (type) => (await api.post(`/spark/run/${type}`)).data,
  getStatus: async (type) => (await api.get(`/spark/status/${type}`)).data,
  getImage: async (path) => {
    const response = await api.get(path, { responseType: 'blob' });
    return URL.createObjectURL(response.data);
  },
};
