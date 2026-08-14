import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { FiDatabase, FiHardDrive, FiShield, FiTrendingUp, FiUsers, FiUser } from 'react-icons/fi';
import { MdLocalHospital } from 'react-icons/md';
import ConfigHeader from './ConfigHeader';
import './ConfigStyles.css';

const cards = [
  { title: 'bedManagement', desc: 'bedManagementDesc', icon: <MdLocalHospital size={36} />, color: '#3182ce', badge: 'admin', path: '/config/camas' },
  { title: 'staffManagement', desc: 'staffManagementDesc', icon: <FiUsers size={36} />, color: '#38a169', badge: 'admin', path: '/config/usuarios' },
  { title: 'diagnoses', desc: 'diagnosesDesc', icon: <FiTrendingUp size={36} />, color: '#ed8936', badge: 'medical', path: '/config/diagnosticos' },
  { title: 'services', desc: 'servicesDesc', icon: <FiDatabase size={36} />, color: '#f56565', badge: 'catalog', path: '/config/servicios' },
  { title: 'backups', desc: 'backupsDesc', icon: <FiShield size={36} />, color: '#805ad5', badge: 'admin', path: '/config/backup' },
  { title: 'automation', desc: 'automationDesc', icon: <FiHardDrive size={36} />, color: '#38b2ac', badge: 'monitoring', path: '/config/automatizacion' },
  { title: 'profile', desc: 'profileDesc', icon: <FiUser size={36} />, color: '#667eea', badge: 'perfil', path: '/config/perfil' },
];

export default function ConfigScreen() {
  const navigate = useNavigate();
  const { t } = useTranslation();

  return (
    <main className="config-page">
      <ConfigHeader title={t('config.title')} showBack={false} />
      <section className="config-content">
        <div className="config-cards-grid">
          {cards.map((item) => (
            <button
              key={item.path}
              type="button"
              className="config-card config-nav-card"
              onClick={() => navigate(item.path)}
            >
              <span className="config-nav-badge" style={{ background: item.color }}>{t(`config.${item.badge}`)}</span>
              <div className="config-nav-icon" style={{ background: item.color }}>{item.icon}</div>
              <h2 className="config-nav-title">{t(`config.${item.title}`)}</h2>
              <p className="config-nav-desc">{t(`config.${item.desc}`)}</p>
            </button>
          ))}
        </div>
      </section>
    </main>
  );
}
