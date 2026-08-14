import { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { FiActivity, FiArrowLeft, FiDownload, FiFileText, FiPrinter, FiShield, FiUser } from 'react-icons/fi';
import { MdOutlineScreenshotMonitor } from 'react-icons/md';
import { usePatient } from '../../context/PatientContext';
import api from '../../services/api';
import moment from 'moment';
import 'moment/locale/es';
import { useTranslation } from 'react-i18next';

moment.locale('es');

function buildAssetUrl(path) {
  if (!path) return null;
  if (/^https?:\/\//i.test(path)) return path;
  const baseUrl = api.defaults.baseURL || '';
  return `${baseUrl.replace('/api/v1', '')}${path.startsWith('/') ? path : `/${path}`}`;
}

function getPatientName(paciente) {
  if (!paciente) return 'Paciente';
  return [paciente.papell, paciente.sapell, paciente.nom_pac].filter(Boolean).join(' ') || 'Paciente';
}

export default function StudyResultsScreen() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { selectedPatient } = usePatient();
  const idAtencion = selectedPatient?.id_atencion || location.state?.id_atencion;
  const idExp = selectedPatient?.Id_exp || location.state?.Id_exp;
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState('');
  const [patient, setPatient] = useState(null);
  const [labResults, setLabResults] = useState([]);
  const [imagingResults, setImagingResults] = useState([]);
  const [selectedExam, setSelectedExam] = useState(null);

  const patientLabel = useMemo(() => `Exp: ${idExp || 'N/A'} | Atención: ${idAtencion || 'N/A'}`, [idAtencion, idExp]);

  useEffect(() => {
    if (!idAtencion || !idExp) {
      setErrorMessage(t('studyResults.selectPatientFirst'));
      setLoading(false);
      return;
    }

    setErrorMessage('');

    const loadData = async () => {
      setLoading(true);
      try {
        const [patientResponse, labResponse, imagingResponse] = await Promise.all([
          api.get(`/paciente/${idAtencion}/${idExp}`),
          api.get(`/exams/patient/${idAtencion}?type=LABORATORIO`),
          api.get(`/exams/patient/${idAtencion}?type=GABINETE`),
        ]);

        setPatient(patientResponse.data?.paciente || null);
        setLabResults(Array.isArray(labResponse.data) ? labResponse.data : []);
        setImagingResults(Array.isArray(imagingResponse.data) ? imagingResponse.data : []);
      } catch (error) {
        console.error('Error loading study results:', error);
        setErrorMessage(t('studyResults.errorLoading'));
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [idAtencion, idExp]);

  const sections = [
    { key: 'lab', title: t('studyResults.labResults'), icon: FiActivity, color: '#0ea5e9', items: labResults },
    { key: 'imaging', title: t('studyResults.imagingResults'), icon: MdOutlineScreenshotMonitor, color: '#f59e0b', items: imagingResults },
  ];

  const renderResultCard = (item, color) => {
    const details = Array.isArray(item.detalles) ? item.detalles : [];
    const hasAttachment = details.some((detail) => detail.archivo_resultado);

    return (
      <article key={`${item.id_examen || item.fecha || 'exam'}_${item.tipo || 'tipo'}`} style={styles.resultCard}>
        <div style={styles.resultHeader}>
          <div>
            <div style={{ ...styles.resultDateBadge, backgroundColor: color }}>{moment(item.fecha).format('DD/MM')}</div>
          </div>
          <div style={styles.resultHeaderContent}>
            <strong style={styles.resultDate}>{moment(item.fecha).format('dddd, D [de] MMMM [de] YYYY [a las] HH:mm')}</strong>
            <span style={styles.resultMeta}>{t('studyResults.doctor')} {item.medico || t('studyResults.notSpecified')}</span>
          </div>
          <span style={{ ...styles.statusPill, backgroundColor: item.estado === 'REALIZADO' ? '#dcfce7' : '#fef3c7', color: item.estado === 'REALIZADO' ? '#166534' : '#92400e' }}>{item.estado || 'PENDIENTE'}</span>
        </div>

        <div style={styles.detailGrid}>
          {details.map((detail, index) => (
            <div key={`${detail.nombre || 'detalle'}-${index}`} style={styles.detailItem}>
              <div style={styles.detailTitleRow}>
                <strong style={styles.detailTitle}>{detail.nombre || 'Estudio'}</strong>
                <span style={{ ...styles.detailStatus, color: detail.estado === 'REALIZADO' ? '#16a34a' : '#d97706' }}>{detail.estado || 'PENDIENTE'}</span>
              </div>
              {detail.resultado ? <p style={styles.detailText}>{detail.resultado}</p> : <p style={styles.detailMuted}>{t('studyResults.noResultCaptured')}</p>}
            </div>
          ))}
        </div>

        {item.observaciones ? <p style={styles.observations}>{item.observaciones}</p> : null}

        <div style={styles.resultActions}>
          <button type="button" style={styles.secondaryButton} onClick={() => setSelectedExam(item)}><FiFileText size={16} /> {t('studyResults.viewDetail')}</button>
          {hasAttachment ? <button type="button" style={styles.primaryButton} onClick={() => {
            const detailWithFile = details.find((detail) => detail.archivo_resultado);
            const url = buildAssetUrl(detailWithFile?.archivo_resultado);
            if (url) window.open(url, '_blank', 'noopener,noreferrer');
          }}><FiDownload size={16} /> {t('studyResults.openAttachment')}</button> : null}
        </div>
      </article>
    );
  };

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <button type="button" onClick={() => navigate(-1)} style={styles.headerButton}><FiArrowLeft size={20} /></button>
        <div>
          <div style={styles.headerEyebrow}>MÉDICO</div>
          <h1 style={styles.headerTitle}>{t('studyResults.title')}</h1>
        </div>
        <div style={styles.headerSpacer} />
      </div>

      <section style={styles.patientCard}>
        <div style={styles.patientAvatar}><FiUser size={30} color="#fff" /></div>
        <div>
          <h2 style={styles.patientName}>{getPatientName(patient)}</h2>
          <p style={styles.patientMeta}>{patientLabel}</p>
        </div>
      </section>

      <section style={styles.shortcutCard}>
        <button type="button" style={styles.shortcutButton} onClick={() => navigate('/medico/lab-exams', { state: { id_atencion: idAtencion, Id_exp: idExp } })}>{t('studyResults.requestLab')}</button>
        <button type="button" style={styles.shortcutButton} onClick={() => navigate('/medico/imaging-exams', { state: { id_atencion: idAtencion, Id_exp: idExp } })}>{t('studyResults.requestImaging')}</button>
        <button type="button" style={styles.shortcutButtonPrimary} onClick={() => navigate('/medico/imprimir', { state: { id_atencion: idAtencion, Id_exp: idExp } })}><FiPrinter size={16} /> {t('studyResults.printDocs')}</button>
      </section>

      {loading ? <div style={styles.loadingCard}>{t('studyResults.loading')}</div> : errorMessage ? <div style={styles.errorCard}>{errorMessage}</div> : (
        <>
          {sections.map((section) => {
            const SectionIcon = section.icon;
            return (
              <section key={section.key} style={styles.sectionCard}>
                <div style={{ ...styles.sectionHeader, background: `linear-gradient(135deg, ${section.color} 0%, ${section.color}cc 100%)` }}>
                  <SectionIcon size={20} />
                  <strong>{section.title}</strong>
                  <span style={styles.sectionCount}>{section.items.length} registros</span>
                </div>
                <div style={styles.sectionBody}>
                  {section.items.length === 0 ? <div style={styles.statusBox}>{t('studyResults.noResults')}</div> : section.items.map((item) => renderResultCard(item, section.color))}
                </div>
              </section>
            );
          })}

          {selectedExam ? (
            <section style={styles.detailPanel}>
              <div style={styles.detailPanelHeader}>
                <strong>{t('studyResults.detailTitle')}</strong>
                <button type="button" style={styles.linkButton} onClick={() => setSelectedExam(null)}>{t('studyResults.close')}</button>
              </div>
              <div style={styles.detailPanelBody}>
                <div style={styles.detailPanelMeta}><span>{t('studyResults.date')}</span><strong>{moment(selectedExam.fecha).format('DD/MM/YYYY HH:mm')}</strong></div>
                <div style={styles.detailPanelMeta}><span>{t('studyResults.physician')}</span><strong>{selectedExam.medico || t('studyResults.notSpecified')}</strong></div>
                <div style={styles.detailPanelMeta}><span>{t('studyResults.observations')}</span><strong>{selectedExam.observaciones || t('studyResults.noObservations')}</strong></div>
                <div style={styles.detailResultsList}>
                  {(selectedExam.detalles || []).map((detail, index) => (
                    <div key={`${detail.nombre || 'detail'}-${index}`} style={styles.detailResultCard}>
                      <strong style={styles.detailResultTitle}>{detail.nombre || 'Estudio'}</strong>
                      <p style={styles.detailResultText}>{detail.resultado || t('studyResults.noResultCaptured')}</p>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          ) : null}
        </>
      )}

      <footer style={styles.footer}><FiShield size={14} /><span>{t('studyResults.footer')}</span></footer>
    </div>
  );
}

const styles = {
  page: { minHeight: '100%', padding: '24px', background: 'linear-gradient(180deg, #faf5ff 0%, #ede9fe 100%)' },
  header: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '16px', padding: '20px 24px', borderRadius: '22px', background: 'linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%)', color: '#fff', boxShadow: '0 18px 50px rgba(99, 102, 241, 0.22)' },
  headerButton: { width: '44px', height: '44px', border: '1px solid rgba(255,255,255,0.24)', borderRadius: '12px', background: 'rgba(255,255,255,0.12)', color: '#fff', display: 'grid', placeItems: 'center' },
  headerEyebrow: { fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.18em', opacity: 0.8, marginBottom: '4px' },
  headerTitle: { margin: 0, fontSize: '28px', fontWeight: 800 },
  headerSpacer: { width: '44px', height: '44px' },
  patientCard: { marginTop: '20px', padding: '18px 20px', borderRadius: '20px', backgroundColor: '#fff', display: 'flex', alignItems: 'center', gap: '16px', boxShadow: '0 12px 32px rgba(15, 23, 42, 0.08)', borderLeft: '5px solid #7c3aed' },
  patientAvatar: { width: '56px', height: '56px', borderRadius: '16px', backgroundColor: '#7c3aed', display: 'grid', placeItems: 'center' },
  patientName: { margin: 0, color: '#0f172a', fontSize: '18px' },
  patientMeta: { margin: '6px 0 0', color: '#64748b' },
  shortcutCard: { marginTop: '18px', display: 'flex', gap: '12px', flexWrap: 'wrap' },
  shortcutButton: { padding: '12px 18px', borderRadius: '14px', border: '1px solid #c4b5fd', backgroundColor: '#fff', color: '#5b21b6', fontWeight: 700 },
  shortcutButtonPrimary: { display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 18px', borderRadius: '14px', border: 'none', backgroundColor: '#4f46e5', color: '#fff', fontWeight: 700 },
  loadingCard: { marginTop: '18px', padding: '30px', borderRadius: '20px', backgroundColor: '#fff', textAlign: 'center', boxShadow: '0 14px 36px rgba(15, 23, 42, 0.08)' },
  errorCard: { marginTop: '18px', padding: '16px', borderRadius: '16px', backgroundColor: '#fff7ed', border: '1px solid #fdba74', color: '#9a3412' },
  sectionCard: { marginTop: '18px', borderRadius: '24px', overflow: 'hidden', backgroundColor: '#fff', boxShadow: '0 14px 36px rgba(15, 23, 42, 0.08)' },
  sectionHeader: { display: 'flex', alignItems: 'center', gap: '10px', padding: '18px 22px', color: '#fff' },
  sectionCount: { marginLeft: 'auto', padding: '4px 10px', borderRadius: '999px', backgroundColor: 'rgba(255,255,255,0.18)', fontSize: '12px' },
  sectionBody: { padding: '18px' },
  statusBox: { padding: '28px', borderRadius: '18px', textAlign: 'center', backgroundColor: '#f8fafc', color: '#64748b' },
  resultCard: { padding: '18px', borderRadius: '18px', border: '1px solid #e9d5ff', backgroundColor: '#faf5ff', marginBottom: '14px' },
  resultHeader: { display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '14px', flexWrap: 'wrap' },
  resultDateBadge: { minWidth: '58px', padding: '12px 10px', borderRadius: '14px', color: '#fff', fontWeight: 800, textAlign: 'center' },
  resultHeaderContent: { flex: 1, minWidth: '220px' },
  resultDate: { color: '#1e1b4b' },
  resultMeta: { display: 'block', marginTop: '4px', color: '#64748b', fontSize: '13px' },
  statusPill: { padding: '6px 10px', borderRadius: '999px', fontWeight: 700, fontSize: '12px' },
  detailGrid: { display: 'grid', gap: '10px', marginBottom: '12px' },
  detailItem: { padding: '14px', borderRadius: '14px', backgroundColor: '#fff', border: '1px solid #ede9fe' },
  detailTitleRow: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', marginBottom: '8px', flexWrap: 'wrap' },
  detailTitle: { color: '#312e81' },
  detailStatus: { fontWeight: 700, fontSize: '12px' },
  detailText: { margin: 0, color: '#334155', lineHeight: 1.5 },
  detailMuted: { margin: 0, color: '#94a3b8' },
  observations: { margin: '0 0 12px', color: '#475569', lineHeight: 1.5 },
  resultActions: { display: 'flex', gap: '10px', flexWrap: 'wrap' },
  secondaryButton: { display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 14px', borderRadius: '12px', border: '1px solid #c4b5fd', backgroundColor: '#fff', color: '#5b21b6', fontWeight: 700 },
  primaryButton: { display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 14px', borderRadius: '12px', border: 'none', backgroundColor: '#4f46e5', color: '#fff', fontWeight: 700 },
  detailPanel: { marginTop: '18px', borderRadius: '24px', overflow: 'hidden', backgroundColor: '#fff', boxShadow: '0 14px 36px rgba(15, 23, 42, 0.08)' },
  detailPanelHeader: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', padding: '18px 22px', backgroundColor: '#ede9fe', color: '#312e81' },
  linkButton: { border: 'none', background: 'transparent', color: '#4f46e5', fontWeight: 700 },
  detailPanelBody: { padding: '20px' },
  detailPanelMeta: { display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', padding: '12px 0', borderBottom: '1px solid #e2e8f0', color: '#475569' },
  detailResultsList: { display: 'grid', gap: '12px', marginTop: '18px' },
  detailResultCard: { padding: '14px', borderRadius: '14px', backgroundColor: '#f8fafc', border: '1px solid #e2e8f0' },
  detailResultTitle: { color: '#0f172a' },
  detailResultText: { margin: '8px 0 0', color: '#475569', lineHeight: 1.5 },
  footer: { marginTop: '26px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', color: '#5b21b6', fontSize: '13px' },
};
