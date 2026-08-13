import { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import {
  FiActivity,
  FiAlertCircle,
  FiArrowLeft,
  FiDroplet,
  FiFileText,
  FiHeart,
  FiPhone,
  FiShield,
  FiUser,
  FiUsers,
} from 'react-icons/fi';
import { MdLocalHospital, MdMedication } from 'react-icons/md';
import { usePatient } from '../../context/PatientContext';
import api from '../../services/api';
import moment from 'moment';
import 'moment/locale/es';
import { useTranslation } from 'react-i18next';

moment.locale('es');

const CACHE_PREFIX = 'ineo_web_cache_patient_detail_';
const CACHE_TTL = 2 * 60 * 1000;

function getCachedValue(key) {
  if (typeof window === 'undefined') return null;

  try {
    const raw = window.localStorage.getItem(CACHE_PREFIX + key);
    if (!raw) return null;

    const parsed = JSON.parse(raw);
    if (Date.now() - parsed.timestamp > parsed.ttl) {
      window.localStorage.removeItem(CACHE_PREFIX + key);
      return null;
    }

    return parsed.data;
  } catch (error) {
    console.error('Error reading patient cache:', error);
    return null;
  }
}

function setCachedValue(key, data, ttl = CACHE_TTL) {
  if (typeof window === 'undefined') return;

  try {
    window.localStorage.setItem(
      CACHE_PREFIX + key,
      JSON.stringify({ data, timestamp: Date.now(), ttl })
    );
  } catch (error) {
    console.error('Error saving patient cache:', error);
  }
}

function calculateAge(fecnac) {
  if (!fecnac) return 'N/A';

  const birthDate = new Date(fecnac);
  const today = new Date();
  let age = today.getFullYear() - birthDate.getFullYear();
  const monthDiff = today.getMonth() - birthDate.getMonth();

  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age -= 1;
  }

  return age;
}

