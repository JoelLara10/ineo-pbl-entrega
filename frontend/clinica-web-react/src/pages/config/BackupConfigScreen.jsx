import { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FiDatabase, FiDownload, FiRefreshCw, FiRotateCcw, FiTrash2 } from 'react-icons/fi';
import ConfigHeader from './ConfigHeader';
import backupService from '../../services/backupService';
import './ConfigStyles.css';
import './BackupStyles.css';

const formatBytes = (bytes) => {
  if (!bytes) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  const index = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  return `${(bytes / (1024 ** index)).toFixed(index ? 1 : 0)} ${units[index]}`;
};

export default function BackupConfigScreen() {
  const { t, i18n } = useTranslation();
  const [backups, setBackups] = useState([]);
  const [collections, setCollections] = useState([]);
  const [selected, setSelected] = useState([]);
  const [type, setType] = useState('completa');
  const [format, setFormat] = useState('json');
  const [loading, setLoading] = useState(true);
  const [working, setWorking] = useState(false);
  const [message, setMessage] = useState('');
  const [health, setHealth] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [backupList, collectionList, dbHealth] = await Promise.all([
        backupService.list(), backupService.collections(), backupService.health(),
      ]);
      setBackups(backupList);
      setCollections(collectionList);
      setSelected(collectionList);
      setHealth(dbHealth);
    } catch (error) {
      setMessage(error.response?.data?.error || t('config.backupLoadError'));
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => { load(); }, [load]);

  const toggleCollection = (name) => setSelected((current) =>
    current.includes(name) ? current.filter((item) => item !== name) : [...current, name]
  );

  const create = async () => {
    if (!selected.length) return setMessage(t('config.backupSelectCollection'));
    setWorking(true);
    try {
      const result = await backupService.create({
        tipo: type,
        formato: format,
        colecciones: selected,
      });
      setMessage(result.message);
      setBackups(await backupService.list());
    } catch (error) {
      setMessage(error.response?.data?.error || t('config.backupCreateError'));
    } finally { setWorking(false); }
  };

  const restore = async (backup) => {
    if (!window.confirm(t('config.backupRestoreConfirm', { filename: backup.filename }))) return;
    setWorking(true);
    try {
      const result = await backupService.restore(backup.filename);
      setMessage(t('config.backupRestoreSuccess', {
        message: result.message,
        collections: result.collections.join(', '),
      }));
    } catch (error) {
      const data = error.response?.data;
      const failed = data?.failed_collections
        ?.map((item) => `${item.collection}: ${item.error}`)
        .join(' | ');
      setMessage(failed
        ? t('config.backupRestorePartial', {
            error: data.error,
            collections: data.collections?.join(', ') || t('config.none'),
            detail: failed,
          })
        : data?.error || t('config.backupRestoreError'));
    } finally { setWorking(false); }
  };

  const remove = async (backup) => {
    if (!window.confirm(t('config.backupDeleteConfirm', { filename: backup.filename }))) return;
    try {
      const result = await backupService.remove(backup.filename);
      setMessage(result.message);
      setBackups(await backupService.list());
    } catch (error) {
      setMessage(error.response?.data?.error || t('config.backupDeleteError'));
    }
  };

  return <main className="config-page"><ConfigHeader title={t('config.headerBackup')} right={<button className="config-refresh-btn" type="button" onClick={load}><FiRefreshCw /></button>} /><section className="config-content">
    <div className="config-card config-main-card"><div className="config-card-header"><FiDatabase size={26} /><h2>{t('config.createBackup')}</h2></div><div className="config-card-body">
      <div className="config-section-box"><div className="config-grid-3"><div><label className="config-label">{t('config.backupType')}</label><select className="config-select" value={type} onChange={(e) => setType(e.target.value)}><option value="completa">{t('config.backupComplete')}</option><option value="incremental">{t('config.backupIncremental')}</option><option value="diferencial">{t('config.backupDifferential')}</option></select></div><div><label className="config-label">{t('config.backupFormat')}</label><select className="config-select" value={format} onChange={(e) => setFormat(e.target.value)}><option value="json">JSON</option><option value="csv">CSV (ZIP)</option><option value="xlsx">Excel (.xlsx)</option><option value="pdf">PDF</option></select></div><div><label className="config-label">{t('config.mongoStatus')}</label><span className={`config-badge ${health?.status === 'ok' ? 'success' : 'danger'}`}>{health?.message || t('config.backupChecking')}</span></div></div>
        <p className="config-help">{type === 'completa' ? t('config.backupCompleteHelp') : type === 'incremental' ? t('config.backupIncrementalHelp') : t('config.backupDifferentialHelp')} {format === 'pdf' ? t('config.backupPdfHelp') : ''}</p>
        <h3 className="config-subtitle config-backup-collections-title">{t('config.automationCollections')}</h3><div className="config-checkbox-grid">{collections.map((name) => <label className="config-check-card" key={name}><input type="checkbox" checked={selected.includes(name)} onChange={() => toggleCollection(name)} /><span>{name}</span></label>)}</div>
      </div>
      <div className="config-form-footer"><button className="config-btn success" type="button" disabled={working} onClick={create}><FiDatabase /> {working ? t('config.backupProcessing') : t('config.backupCreate')}</button></div>
      {message && <div className="config-alert">{message}</div>}
    </div></div>
    <h2 className="config-section-title">{t('config.backupAvailable')}</h2>
    {loading && <div className="config-card">{t('config.backupLoading')}</div>}
    {!loading && backups.length === 0 && <div className="config-card">{t('config.backupNoBackups')}</div>}
    {backups.map((backup) => <article className="config-card" key={backup.filename}><div className="config-row"><div><h3>{backup.filename}</h3><p>{new Date(backup.date).toLocaleString(i18n.language === 'en' ? 'en-US' : 'es-MX')} · {formatBytes(backup.size)}</p><div className="config-backup-tags"><span className="config-badge info">{t(`config.backupType${backup.type?.charAt(0).toUpperCase()}${backup.type?.slice(1)}`, { defaultValue: backup.type })}</span><span className="config-badge info">{backup.format === 'xlsx' ? 'EXCEL' : backup.format}</span>{!backup.restorable && <span className="config-badge warn">{t('config.readOnly')}</span>}</div></div><span className={`config-badge ${backup.automatic ? 'info' : 'success'}`}>{backup.automatic ? t('config.automatic') : t('config.manual')}</span></div><div className="config-actions"><button className="config-btn secondary" type="button" onClick={() => backupService.download(backup.filename)}><FiDownload /> {t('config.download')}</button><button className="config-btn warning" type="button" disabled={working || !backup.restorable} title={backup.restorable ? t('config.restoreBackup') : t('config.pdfCannotRestore')} onClick={() => restore(backup)}><FiRotateCcw /> {t('config.restore')}</button><button className="config-btn danger" type="button" onClick={() => remove(backup)}><FiTrash2 /> {t('config.delete')}</button></div></article>)}
  </section></main>;
}
