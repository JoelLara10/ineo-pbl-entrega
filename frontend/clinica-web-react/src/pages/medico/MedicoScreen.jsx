import { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { FiActivity, FiAlertCircle, FiArrowLeft, FiChevronLeft, FiChevronRight, FiHeart, FiRefreshCw, FiShield, FiUser } from 'react-icons/fi';
import { MdLocalHospital, MdOutlineBed } from 'react-icons/md';
import { useAuth } from '../../context/AuthContext';
import { usePatient } from '../../context/PatientContext';
import api from '../../services/api';
import moment from 'moment';
import 'moment/locale/es';
import 'moment/locale/en-gb';

moment.locale('es');

const CACHE_PREFIX = 'ineo_web_cache_medico_';
const CACHE_TTL = 5 * 60 * 1000;
const ITEMS_PER_PAGE = 6;
const CACHE_KEYS = {
  consulta: 'consulta',
  urgencias: 'urgencias',
  hospitalizados: 'hospitalizados',
};

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
    console.error('Error reading medico cache:', error);
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
    console.error('Error saving medico cache:', error);
  }
}

function getPatientName(item) {
  if (item.nom_pac && item.papell) {
    return `${item.papell} ${item.nom_pac}`;
  }

  return item.nom_pac || 'Paciente';
}

function getPagedData(data, page) {
  const startIndex = (page - 1) * ITEMS_PER_PAGE;
  return data.slice(startIndex, startIndex + ITEMS_PER_PAGE);
}

function getTotalPages(data) {
  return Math.ceil(data.length / ITEMS_PER_PAGE);
}