export default function PatientDetailScreen() {
  const { t, i18n } = useTranslation();
  moment.locale(i18n.language === 'en' ? 'en' : 'es');
  const navigate = useNavigate();
  const location = useLocation();
  const { id, idAtencion, idExp } = useParams();
  const { selectedPatient, selectPatient, setSelectedPatient } = usePatient();
  const routeIdExp = idExp || id || selectedPatient?.Id_exp || location.state?.Id_exp;
  const routeIdAtencion = idAtencion || selectedPatient?.id_atencion || location.state?.id_atencion;
  const [patient, setPatient] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    if (!routeIdExp || !routeIdAtencion) {
      setErrorMessage(t('nursingDetail.errorNotFound'));
      setLoading(false);
      return;
    }

    setErrorMessage('');
    selectPatient?.({ id_atencion: routeIdAtencion, Id_exp: routeIdExp });
    if (!selectPatient) {
      setSelectedPatient({ id_atencion: routeIdAtencion, Id_exp: routeIdExp });
    }

    setLoading(true);
  }, [routeIdAtencion, routeIdExp, selectPatient, setSelectedPatient]);

  useEffect(() => {
    if (!routeIdExp || !routeIdAtencion) {
      return;
    }

    let isCancelled = false;

    const loadPatientData = async () => {
      const cacheKey = `${routeIdAtencion}_${routeIdExp}`;
      const cachedData = getCachedValue(cacheKey);

      if (cachedData) {
        if (!isCancelled) {
          setPatient(cachedData);
          setLoading(false);
        }
        return;
      }

      try {
        const response = await api.get(`/paciente/${routeIdAtencion}/${routeIdExp}`);
        setCachedValue(cacheKey, response.data);
        if (!isCancelled) {
          setPatient(response.data);
        }
      } catch (error) {
        console.error('Error loading nursing patient detail:', error);
        if (!isCancelled) {
          setErrorMessage(t('nursingDetail.errorLoading'));
        }
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    };

    loadPatientData();

    return () => {
      isCancelled = true;
    };
  }, [routeIdAtencion, routeIdExp]);

  const patientData = patient?.paciente || {};
  const familiarData = patient?.familiar || {};
  const medicosData = patient?.medicos || [];
  const camaData = patient?.cama || { num_cama: 'Sin asignar', tipo: '' };

  const patientName = useMemo(() => {
    return [patientData.papell, patientData.sapell, patientData.nom_pac]
      .filter(Boolean)
      .join(' ') || 'Paciente';
  }, [patientData]);

  const modules = [
    {
      title: t('nursingDetail.vitalSigns'),
      subtitle: t('nursingDetail.vitalSignsSub'),
      icon: FiHeart,
      color: '#dc2626',
      background: '#fef2f2',
      path: '/enfermeria/signos-vitales',
    },
    {
      title: t('nursingDetail.nursingNote'),
      subtitle: t('nursingDetail.nursingNoteSub'),
      icon: FiFileText,
      color: '#2563eb',
      background: '#eff6ff',
      path: '/enfermeria/nota',
    },
    {
      title: t('nursingDetail.medications'),
      subtitle: t('nursingDetail.medicationsSub'),
      icon: MdMedication,
      color: '#16a34a',
      background: '#f0fdf4',
      path: '/enfermeria/medicamentos',
    },
    {
      title: t('nursingDetail.nursingAssessment'),
      subtitle: t('nursingDetail.nursingAssessmentSub'),
      icon: FiActivity,
      color: '#7c3aed',
      background: '#f5f3ff',
      path: '/enfermeria/valoracion',
    },
    {
      title: t('nursingDetail.fluidBalance'),
      subtitle: t('nursingDetail.fluidBalanceSub'),
      icon: FiDroplet,
      color: '#0284c7',
      background: '#f0f9ff',
      path: '/enfermeria/balance-hidrico',
    },
    {
      title: t('nursingDetail.nursingCare'),
      subtitle: t('nursingDetail.nursingCareSub'),
      icon: FiShield,
      color: '#ea580c',
      background: '#fff7ed',
      path: '/enfermeria/cuidados',
    },
  ];

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <button type="button" onClick={() => navigate(-1)} style={styles.headerButton}>
          <FiArrowLeft size={20} />
        </button>
        <div>
          <div style={styles.headerEyebrow}>{t('nursingDetail.eyebrow')}</div>
          <h1 style={styles.headerTitle}>{t('nursingDetail.title')}</h1>
        </div>
        <div style={styles.headerSpacer} />
      </div>

      {loading ? (
        <div style={styles.loadingCard}>{t('nursingDetail.loading')}</div>
      ) : errorMessage ? (
        <div style={styles.errorCard}>{errorMessage}</div>
      ) : (
        <>
          <section style={styles.mainCard}>
            <div style={styles.patientHeader}>
              <div style={styles.avatar}>
                <FiUser size={36} color="#fff" />
              </div>
              <div style={styles.patientInfo}>
                <h2 style={styles.patientName}>{patientName}</h2>
                <span style={styles.expBadge}>{t('nursingDetail.record') + ' '}{patientData.Id_exp || routeIdExp}</span>
              </div>
            </div>

            <div style={styles.infoGrid}>
              <div style={styles.infoItem}>
                <span style={styles.infoLabel}>{t('nursingDetail.age')}</span>
                <strong style={styles.infoValue}>{calculateAge(patientData.fecnac)} {t('nursingDetail.years')}</strong>
              </div>
              <div style={styles.infoItem}>
                <span style={styles.infoLabel}>{t('nursingDetail.admissionDate')}</span>
                <strong style={styles.infoValue}>
                  {patientData.fecha ? moment(patientData.fecha).format('DD/MM/YYYY') : 'N/A'}
                </strong>
              </div>
              <div style={styles.infoItem}>
                <span style={styles.infoLabel}>{t('nursingDetail.bed')}</span>
                <strong style={styles.infoValue}>{camaData.num_cama} - {camaData.tipo || 'N/A'}</strong>
              </div>
              <div style={styles.infoItem}>
                <span style={styles.infoLabel}>{t('nursingDetail.diagnosisLabel')}</span>
                <strong style={styles.infoValue}>{patientData.motivo_atn || t('nursingDetail.pending')}</strong>
              </div>
            </div>

            {patientData.alergias ? (
              <div style={styles.warningBox}>
                <div style={styles.boxTitleRow}>
                  <FiAlertCircle size={16} color="#dc2626" />
                  <strong style={{ color: '#dc2626' }}>{t('nursingDetail.allergies')}</strong>
                </div>
                <p style={styles.boxText}>{patientData.alergias}</p>
              </div>
            ) : null}

            {medicosData.length > 0 ? (
              <div style={styles.infoBoxBlue}>
                <div style={styles.boxTitleRow}>
                  <MdLocalHospital size={16} color="#2563eb" />
                  <strong style={{ color: '#2563eb' }}>{t('nursingDetail.treatingDoctors')}</strong>
                </div>
                <div style={styles.listWrap}>
                  {medicosData.map((med, index) => (
                    <span key={`${med.doctor || 'medico'}-${index}`} style={styles.listItem}>• {med.doctor || t('nursingDetail.noName')}</span>
                  ))}
                </div>
              </div>
            ) : null}

            {familiarData?.nombre ? (
              <div style={styles.infoBoxGreen}>
                <div style={styles.boxTitleRow}>
                  <FiUsers size={16} color="#16a34a" />
                  <strong style={{ color: '#16a34a' }}>{t('nursingDetail.responsibleFamily')}</strong>
                </div>
                <p style={styles.boxText}>
                  {familiarData.nombre} ({familiarData.parentesco || t('nursingDetail.notSpecified')})
                </p>
                <p style={styles.boxMeta}><FiPhone size={13} /> {familiarData.telefono || 'N/A'}</p>
              </div>
            ) : null}
          </section>

          <section style={styles.modulesSection}>
            <div style={styles.modulesHeading}>
              <FiActivity size={18} color="#4338ca" />
              <h3 style={styles.modulesTitle}>{t('nursingDetail.nursingActions')}</h3>
            </div>
            <div style={styles.modulesGrid}>
              {modules.map((module) => {
                const ModuleIcon = module.icon;

                return (
                  <button
                    key={module.title}
                    type="button"
                    onClick={() => navigate(module.path, {
                      state: {
                        id_atencion: routeIdAtencion,
                        Id_exp: routeIdExp,
                      },
                    })}
                    style={{ ...styles.moduleCard, backgroundColor: module.background }}
                  >
                    <div style={{ ...styles.moduleIcon, backgroundColor: `${module.color}18`, color: module.color }}>
                      <ModuleIcon size={24} />
                    </div>
                    <strong style={{ ...styles.moduleTitle, color: module.color }}>{module.title}</strong>
                    <span style={styles.moduleSubtitle}>{module.subtitle}</span>
                  </button>
                );
              })}
            </div>
          </section>

          <footer style={styles.footer}>
            <FiShield size={14} />
            <span>{t('nursingDetail.footer')}</span>
          </footer>
        </>
      )}
    </div>
  );
}

