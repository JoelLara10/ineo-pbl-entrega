const PREFIX = '@ineo_admin_cache:';

export const getAdminCache = (key, maxAge = 300000) => {
  try {
    const value = JSON.parse(localStorage.getItem(`${PREFIX}${key}`));
    if (!value?.timestamp || value.data === undefined) return null;
    return {
      ...value,
      isFresh: Date.now() - value.timestamp < maxAge,
    };
  } catch {
    return null;
  }
};

export const setAdminCache = (key, data) => {
  const value = { data, timestamp: Date.now() };
  try {
    localStorage.setItem(`${PREFIX}${key}`, JSON.stringify(value));
  } catch {
    // La aplicación sigue funcionando aunque el navegador no permita almacenamiento.
  }
  return value;
};

export const clearAdminCache = () => {
  Object.keys(localStorage)
    .filter((key) => key.startsWith(PREFIX))
    .forEach((key) => localStorage.removeItem(key));
};
