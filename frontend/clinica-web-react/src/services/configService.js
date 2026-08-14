const STORAGE_KEY = 'ineo_config_module';

const defaultData = {
  camas: [
    { id: 'C-101', nombre: 'Cama 101', area: 'Hospitalización', estado: 'Disponible', tipo: 'General' },
    { id: 'C-102', nombre: 'Cama 102', area: 'Urgencias', estado: 'Ocupada', tipo: 'Observación' },
  ],

  servicios: [
    { id: 'S-001', clave: 'CONS-GEN', descripcion: 'Consulta general', costo: '500', tipo: 'Consulta', unidad: 'Servicio' },
    { id: 'S-002', clave: 'LAB-BAS', descripcion: 'Laboratorio básico', costo: '350', tipo: 'Laboratorio', unidad: 'Estudio' },
  ],

  usuarios: [
    { id: 'U-001', nombre: 'Administrador', usuario: 'admin', rol: 'admin', activo: true },
    { id: 'U-002', nombre: 'Médico General', usuario: 'medico', rol: 'medico', activo: true },
  ],

  automatizacion: {
    respaldosAutomaticos: true,
    horaRespaldo: '22:00',
    limpiarTemporales: true,
    diasRetencion: '30',
  },

  general: {
    nombreClinica: 'INEO Hospital',
    telefono: '722 000 0000',
    direccion: 'Toluca, México',
    moneda: 'MXN',
    tema: 'Morado',
    apiHost: '192.168.1.4',
    apiPort: '5001',
    apiPath: '/api/v1',
  },

  respaldos: [
    {
      id: 'B-001',
      nombre: 'respaldo_inicial.json',
      fecha: new Date().toISOString(),
      tipo: 'Manual',
    },
  ],
};

function readAll() {
  const raw = localStorage.getItem(STORAGE_KEY);

  if (!raw) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(defaultData));
    return defaultData;
  }

  return {
    ...defaultData,
    ...JSON.parse(raw),
  };
}

function saveAll(data) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

export async function getConfigSection(section) {
  const data = readAll();
  return data[section];
}

export async function saveConfigSection(section, value) {
  const data = readAll();
  data[section] = value;
  saveAll(data);
  return value;
}

export async function addConfigItem(section, item) {
  const data = readAll();

  const list = Array.isArray(data[section]) ? data[section] : [];

  data[section] = [
    {
      ...item,
      id: item.id || Date.now().toString(),
    },
    ...list,
  ];

  saveAll(data);

  return data[section];
}

export async function updateConfigItem(section, id, changes) {
  const data = readAll();

  data[section] = (data[section] || []).map((item) =>
    item.id === id ? { ...item, ...changes } : item
  );

  saveAll(data);

  return data[section];
}

export async function deleteConfigItem(section, id) {
  const data = readAll();

  data[section] = (data[section] || []).filter((item) => item.id !== id);

  saveAll(data);

  return data[section];
}

export async function createBackup() {
  const data = readAll();

  const backup = {
    id: `B-${Date.now()}`,
    nombre: `respaldo_${new Date().toISOString().slice(0, 10)}.json`,
    fecha: new Date().toISOString(),
    tipo: 'Manual',
  };

  data.respaldos = [backup, ...(data.respaldos || [])];

  saveAll(data);

  return data.respaldos;
}

export async function resetConfigData() {
  saveAll(defaultData);
  return defaultData;
}

export function getConfigCacheInfo() {
  const data = readAll();

  return {
    updatedAt: new Date().toISOString(),
    size: JSON.stringify(data).length,
  };
}

export async function clearConfigCache() {
  localStorage.removeItem(STORAGE_KEY);
}

export async function restoreDefaultConfig() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(defaultData));
  return defaultData;
}

export async function exportConfig() {
  return readAll();
}

export async function importConfig(data) {
  saveAll(data);
  return data;
}