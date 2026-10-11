import React, { useState, useEffect, useCallback, useRef } from 'react';
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
} from 'react-icons/fi';
import { FaFlask, FaChartBar, FaClipboardList, FaFolderOpen } from 'react-icons/fa';

const PAGE_SIZE = 6;

export default function EstudiosScreen() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const { t, i18n } = useTranslation();
  const isEnglish = i18n.language?.startsWith('en');

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
  const [totalItems, setTotalItems] = useState(0);
  const [hasMore, setHasMore] = useState(false);
  const [hasCachedData, setHasCachedData] = useState(false);
  const [cacheNotice, setCacheNotice] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [counts, setCounts] = useState({ laboratorio: 0, gabinete: 0, total: 0 });
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [error, setError] = useState('');
  const [deleting, setDeleting] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [sortOrder, setSortOrder] = useState('newest');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  const skipFocusRefresh = useRef(false);
  const loadRequestRef = useRef(0);

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
      const requestId = ++loadRequestRef.current;
      const config = SECTION_CONFIG[selectedSection];
      if (!config) {
        setAllItems([]);
        setHasMore(false);
        setTotalItems(0);
        setError(t('studies.invalidSection'));
        return;
      }

      const baseCacheKey = CacheKeys.estudiosAll(
        config.type,
        config.isPending ? 'pending' : 'completed'
      );
      const cacheScope = encodeURIComponent(`${user?.role || 'user'}_${user?.username || 'anonymous'}`);
      const cacheKey = `${baseCacheKey}_full_v2_${cacheScope}_${encodeURIComponent(debouncedSearch)}_${dateFrom}_${dateTo}_${sortOrder}`;
      let cachedData = null;

      const showPage = (items) => {
        const start = (currentPage - 1) * PAGE_SIZE;
        setTotalItems(items.length);
        setAllItems(items.slice(start, start + PAGE_SIZE).map(normalizeItem));
        setHasMore(items.length > currentPage * PAGE_SIZE);
        setHasCachedData(true);
      };

      try {
        setError('');
        setCacheNotice('');
        setLoading(true);
        setLoadingMessage(isEnglish ? 'Loading all studies…' : 'Cargando todos los estudios…');

        if (!force) {
          const cachedEntry = await getCacheEntry(cacheKey);
          if (cachedEntry && Array.isArray(cachedEntry.data)) {
            cachedData = cachedEntry.data;
            showPage(cachedData);
            if (cachedEntry.isFresh) {
              setLoading(false);
              setLoadingMessage('');
              return;
            }
          } else {
            setHasCachedData(false);
            setAllItems([]);
            setTotalItems(0);
          }
        }

        const response = await api.get(`/exams${config.endpoint}`, {
          params: {
            type: config.type,
            all: true,
            q: debouncedSearch,
            from: dateFrom,
            to: dateTo,
            sort: sortOrder,
          },
        });
        if (requestId !== loadRequestRef.current) return;
        const allResults = Array.isArray(response.data) ? response.data : [];
        showPage(allResults);
        await setCache(cacheKey, allResults);
      } catch (err) {
        if (requestId !== loadRequestRef.current) return;
        if (cachedData) {
          setCacheNotice(isEnglish ? 'Showing saved results; refresh failed.' : 'Se muestran datos guardados; no se pudieron actualizar.');
        } else {
          setError(err.response?.data?.error || t('studies.loadError'));
          setAllItems([]);
          setTotalItems(0);
          setHasMore(false);
          setHasCachedData(false);
        }
      } finally {
        if (requestId === loadRequestRef.current) {
          setLoading(false);
          setLoadingMessage('');
        }
      }
    },
    [selectedSection, currentPage, debouncedSearch, dateFrom, dateTo, sortOrder, t, isEnglish, user?.role, user?.username]
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
  }, [selectedSection, loadAllData]);

  useEffect(() => {
    loadCounts();
  }, [loadCounts]);

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
  const activeFilterCount = Number(Boolean(debouncedSearch)) + Number(Boolean(dateFrom)) + Number(Boolean(dateTo)) + Number(sortOrder !== 'newest');
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
        <div style={styles.headerCopy}>
          <div style={styles.headerEyebrow}>{t('studies.module')}</div>
          <h1 style={styles.headerTitle}>{t('studies.management')}</h1>
        </div>
        <button type="button" onClick={onRefresh} style={styles.headerButton} disabled={refreshing}>
          <FiRefreshCw size={20} className={refreshing ? 'spin' : ''} />
        </button>
      </div>

      <div style={styles.summaryStrip}>
        <span>{t('studies.totalPending')}</span>
        <strong style={styles.summaryNumber}>{counts.total}</strong>
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
              {isActive && section.id === 'solicitudes_lab' && <span style={{ ...styles.tabBadge, backgroundColor: section.color }}>{counts.laboratorio}</span>}
              {isActive && section.id === 'solicitudes_gab' && <span style={{ ...styles.tabBadge, backgroundColor: section.color }}>{counts.gabinete}</span>}
            </button>
          );
        })}
      </div>

      <section style={styles.filterPanel} aria-label={isEnglish ? 'Study filters' : 'Filtros de estudios'}>
        <div style={styles.searchRow}>
          <label style={styles.searchBox}>
            <FiSearch size={18} color="#64748b" />
            <input
              type="search"
              value={searchTerm}
              onChange={(event) => { setSearchTerm(event.target.value); setCurrentPage(1); }}
              placeholder={isEnglish ? 'Search patient, study, doctor or folio' : 'Buscar paciente, estudio, médico o folio'}
              style={styles.searchInput}
              aria-label={isEnglish ? 'Search studies' : 'Buscar estudios'}
            />
          </label>
          <button type="button" onClick={() => setShowFilters((visible) => !visible)} style={styles.filterToggle} aria-expanded={showFilters}>
            <FiFilter size={17} />
            {isEnglish ? 'Filters' : 'Filtros'}
            {activeFilterCount > 0 && <span style={styles.filterCount}>{activeFilterCount}</span>}
          </button>
          {activeFilterCount > 0 && (
            <button type="button" onClick={clearFilters} style={styles.clearFilters}>
              {isEnglish ? 'Clear' : 'Limpiar'}
            </button>
          )}
        </div>
        {showFilters && (
          <div style={styles.advancedFilters}>
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
          </div>
        )}
      </section>

      <div style={styles.listArea}>
        {error ? (
          <div style={styles.emptyCard}>
            <div style={styles.emptyEmoji}>⚠️</div>
            <div style={styles.emptyText}>{error}</div>
          </div>
        ) : loading && !hasCachedData ? (
          <div style={styles.loadingCard}><span className="spin" aria-hidden="true">⟳</span> {loadingMessage || t('studies.loading')}</div>
        ) : allItems.length === 0 ? (
          renderEmpty()
        ) : (
          <>
            {cacheNotice && <div style={styles.cacheNotice} role="status">{cacheNotice}</div>}
            {loading && hasCachedData && <div style={styles.syncStatus} role="status"><FiRefreshCw className="spin" size={14} /> {isEnglish ? 'Updating saved results…' : 'Actualizando resultados guardados…'}</div>}
            <div style={styles.grid}>
              {allItems.map((item) => renderItem(item))}
            </div>
            {(currentPage > 1 || hasMore) && (
              <div style={styles.pager}>
                <button type="button" style={styles.pageButton} onClick={() => handlePageChange(currentPage - 1)} disabled={currentPage <= 1 || loading}>
                  <FiChevronLeft size={17} /> {isEnglish ? 'Previous' : 'Anterior'}
                </button>
                <span style={styles.pageLabel}>{isEnglish ? 'Page' : 'Página'} {currentPage} / {Math.max(1, Math.ceil(totalItems / PAGE_SIZE))} · {totalItems} {isEnglish ? 'studies' : 'estudios'}</span>
                <button type="button" style={styles.pageButton} onClick={() => handlePageChange(currentPage + 1)} disabled={!hasMore || loading}>
                  {isEnglish ? 'Next' : 'Siguiente'} <FiChevronRight size={17} />
                </button>
              </div>
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
  filterPanel: { marginTop: '20px', padding: '14px 16px', borderRadius: '16px', background: '#fff', border: '1px solid #e2e8f0', boxShadow: '0 6px 20px rgba(15, 23, 42, 0.04)' },
  searchRow: { display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' },
  searchBox: { flex: '1 1 360px', minWidth: 0, minHeight: '46px', display: 'flex', alignItems: 'center', gap: '10px', padding: '0 14px', border: '1px solid #dbe3ef', borderRadius: '12px', background: '#f8fafc' },
  searchInput: { width: '100%', border: 'none', outline: 'none', background: 'transparent', color: '#1e293b', font: 'inherit' },
  filterToggle: { minHeight: '44px', padding: '0 14px', border: '1px solid #cbd5e1', borderRadius: '11px', background: '#fff', color: '#334155', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '8px', fontWeight: 700, cursor: 'pointer' },
  filterCount: { minWidth: '22px', height: '22px', padding: '0 6px', borderRadius: '999px', display: 'inline-grid', placeItems: 'center', background: '#dbeafe', color: '#1d4ed8', fontSize: '12px' },
  advancedFilters: { display: 'flex', flexWrap: 'wrap', gap: '14px', paddingTop: '16px', marginTop: '14px', borderTop: '1px solid #e2e8f0' },
  cacheNotice: { marginBottom: '10px', padding: '10px 14px', borderRadius: '10px', background: '#fffbeb', color: '#92400e', fontSize: '13px' },
  syncStatus: { marginBottom: '10px', display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '7px', color: '#64748b', fontSize: '12px' },
  pager: { margin: '22px auto 0', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '16px' },
  pageButton: { minHeight: '40px', padding: '0 13px', display: 'inline-flex', alignItems: 'center', gap: '6px', border: '1px solid #cbd5e1', borderRadius: '10px', background: '#fff', color: '#334155', fontWeight: 650, cursor: 'pointer' },
  pageLabel: { color: '#64748b', fontSize: '14px', fontWeight: 600, textAlign: 'center' },
  page: {
    minHeight: '100%',
    width: '100%',
    minWidth: 0,
    boxSizing: 'border-box',
    padding: 'clamp(16px, 2.4vw, 32px)',
    maxWidth: '1500px',
    margin: '0 auto',
    background: '#f8fafc',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 'clamp(8px, 2vw, 16px)',
    minWidth: 0,
    padding: 'clamp(12px, 2vw, 20px)',
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
  headerCopy: { flex: 1, minWidth: 0 },
  headerEyebrow: { fontSize: '12px', letterSpacing: '0.14em', textTransform: 'uppercase', opacity: 0.8, marginBottom: '4px' },
  headerTitle: { margin: 0, fontSize: 'clamp(19px, 2.5vw, 28px)', lineHeight: 1.15, fontWeight: 800, overflowWrap: 'anywhere' },
  summaryStrip: { marginTop: '16px', padding: '12px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderRadius: '12px', border: '1px solid #e2e8f0', background: '#fff', color: '#64748b', fontSize: '14px' },
  summaryNumber: { color: '#1d4ed8', fontSize: '20px', fontWeight: 800 },
  alert: { marginTop: '18px', padding: '14px 16px', borderRadius: '14px', backgroundColor: '#fff7ed', border: '1px solid #fdba74', color: '#9a3412' },
  filters: { marginTop: '18px', padding: '16px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', alignItems: 'end', borderRadius: '18px', backgroundColor: '#fff', boxShadow: '0 8px 24px rgba(15, 23, 42, 0.06)' },
  filterField: { display: 'grid', gap: '7px', flex: '1 1 220px', minWidth: 'min(100%, 220px)' },
  filterLabel: { color: '#475569', fontSize: '13px', fontWeight: 700 },
  filterInput: { boxSizing: 'border-box', width: '100%', minWidth: 0, minHeight: '44px', padding: '9px 11px', borderRadius: '10px', border: '1px solid #cbd5e1', backgroundColor: '#fff', color: '#1e293b', font: 'inherit' },
  clearFilters: { minHeight: '42px', padding: '9px 14px', borderRadius: '10px', border: '1px solid #cbd5e1', backgroundColor: '#f8fafc', color: '#334155', fontWeight: 700, cursor: 'pointer' },
  tabsWrapper: {
    marginTop: '18px',
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(min(100%, 220px), 1fr))',
    gap: '10px',
    backgroundColor: 'transparent',
    padding: '0',
    overflowX: 'auto',
  },
  tab: {
    flex: '1 0 auto',
    padding: '10px 12px',
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
  listArea: { marginTop: '18px', minWidth: 0 },
  grid: {
    width: '100%',
    minWidth: 0,
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(min(100%, 380px), 1fr))',
    gap: '16px',
  },
  card: {
    minWidth: 0,
    boxSizing: 'border-box',
    backgroundColor: '#fff',
    borderRadius: '18px',
    boxShadow: '0 8px 24px rgba(15, 23, 42, 0.06)',
    padding: 'clamp(14px, 2vw, 20px)',
    border: '1px solid #e5eaf1',
    borderLeftWidth: '4px',
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
  cardInfo: { flex: 1, minWidth: 0 },
  patientName: { fontWeight: 700, fontSize: '16px', overflowWrap: 'anywhere' },
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
  examsList: { minWidth: 0, overflowWrap: 'anywhere' },
  dateText: { color: '#64748b' },
  actionRow: {
    display: 'flex',
    gap: '8px',
    flexWrap: 'wrap',
    minWidth: 0,
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