const styles = {
  page: {
    minHeight: '100%',
    padding: '24px',
    background: 'linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%)',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: '16px',
    padding: '20px 24px',
    borderRadius: '20px',
    background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
    color: '#fff',
    boxShadow: '0 18px 50px rgba(79, 70, 229, 0.22)',
  },
  headerButton: {
    width: '44px',
    height: '44px',
    border: '1px solid rgba(255,255,255,0.25)',
    borderRadius: '12px',
    background: 'rgba(255,255,255,0.12)',
    color: '#fff',
    display: 'grid',
    placeItems: 'center',
  },
  headerEyebrow: {
    fontSize: '12px',
    letterSpacing: '0.18em',
    textTransform: 'uppercase',
    opacity: 0.8,
    marginBottom: '4px',
  },
  headerTitle: {
    margin: 0,
    fontSize: '28px',
    fontWeight: 800,
  },
  headerSpacer: {
    width: '44px',
    height: '44px',
  },
  loadingCard: {
    marginTop: '20px',
    padding: '32px',
    textAlign: 'center',
    backgroundColor: '#fff',
    borderRadius: '20px',
    boxShadow: '0 12px 32px rgba(15, 23, 42, 0.08)',
  },
  errorCard: {
    marginTop: '20px',
    padding: '20px',
    backgroundColor: '#fff7ed',
    border: '1px solid #fdba74',
    color: '#9a3412',
    borderRadius: '18px',
  },
  mainCard: {
    marginTop: '20px',
    padding: '24px',
    backgroundColor: '#fff',
    borderRadius: '22px',
    boxShadow: '0 14px 36px rgba(15, 23, 42, 0.08)',
  },
  patientHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '18px',
    marginBottom: '22px',
  },
  avatar: {
    width: '74px',
    height: '74px',
    borderRadius: '999px',
    background: 'linear-gradient(135deg, #2563eb 0%, #7c3aed 100%)',
    display: 'grid',
    placeItems: 'center',
    flexShrink: 0,
  },
  patientInfo: {
    minWidth: 0,
  },
  patientName: {
    margin: 0,
    color: '#0f172a',
    fontSize: '24px',
    fontWeight: 800,
  },
  expBadge: {
    display: 'inline-block',
    marginTop: '8px',
    padding: '6px 12px',
    borderRadius: '999px',
    backgroundColor: '#dbeafe',
    color: '#1d4ed8',
    fontWeight: 700,
    fontSize: '13px',
  },
  infoGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
    gap: '14px',
    marginBottom: '18px',
  },
  infoItem: {
    padding: '16px',
    borderRadius: '16px',
    backgroundColor: '#f8fafc',
    border: '1px solid #e2e8f0',
  },
  infoLabel: {
    display: 'block',
    color: '#64748b',
    fontSize: '12px',
    textTransform: 'uppercase',
    letterSpacing: '0.06em',
    marginBottom: '6px',
  },
  infoValue: {
    color: '#0f172a',
    fontSize: '15px',
  },
  warningBox: {
    padding: '16px',
    borderRadius: '16px',
    backgroundColor: '#fef2f2',
    marginBottom: '14px',
  },
  infoBoxBlue: {
    padding: '16px',
    borderRadius: '16px',
    backgroundColor: '#eff6ff',
    marginBottom: '14px',
  },
  infoBoxGreen: {
    padding: '16px',
    borderRadius: '16px',
    backgroundColor: '#f0fdf4',
  },
  boxTitleRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '8px',
  },
  boxText: {
    margin: 0,
    color: '#334155',
    lineHeight: 1.5,
  },
  boxMeta: {
    margin: '8px 0 0',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    color: '#475569',
  },
  listWrap: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
  },
  listItem: {
    color: '#334155',
  },
  modulesSection: {
    marginTop: '22px',
  },
  modulesHeading: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginBottom: '14px',
  },
  modulesTitle: {
    margin: 0,
    fontSize: '20px',
    color: '#1e293b',
  },
  modulesGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
    gap: '14px',
  },
  moduleCard: {
    border: 'none',
    borderRadius: '18px',
    padding: '18px',
    textAlign: 'left',
    boxShadow: '0 10px 28px rgba(15, 23, 42, 0.06)',
  },
  moduleIcon: {
    width: '52px',
    height: '52px',
    borderRadius: '16px',
    display: 'grid',
    placeItems: 'center',
    marginBottom: '12px',
  },
  moduleTitle: {
    display: 'block',
    marginBottom: '6px',
    fontSize: '16px',
  },
  moduleSubtitle: {
    color: '#475569',
  },
  footer: {
    marginTop: '28px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    color: '#64748b',
    fontSize: '13px',
  },
};