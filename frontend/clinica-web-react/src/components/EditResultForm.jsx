import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FiArrowLeft, FiSave, FiFile } from 'react-icons/fi';
import api from '../services/api';
import { invalidateCachePrefix, removeCache } from '../services/EstudiosCache';
import { useTranslation } from 'react-i18next';

const CACHE_KEYS = {
  counts: 'estudios_counts',
  examenInfo: (id) => `examen_info_${id}`,
};

export default function EditResultForm() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);

  const id_examen = queryParams.get('id_examen');
  const tipo = queryParams.get('tipo') || 'LABORATORIO';
  const returnSection = queryParams.get('returnSection') || 'resultados_lab';

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [info, setInfo] = useState({
    paciente: '',
    habitacion: '',
    archivos: [],
    observaciones: '',
  });
  const [nuevosArchivos, setNuevosArchivos] = useState([]);
  const [archivosAEliminar, setArchivosAEliminar] = useState({});
  const [error, setError] = useState('');

  useEffect(() => {
    const loadInfo = async () => {
      if (!id_examen) {
        setError(t('studies.missingExamId'));
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await api.get(`/exams/${id_examen}/edit-info?type=${tipo}`);
        const data = response.data;

        setInfo({
          paciente: data.paciente || '',
          habitacion: data.habitacion || '',
          archivos: data.archivos || [],
          observaciones: data.observaciones || '',
        });

        const eliminarState = {};
        (data.archivos || []).forEach((nombre) => {
          eliminarState[nombre] = false;
        });
        setArchivosAEliminar(eliminarState);
        setError('');
      } catch (err) {
        console.error('Error loading info:', err);
        setError(t('studies.couldNotLoadInfo'));
      } finally {
        setLoading(false);
      }
    };

    loadInfo();
  }, [id_examen, tipo, t]);

  const handleFileChange = (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    const MAX_SIZE = 25 * 1024 * 1024;
    const validExtensions = ['pdf', 'png', 'jpg', 'jpeg'];

    const newFiles = files
      .filter((file) => {
        const ext = file.name.split('.').pop().toLowerCase();
        if (!validExtensions.includes(ext)) {
          alert(t('studies.invalidFileFormat', { file: file.name }));
          return false;
        }
        if (file.size > MAX_SIZE) {
          alert(t('studies.fileTooLarge', { file: file.name }));
          return false;
        }
        return true;
      })
      .map((file) => ({
        file,
        name: file.name,
        size: file.size,
        type: file.type,
        id: `${file.name}_${file.size}_${Date.now()}`,
      }));

    setNuevosArchivos((prev) => [...prev, ...newFiles]);
    e.target.value = '';
  };

  const removeNuevoArchivo = (id) => {
    setNuevosArchivos((prev) => prev.filter((f) => f.id !== id));
  };

  const toggleEliminar = (nombre) => {
    setArchivosAEliminar((prev) => ({
      ...prev,
      [nombre]: !prev[nombre],
    }));
  };

  const handleSubmit = async () => {
    const archivosExistentes = info.archivos.filter(
      (nombre) => !archivosAEliminar[nombre]
    );

    if (archivosExistentes.length === 0 && nuevosArchivos.length === 0) {
      alert(t('studies.keepOneFile'));
      return;
    }

    setSubmitting(true);

    try {
      const formData = new FormData();

      nuevosArchivos.forEach((item) => {
        formData.append('archivos', item.file, item.file.name);
      });

      const eliminarList = Object.keys(archivosAEliminar).filter(
        (nombre) => archivosAEliminar[nombre]
      );
      eliminarList.forEach((nombre) => {
        formData.append('eliminar_archivos', nombre);
      });

      formData.append('observaciones', info.observaciones);
      formData.append('type', tipo);

      await api.put(`/exams/${id_examen}/edit`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000,
      });

      // Invalidate only caches of this type
      await invalidateCachePrefix(`estudios_all_${tipo}_`);
      await removeCache(CACHE_KEYS.counts);
      await removeCache(CACHE_KEYS.examenInfo(id_examen));

      alert(t('studies.changesSaved'));
      navigate(`/estudios?initialSection=${returnSection}`);
    } catch (err) {
      console.error('Error updating:', err);
      let msg = t('studies.updateError');
      if (err.response?.data?.error) {
        msg = err.response.data.error;
      } else if (err.message) {
        msg = err.message;
      }
      alert(msg);
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
          <p style={styles.errorText}>{error}</p>
          <button style={styles.retryBtn} onClick={() => navigate(-1)}>
            {t('studies.goBack')}
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
      <div style={styles.page}>
        {/* Header */}
        <div style={styles.header}>
          <button type="button" onClick={() => navigate(-1)} style={styles.headerButton}>
            <FiArrowLeft size={20} />
          </button>
          <div>
            <div style={styles.headerEyebrow}>{t('studies.results')}</div>
            <h1 style={styles.headerTitle}>{t('studies.editResults')}</h1>
          </div>
          <div style={{ width: 44 }}></div>
        </div>

        {/* Content */}
        <div style={styles.content}>
          {/* Patient info card */}
          <div style={styles.card}>
            <div style={styles.infoRow}>
              <span style={styles.label}>{t('studies.patient')}:</span>
              <span style={styles.value}>{info.paciente}</span>
            </div>
            <div style={styles.infoRow}>
              <span style={styles.label}>{t('studies.room')}:</span>
              <span style={styles.value}>{info.habitacion}</span>
            </div>
          </div>

          {/* Existing files card */}
          <div style={styles.card}>
            <h3 style={styles.sectionTitle}>{t('studies.existingFiles')}</h3>
            {info.archivos.length === 0 ? (
              <p style={styles.emptyText}>{t('studies.noFilesRegistered')}</p>
            ) : (
              <ul style={styles.fileList}>
                {info.archivos.map((nombre) => (
                  <li key={nombre} style={styles.fileItem}>
                    <FiFile style={styles.fileIcon} />
                    <span style={styles.fileName}>{nombre}</span>
                    <label style={styles.switchLabel}>
                      <input
                        type="checkbox"
                        checked={archivosAEliminar[nombre] || false}
                        onChange={() => toggleEliminar(nombre)}
                        style={styles.checkbox}
                      />
                      <span style={styles.switchText}>{t('studies.delete')}</span>
                    </label>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Add new files card */}
          <div style={styles.card}>
            <h3 style={styles.sectionTitle}>{t('studies.addNewFiles')}</h3>
            <input
              type="file"
              multiple
              accept=".pdf,.png,.jpg,.jpeg"
              onChange={handleFileChange}
              style={styles.fileInput}
            />
            {nuevosArchivos.length > 0 && (
              <ul style={styles.fileList}>
                {nuevosArchivos.map((item) => (
                  <li key={item.id} style={styles.fileItem}>
                    <FiFile style={styles.fileIcon} />
                    <span style={styles.fileName}>{item.name}</span>
                    <span style={styles.fileSize}>
                      {(item.size / 1024 / 1024).toFixed(2)} MB
                    </span>
                    <button
                      style={styles.removeBtn}
                      onClick={() => removeNuevoArchivo(item.id)}
                    >
                      ✕
                    </button>
                  </li>
                ))}
              </ul>
            )}
            <p style={styles.hint}>{t('studies.formatsHint')}</p>
          </div>

          {/* Observations card */}
          <div style={styles.card}>
            <h3 style={styles.sectionTitle}>{t('studies.observations')}</h3>
            <textarea
              style={styles.textarea}
              rows="4"
              placeholder={t('studies.observationsPlaceholder')}
              value={info.observaciones}
              onChange={(e) => setInfo({ ...info, observaciones: e.target.value })}
            />
          </div>

          {/* Submit button */}
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
                <FiSave size={18} /> {t('studies.saveChanges')}
              </>
            )}
          </button>
        </div>

        <footer style={styles.footer}>
          <FiArrowLeft size={14} style={{ transform: 'rotate(180deg)' }} />
          <span>{t('studies.secureFooter')}</span>
        </footer>
      </div>
    </>
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
  content: {
    marginTop: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '18px',
  },
  card: {
    padding: '20px 24px',
    backgroundColor: '#fff',
    borderRadius: '20px',
    boxShadow: '0 12px 32px rgba(15, 23, 42, 0.08)',
  },
  infoRow: {
    display: 'flex',
    gap: '12px',
    padding: '6px 0',
    fontSize: '15px',
  },
  label: {
    fontWeight: 600,
    color: '#64748b',
    minWidth: '80px',
  },
  value: {
    color: '#1e293b',
    fontWeight: 500,
  },
  sectionTitle: {
    fontSize: '18px',
    fontWeight: 700,
    color: '#1e293b',
    margin: '0 0 14px 0',
  },
  fileList: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  fileItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '10px 14px',
    backgroundColor: '#f8fafc',
    borderRadius: '12px',
  },
  fileIcon: { color: '#64748b', fontSize: '18px' },
  fileName: { flex: 1, fontSize: '14px', fontWeight: 500, color: '#1e293b' },
  fileSize: { fontSize: '13px', color: '#64748b' },
  switchLabel: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    fontSize: '13px',
    color: '#64748b',
    cursor: 'pointer',
  },
  checkbox: { width: '16px', height: '16px', accentColor: '#ef4444' },
  switchText: { fontWeight: 500 },
  fileInput: {
    display: 'block',
    width: '100%',
    padding: '10px 12px',
    borderRadius: '12px',
    border: '1px dashed #cbd5e1',
    backgroundColor: '#f8fafc',
    fontSize: '14px',
    cursor: 'pointer',
    transition: 'border 0.2s',
    outline: 'none',
    marginBottom: '12px',
  },
  removeBtn: {
    background: 'transparent',
    border: 'none',
    color: '#ef4444',
    cursor: 'pointer',
    padding: '4px 6px',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: 700,
  },
  hint: {
    marginTop: '10px',
    fontSize: '13px',
    color: '#94a3b8',
  },
  emptyText: {
    color: '#94a3b8',
    fontSize: '14px',
    textAlign: 'center',
    padding: '12px 0',
  },
  textarea: {
    width: '100%',
    padding: '12px 14px',
    borderRadius: '12px',
    border: '1px solid #000000ff',
    fontSize: '14px',
    fontFamily: 'inherit',
    resize: 'vertical',
    backgroundColor: '#f8fafc',
    transition: 'border 0.2s',
    outline: 'none',
    color: '#000000ff',
  },
  submitBtn: {
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
