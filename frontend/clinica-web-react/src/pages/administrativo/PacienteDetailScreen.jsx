import { useCallback, useEffect, useMemo, useState } from 'react';
import { FiDownload, FiPlus, FiSearch, FiTrash2 } from 'react-icons/fi';
import { useLocation, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import adminService from '../../services/adminService';
import AdminLayout from './AdminLayout';
import useAdminData from './useAdminData';

const LIMIT = 5;
const documentDefaults = [
  ['initial-sheet', 'initialSheet'], ['front-sheet', 'frontSheet'], ['contract', 'contract'],
  ['consent', 'consent'], ['identification-sheet', 'identificationSheet'],
];
const accountsFrom = (value) => Array.isArray(value) ? value : value?.activeAccounts || value?.accounts || value?.data || [];
export default function PacienteDetailScreen() {
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const { id } = useParams();
  const selected = location.state?.patient || {};
  const selectedAttention = selected.id_atencion || selected.idAtencion || selected.attention;
  const selectedRecord = selected.Id_exp || selected.id_exp || selected.record || id;
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [attention, setAttention] = useState(selectedAttention || '');
  const [account, setAccount] = useState(null);
  const [options, setOptions] = useState({ servicios: [], medicamentos: [] });
  const [charge, setCharge] = useState({ type: 'service', id: '', description: '', quantity: 1 });
  const [busy, setBusy] = useState('');
  const [message, setMessage] = useState('');
  const loader = useCallback(() => adminService.getAccounts(''), []);
  const listState = useAdminData('accounts:all:complete', loader, []);
  const filtered = useMemo(() => accountsFrom(listState.data).filter((item) => !search || Object.values(item).join(' ').toLowerCase().includes(search.toLowerCase())), [listState.data, search]);

  const loadAccount = useCallback(async (idAttention) => {
    if (!idAttention) return;
    setBusy('account'); setMessage('');
    try {
      const [value, opts] = await Promise.all([adminService.getAccount(idAttention), adminService.getOptions()]);
      setAccount(value); setOptions(opts || {}); setAttention(idAttention);
    } catch (error) { setMessage(error.response?.data?.error || error.message); }
    finally { setBusy(''); }
  }, []);
  useEffect(() => { if (selectedAttention) loadAccount(selectedAttention); }, [loadAccount, selectedAttention]);

  const currency = (value) => new Intl.NumberFormat(i18n.language, { style: 'currency', currency: 'MXN' }).format(Number(value || 0));
  const patient = account?.patient || selected;
  const charges = account?.charges || account?.items || [];
  const documents = account?.documents?.length ? account.documents : documentDefaults.map(([key, label]) => ({
    key, title: t(`administrative.${label}`), endpoint: selectedRecord && attention ? `/api/v1/pdf/${key}/${selectedRecord}/${attention}` : '', filename: `${key}_${attention}.pdf`,
  }));
  const reloadAll = async () => { await listState.reload(); if (attention) await loadAccount(attention); };
  const addCharge = async () => {
    if (!attention || (!charge.id && !charge.description)) return;
    setBusy('charge');
    try {
      const value = await adminService.addCharge(attention, { type: charge.type, item_id: charge.id || undefined, description: charge.description || undefined, quantity: Number(charge.quantity) || 1 });
      setAccount(value.account || value); setCharge({ type: 'service', id: '', description: '', quantity: 1 });
    } catch (error) { setMessage(error.response?.data?.error || error.message); } finally { setBusy(''); }
  };
  const removeCharge = async (chargeId) => {
    if (!window.confirm(t('administrative.confirmRemoveCharge'))) return;
    try { const value = await adminService.removeCharge(attention, chargeId); setAccount(value.account || value); } catch (error) { setMessage(error.response?.data?.error || error.message); }
  };
  const closeAccount = async () => {
    if (!window.confirm(t('administrative.confirmCloseAccount'))) return;
    try { const value = await adminService.closeAccount(attention); setAccount(value.account || value); } catch (error) { setMessage(error.response?.data?.error || error.message); }
  };
  const download = async (file) => {
    setBusy(file.key);
    try { await adminService.downloadDocument(file); } catch (error) { setMessage(error.response?.data?.error || error.message); } finally { setBusy(''); }
  };
  const total = account?.total ?? charges.reduce((sum, item) => sum + Number(item.quantity || 1) * Number(item.price || item.amount || 0), 0);
  const paid = account?.advance ?? account?.total_paid ?? 0;

  return <AdminLayout title={t('administrative.patientAccount')} subtitle={patient?.name || patient?.patient || t('administrative.selectAccount')} onRefresh={reloadAll} refreshing={listState.refreshing} updatedAt={listState.updatedAt}>
    {message && <div className="adm-alert">{message}</div>}
    <section className="adm-panel adm-section"><div className="adm-section-head"><h2>{t('administrative.accounts')}</h2><span className="adm-badge">{filtered.length}</span></div><div className="adm-toolbar"><div className="adm-search"><FiSearch /><input value={search} onChange={(event) => { setSearch(event.target.value); setPage(1); }} placeholder={t('administrative.searchAccounts')} /></div></div>
      <div className="adm-table-wrap"><table className="adm-table"><thead><tr><th>{t('administrative.account')}</th><th>{t('administrative.record')}</th><th>{t('administrative.patient')}</th><th>{t('administrative.area')}</th><th>{t('administrative.balance')}</th><th>{t('common.actions')}</th></tr></thead><tbody>{filtered.slice((page - 1) * LIMIT, page * LIMIT).map((item, index) => <tr key={item.id_atencion || item.attention || index}><td>{item.attention || item.id_atencion}</td><td>{item.record || item.Id_exp}</td><td>{item.patient || item.name}</td><td>{item.area || item.bed || '-'}</td><td>{currency(item.balance ?? item.pending)}</td><td><button className="adm-button" onClick={() => loadAccount(item.id_atencion || item.attention)}>{t('administrative.openAccount')}</button></td></tr>)}</tbody></table></div>
      <div className="adm-pagination"><button disabled={page === 1} onClick={() => setPage(page - 1)}>‹</button><span>{page} / {Math.max(1, Math.ceil(filtered.length / LIMIT))}</span><button disabled={page >= Math.ceil(filtered.length / LIMIT)} onClick={() => setPage(page + 1)}>›</button></div>
    </section>
    {busy === 'account' && <div className="adm-loading">{t('common.loading')}</div>}
    {account && <><div className="adm-summary"><div className="adm-stat"><span>{t('administrative.subtotal')}</span><strong>{currency(account.subtotal)}</strong></div><div className="adm-stat"><span>{t('administrative.tax')}</span><strong>{currency(account.iva || account.tax)}</strong></div><div className="adm-stat"><span>{t('administrative.total')}</span><strong>{currency(total)}</strong></div><div className="adm-stat"><span>{t('administrative.balance')}</span><strong>{currency(account.balance ?? total - paid)}</strong></div></div>
      <section className="adm-panel adm-section"><h2>{t('administrative.addCharge')}</h2><div className="adm-form-grid"><div className="adm-field"><label>{t('administrative.chargeType')}</label><select value={charge.type} onChange={(e) => setCharge({ ...charge, type: e.target.value, id: '' })}><option value="service">{t('administrative.service')}</option><option value="medicine">{t('administrative.medicine')}</option></select></div><div className="adm-field"><label>{t('administrative.item')}</label><select value={charge.id} onChange={(e) => setCharge({ ...charge, id: e.target.value })}><option value="">{t('common.select')}</option>{(charge.type === 'service' ? options.servicios : options.medicamentos || []).map((item) => <option key={item.id || item.id_servicio || item.id_medicamento} value={item.id || item.id_servicio || item.id_medicamento}>{item.nombre || item.name || item.descripcion}</option>)}</select></div><div className="adm-field"><label>{t('administrative.quantity')}</label><input type="number" min="1" value={charge.quantity} onChange={(e) => setCharge({ ...charge, quantity: e.target.value })} /></div></div><div className="adm-toolbar"><button className="adm-button adm-button-success" onClick={addCharge} disabled={busy === 'charge'}><FiPlus />{t('administrative.add')}</button></div></section>
      <section className="adm-panel adm-section"><h2>{t('administrative.charges')}</h2><div className="adm-table-wrap"><table className="adm-table"><thead><tr><th>{t('administrative.description')}</th><th>{t('administrative.quantity')}</th><th>{t('administrative.price')}</th><th>{t('administrative.amount')}</th><th>{t('common.actions')}</th></tr></thead><tbody>{charges.map((item, index) => <tr key={item.id || item.charge_id || index}><td>{item.description || item.nombre}</td><td>{item.quantity || 1}</td><td>{currency(item.price)}</td><td>{currency(item.amount ?? Number(item.quantity || 1) * Number(item.price || 0))}</td><td><button className="adm-button adm-button-danger" onClick={() => removeCharge(item.id || item.charge_id)}><FiTrash2 /></button></td></tr>)}</tbody></table></div></section>
      <section className="adm-panel adm-section"><h2>{t('administrative.documents')}</h2><div className="adm-documents">{documents.map((file) => <button className="adm-document" key={file.key || file.endpoint} onClick={() => download(file)} disabled={!file.endpoint || busy === file.key}><FiDownload /> <strong>{file.title || t(`administrative.${file.key}`)}</strong></button>)}</div></section>
      <div className="adm-toolbar"><button className="adm-button adm-button-danger" onClick={closeAccount}>{t('administrative.closeAccount')}</button></div>
    </>}
  </AdminLayout>;
}
