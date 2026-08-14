import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FiSave } from 'react-icons/fi';
import ConfigHeader from './ConfigHeader';
import { readPermanent, savePermanent } from './configCache';
import './ConfigStyles.css';

const defaults = {
  nombreClinica: 'INEO Hospital',
  telefono: '722 000 0000',
  direccion: 'Toluca, México',
  moneda: 'MXN',
  tema: 'Morado',
  apiHost: '192.168.1.4',
  apiPort: '5001',
  apiPath: '/api/v1',
};

export default function GeneralSettingsScreen() {
  const { t } = useTranslation();
  const [form, setForm] = useState(() => readPermanent('general', defaults));
  const [msg, setMsg] = useState('');

  const save = (event) => {
    event.preventDefault();
    savePermanent('general', form);
    setMsg(t('config.generalSaved'));
  };

  return (
    <main className="config-page">
      <ConfigHeader title={t('config.generalTitle')} />
      <section className="config-content">
        <form className="config-card config-main-card" onSubmit={save}>
          <div className="config-card-header"><h2>🏥 {t('config.generalTitle')}</h2></div>
          <div className="config-card-body">
            <div className="config-section-box">
              <h3 className="config-subtitle">{t('config.clinicData')}</h3>
              <label className="config-label">{t('config.clinicName')}</label>
              <input className="config-input" value={form.nombreClinica} onChange={(e) => setForm({ ...form, nombreClinica: e.target.value })} />
              <label className="config-label">{t('config.phone')}</label>
              <input className="config-input" value={form.telefono} onChange={(e) => setForm({ ...form, telefono: e.target.value })} />
              <label className="config-label">{t('config.address')}</label>
              <input className="config-input" value={form.direccion} onChange={(e) => setForm({ ...form, direccion: e.target.value })} />
              <div className="config-grid-2">
                <div>
                  <label className="config-label">{t('config.currency')}</label>
                  <input className="config-input" value={form.moneda} onChange={(e) => setForm({ ...form, moneda: e.target.value.toUpperCase() })} />
                </div>
                <div>
                  <label className="config-label">{t('config.theme')}</label>
                  <select className="config-select" value={form.tema} onChange={(e) => setForm({ ...form, tema: e.target.value })}>
                    <option value="Morado">{t('config.themePurple')}</option>
                    <option value="Azul">{t('config.themeBlue')}</option>
                    <option value="Verde">{t('config.themeGreen')}</option>
                    <option value="Oscuro">{t('config.themeDark')}</option>
                  </select>
                </div>
              </div>
            </div>
            <div className="config-section-box">
              <h3 className="config-subtitle">{t('config.apiConnection')}</h3>
              <div className="config-grid-3">
                <div><label className="config-label">{t('config.serverIp')}</label><input className="config-input" value={form.apiHost} onChange={(e) => setForm({ ...form, apiHost: e.target.value })} /></div>
                <div><label className="config-label">{t('config.port')}</label><input className="config-input" value={form.apiPort} onChange={(e) => setForm({ ...form, apiPort: e.target.value })} /></div>
                <div><label className="config-label">{t('config.basePath')}</label><input className="config-input" value={form.apiPath} onChange={(e) => setForm({ ...form, apiPath: e.target.value })} /></div>
              </div>
            </div>
            <div className="config-form-footer">
              <button className="config-btn success" type="submit"><FiSave /> {t('config.saveSettings')}</button>
            </div>
            {msg && <div className="config-alert success">{msg}</div>}
          </div>
        </form>
      </section>
    </main>
  );
}
