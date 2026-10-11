import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useTranslation } from 'react-i18next';
import api from '../../services/api';
import {
  getCacheEntry,
  setCache,
  removeCache,
  invalidateCachePrefix,
  CacheKeys,
} from '../../services/EstudiosCache';
import Pagination from '../../components/Pagination';
import {
  FiArrowLeft,
  FiRefreshCw,
  FiUpload,
  FiEye,
  FiEdit,
  FiTrash2,
  FiSearch,
  FiFilter,
  FiChevronLeft,
  FiChevronRight,
  FiUser,
  FiHome,
  FiCalendar,
} from 'react-icons/fi';
import { FaFlask, FaChartBar, FaClipboardList, FaFolderOpen } from 'react-icons/fa';

const PAGE_SIZE = 6;

export default function EstudiosScreen() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const { t, i18n } = useTranslation();

  const SECTIONS = [
    { id: 'solicitudes_lab', label: t('studies.labRequests'), icon: <FaFlask />, color: '#4299e1' },
    { id: 'solicitudes_gab', label: t('studies.imagingRequests'), icon: <FaChartBar />, color: '#ed8936' },
    { id: 'resultados_lab', label: t('studies.labResults'), icon: <FaClipboardList />, color: '#48bb78' },
    { id: 'resultados_gab', label: t('studies.imagingResults'), icon: <FaFolderOpen />, color: '#9f7aea' },
  ];

  const SECTION_CONFIG = {
    solicitudes_lab: { endpoint: '/pending', type: 'LABORATORIO', isPending: true },
    solicitudes_gab: { endpoint: '/pending', type: 'GABINETE', isPending: true },
    resultados_lab: { endpoint: '/completed', type: 'LABORATORIO', isPending: false },
    resultados_gab: { endpoint: '/completed', type: 'GABINETE', isPending: false },
  };

  const queryParams = new URLSearchParams(location.search);
  const initialSection = queryParams.get('initialSection') || queryParams.get('section');

  const [selectedSection, setSelectedSection] = useState(
    initialSection && SECTION_CONFIG[initialSection] ? initialSection : 'solicitudes_lab'
  );
  const [allItems, setAllItems] = useState([]);
  const [hasMore, setHasMore] = useState(false);
  const [hasCachedData, setHasCachedData] = useState(false);
  const [cacheNotice, setCacheNotice] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [counts, setCounts] = useState({ laboratorio: 0, gabinete: 0, total: 0 });
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [deleting, setDeleting] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [sortOrder, setSortOrder] = useState('newest');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  const initialLoadDone = useRef(false);
  const skipFocusRefresh = useRef(false);

  const normalizeItem = (item = {}) => ({
    id_examen: item.id_examen ?? item._id ?? '',
    paciente:
      typeof item.paciente === 'string'
        ? item.paciente
        : item.paciente?.nombre || item.nombre_paciente || t('studies.patient'),
    medico:
      typeof item.medico === 'string'
        ? item.medico
        : item.medico?.nombre || item.nombre_medico || t('studies.doctor'),
    estudios: Array.isArray(item.estudios)
      ? item.estudios.join(', ')
      : item.estudios || t('studies.noStudies'),
    fecha: item.fecha_solicitud || item.fecha || null,
    fecha_realizado: item.fecha_realizado || null,
    habitacion: item.habitacion || item.numero_habitacion || item.cama || 'N/A',
  });

  const loadAllData = useCallback(
    async (force = false) => {
      const config = SECTION_CONFIG[selectedSection];
      if (!config) {
        setAllItems([]);
        setHasMore(false);
        setError(t('studies.invalidSection'));
        return;
      }

      const baseCacheKey = CacheKeys.estudiosAll(
        config.type,
        config.isPending ? 'pending' : 'completed'
      );
      const cacheKey = `${baseCacheKey}_${currentPage}_${encodeURIComponent(debouncedSearch)}_${dateFrom}_${dateTo}_${sortOrder}`;
      let cachedData = null;

      try {
        setError('');
        setCacheNotice('');
        setLoading(true);

        if (!force) {
          const cachedEntry = await getCacheEntry(cacheKey);
          if (cachedEntry) {
            cachedData = Array.isArray(cachedEntry.data)
              ? { items: cachedEntry.data.slice(0, PAGE_SIZE), hasMore: cachedEntry.data.length > PAGE_SIZE }
              : cachedEntry.data;
            const cachedItems = Array.isArray(cachedData?.items) ? cachedData.items : [];
            setAllItems(cachedItems.map(normalizeItem));
            setHasMore(Boolean(cachedData?.hasMore));
            setHasCachedData(true);

            if (cachedEntry.isFresh) {
              setLoading(false);
              return;
            }
          }
        }

        const response = await api.get(`/exams${config.endpoint}`, {
          params: {
            type: config.type,
            page: currentPage,
            limit: PAGE_SIZE + 1,
            q: debouncedSearch,
            from: dateFrom,
            to: dateTo,
            sort: sortOrder,
          },
        });
        const received = Array.isArray(response.data) ? response.data : [];
        const pageData = {
          items: received.slice(0, PAGE_SIZE),
          hasMore: received.length > PAGE_SIZE,
        };
        const normalized = pageData.items.map(normalizeItem);
        setAllItems(normalized);
        setHasMore(pageData.hasMore);
        setHasCachedData(true);
        await setCache(cacheKey, pageData);
      } catch (err) {
        if (cachedData) {
          setCacheNotice(isEnglish ? 'Showing saved results; refresh failed.' : 'Se muestran datos guardados; no se pudieron actualizar.');
        } else {
          setError(err.response?.data?.error || t('studies.loadError'));
          setAllItems([]);
          setHasMore(false);
          setHasCachedData(false);
        }
      } finally {
        setLoading(false);
      }
    },
    [selectedSection, currentPage, debouncedSearch, dateFrom, dateTo, sortOrder, t]
  );

  const loadCounts = useCallback(
    async (force = false) => {
      try {
        if (!force) {
          const cachedEntry = await getCacheEntry(CacheKeys.counts);
          if (cachedEntry) {
            setCounts(cachedEntry.data);
            if (cachedEntry.isFresh) return;
          }
        }
        const response = await api.get('/exams/counts');
        const nextCounts = {
          laboratorio: response.data?.laboratorio ?? 0,
          gabinete: response.data?.gabinete ?? 0,
          total: response.data?.total ?? 0,
        };
        setCounts(nextCounts);
        await setCache(CacheKeys.counts, nextCounts);
      } catch (error) {
        console.error('Error loading counts:', error);
      }
    },
    []
  );

  useEffect(() => {
    const timer = window.setTimeout(() => setDebouncedSearch(searchTerm.trim()), 300);
    return () => window.clearTimeout(timer);
  }, [searchTerm]);

  useEffect(() => {
    const querySection = new URLSearchParams(location.search).get('initialSection')
      || new URLSearchParams(location.search).get('section');
    if (querySection && SECTION_CONFIG[querySection]) {
      setSelectedSection(querySection);
      setCurrentPage(1);
    }
  }, [location.search]);

  useEffect(() => {
    skipFocusRefresh.current = false;
    loadAllData();
    loadCounts();
    initialLoadDone.current = true;
  }, [selectedSection, loadAllData, loadCounts]);

  const onRefresh = async () => {
    setRefreshing(true);
    skipFocusRefresh.current = true;
    await invalidateCachePrefix('estudios_all_');
    await removeCache(CacheKeys.counts);
    await Promise.all([loadAllData(true), loadCounts(true)]);
    setRefreshing(false);
    skipFocusRefresh.current = false;
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const handleUpload = (item) => {
    const tipo = selectedSection.includes('lab') ? 'LABORATORIO' : 'GABINETE';
    skipFocusRefresh.current = false;
    
    const params = new URLSearchParams({
      id_examen: item.id_examen,
      tipo: tipo,
      paciente: item.paciente,
      habitacion: item.habitacion,
      estudios: item.estudios,
      returnSection: selectedSection,
    });
    
    navigate(`/subir-resultado?${params.toString()}`);
  };

  const handleView = (id_examen) => {
    const tipo = selectedSection.includes('lab') ? 'LABORATORIO' : 'GABINETE';
    const screen = tipo === 'LABORATORIO' ? 'ver-resultado-lab' : 'ver-resultado-gab';
    navigate(`/${screen}?id_examen=${id_examen}&tipo=${tipo}`);
  };

  const handleEdit = (id_examen) => {
    const tipo = selectedSection.includes('lab') ? 'LABORATORIO' : 'GABINETE';
    const screen = tipo === 'LABORATORIO' ? 'editar-resultado-lab' : 'editar-resultado-gab';
    navigate(`/${screen}?id_examen=${id_examen}&tipo=${tipo}&returnSection=${selectedSection}`);
  };

  const handleDelete = (id_examen) => {
    const tipo = selectedSection.includes('lab') ? 'laboratorio' : 'gabinete';
    const tipoDisplay = tipo === 'laboratorio' ? t('studies.laboratory') : t('studies.imaging');
    if (!window.confirm(t('studies.deleteConfirm', { type: tipoDisplay }))) return;

    if (deleting) return;
    setDeleting(true);

    (async () => {
      try {
        await api.delete(`/exams/${id_examen}/results?type=${tipo}`);

        alert(t('studies.deleteSuccess', { type: tipoDisplay }));

        const tipoUpper = tipo.toUpperCase();
        await invalidateCachePrefix(`estudios_all_${tipoUpper}_`);
        await removeCache(CacheKeys.counts);

        await Promise.all([
          loadAllData(true),
          loadCounts(true),
        ]);
      } catch (error) {
        console.error('Error deleting:', error);
        let msg = t('studies.deleteError');
        if (error.response?.data?.error) {
          msg = error.response.data.error;
        }
        alert(msg);
      } finally {
        setDeleting(false);
      }
    })();
  };

  const isPending = selectedSection.startsWith('solicitudes');
  const isEnglish = i18n.language?.startsWith('en');
  const clearFilters = () => {
    setSearchTerm('');
    setDebouncedSearch('');
    setDateFrom('');
    setDateTo('');
    setSortOrder('newest');
    setCurrentPage(1);
  };

  const renderItem = (item) => {
    const sectionColor = SECTIONS.find(s => s.id === selectedSection)?.color || '#4299e1';
    return (
      <div key={item.id_examen} style={{ ...styles.card, borderLeftColor: sectionColor }}>
        <div style={styles.cardHeader}>
          <div style={styles.avatar}>{String(item.paciente).charAt(0)}</div>
          <div style={styles.cardInfo}>
            <div style={styles.patientName}>{item.paciente}</div>
            <div style={styles.patientDetail}>🛏️ {item.habitacion}</div>
          </div>
          {!isPending && <div style={styles.completedBadge}>✅</div>}
        </div>

        <div style={styles.cardBody}>
          <div style={styles.infoRow}>
            <span style={styles.infoIcon}>🔬</span>
            <span style={styles.examsList}>{item.estudios}</span>
          </div>
          <div style={styles.infoRow}>
            <span style={styles.infoIcon}>📅</span>
            <span style={styles.dateText}>
              {t('studies.requested')} {item.fecha ? new Date(item.fecha).toLocaleDateString(i18n.language === 'en' ? 'en-US' : 'es-MX') : t('studies.dateUnavailable')}
            </span>
          </div>
          {!isPending && item.fecha_realizado && (
            <div style={styles.infoRow}>
              <span style={styles.infoIcon}>✅</span>
              <span style={styles.dateText}>
                {t('studies.completed')} {new Date(item.fecha_realizado).toLocaleDateString(i18n.language === 'en' ? 'en-US' : 'es-MX')}
              </span>
            </div>
          )}
        </div>

        <div style={styles.actionRow}>
          {isPending ? (
            <button style={styles.btnUpload} onClick={() => handleUpload(item)}>
              <FiUpload size={16} /> {t('studies.upload')}
            </button>
          ) : (
            <>
              <button style={styles.btnView} onClick={() => handleView(item.id_examen)}>
                <FiEye size={16} /> {t('studies.view')}
              </button>
              <button style={styles.btnEdit} onClick={() => handleEdit(item.id_examen)}>
                <FiEdit size={16} /> {t('studies.edit')}
              </button>
              <button 
                style={{ ...styles.btnDelete, opacity: deleting ? 0.6 : 1 }}
                onClick={() => handleDelete(item.id_examen)}
                disabled={deleting}
              >
                <FiTrash2 size={16} /> {t('studies.delete')}
              </button>
            </>
          )}
        </div>
      </div>
    );
  };

  const renderEmpty = () => (
    <div style={styles.emptyCard}>
      <div style={styles.emptyEmoji}>📭</div>
      <div style={styles.emptyText}>
        {isPending ? t('studies.noPendingRequests') : t('studies.noResults')}
      </div>
      <div style={styles.emptySubtext}>
        {isPending ? t('studies.allRequestsCompleted') : t('studies.noResultsUploaded')}
      </div>
    </div>
  );

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <button type="button" onClick={() => navigate(-1)} style={styles.headerButton}>
          <FiArrowLeft size={20} />
        </button>
        <div>
          <div style={styles.headerEyebrow}>{t('studies.module')}</div>
          <h1 style={styles.headerTitle}>{t('studies.management')}</h1>
        </div>
        <button type="button" onClick={onRefresh} style={styles.headerButton} disabled={refreshing}>
          <FiRefreshCw size={20} className={refreshing ? 'spin' : ''} />
        </button>
      </div>

      <div style={styles.heroCard}>
        <div>
          <p style={styles.heroGreeting}>{t('studies.welcomeBack', { user: user?.username || t('studies.user') })}</p>
          <p style={styles.heroDate}>{new Date().toLocaleDateString(i18n.language === 'en' ? 'en-US' : 'es-MX', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
        </div>
        <div style={styles.heroPill}>{t('studies.totalPending')}: {counts.total}</div>
      </div>

      {error ? <div style={styles.alert}>{error}</div> : null}

      <div style={styles.tabsWrapper}>
        {SECTIONS.map((section) => {
          const isActive = selectedSection === section.id;
          return (
            <button
              key={section.id}
              style={{
                ...styles.tab,
                ...(isActive ? styles.tabActive : {}),
                ...(isActive ? { borderBottomColor: section.color } : {}),
              }}
              onClick={() => {
                setSelectedSection(section.id);
                setCurrentPage(1);
                skipFocusRefresh.current = true;
              }}
            >
              <span style={styles.tabIcon}>{section.icon}</span>
              <span style={styles.tabLabel}>{section.label}</span>
              {isActive && <span style={{ ...styles.tabBadge, backgroundColor: section.color }}>{allItems.length}</span>}
            </button>
          );
        })}
      </div>

      <section style={styles.filters} aria-label={isEnglish ? 'Request filters' : 'Filtros de solicitudes'}>
        <label style={styles.filterField}>
          <span style={styles.filterLabel}>{isEnglish ? 'Search' : 'Buscar paciente o solicitud'}</span>
          <input
            type="search"
            value={searchTerm}
            onChange={(event) => { setSearchTerm(event.target.value); setCurrentPage(1); }}
            placeholder={isEnglish ? 'Patient, study, doctor, room or folio' : 'Paciente, estudio, médico, cama o folio'}
            style={styles.filterInput}
          />
        </label>
        <label style={styles.filterField}>
          <span style={styles.filterLabel}>{isEnglish ? 'From' : 'Desde'}</span>
          <input type="date" value={dateFrom} onChange={(event) => { setDateFrom(event.target.value); setCurrentPage(1); }} style={styles.filterInput} />
        </label>
        <label style={styles.filterField}>
          <span style={styles.filterLabel}>{isEnglish ? 'To' : 'Hasta'}</span>
          <input type="date" value={dateTo} onChange={(event) => { setDateTo(event.target.value); setCurrentPage(1); }} style={styles.filterInput} />
        </label>
        <label style={styles.filterField}>
          <span style={styles.filterLabel}>{isEnglish ? 'Sort by date' : 'Ordenar por fecha'}</span>
          <select value={sortOrder} onChange={(event) => { setSortOrder(event.target.value); setCurrentPage(1); }} style={styles.filterInput}>
            <option value="newest">{isEnglish ? 'Newest first' : 'Más recientes'}</option>
            <option value="oldest">{isEnglish ? 'Oldest first' : 'Más antiguas'}</option>
          </select>
        </label>
        <button type="button" onClick={clearFilters} style={styles.clearFilters}>
          {isEnglish ? 'Clear filters' : 'Limpiar filtros'}
        </button>
      </section>

      <div style={styles.listArea}>
        {error ? (
          <div style={styles.emptyCard}>
            <div style={styles.emptyEmoji}>⚠️</div>
            <div style={styles.emptyText}>{error}</div>
          </div>
        ) : loading && allItems.length === 0 ? (
          <div style={styles.loadingCard}>{t('studies.loading')}</div>
        ) : allItems.length === 0 ? (
          renderEmpty()
        ) : filteredItems.length === 0 ? (
          <div style={styles.emptyCard}>
            <div style={styles.emptyEmoji}>🔎</div>
            <div style={styles.emptyText}>{isEnglish ? 'No requests match these filters.' : 'No hay solicitudes que coincidan con esos filtros.'}</div>
            <button type="button" style={styles.clearFilters} onClick={clearFilters}>{isEnglish ? 'Clear filters' : 'Limpiar filtros'}</button>
          </div>
        ) : (
          <>
            <div style={styles.grid}>
              {paginatedItems.map((item) => renderItem(item))}
            </div>
            {totalPages > 1 && (
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={handlePageChange}
                itemsPerPage={PAGE_SIZE}
                totalItems={filteredItems.length}
              />
            )}
          </>
        )}
      </div>

      <footer style={styles.footer}>
        <FiArrowLeft size={14} style={{ transform: 'rotate(180deg)' }} />
        <span>{t('studies.secureFooter')}</span>
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
    cursor: 'pointer',
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
  filters: { marginTop: '18px', padding: '16px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', alignItems: 'end', borderRadius: '18px', backgroundColor: '#fff', boxShadow: '0 8px 24px rgba(15, 23, 42, 0.06)' },
  filterField: { display: 'grid', gap: '6px', minWidth: 0 },
  filterLabel: { color: '#475569', fontSize: '13px', fontWeight: 700 },
  filterInput: { width: '100%', minHeight: '42px', padding: '9px 11px', borderRadius: '10px', border: '1px solid #cbd5e1', backgroundColor: '#fff', color: '#1e293b', font: 'inherit' },
  clearFilters: { minHeight: '42px', padding: '9px 14px', borderRadius: '10px', border: '1px solid #cbd5e1', backgroundColor: '#f8fafc', color: '#334155', fontWeight: 700, cursor: 'pointer' },
  tabsWrapper: {
    marginTop: '22px',
    display: 'flex',
    gap: '8px',
    backgroundColor: 'transparent',
    padding: '0',
    overflowX: 'auto',
  },
  tab: {
    flex: '1 0 auto',
    padding: '10px 18px',
    borderRadius: '12px',
    borderTopWidth: '1px',
    borderTopStyle: 'solid',
    borderTopColor: '#e2e8f0',
    borderRightWidth: '1px',
    borderRightStyle: 'solid',
    borderRightColor: '#e2e8f0',
    borderBottomWidth: '3px',
    borderBottomStyle: 'solid',
    borderBottomColor: 'transparent',
    borderLeftWidth: '1px',
    borderLeftStyle: 'solid',
    borderLeftColor: '#e2e8f0',
    background: '#ffffff',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontWeight: 600,
    color: '#1e293b',
    cursor: 'pointer',
    transition: 'all 0.2s',
    position: 'relative',
    boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
  },
  tabActive: {
    background: '#f1f5f9',
    borderTopColor: '#cbd5e1',
    borderRightColor: '#cbd5e1',
    borderLeftColor: '#cbd5e1',
    borderBottomWidth: '3px',
    boxShadow: '0 4px 8px rgba(0,0,0,0.05)',
  },
  tabIcon: { fontSize: '18px' },
  tabLabel: { fontSize: '14px', whiteSpace: 'nowrap' },
  tabBadge: {
    marginLeft: '6px',
    padding: '2px 8px',
    borderRadius: '999px',
    color: '#fff',
    fontSize: '12px',
    fontWeight: 700,
  },
  listArea: { marginTop: '18px' },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
    gap: '18px',
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: '18px',
    boxShadow: '0 8px 24px rgba(15, 23, 42, 0.06)',
    padding: '18px',
    borderLeftWidth: '6px',
    borderLeftStyle: 'solid',
    borderLeftColor: '#4299e1',
    transition: 'transform 0.2s, box-shadow 0.2s',
    display: 'flex',
    flexDirection: 'column',
  },
  cardHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '14px',
  },
  avatar: {
    width: '44px',
    height: '44px',
    borderRadius: '12px',
    backgroundColor: '#e2e8f0',
    display: 'grid',
    placeItems: 'center',
    fontWeight: 700,
    fontSize: '18px',
    color: '#475569',
  },
  cardInfo: { flex: 1 },
  patientName: { fontWeight: 700, fontSize: '16px' },
  patientDetail: { fontSize: '14px', color: '#64748b' },
  completedBadge: { fontSize: '20px' },
  cardBody: {
    flex: 1,
    marginBottom: '16px',
  },
  infoRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '6px',
    fontSize: '14px',
    color: '#334155',
  },
  infoIcon: { fontSize: '16px', width: '24px', textAlign: 'center' },
  examsList: { wordBreak: 'break-word' },
  dateText: { color: '#64748b' },
  actionRow: {
    display: 'flex',
    gap: '8px',
    flexWrap: 'wrap',
    borderTop: '1px solid #e2e8f0',
    paddingTop: '14px',
  },
  btnUpload: {
    padding: '8px 16px',
    borderRadius: '999px',
    border: 'none',
    backgroundColor: '#4299e1',
    color: '#fff',
    fontWeight: 600,
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    cursor: 'pointer',
    fontSize: '13px',
  },
  btnView: {
    padding: '8px 16px',
    borderRadius: '999px',
    border: 'none',
    backgroundColor: '#48bb78',
    color: '#fff',
    fontWeight: 600,
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    cursor: 'pointer',
    fontSize: '13px',
  },
  btnEdit: {
    padding: '8px 16px',
    borderRadius: '999px',
    border: 'none',
    backgroundColor: '#ed8936',
    color: '#fff',
    fontWeight: 600,
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    cursor: 'pointer',
    fontSize: '13px',
  },
  btnDelete: {
    padding: '8px 16px',
    borderRadius: '999px',
    border: 'none',
    backgroundColor: '#fc8181',
    color: '#fff',
    fontWeight: 600,
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    cursor: 'pointer',
    fontSize: '13px',
  },
  emptyCard: {
    padding: '40px 20px',
    textAlign: 'center',
    backgroundColor: '#fff',
    borderRadius: '18px',
    boxShadow: '0 8px 24px rgba(15, 23, 42, 0.06)',
  },
  emptyEmoji: { fontSize: '48px', marginBottom: '12px' },
  emptyText: { fontSize: '18px', fontWeight: 600, color: '#1e293b' },
  emptySubtext: { fontSize: '14px', color: '#94a3b8', marginTop: '4px' },
  loadingCard: {
    padding: '32px',
    textAlign: 'center',
    backgroundColor: '#fff',
    borderRadius: '20px',
    boxShadow: '0 12px 32px rgba(15, 23, 42, 0.08)',
    color: '#64748b',
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
