import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FiChevronLeft, FiChevronRight, FiEdit2, FiSave, FiSearch, FiTrash2, FiX } from 'react-icons/fi';
import ConfigHeader from './ConfigHeader';
import api from '../../services/api';
import { paginate, pages } from './configCache';
import './ConfigStyles.css';

const ITEMS_PER_PAGE = 8;
const emptyForm = { id_cie10: '', diag: '' };

export default function DiagnosticosConfigScreen() {
  const { t } = useTranslation();
  const [diagnosticos, setDiagnosticos] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editId, setEditId] = useState(null);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const response = await api.get('/catalog/diagnostics');
      setDiagnosticos(Array.isArray(response.data) ? response.data : []);
    } catch (error) {
      setMessage(error.response?.data?.error || t('config.diagnosticLoadError'));
    } finally { setLoading(false); }
  }, [t]);

  useEffect(() => { load(); }, [load]);

  const filtered = useMemo(() => {
    const query = search.trim().toLowerCase();
    if (!query) return diagnosticos;
    return diagnosticos.filter((item) => `${item.id_cie10} ${item.diag}`.toLowerCase().includes(query));
  }, [diagnosticos, search]);

  const totalPages = pages(filtered, ITEMS_PER_PAGE);
  const list = paginate(filtered, Math.min(page, totalPages), ITEMS_PER_PAGE);
  const reset = () => { setForm(emptyForm); setEditId(null); };

  const save = async (event) => {
    event.preventDefault();
    if (!form.id_cie10.trim() || !form.diag.trim()) return setMessage(t('config.diagnosticRequired'));
    try {
      if (editId === null) await api.post('/catalog/diagnostics', form);
      else await api.put(`/catalog/diagnostics/${editId}`, form);
      setMessage(editId === null ? t('config.diagnosticSaved') : t('config.diagnosticUpdated'));
      reset();
      await load();
    } catch (error) {
      setMessage(error.response?.data?.error || t('config.diagnosticSaveError'));
    }
  };

  const edit = (item) => {
    setEditId(item.id_diag);
    setForm({ id_cie10: item.id_cie10 || '', diag: item.diag || '' });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const remove = async (item) => {
    if (!window.confirm(t('config.diagnosticDeleteConfirm', { code: item.id_cie10 }))) return;
    try {
      await api.delete(`/catalog/diagnostics/${item.id_diag}`);
      setMessage(t('config.diagnosticDeleted'));
      await load();
    } catch (error) {
      setMessage(error.response?.data?.error || t('config.diagnosticDeleteError'));
    }
  };

  return <main className="config-page"><ConfigHeader title={t('config.headerDiagnoses')} /><section className="config-content">
    <form className="config-card config-main-card" onSubmit={save}><div className="config-card-header"><h2>{editId === null ? t('config.diagnosticRegister') : t('config.diagnosticEdit')}</h2></div><div className="config-card-body">
      <div className="config-section-box"><div className="config-grid-2"><div><label className="config-label">{t('config.diagnosticCode')}</label><input className="config-input" value={form.id_cie10} onChange={(e) => setForm({ ...form, id_cie10: e.target.value.toUpperCase() })} placeholder="H57.9" required /></div><div><label className="config-label">{t('config.diagnosticName')}</label><input className="config-input" value={form.diag} onChange={(e) => setForm({ ...form, diag: e.target.value })} required /></div></div></div>
      <div className="config-form-footer"><button className="config-btn secondary" type="button" onClick={reset}><FiX /> {t('config.cancel')}</button><button className="config-btn success" type="submit"><FiSave /> {editId === null ? t('config.saveDiagnostic') : t('config.updateDiagnostic')}</button></div>
      {message && <div className="config-alert">{message}</div>}
    </div></form>
    <h2 className="config-section-title">{t('config.diagnosticsRegistered')}</h2>
    <div className="config-search"><FiSearch className="config-search-icon" /><input className="config-input" value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} placeholder={t('config.diagnosticSearch')} /></div>
    {loading && <div className="config-card">{t('config.diagnosticLoading')}</div>}
    {!loading && list.map((item) => <article className="config-card" key={item.id_diag}><div className="config-row"><div><h3>{item.id_cie10}</h3><p>{item.diag}</p></div></div><div className="config-actions"><button className="config-btn warning" type="button" onClick={() => edit(item)}><FiEdit2 /> {t('config.edit')}</button><button className="config-btn danger" type="button" onClick={() => remove(item)}><FiTrash2 /> {t('config.delete')}</button></div></article>)}
    {!loading && !list.length && <div className="config-card">{t('config.diagnosticEmpty')}</div>}
    {filtered.length > ITEMS_PER_PAGE && <div className="config-pagination"><button className="config-btn secondary" type="button" disabled={page === 1} onClick={() => setPage(page - 1)}><FiChevronLeft /></button><span className="config-page-pill">{page} / {totalPages}</span><button className="config-btn secondary" type="button" disabled={page === totalPages} onClick={() => setPage(page + 1)}><FiChevronRight /></button></div>}
  </section></main>;
}
