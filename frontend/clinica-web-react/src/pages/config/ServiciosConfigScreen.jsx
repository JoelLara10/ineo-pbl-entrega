import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FiChevronLeft, FiChevronRight, FiEdit2, FiSave, FiSearch, FiTrash2, FiX } from 'react-icons/fi';
import ConfigHeader from './ConfigHeader';
import api from '../../services/api';
import { paginate, pages } from './configCache';
import './ConfigStyles.css';

const ITEMS_PER_PAGE = 8;
const typeKeys = { 1: 'serviceTypeConsultation', 2: 'serviceTypeProcedure', 3: 'serviceTypeLaboratory', 4: 'serviceTypeImaging', 5: 'serviceTypeHospitalization' };
const providerKeys = { 1: 'serviceProviderIneo', 2: 'serviceProviderExternal' };
const emptyForm = {
  serv_cve: '', serv_desc: '', serv_costo: '', serv_umed: 'SERVICIO', tipo: '1', proveedor: '1',
  grupo: 'SERVICIOS HOSPITALARIOS', codigo_sat: '', c_cveuni: '', iva: '16', serv_activo: 'SI',
  serv_costo2: '', serv_costo3: '', serv_costo4: '', serv_costo5: '', serv_costo6: '', serv_costo7: '', serv_costo8: '',
};
export default function ServiciosConfigScreen() {
  const { t } = useTranslation();
  const [servicios, setServicios] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editId, setEditId] = useState(null);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [msg, setMsg] = useState('');
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get('/catalog/services');
      setServicios(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      setMsg(error.response?.data?.error || t('config.serviceLoadError'));
    } finally { setLoading(false); }
  }, [t]);

  useEffect(() => { load(); }, [load]);

  const filtered = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) return servicios;
    return servicios.filter((service) =>
      [service.serv_cve, service.serv_desc, t(`config.${typeKeys[service.tipo]}`), t(`config.${providerKeys[service.proveedor]}`), service.grupo]
        .join(' ').toLowerCase().includes(query)
    );
  }, [servicios, search, t]);

  const totalPages = pages(filtered, ITEMS_PER_PAGE);
  const list = paginate(filtered, Math.min(page, totalPages), ITEMS_PER_PAGE);
  const reset = () => { setForm(emptyForm); setEditId(null); };

  const save = async (event) => {
    event.preventDefault();
    if (!form.serv_cve.trim() || !form.serv_desc.trim() || form.serv_costo === '') return setMsg(t('config.serviceRequired'));
    const duplicate = servicios.some((service) => service.serv_cve.toLowerCase() === form.serv_cve.trim().toLowerCase() && service.id_serv !== editId);
    if (duplicate) return setMsg(t('config.serviceDuplicate'));
    const payload = { ...form, serv_cve: form.serv_cve.trim().toUpperCase(), serv_desc: form.serv_desc.trim() };
    try {
      if (editId === null) await api.post('/catalog/services', payload);
      else await api.put(`/catalog/services/${editId}`, payload);
      setMsg(editId === null ? t('config.serviceSaved') : t('config.serviceUpdated'));
      reset(); setPage(1); await load();
    } catch (error) {
      setMsg(error.response?.data?.error || t('config.serviceSaveError'));
    }
  };

  const edit = (service) => {
    setEditId(service.id_serv);
    setForm({ ...emptyForm, ...service, iva: Number(service.iva || 0) <= 1 ? Number(service.iva || 0) * 100 : service.iva });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const remove = async (service) => {
    if (!window.confirm(t('config.serviceDeleteConfirm', { code: service.serv_cve }))) return;
    try {
      await api.delete(`/catalog/services/${service.id_serv}`);
      setMsg(t('config.serviceDeleted'));
      await load();
    } catch (error) {
      setMsg(error.response?.data?.error || t('config.serviceDeleteError'));
    }
  };

  return (
    <main className="config-page">
      <ConfigHeader title={t('config.headerServices')} />
      <section className="config-content">
        <form className="config-card config-main-card" onSubmit={save}>
          <div className="config-card-header"><h2>{editId === null ? t('config.registerService') : t('config.editService')}</h2></div>
          <div className="config-card-body">
            <div className="config-section-box">
              <h3 className="config-subtitle">{t('config.serviceMain')}</h3>
              <div className="config-grid-3">
                <Field label={t('config.serviceKey')}><input className="config-input" value={form.serv_cve} onChange={(e) => setForm({ ...form, serv_cve: e.target.value.toUpperCase() })} placeholder="SERV-001" required /></Field>
                <Field label={t('config.serviceDescription')}><input className="config-input" value={form.serv_desc} onChange={(e) => setForm({ ...form, serv_desc: e.target.value })} required /></Field>
                <Field label={t('config.servicePrice')}><input className="config-input" type="number" min="0" step="0.01" value={form.serv_costo} onChange={(e) => setForm({ ...form, serv_costo: e.target.value })} required /></Field>
                <Field label={t('config.serviceUnit')}><select className="config-select" value={form.serv_umed} onChange={(e) => setForm({ ...form, serv_umed: e.target.value })}>{['CONSULTA', 'EQUIPO', 'ESTUDIO', 'HORA', 'SERVICIO'].map((value) => <option key={value} value={value}>{t(`config.unit${value.charAt(0)}${value.slice(1).toLowerCase()}`)}</option>)}</select></Field>
                <Field label={t('config.serviceType')}><select className="config-select" value={form.tipo} onChange={(e) => setForm({ ...form, tipo: e.target.value })}>{Object.entries(typeKeys).map(([id, key]) => <option key={id} value={id}>{t(`config.${key}`)}</option>)}</select></Field>
                <Field label={t('config.serviceStatus')}><select className="config-select" value={form.serv_activo} onChange={(e) => setForm({ ...form, serv_activo: e.target.value })}><option value="SI">{t('config.active')}</option><option value="NO">{t('config.inactive')}</option></select></Field>
              </div>
            </div>
            <div className="config-section-box">
              <h3 className="config-subtitle">{t('config.serviceFiscal')}</h3>
              <div className="config-grid-3">
                <Field label={t('config.serviceProvider')}><select className="config-select" value={form.proveedor} onChange={(e) => setForm({ ...form, proveedor: e.target.value })}>{Object.entries(providerKeys).map(([id, key]) => <option key={id} value={id}>{t(`config.${key}`)}</option>)}</select></Field>
                <Field label={t('config.serviceGroup')}><select className="config-select" value={form.grupo} onChange={(e) => setForm({ ...form, grupo: e.target.value })}><option value="SERVICIOS HOSPITALARIOS">{t('config.serviceGroupHospital')}</option><option value="IMAGENOLOGIA">{t('config.serviceGroupImaging')}</option></select></Field>
                <Field label={t('config.serviceSat')}><input className="config-input" value={form.codigo_sat} onChange={(e) => setForm({ ...form, codigo_sat: e.target.value })} placeholder="85101500" /></Field>
                <Field label={t('config.serviceUnitKey')}><input className="config-input" value={form.c_cveuni} onChange={(e) => setForm({ ...form, c_cveuni: e.target.value.toUpperCase() })} placeholder="E48" /></Field>
                <Field label={t('config.serviceVat')}><input className="config-input" type="number" min="0" max="100" value={form.iva} onChange={(e) => setForm({ ...form, iva: e.target.value })} /></Field>
              </div>
            </div>
            <details className="config-section-box">
              <summary className="config-subtitle">{t('config.servicePrices')}</summary>
              <div className="config-grid-3">{[2, 3, 4, 5, 6, 7, 8].map((number) => {
                const key = `serv_costo${number}`;
                return <Field key={key} label={t('config.additionalPrice', { number })}><input className="config-input" type="number" min="0" step="0.01" value={form[key]} onChange={(e) => setForm({ ...form, [key]: e.target.value })} /></Field>;
              })}</div>
            </details>
            <div className="config-form-footer"><button className="config-btn secondary" type="button" onClick={reset}><FiX /> {t('config.cancel')}</button><button className="config-btn success" type="submit"><FiSave /> {editId === null ? t('config.saveService') : t('config.updateService')}</button></div>
            {msg && <div className="config-alert">{msg}</div>}
          </div>
        </form>

        <h2 className="config-section-title">{t('config.servicesRegistered')}</h2>
        <div className="config-search"><FiSearch className="config-search-icon" /><input className="config-input" value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} placeholder={t('config.searchService')} /></div>
        {loading && <div className="config-card">{t('config.loadingServices')}</div>}
        {!loading && <div className="config-table-wrap"><table className="config-table">
          <thead><tr><th>ID</th><th>{t('config.serviceKey')}</th><th>{t('config.serviceDescription')}</th><th>{t('config.servicePrice')}</th><th>{t('config.serviceUnitShort')}</th><th>{t('config.serviceType')}</th><th>{t('config.serviceStatus')}</th><th>{t('config.actions')}</th></tr></thead>
          <tbody>{list.map((service) => <tr key={service.id_serv}>
            <td>{service.id_serv}</td><td><strong>{service.serv_cve}</strong></td><td>{service.serv_desc}</td><td>${Number(service.serv_costo || 0).toFixed(2)}</td><td>{service.serv_umed}</td><td>{typeKeys[service.tipo] ? t(`config.${typeKeys[service.tipo]}`) : t('config.noType')}</td>
            <td><span className={`config-badge ${service.serv_activo === 'SI' ? 'success' : 'danger'}`}>{service.serv_activo === 'SI' ? t('config.activeStatus') : t('config.inactiveStatus')}</span></td>
            <td><div className="config-actions"><button className="config-btn warning" type="button" onClick={() => edit(service)}><FiEdit2 /></button><button className="config-btn danger" type="button" onClick={() => remove(service)}><FiTrash2 /></button></div></td>
          </tr>)}</tbody>
        </table></div>}
        {filtered.length > ITEMS_PER_PAGE && <div className="config-pagination"><button className="config-btn secondary" type="button" disabled={page === 1} onClick={() => setPage(page - 1)}><FiChevronLeft /></button><span className="config-page-pill">{page} / {totalPages}</span><button className="config-btn secondary" type="button" disabled={page === totalPages} onClick={() => setPage(page + 1)}><FiChevronRight /></button></div>}
      </section>
    </main>
  );
}

function Field({ label, children }) {
  return <div><label className="config-label">{label}</label>{children}</div>;
}
