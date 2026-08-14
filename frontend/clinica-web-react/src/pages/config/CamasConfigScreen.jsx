import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FiChevronLeft, FiChevronRight, FiEdit2, FiSave, FiSearch, FiTrash2, FiX } from 'react-icons/fi';
import ConfigHeader from './ConfigHeader';
import api from '../../services/api';
import { paginate, pages } from './configCache';
import './ConfigStyles.css';

const ITEMS_PER_PAGE = 8;
const emptyForm = { numero: '', area: 'Hospitalizado', tipo_habitacion: 'General', piso: '', seccion: '', ocupada: 0 };
export default function CamasConfigScreen() {
  const { t } = useTranslation();
  const [camas, setCamas] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get('/beds');
      setCamas(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      setMessage(error.response?.data?.error || t('config.bedLoadError'));
    } finally { setLoading(false); }
  }, [t]);

  useEffect(() => { load(); }, [load]);

  const filtered = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) return camas;
    return camas.filter((cama) =>
      [cama.id_cama, cama.numero, cama.area, cama.tipo_habitacion, cama.piso, cama.seccion, cama.ocupada ? t('config.bedOccupied') : t('config.bedFree')]
        .join(' ').toLowerCase().includes(query)
    );
  }, [camas, search, t]);

  const totalPages = pages(filtered, ITEMS_PER_PAGE);
  const visibleBeds = paginate(filtered, Math.min(page, totalPages), ITEMS_PER_PAGE);
  const resetForm = () => { setForm(emptyForm); setEditingId(null); };

  const save = async (event) => {
    event.preventDefault();
    if (!form.numero.trim() || !form.area) return setMessage(t('config.bedRequired'));
    const duplicate = camas.some((cama) => cama.numero.toLowerCase() === form.numero.trim().toLowerCase() && cama.id_cama !== editingId);
    if (duplicate) return setMessage(t('config.bedDuplicate'));

    const payload = { ...form, numero: form.numero.trim(), ocupada: Number(form.ocupada) };
    try {
      if (editingId !== null) await api.put(`/beds/${editingId}`, payload);
      else await api.post('/beds', payload);
      setMessage(editingId !== null ? t('config.bedUpdated') : t('config.bedSaved'));
      resetForm(); setPage(1); await load();
    } catch (error) {
      setMessage(error.response?.data?.error || t('config.bedSaveError'));
    }
  };

  const edit = (cama) => {
    setEditingId(cama.id_cama);
    setForm({ ...emptyForm, ...cama, ocupada: Number(cama.ocupada) });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const remove = async (cama) => {
    if (cama.ocupada) return setMessage(t('config.bedOccupiedError'));
    if (!window.confirm(t('config.bedDeleteConfirm', { number: cama.numero }))) return;
    try {
      await api.delete(`/beds/${cama.id_cama}`);
      setMessage(t('config.bedDeleted'));
      await load();
    } catch (error) {
      setMessage(error.response?.data?.error || t('config.bedDeleteError'));
    }
  };

  return (
    <main className="config-page">
      <ConfigHeader title={t('config.headerBeds')} />
      <section className="config-content">
        <form className="config-card config-main-card" onSubmit={save}>
          <div className="config-card-header"><h2>{editingId !== null ? t('config.editBed') : t('config.registerBed')}</h2></div>
          <div className="config-card-body">
            <div className="config-section-box">
              <h3 className="config-subtitle">{t('config.bedData')}</h3>
              <div className="config-grid-3">
                <div><label className="config-label">{t('config.bedNumber')}</label><input className="config-input" value={form.numero} onChange={(e) => setForm({ ...form, numero: e.target.value })} placeholder="Ej. H-101" required /></div>
                <div><label className="config-label">{t('config.bedArea')}</label><select className="config-select" value={form.area} onChange={(e) => setForm({ ...form, area: e.target.value })}><option value="Hospitalizado">{t('config.areaHospitalized')}</option><option value="Urgencias">{t('config.areaEmergency')}</option></select></div>
                <div><label className="config-label">{t('config.bedRoomType')}</label><select className="config-select" value={form.tipo_habitacion} onChange={(e) => setForm({ ...form, tipo_habitacion: e.target.value })}><option value="General">{t('config.roomGeneral')}</option><option value="Observación">{t('config.roomObservation')}</option><option value="Terapia intensiva">{t('config.roomIntensiveCare')}</option><option value="Recuperación">{t('config.roomRecovery')}</option><option value="Consulta">{t('config.roomConsultation')}</option></select></div>
                <div><label className="config-label">{t('config.bedFloor')}</label><input className="config-input" value={form.piso} onChange={(e) => setForm({ ...form, piso: e.target.value })} placeholder="Ej. 1" /></div>
                <div><label className="config-label">{t('config.bedSection')}</label><input className="config-input" value={form.seccion} onChange={(e) => setForm({ ...form, seccion: e.target.value })} placeholder="Ej. A" /></div>
                <div><label className="config-label">{t('config.bedStatus')}</label><select className="config-select" value={form.ocupada} onChange={(e) => setForm({ ...form, ocupada: Number(e.target.value) })}><option value={0}>{t('config.bedFree')}</option><option value={1}>{t('config.bedOccupied')}</option></select></div>
              </div>
            </div>
            <div className="config-form-footer">
              <button className="config-btn secondary" type="button" onClick={resetForm}><FiX /> {t('config.cancel')}</button>
              <button className="config-btn success" type="submit"><FiSave /> {editingId !== null ? t('config.updateBed') : t('config.saveBed')}</button>
            </div>
            {message && <div className="config-alert">{message}</div>}
          </div>
        </form>

        <div className="config-list-heading">
          <div><h2 className="config-section-title">{t('config.bedsRegistered')}</h2><p className="config-muted">{t('config.bedCount', { count: filtered.length })}</p></div>
          <div className="config-search"><FiSearch className="config-search-icon" /><input className="config-input" value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} placeholder={t('config.searchBed')} /></div>
        </div>

        {loading && <div className="config-card">{t('config.loadingBeds')}</div>}
        {!loading && <div className="config-table-wrap">
          <table className="config-table">
            <thead><tr><th>ID</th><th>{t('config.bedNumber')}</th><th>{t('config.bedArea')}</th><th>{t('config.room')}</th><th>{t('config.bedFloor')}</th><th>{t('config.bedSection')}</th><th>{t('config.bedStatus')}</th><th>{t('config.actions')}</th></tr></thead>
            <tbody>{visibleBeds.map((cama) => <tr key={cama.id_cama}>
              <td>{cama.id_cama}</td><td><strong>{cama.numero}</strong></td><td>{cama.area}</td><td>{cama.tipo_habitacion || 'N/A'}</td><td>{cama.piso || 'N/A'}</td><td>{cama.seccion || 'N/A'}</td>
              <td><span className={`config-badge ${cama.ocupada ? 'danger' : 'success'}`}>{cama.ocupada ? t('config.bedOccupied') : t('config.bedFree')}</span></td>
              <td><div className="config-actions compact"><button className="config-btn warning icon-only" type="button" title={t('config.edit')} onClick={() => edit(cama)}><FiEdit2 /></button><button className="config-btn danger icon-only" type="button" title={t('config.delete')} onClick={() => remove(cama)}><FiTrash2 /></button></div></td>
            </tr>)}</tbody>
          </table>
          {!visibleBeds.length && <div className="config-empty">{t('config.bedsEmpty')}</div>}
        </div>}
        {filtered.length > ITEMS_PER_PAGE && <div className="config-pagination"><button className="config-btn secondary" type="button" disabled={page === 1} onClick={() => setPage(page - 1)}><FiChevronLeft /></button><span className="config-page-pill">{page} / {totalPages}</span><button className="config-btn secondary" type="button" disabled={page === totalPages} onClick={() => setPage(page + 1)}><FiChevronRight /></button></div>}
      </section>
    </main>
  );
}
