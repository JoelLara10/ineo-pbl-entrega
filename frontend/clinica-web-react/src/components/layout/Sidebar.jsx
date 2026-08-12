import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../../context/AuthContext';
import { usePatient } from '../../context/PatientContext';
import {
  FiHome, FiSettings, FiLogOut, FiUser, FiHeart, FiFileText,
  FiClipboard, FiActivity, FiPrinter, FiMonitor, FiBarChart2,
} from 'react-icons/fi';
import { MdLocalHospital } from 'react-icons/md';
import './Sidebar.css';

const iconMap = {
  'home-outline': FiHome,
  'speedometer-outline': FiActivity,
  'medkit-outline': FiHeart,
  'flask-outline': FiActivity,
  'document-text-outline': FiFileText,
  'heart-outline': FiHeart,
  'clipboard-outline': FiClipboard,
  'scan-outline': FiMonitor,
  'print-outline': FiPrinter,
  'settings-outline': FiSettings,
  'options-outline': FiSettings,
  'pulse-outline': FiActivity,
  'folder-open-outline': FiFileText,
  'bar-chart-outline': FiBarChart2,
};

const Icon = ({ name, size = 20, color = '#718096' }) => {
  const Component = iconMap[name] || FiHome;
  return <Component size={size} color={color} />;
};

const roleLabels = {
  admin: 'ADMIN', administrativo: 'ADMINISTRATIVO',
  medico: 'MÉDICO', enfermero: 'ENFERMERÍA',
  enfermeria: 'ENFERMERÍA', estudios: 'ESTUDIOS',
};

const roleLabelsEn = {
  admin: 'ADMIN', administrativo: 'ADMINISTRATIVE',
  medico: 'MEDICAL', enfermero: 'NURSING',
  enfermeria: 'NURSING', estudios: 'STUDIES',
};

