import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FiArrowLeft, FiEye, FiFolder, FiFile } from 'react-icons/fi';
import api from '../services/api';
import { useTranslation } from 'react-i18next';

export default function ViewResultForm() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const id_examen = queryParams.get('id_examen');
  const tipo = queryParams.get('tipo') || 'LABORATORIO';

  const [loading, setLoading] = useState(true);
  const [archivos, setArchivos] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState('');

  // Obtener la URL base del servidor (sin /api/v1)
  const baseUrl = api.defaults.baseURL?.replace('/api/v1', '') || '';

  useEffect(() => {
    const loadFiles = async () => {
      if (!id_examen) {
        setError(t('studies.missingExamId'));
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await api.get(`/exams/${id_examen}/files`, {
          params: { type: tipo },
        });
        setArchivos(response.data);
        if (response.data.length > 0) {
          setSelectedFile(response.data[0]);
        }
        setError('');
      } catch (err) {
        console.error('Error loading files:', err);
        setError(t('studies.couldNotLoadFiles'));
      } finally {
        setLoading(false);
      }
    };
    loadFiles();
  }, [id_examen, tipo, t]);

  const handleSelectFile = (file) => {
    setSelectedFile(file);
  };

  // Render preview
  const renderPreview = () => {
    if (!selectedFile) {
      return (
        <div style={styles.previewPlaceholder}>
          <FiFile size={48} color="#cbd5e0" />
          <p style={styles.placeholderText}>{t('studies.selectAFile')}</p>
          <p style={styles.placeholderSubtext}>
            {t('studies.clickFileToPreview')}
          </p>
        </div>
      );
    }

    const ext = selectedFile.tipo?.toLowerCase();
    const fileUrl = `${baseUrl}${selectedFile.url}`;

    if (ext === 'pdf') {
      return (
        <div style={styles.previewPdf}>
          <div style={styles.pdfIconWrapper}>
            <FiFile size={56} color="#667eea" />
          </div>
          <p style={styles.pdfName}>{selectedFile.nombre}</p>
          <div style={styles.pdfBadge}>PDF</div>
          <p style={styles.pdfInfo}>{t('studies.previewAvailable')}</p>
        </div>
      );
    } else if (['png', 'jpg', 'jpeg', 'gif'].includes(ext)) {
      return (
        <div style={styles.imageContainer}>
          <img
            src={fileUrl}
            alt={selectedFile.nombre}
            style={styles.previewImage}
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = '';
            }}
          />
        </div>
      );
    } else {
      return (
        <div style={styles.previewPlaceholder}>
          <FiFile size={48} color="#a0aec0" />
          <p style={styles.placeholderText}>{t('studies.unsupportedFormat')}</p>
          <p style={styles.placeholderSubtext}>
            {t('studies.cannotPreview')}
          </p>
        </div>
      );
    }
  };

  if (loading) {
    return (
      <div style={styles.page}>
        <div style={styles.centered}>
          <div style={styles.spinner}></div>
          <span style={styles.loadingText}>{t('studies.loadingFiles')}</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.page}>
        <div style={styles.centered}>
          <FiFile size={48} color="#e53e3e" />
          <p style={styles.errorText}>{error}</p>
          <button style={styles.retryBtn} onClick={() => navigate(-1)}>
            {t('studies.goBack')}
          </button>
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
          <h1 style={styles.headerTitle}>{t('studies.viewResults')}</h1>
        </div>
        <div style={{ width: 44 }}></div>
      </div>

      {/* Main content: two columns */}
      <div style={styles.main}>
        {/* File list card */}
        <div style={styles.cardList}>
          <div style={styles.sectionHeader}>
            <FiFolder size={20} color="#64748b" />
            <span style={styles.sectionTitle}>{t('studies.availableFiles')}</span>
            <span style={styles.badge}>{archivos.length}</span>
          </div>
          <div style={styles.fileList}>
            {archivos.length === 0 ? (
              <p style={styles.emptyText}>{t('studies.noFilesRegistered')}</p>
            ) : (
              archivos.map((file, index) => (
                <button
                  key={index}
                  style={{
                    ...styles.fileItem,
                    ...(selectedFile?.nombre === file.nombre ? styles.fileItemActive : {}),
                  }}
                  onClick={() => handleSelectFile(file)}
                >
                  <span style={styles.fileIcon}>
                    {file.tipo === 'pdf' ? '📄' : '🖼️'}
                  </span>
                  <span style={styles.fileName}>{file.nombre}</span>
                  <span style={styles.fileBadge}>{file.tipo.toUpperCase()}</span>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Preview card */}
        <div style={styles.cardPreview}>
          <div style={styles.sectionHeader}>
            <FiEye size={20} color="#64748b" />
            <span style={styles.sectionTitle}>{t('studies.preview')}</span>
          </div>
          <div style={styles.previewBox}>{renderPreview()}</div>
        </div>
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
  main: {
    marginTop: '20px',
    display: 'flex',
    gap: '20px',
    flexWrap: 'wrap',
  },
  cardList: {
    flex: '1 1 300px',
    minWidth: '260px',
    padding: '20px 24px',
    backgroundColor: '#fff',
    borderRadius: '20px',
    boxShadow: '0 12px 32px rgba(15, 23, 42, 0.08)',
    display: 'flex',
    flexDirection: 'column',
  },
  cardPreview: {
    flex: '2 1 400px',
    minWidth: '300px',
    padding: '20px 24px',
    backgroundColor: '#fff',
    borderRadius: '20px',
    boxShadow: '0 12px 32px rgba(15, 23, 42, 0.08)',
    display: 'flex',
    flexDirection: 'column',
  },
  sectionHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginBottom: '16px',
    paddingBottom: '12px',
    borderBottom: '1px solid #e2e8f0',
  },
  sectionTitle: {
    fontSize: '16px',
    fontWeight: 700,
    color: '#1e293b',
  },
  badge: {
    marginLeft: 'auto',
    padding: '2px 10px',
    borderRadius: '999px',
    backgroundColor: '#dbeafe',
    color: '#1d4ed8',
    fontWeight: 700,
    fontSize: '14px',
  },
  fileList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
    flex: 1,
    overflowY: 'auto',
    maxHeight: '400px',
  },
  fileItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '10px 14px',
    borderRadius: '12px',
    border: '1px solid transparent',
    background: '#f8fafc',
    cursor: 'pointer',
    transition: 'all 0.2s',
    textAlign: 'left',
    width: '100%',
    fontFamily: 'inherit',
  },
  fileItemActive: {
    borderColor: '#2563eb',
    backgroundColor: '#eff6ff',
    boxShadow: '0 0 0 1px #2563eb',
  },
  fileIcon: { fontSize: '20px' },
  fileName: {
    flex: 1,
    fontSize: '14px',
    fontWeight: 500,
    color: '#1e293b',
    wordBreak: 'break-word',
  },
  fileBadge: {
    padding: '2px 10px',
    borderRadius: '999px',
    backgroundColor: '#e2e8f0',
    color: '#475569',
    fontSize: '11px',
    fontWeight: 700,
    textTransform: 'uppercase',
  },
  emptyText: { color: '#94a3b8', fontSize: '14px', textAlign: 'center', padding: '20px 0' },
  previewBox: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '300px',
    backgroundColor: '#f8fafc',
    borderRadius: '16px',
    padding: '16px',
  },
  previewPlaceholder: {
    textAlign: 'center',
    color: '#94a3b8',
  },
  placeholderText: { fontSize: '18px', fontWeight: 600, color: '#64748b', marginTop: '8px' },
  placeholderSubtext: { fontSize: '14px', color: '#94a3b8', marginTop: '4px' },
  previewPdf: {
    textAlign: 'center',
  },
  pdfIconWrapper: {
    display: 'inline-block',
    padding: '16px',
    backgroundColor: '#e0e7ff',
    borderRadius: '16px',
    marginBottom: '12px',
  },
  pdfName: { fontSize: '16px', fontWeight: 600, color: '#1e293b', marginBottom: '4px' },
  pdfBadge: {
    display: 'inline-block',
    padding: '4px 12px',
    borderRadius: '999px',
    backgroundColor: '#dc2626',
    color: '#fff',
    fontWeight: 700,
    fontSize: '13px',
  },
  pdfInfo: { fontSize: '14px', color: '#64748b', marginTop: '12px' },
  imageContainer: {
    width: '100%',
    height: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  previewImage: {
    maxWidth: '100%',
    maxHeight: '400px',
    borderRadius: '12px',
    objectFit: 'contain',
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
