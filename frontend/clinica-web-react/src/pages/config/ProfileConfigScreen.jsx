import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import ConfigHeader from './ConfigHeader';
import './ConfigStyles.css';

export default function ProfileConfigScreen() {
  const { user } = useAuth();
  const { t } = useTranslation();
  const unavailable = t('config.profileNoData');
  return <main className="config-page">
    <ConfigHeader title={t('config.headerProfile')} />
    <section className="config-content">
      <div className="config-card config-profile">
        <div className="config-avatar">{user?.username?.charAt(0)?.toUpperCase() || 'U'}</div>
        <div><h2>{user?.nombre || user?.username || t('config.profileUser')}</h2><span className="config-badge">{user?.role || unavailable}</span><p className="config-cache">{t('config.profileAuthenticated')}</p></div>
      </div>
      <div className="config-card"><h3>{t('config.profileData')}</h3><p><b>{t('config.profileUser')}:</b> {user?.username || unavailable}</p><p><b>{t('config.profileRole')}:</b> {user?.role || unavailable}</p><p><b>{t('config.profileEmail')}:</b> {user?.email || unavailable}</p><p><b>{t('config.profilePhone')}:</b> {user?.telefono || unavailable}</p></div>
    </section>
  </main>;
}
