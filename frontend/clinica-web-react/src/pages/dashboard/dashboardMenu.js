export const getDashboardMenuOptions = (role, t, pendingStudiesTotal = 0) => {
  const normalizedRole = role?.toLowerCase();
  const administrative = {
    name: t('dashboard.adminModule'),
    icon: 'business-outline',
    path: '/admin',
    color: '#667eea',
    description: t('dashboard.adminDesc'),
  };
  const analysis = {
    name: t('dashboard.analysisModule'),
    icon: 'bar-chart-outline',
    path: '/admin/spark',
    color: '#0ea5e9',
    description: t('dashboard.analysisDesc'),
  };
  const studies = {
    name: t('dashboard.studiesModule'),
    icon: 'flask-outline',
    path: '../estudios/',
    color: '#ed8936',
    description: t('dashboard.studiesDesc'),
    badge: pendingStudiesTotal,
  };

  if (normalizedRole === 'admin') return [
    administrative,
    { name: t('dashboard.nursingModule'), icon: 'medkit-outline', path: '/enfermeria', color: '#f56565', description: t('dashboard.nursingDesc') },
    { name: t('dashboard.medicalModule'), icon: 'pulse-outline', path: '/medico', color: '#48bb78', description: t('dashboard.medicalDesc') },
    studies,
    { name: t('dashboard.configModule'), icon: 'settings-outline', path: '/config', color: '#718096', description: t('dashboard.configDesc') },
    analysis,
  ];
  if (normalizedRole === 'administrativo') return [administrative, analysis];
  if (normalizedRole === 'enfermero' || normalizedRole === 'enfermeria') return [
    { name: t('dashboard.nursingModule'), icon: 'medkit-outline', path: '/enfermeria', color: '#9f7aea', description: t('dashboard.nursingDescShort') },
  ];
  if (normalizedRole === 'medico') return [
    { name: t('dashboard.medicalModule'), icon: 'pulse-outline', path: '/medico', color: '#48bb78', description: t('dashboard.medicalDescShort') },
  ];
  if (normalizedRole === 'estudios') return [{ ...studies }];
  return [];
};