export default function Sidebar({ isOpen, onClose }) {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  const { selectedPatient } = usePatient();

  const role = user?.role;
  const isAdmin      = role === 'admin';
  const isMedico     = role === 'medico';
  const isEnfermeria = role === 'enfermero' || role === 'enfermeria';
  const isEstudios   = role === 'estudios';
  const isPatientSelected = !!selectedPatient?.id_atencion;

  const currentPath = location.pathname;
  const currentModule = currentPath.startsWith('/admin/spark') ? 'spark'
    : currentPath.startsWith('/enfermeria') ? 'enfermeria'
    : currentPath.startsWith('/medico') ? 'medico'
    : currentPath.startsWith('/estudios') ? 'estudios'
    : currentPath.startsWith('/config') ? 'config'
    : ['/admin', '/pacientes', '/nuevo-paciente', '/cuenta-paciente', '/censo', '/corte-caja'].some((path) => currentPath.startsWith(path)) ? 'administrativo'
    : 'general';

  const handleNav = (path) => {
    const patientState = selectedPatient?.id_atencion
      ? {
          id_atencion: selectedPatient.id_atencion,
          Id_exp: selectedPatient?.Id_exp,
        }
      : undefined;

    navigate(path, { state: patientState });
    onClose?.();
  };

  const handleLogout = () => {
    if (window.confirm(t('sidebar.confirmLogout'))) logout();
  };

  const rl = i18n.language === 'en' ? roleLabelsEn : roleLabels;

  const menuSections = [];

  const principalItems = [
    { name: t('sidebar.dashboard'), icon: 'home-outline', path: '/', requiresPatient: false },
  ];

  if (isMedico || (isAdmin && currentModule === 'medico'))
    principalItems.push({ name: t('sidebar.medicalPanel'), icon: 'speedometer-outline', path: '/medico', requiresPatient: false });

  if (isEnfermeria || (isAdmin && currentModule === 'enfermeria'))
    principalItems.push({ name: t('sidebar.nursingPanel'), icon: 'medkit-outline', path: '/enfermeria', requiresPatient: false });

  if (isEstudios || (isAdmin && currentModule === 'estudios'))
    principalItems.push({ name: t('sidebar.studiesPanel'), icon: 'flask-outline', path: '/estudios', requiresPatient: false });

  menuSections.push({ title: t('sidebar.principal'), items: principalItems });

  if ((isAdmin || role === 'administrativo') && currentModule === 'spark') {
    menuSections.push({
      title: t('sidebar.sparkSection'),
      items: [
        { name: t('spark.types.analytics.title'), icon: 'bar-chart-outline', path: '/admin/spark/analytics', requiresPatient: false },
        { name: t('spark.types.met.title'), icon: 'speedometer-outline', path: '/admin/spark/met', requiresPatient: false },
        { name: t('spark.types.clinical.title'), icon: 'pulse-outline', path: '/admin/spark/clinical', requiresPatient: false },
        { name: t('spark.types.unsupervised.title'), icon: 'flask-outline', path: '/admin/spark/unsupervised', requiresPatient: false },
      ],
    });
  }

  if (isMedico || (isAdmin && currentModule === 'medico')) {
    menuSections.push({
      title: t('sidebar.clinicalHistory'),
      items: [{ name: t('sidebar.clinicalHistoryItem'), icon: 'document-text-outline', path: '/medico/historia-clinica', requiresPatient: true }],
    });
    menuSections.push({
      title: t('sidebar.medicalNotes'),
      items: [
        { name: t('sidebar.vitalSigns'),           icon: 'heart-outline',         path: '/medico/signos-vitales',   requiresPatient: true },
        { name: t('sidebar.medicalNote'),        icon: 'document-text-outline', path: '/medico/nota-medica',      requiresPatient: true },
        { name: t('sidebar.diagnosis'),              icon: 'clipboard-outline',     path: '/medico/diagnostico',      requiresPatient: true },
        { name: t('sidebar.prescription'),                   icon: 'medkit-outline',        path: '/medico/receta',           requiresPatient: true },
        { name: t('sidebar.labExams'),  icon: 'flask-outline',         path: '/medico/lab-exams',        requiresPatient: true },
        { name: t('sidebar.imagingExams'),     icon: 'scan-outline',          path: '/medico/imaging-exams',    requiresPatient: true },
      ],
    });
    menuSections.push({
      title: t('sidebar.documents'),
      items: [
        { name: t('sidebar.printDocs'),    icon: 'print-outline',         path: '/medico/imprimir',   requiresPatient: true },
        { name: t('sidebar.studyResults'), icon: 'document-text-outline', path: '/medico/resultados', requiresPatient: true },
      ],
    });
  }

  if (isEnfermeria || (isAdmin && currentModule === 'enfermeria')) {
    menuSections.push({
      title: t('sidebar.nursingNotes'),
      items: [
        { name: t('sidebar.vitalSigns'),              icon: 'heart-outline',         path: '/enfermeria/signos-vitales', requiresPatient: true },
        { name: t('sidebar.nursingNote'),          icon: 'document-text-outline', path: '/enfermeria/nota',           requiresPatient: true },
        { name: t('sidebar.medicationAdmin'), icon: 'medkit-outline',        path: '/enfermeria/medicamentos',   requiresPatient: true },
        { name: t('sidebar.nursingAssessment'),    icon: 'clipboard-outline',     path: '/enfermeria/valoracion',     requiresPatient: true },
        { name: t('sidebar.fluidBalance'),             icon: 'water-outline',         path: '/enfermeria/balance-hidrico', requiresPatient: true },
        { name: t('sidebar.nursingCare'),      icon: 'shield-checkmark-outline', path: '/enfermeria/cuidados',     requiresPatient: true },
      ],
    });
  }

  if (isAdmin && currentModule === 'config') {
    menuSections.push({
      title: t('sidebar.configSection'),
      items: [
        { name: t('sidebar.configUsers'),      icon: 'options-outline',     path: '/config/usuarios',       requiresPatient: false },
        { name: t('sidebar.configDiagnoses'),  icon: 'clipboard-outline',   path: '/config/diagnosticos',   requiresPatient: false },
        { name: t('sidebar.configBeds'),       icon: 'medkit-outline',      path: '/config/camas',          requiresPatient: false },
        { name: t('sidebar.configServices'),   icon: 'clipboard-outline',   path: '/config/servicios',      requiresPatient: false },
        { name: t('sidebar.configAutomation'), icon: 'pulse-outline',       path: '/config/automatizacion', requiresPatient: false },
        { name: t('sidebar.configBackup'),     icon: 'folder-open-outline', path: '/config/backup',         requiresPatient: false },
        { name: t('sidebar.configProfile'),    icon: 'home-outline',        path: '/config/perfil',         requiresPatient: false },
      ],
    });
  }

  if ((isAdmin || role === 'administrativo') && currentModule === 'administrativo') {
    menuSections.push({
      title: t('sidebar.administration'),
      items: [
        { name: t('administrative.patients'), icon: 'folder-open-outline', path: '/pacientes', requiresPatient: false },
        { name: t('administrative.newPatient'), icon: 'options-outline', path: '/nuevo-paciente', requiresPatient: false },
        { name: t('administrative.patientAccount'), icon: 'document-text-outline', path: '/cuenta-paciente', requiresPatient: false },
        { name: t('administrative.census'), icon: 'pulse-outline', path: '/censo', requiresPatient: false },
        { name: t('administrative.cashCut'), icon: 'clipboard-outline', path: '/corte-caja', requiresPatient: false },
      ],
    });
  }

  if ((isEstudios || isAdmin) && currentModule === 'estudios') {
    menuSections.push({
      title: t('sidebar.studies'),
      items: [
        { name: t('sidebar.labRequests'),      icon: 'flask-outline',         path: '/estudios?section=solicitudes_lab', requiresPatient: false },
        { name: t('sidebar.imagingRequests'), icon: 'scan-outline',          path: '/estudios?section=solicitudes_gab', requiresPatient: false },
        { name: t('sidebar.labResults'),       icon: 'document-text-outline', path: '/estudios?section=resultados_lab',  requiresPatient: false },
        { name: t('sidebar.imagingResults'),  icon: 'folder-open-outline',   path: '/estudios?section=resultados_gab',  requiresPatient: false },
      ],
    });
  }

  const moduleItems = [];
  if (isAdmin || role === 'administrativo')
    moduleItems.push({ name: t('sidebar.administration'), icon: 'settings-outline', path: '/admin',       requiresPatient: false });
  if (isAdmin || role === 'administrativo')
    moduleItems.push({ name: t('sidebar.spark'), icon: 'bar-chart-outline', path: '/admin/spark', requiresPatient: false });
  if (isAdmin || isMedico)
    moduleItems.push({ name: t('sidebar.medical'),         icon: 'pulse-outline',    path: '/medico',      requiresPatient: false });
  if (isAdmin || isEnfermeria)
    moduleItems.push({ name: t('sidebar.nursing'),     icon: 'medkit-outline',   path: '/enfermeria',  requiresPatient: false });
  if (isAdmin || isEstudios)
    moduleItems.push({ name: t('sidebar.studies').charAt(0) + t('sidebar.studies').slice(1).toLowerCase(),       icon: 'flask-outline',    path: '/estudios',    requiresPatient: false });
  if (isAdmin)
    moduleItems.push({ name: t('sidebar.config'),  icon: 'options-outline',  path: '/config',      requiresPatient: false });

  if (moduleItems.length) menuSections.push({ title: t('sidebar.modules'), items: moduleItems });

  const userPrefix = isEnfermeria ? 'Enf.' : 'Dr.';
  const roleLabel = rl[role] || 'USER';

  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
      {/* Header */}
      <div className="sidebar-header">
        <div className="brand-row">
          <span className="brand-title">INEO</span>
          <span className="brand-version">v2.0</span>
        </div>
        <div className="user-info">
          <div className="user-avatar"><FiUser size={28} color="#fff" /></div>
          <div>
            <p className="user-name">{userPrefix} {user?.username}</p>
            <span className="role-badge">{roleLabel}</span>
          </div>
        </div>
      </div>

      {/* Menu */}
      <nav className="sidebar-nav">
        {menuSections.map((section, si) => (
          <div key={si} className="nav-section">
            <p className="section-title">{section.title}</p>
            {section.items.map((item, ii) => {
              const enabled = !item.requiresPatient || isPatientSelected;
              const active  = currentPath === item.path || currentPath.startsWith(item.path + '/');
              return (
                <button
                  key={ii}
                  className={`nav-item ${active ? 'active' : ''} ${!enabled ? 'disabled' : ''}`}
                  onClick={() => {
                    if (enabled) handleNav(item.path);
                    else alert(t('sidebar.selectPatientFirst'));
                  }}
                >
                  <Icon name={item.icon} color={!enabled ? '#a0aec0' : active ? '#667eea' : '#718096'} />
                  <span>{item.name}</span>
                </button>
              );
            })}
          </div>
        ))}
      </nav>

      {/* Logout */}
      <button className="logout-btn" onClick={handleLogout}>
        <FiLogOut size={20} color="#e53e3e" />
        <span>{t('sidebar.logout')}</span>
      </button>
    </aside>
  );
}
