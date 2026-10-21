import { useCallback, useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { OfflinePreferencesContext } from '../context/OfflinePreferencesContext';
import { clearClinicalCache } from '../services/clinicalCache';
import { clearOfflineQueue, flushLanguage, queueLanguage, readOfflineQueue } from '../services/offlineQueue';

export default function OfflineBoundary({ children }) {
  const { user, logout } = useAuth();
  const { t, i18n } = useTranslation();
  const [online, setOnline] = useState(navigator.onLine !== false);
  const [pending, setPending] = useState(false);
  const [failed, setFailed] = useState(false);
  const owner = user?.id || user?.username;
  const currentOwner = useRef(owner);
  currentOwner.current = owner;
  const sync = useCallback(async () => {
    if (!owner) return;
    setFailed(false);
    try {
      await flushLanguage(owner, (data) => api.put('/auth/preferences', data, { preferenceOwner: owner }), () => currentOwner.current === owner);
    } catch { setFailed(true); }
    setPending(!!readOfflineQueue(owner));
  }, [owner]);
  useEffect(() => {
    const connect = () => { setOnline(true); sync(); };
    const disconnect = () => { clearClinicalCache(); setOnline(false); };
    window.addEventListener('online', connect);
    window.addEventListener('offline', disconnect);
    if (owner) { setPending(!!readOfflineQueue(owner)); sync(); } else clearOfflineQueue();
    return () => { window.removeEventListener('online', connect); window.removeEventListener('offline', disconnect); };
  }, [owner, sync]);
  const changeLanguage = async (language) => {
    await i18n.changeLanguage(language);
    if (owner) { queueLanguage(owner, language); setPending(true); sync(); }
  };
  return <OfflinePreferencesContext.Provider value={{ changeLanguage }}>
    {(!online || (owner && failed)) && <aside className="offline-toolbar" aria-label={t('offline.preferences')}>
      <span role="status">{!online ? t('offline.disconnected') : failed ? t('offline.failed') : pending ? t('offline.pending') : t('offline.online')}</span>
      {online && pending && <button onClick={sync}>{t('offline.retry')}</button>}
    </aside>}
    {!online ? <main className="offline-shell">
      <label>{t('offline.language')} <select value={i18n.resolvedLanguage || 'es'} onChange={(event) => changeLanguage(event.target.value)}>
        <option value="es">Español</option><option value="en">English</option>
      </select></label>
      <h1>{t('offline.title')}</h1><p>{t('offline.hint')}</p>
      <p>{t('offline.safeAction')}</p>
      {user && <button onClick={logout}>{t('offline.logout')}</button>}
    </main> : children}
  </OfflinePreferencesContext.Provider>;
}
