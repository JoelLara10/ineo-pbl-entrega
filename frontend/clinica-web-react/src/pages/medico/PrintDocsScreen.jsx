import { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { FiArrowLeft, FiClock, FiFileText, FiPrinter, FiShield, FiUser } from 'react-icons/fi';
import { MdMedication, MdOutlineScreenshotMonitor } from 'react-icons/md';
import { usePatient } from '../../context/PatientContext';
import api from '../../services/api';
import { useTranslation } from 'react-i18next';

function getPatientName(patientInfo) {
  if (!patientInfo) return 'Paciente';
  return [patientInfo.papell, patientInfo.sapell, patientInfo.nom_pac].filter(Boolean).join(' ') || 'Paciente';
}

const PRINT_HISTORY_KEY = '@ineo_print_history';
const PRINT_HISTORY_LIMIT = 5;

function loadPrintHistory() {
  if (typeof window === 'undefined') return [];

  try {
    const storedHistory = JSON.parse(window.localStorage.getItem(PRINT_HISTORY_KEY) || '[]');
    return Array.isArray(storedHistory) ? storedHistory.slice(0, PRINT_HISTORY_LIMIT) : [];
  } catch {
    return [];
  }
}

export default function PrintDocsScreen() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { selectedPatient } = usePatient();
  const idAtencion = selectedPatient?.id_atencion || location.state?.id_atencion;
  const idExp = selectedPatient?.Id_exp || location.state?.Id_exp;
  const [loading, setLoading] = useState(true);
  const [loadingDoc, setLoadingDoc] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [patientInfo, setPatientInfo] = useState(null);
  const [printHistory, setPrintHistory] = useState(loadPrintHistory);

  const patientLabel = useMemo(() => `Exp: ${idExp || 'N/A'} | Atención: ${idAtencion || 'N/A'}`, [idAtencion, idExp]);

  const savePrintedDocument = (documentType) => {
    const documentItem = printItems.find((item) => item.id === documentType);
    if (!documentItem) return;

    const newEntry = {
      id: `${Date.now()}-${documentType}`,
      documentType,
      patientName: getPatientName(patientInfo),
      idExp: idExp || 'N/A',
      idAtencion: idAtencion || 'N/A',
      printedAt: new Date().toISOString(),
    };

    setPrintHistory((currentHistory) => {
      const updatedHistory = [newEntry, ...currentHistory].slice(0, PRINT_HISTORY_LIMIT);
      window.localStorage.setItem(PRINT_HISTORY_KEY, JSON.stringify(updatedHistory));
      return updatedHistory;
    });
  };

  useEffect(() => {
    if (!idAtencion || !idExp) {
      setErrorMessage(t('printDocs.selectPatientFirst'));
      setLoading(false);
      return;
    }

    setErrorMessage('');

    const loadPatientInfo = async () => {
      setLoading(true);
      try {
        const response = await api.get(`/paciente/${idAtencion}/${idExp}`);
        setPatientInfo(response.data?.paciente || null);
      } catch (error) {
        console.error('Error loading patient info for print docs:', error);
        setErrorMessage(t('printDocs.errorLoading'));
      } finally {
        setLoading(false);
      }
    };

    loadPatientInfo();
  }, [idAtencion, idExp]);

  const openPdfUrl = (path) => {
    const token = typeof window !== 'undefined' ? window.localStorage.getItem('@ineo_token') : '';
    if (!token) {
      window.alert(t('printDocs.noActiveSession'));
      return false;
    }
    const baseUrl = (api.defaults.baseURL || '').replace(/\/$/, '');
    const query = new URLSearchParams({
      token,
      id_atencion: String(idAtencion),
    }).toString();
    const url = `${baseUrl}${path}?${query}`;
    window.open(url, '_blank', 'noopener,noreferrer');
    return true;
  };

  const handlePrint = async (documentType) => {
    if (!idAtencion) return;

    setLoadingDoc(documentType);
    try {
      switch (documentType) {
        case 'vital-signs': {
          const response = await api.get(`/appointments/${idAtencion}/vital-signs`);
          const lastItem = Array.isArray(response.data) ? response.data[0] : null;
          if (!lastItem?.id_signos) throw new Error('No hay signos vitales');
          if (!openPdfUrl(`/pdf/vital-signs/${lastItem.id_signos}`)) return;
          break;
        }
        case 'medical-note': {
          const response = await api.get(`/appointments/${idAtencion}/medical-notes`);
          const lastItem = Array.isArray(response.data) ? response.data[0] : null;
          if (!lastItem?.id_nota) throw new Error('No hay notas médicas');
          if (!openPdfUrl(`/pdf/medical-note/${lastItem.id_nota}`)) return;
          break;
        }
        case 'diagnosis': {
          const response = await api.get(`/appointments/${idAtencion}/diagnosis`);
          if (!response.data?.id_diagnostico) throw new Error('No hay diagnóstico');
          if (!openPdfUrl(`/pdf/diagnosis/${response.data.id_diagnostico}`)) return;
          break;
        }
        case 'prescription': {
          const response = await api.get(`/appointments/${idAtencion}/prescriptions`);
          const lastItem = Array.isArray(response.data) ? response.data[0] : null;
          if (!lastItem?.id_receta) throw new Error('No hay recetas');
          if (!openPdfUrl(`/pdf/prescription/${lastItem.id_receta}`)) return;
          break;
        }
        case 'lab-exams': {
          const response = await api.get(`/exams/requested/${idAtencion}?type=LABORATORIO`);
          const lastItem = Array.isArray(response.data) ? response.data[0] : null;
          if (!lastItem?.id_examen) throw new Error('No hay exámenes de laboratorio');
          if (!openPdfUrl(`/pdf/lab/${lastItem.id_examen}`)) return;
          break;
        }
        case 'imaging-exams': {
          const response = await api.get(`/exams/requested/${idAtencion}?type=GABINETE`);
          const lastItem = Array.isArray(response.data) ? response.data[0] : null;
          if (!lastItem?.id_examen) throw new Error('No hay exámenes de gabinete');
          if (!openPdfUrl(`/pdf/imaging/${lastItem.id_examen}`)) return;
          break;
        }
        default:
          return;
      }
      savePrintedDocument(documentType);
    } catch (error) {
      console.error('Error printing document:', error);
      window.alert(error.message || 'No se pudo preparar el documento para imprimir');
    } finally {
      setLoadingDoc('');
    }
  };

  const printItems = [
    { id: 'vital-signs', title: t('printDocs.vitalSigns'), description: t('printDocs.vitalSignsDesc'), icon: FiFileText, color: '#dc2626', accent: '#fef2f2' },
    { id: 'medical-note', title: t('printDocs.medicalNote'), description: t('printDocs.medicalNoteDesc'), icon: FiFileText, color: '#2563eb', accent: '#eff6ff' },
    { id: 'diagnosis', title: t('printDocs.diagnosis'), description: t('printDocs.diagnosisDesc'), icon: FiFileText, color: '#16a34a', accent: '#f0fdf4' },
    { id: 'prescription', title: t('printDocs.prescription'), description: t('printDocs.prescriptionDesc'), icon: MdMedication, color: '#ea580c', accent: '#fff7ed' },
    { id: 'lab-exams', title: t('printDocs.labExams'), description: t('printDocs.labExamsDesc'), icon: FiFileText, color: '#0ea5e9', accent: '#f0f9ff' },
    { id: 'imaging-exams', title: t('printDocs.imagingExams'), description: t('printDocs.imagingExamsDesc'), icon: MdOutlineScreenshotMonitor, color: '#7c3aed', accent: '#faf5ff' },
  ];

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <button type="button" onClick={() => navigate(-1)} style={styles.headerButton}><FiArrowLeft size={20} /></button>
        <div>
          <div style={styles.headerEyebrow}>MÉDICO</div>
          <h1 style={styles.headerTitle}>{t('printDocs.title')}</h1>
        </div>
        <div style={styles.headerSpacer} />
      </div>

      <section style={styles.patientCard}>
        <div style={styles.patientAvatar}><FiUser size={30} color="#fff" /></div>
        <div>
          <h2 style={styles.patientName}>{getPatientName(patientInfo)}</h2>
          <p style={styles.patientMeta}>{patientLabel}</p>
        </div>
      </section>

      {loading ? <div style={styles.loadingCard}>{t('printDocs.loading')}</div> : errorMessage ? <div style={styles.errorCard}>{errorMessage}</div> : (
        <section style={styles.mainCard}>
          <div style={styles.cardHeader}><FiPrinter size={20} /><strong>{t('printDocs.selectDoc')}</strong></div>
          <div style={styles.cardBody}>
            <div style={styles.grid}>
              {printItems.map((item) => {
                const Icon = item.icon;
                const isBusy = loadingDoc === item.id;
                return (
                  <button key={item.id} type="button" style={{ ...styles.printCard, backgroundColor: item.accent }} onClick={() => handlePrint(item.id)} disabled={Boolean(loadingDoc)}>
                    <div style={{ ...styles.printIcon, backgroundColor: item.color }}><Icon size={22} color="#fff" /></div>
                    <div style={styles.printContent}>
                      <strong style={{ ...styles.printTitle, color: item.color }}>{item.title}</strong>
                      <span style={styles.printDescription}>{item.description}</span>
                    </div>
                    <span style={{ ...styles.printAction, color: item.color }}>{isBusy ? t('printDocs.preparing') : t('printDocs.print')}</span>
                  </button>
                );
              })}
            </div>
            <div style={styles.historySection}>
              <div style={styles.historyHeader}>
                <div style={styles.historyTitle}><FiClock size={18} /><strong>{t('printDocs.recentHistory')}</strong></div>
                <span style={styles.historyLimit}>{t('printDocs.lastDocuments', { count: PRINT_HISTORY_LIMIT })}</span>
              </div>

              {printHistory.length === 0 ? (
                <div style={styles.emptyHistory}>{t('printDocs.noPrintHistory')}</div>
              ) : (
                <div style={styles.historyList}>
                  {printHistory.map((entry) => {
                    const documentItem = printItems.find((item) => item.id === entry.documentType);
                    return (
                      <div key={entry.id} style={styles.historyItem}>
                        <div style={{ ...styles.historyIcon, backgroundColor: documentItem?.accent || '#f8fafc', color: documentItem?.color || '#475569' }}>
                          <FiPrinter size={17} />
                        </div>
                        <div style={styles.historyContent}>
                          <strong style={styles.historyDocument}>{documentItem?.title || entry.documentType}</strong>
                          <span style={styles.historyPatient}>{entry.patientName}</span>
                          <span style={styles.historyMeta}>{t('printDocs.historyIds', { idExp: entry.idExp, idAtencion: entry.idAtencion })}</span>
                        </div>
                        <time style={styles.historyDate} dateTime={entry.printedAt}>
                          {new Intl.DateTimeFormat(i18n.language, { dateStyle: 'short', timeStyle: 'short' }).format(new Date(entry.printedAt))}
                        </time>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
            <div style={styles.noteBox}>{t('printDocs.docsNote')}</div>
          </div>
        </section>
      )}

      <footer style={styles.footer}><FiShield size={14} /><span>{t('printDocs.footer')}</span></footer>
    </div>
  );
}

const styles = {
  page: { minHeight: '100%', padding: '24px', background: 'linear-gradient(180deg, #eef2ff 0%, #e0e7ff 100%)' },
  header: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px', padding: '20px 24px', borderRadius: '22px', background: 'linear-gradient(135deg, #4f46e5 0%, #4338ca 100%)', color: '#fff', boxShadow: '0 18px 50px rgba(79, 70, 229, 0.22)' },
  headerButton: { width: '44px', height: '44px', border: '1px solid rgba(255,255,255,0.24)', borderRadius: '12px', background: 'rgba(255,255,255,0.12)', color: '#fff', display: 'grid', placeItems: 'center' },
  headerEyebrow: { fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.18em', opacity: 0.8, marginBottom: '4px' },
  headerTitle: { margin: 0, fontSize: '28px', fontWeight: 800 },
  headerSpacer: { width: '44px', height: '44px' },
  patientCard: { marginTop: '20px', padding: '18px 20px', borderRadius: '20px', backgroundColor: '#fff', display: 'flex', alignItems: 'center', gap: '16px', boxShadow: '0 12px 32px rgba(15, 23, 42, 0.08)', borderLeft: '5px solid #4f46e5' },
  patientAvatar: { width: '56px', height: '56px', borderRadius: '16px', backgroundColor: '#4f46e5', display: 'grid', placeItems: 'center' },
  patientName: { margin: 0, color: '#0f172a', fontSize: '18px' },
  patientMeta: { margin: '6px 0 0', color: '#64748b' },
  loadingCard: { marginTop: '18px', padding: '30px', borderRadius: '20px', backgroundColor: '#fff', textAlign: 'center', boxShadow: '0 14px 36px rgba(15, 23, 42, 0.08)' },
  errorCard: { marginTop: '18px', padding: '16px', borderRadius: '16px', backgroundColor: '#fff7ed', border: '1px solid #fdba74', color: '#9a3412' },
  mainCard: { marginTop: '18px', borderRadius: '24px', overflow: 'hidden', backgroundColor: '#fff', boxShadow: '0 14px 36px rgba(15, 23, 42, 0.08)' },
  cardHeader: { display: 'flex', alignItems: 'center', gap: '10px', padding: '18px 22px', background: 'linear-gradient(135deg, #4f46e5 0%, #4338ca 100%)', color: '#fff' },
  cardBody: { padding: '20px' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px' },
  printCard: { display: 'flex', alignItems: 'center', gap: '14px', padding: '18px', borderRadius: '18px', border: '1px solid #e2e8f0', textAlign: 'left' },
  printIcon: { width: '48px', height: '48px', borderRadius: '14px', display: 'grid', placeItems: 'center', flexShrink: 0 },
  printContent: { flex: 1, minWidth: 0 },
  printTitle: { display: 'block', marginBottom: '6px' },
  printDescription: { color: '#475569', fontSize: '14px', lineHeight: 1.4 },
  printAction: { fontWeight: 700, fontSize: '13px' },
  noteBox: { marginTop: '18px', padding: '16px', borderRadius: '16px', backgroundColor: '#eef2ff', color: '#312e81' },
  historySection: { marginTop: '20px', paddingTop: '20px', borderTop: '1px solid #e2e8f0' },
  historyHeader: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', marginBottom: '12px' },
  historyTitle: { display: 'flex', alignItems: 'center', gap: '8px', color: '#312e81' },
  historyLimit: { color: '#64748b', fontSize: '12px' },
  emptyHistory: { padding: '20px', borderRadius: '14px', backgroundColor: '#f8fafc', color: '#64748b', textAlign: 'center' },
  historyList: { display: 'grid', gap: '10px' },
  historyItem: { display: 'flex', alignItems: 'center', gap: '12px', padding: '13px 14px', borderRadius: '14px', border: '1px solid #e2e8f0', backgroundColor: '#fff' },
  historyIcon: { width: '38px', height: '38px', borderRadius: '11px', display: 'grid', placeItems: 'center', flexShrink: 0 },
  historyContent: { display: 'grid', gap: '2px', flex: 1, minWidth: 0 },
  historyDocument: { color: '#0f172a', fontSize: '14px' },
  historyPatient: { color: '#475569', fontSize: '13px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' },
  historyMeta: { color: '#64748b', fontSize: '12px' },
  historyDate: { color: '#475569', fontSize: '12px', textAlign: 'right', flexShrink: 0 },
  footer: { marginTop: '26px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', color: '#312e81', fontSize: '13px' },
};
