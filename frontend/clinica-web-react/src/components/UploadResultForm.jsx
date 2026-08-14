import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FiArrowLeft, FiUpload, FiX, FiFile } from 'react-icons/fi';
import api from '../services/api';
import { getCache, setCache, invalidateCachePrefix, removeCache } from '../services/EstudiosCache';
import { useTranslation } from 'react-i18next';

const CACHE_KEYS = {
  counts: 'estudios_counts',
  examenInfo: (id) => `examen_info_${id}`,
};

export default function UploadResultForm() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  
  const id_examen = queryParams.get('id_examen');
  const tipo = queryParams.get('tipo') || 'LABORATORIO';
  const pacienteParam = queryParams.get('paciente');
  const habitacionParam = queryParams.get('habitacion');
  const estudiosParam = queryParams.get('estudios');
  const returnSection = queryParams.get('returnSection') || 'solicitudes_lab';

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [solicitud, setSolicitud] = useState(null);
  const [observaciones, setObservaciones] = useState('');
  const [archivos, setArchivos] = useState([]);
  const [error, setError] = useState('');

  const fileInputRef = useRef(null);

  useEffect(() => {
    if (!id_examen) {
      setError(t('studies.missingExamId'));
      setLoading(false);
      return;
    }

    const loadSolicitud = async () => {
      try {
        setLoading(true);
        let data = null;

        if (pacienteParam && habitacionParam && estudiosParam) {
          data = {
            paciente: pacienteParam,
            habitacion: habitacionParam,
            estudios: estudiosParam,
          };
          console.log('📦 Using data from query params');
        } else {
          const cacheKey = CACHE_KEYS.examenInfo(id_examen);
          let cached = await getCache(cacheKey);
          if (cached) {
            data = cached;
            console.log('📦 Using cache');
          } else {
            console.log('🌐 Loading from API');
            const response = await api.get(`/exams/${id_examen}/info`);
            data = response.data;
            await setCache(cacheKey, data);
          }
        }

        setSolicitud(data);
        setError('');
      } catch (err) {
        console.error('Error loading request:', err);
        setError(t('studies.loadInfoError', { error: err.message || t('studies.unknownError') }));
      } finally {
        setLoading(false);
      }
    };

    loadSolicitud();
  }, [id_examen, pacienteParam, habitacionParam, estudiosParam, t]);

  const pickDocuments = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event) => {
    const files = event.target.files;
    if (files.length === 0) return;

    const selectedFiles = Array.from(files).map(file => ({
      file: file,
      name: file.name,
      type: file.type,
      size: file.size,
    }));

    setArchivos(prev => {
      const existingNames = new Set(prev.map(f => f.name));
      const newFiles = selectedFiles.filter(f => !existingNames.has(f.name));
      return [...prev, ...newFiles];
    });

    event.target.value = '';
  };

  const removeFile = (index) => {
    setArchivos(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (archivos.length === 0) {
      window.alert(t('studies.selectAtLeastOneFile'));
      return;
    }

    const MAX_SIZE = 25 * 1024 * 1024;
    for (const archivo of archivos) {
      if (archivo.size > MAX_SIZE) {
        window.alert(t('studies.fileTooLarge', { file: archivo.name }));
        return;
      }
    }

    setSubmitting(true);

    try {
      const formData = new FormData();
      archivos.forEach(({ file, name }) => {
        formData.append('archivos', file, name);
      });
      formData.append('observaciones', observaciones);
      formData.append('type', tipo);

      await api.post(`/exams/${id_examen}/results/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000,
      });

      // Invalidate only caches of this type
      await invalidateCachePrefix(`estudios_all_${tipo}_`);
      await removeCache(CACHE_KEYS.counts);
      await removeCache(CACHE_KEYS.examenInfo(id_examen));

      window.alert(t('studies.uploadSuccess'));
      navigate(`/estudios?initialSection=${returnSection}`);
    } catch (err) {
      console.error('Error uploading:', err);
      let msg = t('studies.uploadError');
      if (err.response?.data?.error) msg = err.response.data.error;
      else if (err.message) msg = err.message;
      window.alert(msg);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div style={styles.page}>
        <div style={styles.centered}>
          <div style={styles.spinner}></div>
          <span style={styles.loadingText}>{t('studies.loadingData')}</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.page}>
        <div style={styles.centered}>
          <div style={styles.errorText}>{error}</div>
          <button style={styles.retryBtn} onClick={() => navigate(-1)}>{t('studies.goBack')}</button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.page}>
      {/* Header */}
      <div style={styles.header}>
        <button type="button" onClick={() => navigate(-1)} style={styles.headerButton}>
          <FiArrowLeft size={20} />
        </button>
        <div>
          <div style={styles.headerEyebrow}>{t('studies.results')}</div>
          <h1 style={styles.headerTitle}>{t('studies.uploadResults')}</h1>
        </div>
        <div style={{ width: 44 }}></div>
      </div>

      {/* Hero / Info Card */}
      <div style={styles.heroCard}>
        <div style={styles.heroInfo}>
          <p style={styles.heroGreeting}>{t('studies.patientDetails')}</p>
          <p style={styles.heroDate}>
            {solicitud?.paciente || t('studies.patient')} • 🛏️ {solicitud?.habitacion || 'N/A'}
          </p>
          <p style={styles.heroStudy}>📋 {solicitud?.estudios || t('studies.noStudies')}</p>
        </div>
        <div style={styles.heroPill}>
          {tipo === 'LABORATORIO' ? t('studies.laboratory') : t('studies.imaging')}
        </div>
      </div>

      {/* File Selection Card */}
      <div style={styles.card}>
        <div style={styles.cardTitle}>{t('studies.selectFiles')}</div>
        <button style={styles.pickBtn} onClick={pickDocuments}>
          <FiUpload size={18} /> {t('studies.chooseFiles')}
        </button>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          multiple
          accept=".pdf,.png,.jpg,.jpeg"
          style={{ display: 'none' }}
        />

        {archivos.length > 0 && (
          <div style={styles.fileList}>
            {archivos.map((archivo, index) => (
              <div key={index} style={styles.fileItem}>
                <FiFile style={styles.fileIcon} />
                <span style={styles.fileName}>{archivo.name}</span>
                <span style={styles.fileSize}>
                  {(archivo.size / 1024 / 1024).toFixed(2)} MB
                </span>
                <button style={styles.removeFileBtn} onClick={() => removeFile(index)}>
                  <FiX size={16} />
                </button>
              </div>
            ))}
          </div>
        )}

        <div style={styles.hint}>{t('studies.formatsHint')}</div>
      </div>

      {/* Observations Card */}
      <div style={styles.card}>
        <div style={styles.cardTitle}>{t('studies.observations')}</div>
        <textarea
          style={styles.textarea}
          rows="4"
          placeholder={t('studies.observationsPlaceholder')}
          value={observaciones}
          onChange={(e) => setObservaciones(e.target.value)}
        />
      </div>

      {/* Submit Button */}
      <button
        style={{
          ...styles.submitBtn,
          opacity: submitting ? 0.7 : 1,
          cursor: submitting ? 'default' : 'pointer',
        }}
        onClick={handleSubmit}
        disabled={submitting}
      >
        {submitting ? (
          <div style={styles.spinnerSmall}></div>
        ) : (
          <>
            <FiUpload size={18} /> {t('studies.uploadResults')}
          </>
        )}
      </button>

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
    display: 'flex',
    flexDirection: 'column',
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
    flexWrap: 'wrap',
  },
  heroInfo: { flex: 1 },
  heroGreeting: { margin: 0, fontSize: '20px', fontWeight: 700, color: '#1e293b' },
  heroDate: { margin: '4px 0 0', color: '#64748b', fontSize: '15px' },
  heroStudy: { margin: '4px 0 0', color: '#334155', fontSize: '14px', wordBreak: 'break-word' },
  heroPill: {
    padding: '10px 16px',
    borderRadius: '999px',
    backgroundColor: '#dbeafe',
    color: '#1d4ed8',
    fontWeight: 700,
    whiteSpace: 'nowrap',
    fontSize: '14px',
  },
  card: {
    marginTop: '18px',
    padding: '20px 24px',
    backgroundColor: '#fff',
    borderRadius: '20px',
    boxShadow: '0 12px 32px rgba(15, 23, 42, 0.08)',
  },
  cardTitle: {
    fontSize: '18px',
    fontWeight: 700,
    color: '#1e293b',
    marginBottom: '14px',
  },
  pickBtn: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    padding: '10px 20px',
    borderRadius: '999px',
    border: 'none',
    backgroundColor: '#4299e1',
    color: '#fff',
    fontWeight: 600,
    fontSize: '15px',
    cursor: 'pointer',
    transition: 'background 0.2s',
  },
  fileList: {
    marginTop: '14px',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  fileItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '10px 14px',
    backgroundColor: '#f1f5f9',
    borderRadius: '12px',
  },
  fileIcon: { color: '#64748b', fontSize: '20px' },
  fileName: { flex: 1, fontSize: '14px', fontWeight: 500, color: '#1e293b' },
  fileSize: { fontSize: '13px', color: '#64748b' },
  removeFileBtn: {
    background: 'transparent',
    border: 'none',
    color: '#ef4444',
    cursor: 'pointer',
    padding: '4px',
    display: 'grid',
    placeItems: 'center',
    borderRadius: '8px',
  },
  hint: {
    marginTop: '12px',
    fontSize: '13px',
    color: '#94a3b8',
  },
  textarea: {
    width: '100%',
    padding: '12px 14px',
    borderRadius: '12px',
    border: '1px solid #e2e8f0',
    fontSize: '14px',
    fontFamily: 'inherit',
    resize: 'vertical',
    backgroundColor: '#f8fafc',
    transition: 'border 0.2s',
    outline: 'none',
  },
  submitBtn: {
    marginTop: '20px',
    padding: '14px 24px',
    borderRadius: '999px',
    border: 'none',
    backgroundColor: '#48bb78',
    color: '#fff',
    fontWeight: 700,
    fontSize: '16px',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    width: '100%',
    maxWidth: '300px',
    alignSelf: 'center',
    transition: 'background 0.2s, opacity 0.2s',
    cursor: 'pointer',
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
  centered: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '50vh',
    gap: '16px',
  },
  spinner: {
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    border: '4px solid #e2e8f0',
    borderTopColor: '#2563eb',
    animation: 'spin 0.8s linear infinite',
  },
  spinnerSmall: {
    width: '20px',
    height: '20px',
    borderRadius: '50%',
    border: '3px solid rgba(255,255,255,0.3)',
    borderTopColor: '#fff',
    animation: 'spin 0.8s linear infinite',
  },
  loadingText: { color: '#64748b', fontSize: '16px' },
  errorText: { color: '#dc2626', fontSize: '16px', textAlign: 'center' },
  retryBtn: {
    padding: '10px 24px',
    borderRadius: '999px',
    border: 'none',
    backgroundColor: '#4299e1',
    color: '#fff',
    fontWeight: 600,
    cursor: 'pointer',
    fontSize: '15px',
  },
};
