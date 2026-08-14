import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FiClock, FiSave } from 'react-icons/fi';
import ConfigHeader from './ConfigHeader';
import backupService from '../../services/backupService';
import './ConfigStyles.css';
import './BackupStyles.css';

const defaults = { activo: false, tipo: 'completa', formato: 'json', intervalo: 1440, max_backups: 4, colecciones: [] };

export default function AutomationConfigScreen() {
  const { t } = useTranslation();
  const [form, setForm] = useState(defaults);
  const [collections, setCollections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');

  useEffect(() => {
    Promise.all([backupService.getAutomation(), backupService.collections()])
      .then(([config, names]) => {
        setForm({ ...defaults, ...config, colecciones: config.colecciones?.length ? config.colecciones : names });
        setCollections(names);
      })
      .catch((error) => setMessage(error.response?.data?.error || t('config.automationLoadError')))
      .finally(() => setLoading(false));
  }, [t]);

  const toggleCollection = (name) => setForm((current) => ({
    ...current,
    colecciones: current.colecciones.includes(name)
      ? current.colecciones.filter((item) => item !== name)
      : [...current.colecciones, name],
  }));

  const save = async (event) => {
    event.preventDefault();
    setLoading(true);
    try {
      const result = await backupService.updateAutomation(form);
      setForm(result);
      setMessage(result.activo ? t('config.automationSaved') : t('config.automationDisabled'));
    } catch (error) {
      setMessage(error.response?.data?.error || t('config.automationSaveError'));
    } finally { setLoading(false); }
  };

  return <main className="config-page"><ConfigHeader title={t('config.headerAutomation')} /><section className="config-content"><form className="config-card config-main-card" onSubmit={save}>
    <div className="config-card-header"><FiClock size={26} /><h2>{t('config.automationTitle')}</h2></div><div className="config-card-body">
      <div className="config-section-box"><label className="config-toggle-row"><span><strong>{t('config.automationActive')}</strong><small>{t('config.automationActiveDesc')}</small></span><input className="config-switch" type="checkbox" checked={form.activo} onChange={(e) => setForm({ ...form, activo: e.target.checked })} /></label></div>
      <div className="config-section-box"><h3 className="config-subtitle">{t('config.automationSchedule')}</h3><div className="config-grid-3">
        <div><label className="config-label">{t('config.backupType')}</label><select className="config-select" value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })}><option value="completa">{t('config.backupComplete')}</option><option value="incremental">{t('config.backupIncremental')}</option><option value="diferencial">{t('config.backupDifferential')}</option></select></div>
        <div><label className="config-label">{t('config.backupFormat')}</label><select className="config-select" value={form.formato} onChange={(e) => setForm({ ...form, formato: e.target.value })}><option value="json">JSON</option><option value="csv">CSV (ZIP)</option><option value="xlsx">Excel (.xlsx)</option><option value="pdf">PDF</option></select></div>
        <div><label className="config-label">{t('config.automationInterval')}</label><input className="config-input" type="number" min="5" max="525600" value={form.intervalo} onChange={(e) => setForm({ ...form, intervalo: Number(e.target.value) })} /><small className="config-help">{t('config.automationIntervalHelp')}</small></div>
        <div><label className="config-label">{t('config.automationMaxBackups')}</label><input className="config-input" type="number" min="1" max="50" value={form.max_backups} onChange={(e) => setForm({ ...form, max_backups: Number(e.target.value) })} /></div>
      </div></div>
      <div className="config-section-box"><h3 className="config-subtitle">{t('config.automationCollections')}</h3><div className="config-checkbox-grid">{collections.map((name) => <label className="config-check-card" key={name}><input type="checkbox" checked={form.colecciones.includes(name)} onChange={() => toggleCollection(name)} /><span>{name}</span></label>)}</div></div>
      <div className="config-form-footer"><button className="config-btn success" type="submit" disabled={loading}><FiSave /> {loading ? t('config.automationSaving') : t('config.automationSave')}</button></div>
      {message && <div className="config-alert">{message}</div>}
    </div>
  </form></section></main>;
}
