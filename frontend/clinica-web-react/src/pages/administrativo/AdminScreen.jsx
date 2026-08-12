import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { FiUsers, FiUserPlus, FiFileText, FiBarChart2, FiDollarSign } from 'react-icons/fi';
import { MdOutlineBed } from 'react-icons/md';
import AdminLayout from './AdminLayout';

export default function AdminScreen() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const items = [
    ['patients', '/pacientes', FiUsers, '#667eea'],
    ['newPatient', '/nuevo-paciente', FiUserPlus, '#48bb78'],
    ['patientAccount', '/cuenta-paciente', FiFileText, '#ed8936'],
    ['census', '/censo', FiBarChart2, '#38b2ac'],
    ['cashCut', '/corte-caja', FiDollarSign, '#d69e2e'],
    ['beds', '/config/camas', MdOutlineBed, '#9f7aea'],
  ];
  return (
    <AdminLayout title={t('administrative.title')} subtitle={t('administrative.subtitle')}>
      <div className="adm-grid">
        {items.map(([key, path, Icon, color]) => (
          <button className="adm-card adm-module" key={key} onClick={() => navigate(path)}>
            <span className="adm-module-icon" style={{ color, background: `${color}18` }}><Icon /></span>
            <h3>{t(`administrative.${key}`)}</h3>
            <p>{t('administrative.openModule')}</p>
          </button>
        ))}
      </div>
    </AdminLayout>
  );
}