export default function MedicoScreen() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { selectPatient } = usePatient();
  const [patientsByArea, setPatientsByArea] = useState({ consulta: [], urgencias: [], hospitalizados: [] });
  const [pages, setPages] = useState({ consulta: 1, urgencias: 1, hospitalizados: 1 });
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    moment.locale(i18n.language === 'en' ? 'en-gb' : 'es');
  }, [i18n.language]);

  const loadPatients = useCallback(async (forceRefresh = false) => {
    setLoading(true);
    setErrorMessage('');

    if (!forceRefresh) {
      const cachedConsulta = getCachedValue(CACHE_KEYS.consulta);
      const cachedUrgencias = getCachedValue(CACHE_KEYS.urgencias);
      const cachedHospitalizados = getCachedValue(CACHE_KEYS.hospitalizados);

      if (cachedConsulta && cachedUrgencias && cachedHospitalizados) {
        setPatientsByArea({
          consulta: cachedConsulta,
          urgencias: cachedUrgencias,
          hospitalizados: cachedHospitalizados,
        });
        setLoading(false);
        return;
      }
    }

    try {
      const response = await api.get('/medico');
      const nextState = {
        consulta: response.data.beds_consulta || [],
        urgencias: response.data.beds_preparacion || [],
        hospitalizados: response.data.beds_recuperacion || [],
      };

      setCachedValue(CACHE_KEYS.consulta, nextState.consulta);
      setCachedValue(CACHE_KEYS.urgencias, nextState.urgencias);
      setCachedValue(CACHE_KEYS.hospitalizados, nextState.hospitalizados);
      setPatientsByArea(nextState);
    } catch (error) {
      console.error('Error loading medico patients:', error);

      const cachedConsulta = getCachedValue(CACHE_KEYS.consulta);
      const cachedUrgencias = getCachedValue(CACHE_KEYS.urgencias);
      const cachedHospitalizados = getCachedValue(CACHE_KEYS.hospitalizados);

      if (cachedConsulta || cachedUrgencias || cachedHospitalizados) {
        setPatientsByArea({
          consulta: cachedConsulta || [],
          urgencias: cachedUrgencias || [],
          hospitalizados: cachedHospitalizados || [],
        });
        setErrorMessage(t('medical.offlineMessage'));
      } else {
        setErrorMessage(t('medical.errorMessage'));
      }
    } finally {
      setLoading(false);
    }
  }, [t, i18n.language]);

  useEffect(() => {
    loadPatients();
  }, [loadPatients]);

  const onRefresh = useCallback(async () => {
    setRefreshing(true);
    setPages({ consulta: 1, urgencias: 1, hospitalizados: 1 });
    await loadPatients(true);
    setRefreshing(false);
  }, [loadPatients]);

  const totalPatients = useMemo(() => (
    patientsByArea.consulta.length + patientsByArea.urgencias.length + patientsByArea.hospitalizados.length
  ), [patientsByArea]);

  const handlePatientClick = (item) => {
    const isOccupied = item.estatus === 'OCUPADA' && item.tiene_atencion;
    if (!isOccupied || !item.id_atencion || !item.Id_exp) return;

    selectPatient({ id_atencion: item.id_atencion, Id_exp: item.Id_exp, ...item });
    navigate(`/medico/paciente/${item.id_atencion}/${item.Id_exp}`, {
      state: { id_atencion: item.id_atencion, Id_exp: item.Id_exp },
    });
  };

  const sections = [
    { key: 'consulta', title: t('medical.outpatient'), color: '#4299e1', icon: MdLocalHospital, emptyLabel: t('medical.noOutpatient') },
    { key: 'urgencias', title: t('medical.emergency'), color: '#f56565', icon: FiAlertCircle, emptyLabel: t('medical.noEmergency') },
    { key: 'hospitalizados', title: t('medical.hospitalized'), color: '#48bb78', icon: MdOutlineBed, emptyLabel: t('medical.noHospitalized') },
  ];

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <button type="button" onClick={() => navigate(-1)} style={styles.headerButton}>
          <FiArrowLeft size={20} />
        </button>
        <div>
          <div style={styles.headerEyebrow}>{t('medical.headerEyebrow')}</div>
          <h1 style={styles.headerTitle}>{t('medical.headerTitle')}</h1>
        </div>
        <button type="button" onClick={onRefresh} style={styles.headerButton} disabled={refreshing}>
          <FiRefreshCw size={20} />
        </button>
      </div>

      <div style={styles.heroCard}>
        <div>
          <p style={styles.heroGreeting}>{t('medical.greeting', { name: user?.username || 'User' })}</p>
          <p style={styles.heroDate}>{moment().format('dddd, D [de] MMMM [de] YYYY')}</p>
        </div>
        <div style={styles.heroPill}>{t('medical.totalPatients', { count: totalPatients })}</div>
      </div>

      {errorMessage ? <div style={styles.alert}>{errorMessage}</div> : null}

      {loading ? (
        <div style={styles.loadingCard}>{t('medical.loading')}</div>
      ) : (
        sections.map((section) => {
          const sectionData = patientsByArea[section.key];
          const page = pages[section.key];
          const totalPages = getTotalPages(sectionData);
          const pagedData = getPagedData(sectionData, page);
          const SectionIcon = section.icon;

          return (
            <section key={section.key} style={styles.section}>
              <div style={{ ...styles.sectionHeader, borderLeftColor: section.color }}>
                <div style={styles.sectionTitleRow}>
                  <SectionIcon size={20} color={section.color} />
                  <h2 style={styles.sectionTitle}>{section.title}</h2>
                </div>
                <span style={{ ...styles.countBadge, backgroundColor: section.color }}>{sectionData.length}</span>
              </div>

              <div style={styles.grid}>
                {pagedData.length > 0 ? (
                  pagedData.map((item, index) => {
                    const isOccupied = item.estatus === 'OCUPADA' && item.tiene_atencion;

                    return (
                      <button
                        key={item.id_atencion || item.id_cama || `${section.key}-${index}`}
                        type="button"
                        onClick={() => handlePatientClick(item)}
                        style={{
                          ...styles.card,
                          borderColor: isOccupied ? section.color : '#e2e8f0',
                          cursor: isOccupied ? 'pointer' : 'default',
                          opacity: isOccupied ? 1 : 0.82,
                        }}
                      >
                        <div style={{ ...styles.cardIcon, backgroundColor: `${section.color}18`, color: section.color }}>
                          {isOccupied ? <FiUser size={24} /> : <MdOutlineBed size={24} />}
                        </div>
                        <strong style={styles.cardTitle}>{t('medical.bed', { num: item.num_cama || '--' })}</strong>
                        <span style={styles.cardName}>{isOccupied ? getPatientName(item) : t('medical.available')}</span>
                        <span style={{ ...styles.cardStatus, backgroundColor: isOccupied ? section.color : '#94a3b8' }}>
                          {isOccupied ? t('medical.occupied') : t('medical.availableStatus')}
                        </span>
                      </button>
                    );
                  })
                ) : (
                  <div style={styles.emptyCard}>{section.emptyLabel}</div>
                )}
              </div>

              {totalPages > 1 ? (
                <div style={styles.pagination}>
                  <button
                    type="button"
                    onClick={() => setPages((current) => ({ ...current, [section.key]: page - 1 }))}
                    disabled={page === 1}
                    style={styles.paginationButton}
                  >
                    <FiChevronLeft size={18} />
                  </button>
                  <span style={styles.paginationText}>{page} / {totalPages}</span>
                  <button
                    type="button"
                    onClick={() => setPages((current) => ({ ...current, [section.key]: page + 1 }))}
                    disabled={page === totalPages}
                    style={styles.paginationButton}
                  >
                    <FiChevronRight size={18} />
                  </button>
                </div>
              ) : null}
            </section>
          );
        })
      )}

      <footer style={styles.footer}>
        <FiShield size={14} />
        <span>{t('medical.footer')}</span>
      </footer>
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
    border: '1px solid rgba(255,255,255,0.28)',
    borderRadius: '12px',
    background: 'rgba(255,255,255,0.12)',
    color: '#fff',
    display: 'grid',
    placeItems: 'center',
  },
  headerEyebrow: { fontSize: '12px', letterSpacing: '0.18em', textTransform: 'uppercase', opacity: 0.8, marginBottom: '4px' },
  headerTitle: { margin: 0, fontSize: '28px', fontWeight: 800 },
  heroCard: {
    marginTop: '20px',
    padding: '20px 24px',
    backgroundColor: '#fff',
    borderRadius: '20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: '16px',
    boxShadow: '0 12px 32px rgba(15, 23, 42, 0.08)',
  },
  heroGreeting: { margin: 0, fontSize: '22px', fontWeight: 700 },
  heroDate: { margin: '6px 0 0', color: '#64748b' },
  heroPill: { padding: '10px 16px', borderRadius: '999px', backgroundColor: '#dbeafe', color: '#1d4ed8', fontWeight: 700, whiteSpace: 'nowrap' },
  alert: { marginTop: '18px', padding: '14px 16px', borderRadius: '14px', backgroundColor: '#fff7ed', border: '1px solid #fdba74', color: '#9a3412' },
  loadingCard: { marginTop: '20px', padding: '32px', textAlign: 'center', backgroundColor: '#fff', borderRadius: '20px', boxShadow: '0 12px 32px rgba(15, 23, 42, 0.08)' },
  section: { marginTop: '22px' },
  sectionHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '16px', padding: '16px 18px', backgroundColor: '#fff', borderRadius: '18px', borderLeft: '6px solid', boxShadow: '0 10px 30px rgba(15, 23, 42, 0.07)' },
  sectionTitleRow: { display: 'flex', alignItems: 'center', gap: '10px' },
  sectionTitle: { margin: 0, fontSize: '18px', fontWeight: 700 },
  countBadge: { minWidth: '36px', padding: '6px 10px', borderRadius: '999px', color: '#fff', fontWeight: 700, textAlign: 'center' },
  grid: { marginTop: '14px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '14px' },
  card: { border: '1px solid #e2e8f0', borderRadius: '18px', backgroundColor: '#fff', padding: '18px', textAlign: 'left', boxShadow: '0 8px 24px rgba(15, 23, 42, 0.06)' },
  cardIcon: { width: '52px', height: '52px', borderRadius: '16px', display: 'grid', placeItems: 'center', marginBottom: '14px' },
  cardTitle: { display: 'block', fontSize: '16px', marginBottom: '6px' },
  cardName: { display: 'block', minHeight: '20px', color: '#64748b', marginBottom: '14px' },
  cardStatus: { display: 'inline-block', padding: '6px 10px', borderRadius: '999px', color: '#fff', fontSize: '12px', fontWeight: 700, letterSpacing: '0.04em' },
  emptyCard: { padding: '28px', borderRadius: '18px', backgroundColor: '#fff', textAlign: 'center', color: '#94a3b8', boxShadow: '0 8px 24px rgba(15, 23, 42, 0.06)' },
  pagination: { marginTop: '12px', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '12px' },
  paginationButton: { width: '38px', height: '38px', borderRadius: '10px', border: '1px solid #cbd5e1', backgroundColor: '#fff', color: '#334155', display: 'grid', placeItems: 'center' },
  paginationText: { fontWeight: 700, color: '#475569' },
  footer: { marginTop: '28px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', color: '#64748b', fontSize: '13px' },
};
