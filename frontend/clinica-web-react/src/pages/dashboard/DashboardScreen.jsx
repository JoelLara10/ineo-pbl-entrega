import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';
import {
  FiUsers, FiActivity, FiLogOut, FiSettings, FiRefreshCw,
} from 'react-icons/fi';
import { MdOutlineBed } from 'react-icons/md';
import { GiMedicinePills, GiChemicalDrop } from 'react-icons/gi';
import moment from 'moment';
import 'moment/locale/es';
import 'moment/locale/en-gb';
import './DashboardScreen.css';

const iconMap = {
  'business-outline': FiSettings,
  'medkit-outline':   GiMedicinePills,
  'pulse-outline':    FiActivity,
  'flask-outline':    GiChemicalDrop,
  'settings-outline': FiSettings,
};

const Icon = ({ name, size = 36, color = '#667eea' }) => {
  const Component = iconMap[name] || FiActivity;
  return <Component size={size} color={color} />;
};

export default function DashboardScreen() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const [stats, setStats] = useState({
    active_patients: { total: 0 },
    bed_occupancy:   { occupied: 0 },
  });
  const [pendingStudies, setPendingStudies] = useState({ total: 0 });
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    moment.locale(i18n.language === 'en' ? 'en-gb' : 'es');
  }, [i18n.language]);

  useEffect(() => { loadDashboardData(); }, []);

  const loadDashboardData = async () => {
    try {
      const [statsRes, studiesRes] = await Promise.all([
        api.get('/analytics/dashboard').catch(() => ({ data: {} })),
        api.get('/exams/counts').catch(() => ({ data: { total: 0 } })),
      ]);
      setStats(statsRes.data);
      setPendingStudies(studiesRes.data);
    } catch (err) {
      console.error('Error loading dashboard:', err);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const getMenuOptions = () => {
    const role = user?.role?.toLowerCase();
    const studies = { name: t('dashboard.studiesModule'), icon: 'flask-outline', path: '../estudios/', color: '#ed8936', description: t('dashboard.studiesDesc'), badge: pendingStudies.total };

    if (role === 'admin' || role === 'administrativo') return [
      { name: t('dashboard.adminModule'), icon: 'business-outline', path: '/admin',      color: '#667eea', description: t('dashboard.adminDesc') },
      { name: t('dashboard.nursingModule'),     icon: 'medkit-outline',   path: '/enfermeria', color: '#f56565', description: t('dashboard.nursingDesc') },
      { name: t('dashboard.medicalModule'),         icon: 'pulse-outline',    path: '/medico',     color: '#48bb78', description: t('dashboard.medicalDesc') },
      { ...studies },
      { name: t('dashboard.configModule'),  icon: 'settings-outline', path: '/config',     color: '#718096', description: t('dashboard.configDesc') },
    ];
    if (role === 'enfermero' || role === 'enfermeria') return [
      { name: t('dashboard.nursingModule'), icon: 'medkit-outline', path: '/enfermeria', color: '#9f7aea', description: t('dashboard.nursingDescShort') },
    ];
    if (role === 'medico') return [
      { name: t('dashboard.medicalModule'),  icon: 'pulse-outline', path: '/medico',   color: '#48bb78', description: t('dashboard.medicalDescShort') },
      { ...studies, description: t('dashboard.studiesDescShort') },
    ];
    if (role === 'estudios') return [{ ...studies }];
    return [];
  };

  const menuOptions = getMenuOptions();

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="dash-header">
        <div className="dash-header-content">
          <div>
            <h2 className="dash-greeting">{t('dashboard.greeting', { name: user?.username || 'User' })}</h2>
            <p className="dash-date">{moment().format('dddd, D [de] MMMM [de] YYYY')}</p>
          </div>
          <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <button className="dash-icon-btn" onClick={onRefresh} title={t('dashboard.refresh')}>
              <FiRefreshCw size={22} color="#fff" className={refreshing ? 'spin' : ''} />
            </button>
            <button className="dash-icon-btn" onClick={logout} title={t('dashboard.logout')}>
              <FiLogOut size={22} color="#fff" />
            </button>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="stats-container">
        <div className="stat-card">
          <FiUsers size={32} color="#667eea" />
          <span className="stat-number">{stats.active_patients?.total || 0}</span>
          <span className="stat-label">{t('dashboard.activePatients')}</span>
        </div>
        <div className="stat-card">
          <MdOutlineBed size={32} color="#48bb78" />
          <span className="stat-number">{stats.bed_occupancy?.occupied || 0}</span>
          <span className="stat-label">{t('dashboard.occupiedBeds')}</span>
        </div>
        <div className="stat-card">
          <GiChemicalDrop size={32} color="#ed8936" />
          <span className="stat-number">{pendingStudies.total || 0}</span>
          <span className="stat-label">{t('dashboard.pendingStudies')}</span>
        </div>
      </div>

      {/* Menu */}
      <div className="menu-container">
        <h3 className="menu-title">{t('dashboard.systemModules')}</h3>
        <div className="menu-grid">
          {menuOptions.map((option, i) => (
            <button
              key={i}
              className="menu-card"
              onClick={() => navigate(option.path)}
            >
              {option.badge > 0 && (
                <span className="badge">{option.badge}</span>
              )}
              <div className="menu-icon-wrap" style={{ backgroundColor: `${option.color}20` }}>
                <Icon name={option.icon} size={36} color={option.color} />
              </div>
              <span className="menu-name">{option.name}</span>
              <span className="menu-desc">{option.description}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
