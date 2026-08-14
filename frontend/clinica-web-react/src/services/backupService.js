import api from './api';

const backupService = {
  list: async () => (await api.get('/backup')).data,
  collections: async () => (await api.get('/backup/collections')).data,
  create: async (payload) => (await api.post('/backup/create', payload)).data,
  restore: async (filename) => (await api.post('/backup/restore', { filename })).data,
  remove: async (filename) => (await api.delete(`/backup/${encodeURIComponent(filename)}`)).data,
  clean: async (keep = 4) => (await api.post('/backup/clean', { keep })).data,
  health: async () => (await api.get('/backup/health')).data,
  getAutomation: async () => (await api.get('/backup/automation')).data,
  updateAutomation: async (payload) => (await api.put('/backup/automation', payload)).data,
  download: async (filename) => {
    const response = await api.get(`/backup/download/${encodeURIComponent(filename)}`, { responseType: 'blob' });
    const url = URL.createObjectURL(response.data);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
  },
};

export default backupService;
