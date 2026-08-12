import { useCallback, useState } from 'react';
import { FiEye, FiSearch } from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import adminService from '../../services/adminService';
import AdminLayout from './AdminLayout';
import useAdminData from './useAdminData';

const LIMIT = 5;
const currency = (value, language) => new Intl.NumberFormat(language, { style: 'currency', currency: 'MXN' }).format(Number(value || 0));
export default function CorteCajaScreen() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [movementPage, setMovementPage] = useState(1);
  const [accountPage, setAccountPage] = useState(1);
  const loader = useCallback(() => adminService.getCashCut(), []);
  const state = useAdminData('cash-cut:all:complete', loader, { movements: [], activeAccounts: [], summary: {} });
  const matches = (item) => !search || Object.values(item).join(' ').toLowerCase().includes(search.toLowerCase());
  const movements = (state.data?.movements || state.data?.data || []).filter(matches);
  const accounts = (state.data?.activeAccounts || state.data?.accounts || []).filter(matches);
  const totals = state.data?.summary || {
    income: movements.reduce((sum, item) => sum + Number(item.amount || 0), 0),
    movements: movements.length,
    activeAccounts: accounts.length,
  };
  const pager = (page, total, setPage) => <div className="adm-pagination"><button disabled={page === 1} onClick={() => setPage(page - 1)}>‹</button><span>{page} / {Math.max(1, Math.ceil(total / LIMIT))}</span><button disabled={page >= Math.ceil(total / LIMIT)} onClick={() => setPage(page + 1)}>›</button></div>;
  return <AdminLayout title={t('administrative.cashCut')} subtitle={t('administrative.cashCutDesc')} onRefresh={state.reload} refreshing={state.refreshing} updatedAt={state.updatedAt}>
    <div className="adm-summary"><div className="adm-stat" style={{ '--accent': '#48bb78' }}><span>{t('administrative.income')}</span><strong>{currency(totals.income ?? totals.total_income, i18n.language)}</strong></div><div className="adm-stat" style={{ '--accent': '#667eea' }}><span>{t('administrative.movements')}</span><strong>{totals.movements ?? movements.length}</strong></div><div className="adm-stat" style={{ '--accent': '#ed8936' }}><span>{t('administrative.activeAccounts')}</span><strong>{totals.activeAccounts ?? accounts.length}</strong></div></div>
    <div className="adm-toolbar"><div className="adm-search"><FiSearch /><input value={search} onChange={(event) => { setSearch(event.target.value); setMovementPage(1); setAccountPage(1); }} placeholder={t('administrative.searchCash')} /></div></div>
    {state.error && <div className="adm-alert">{state.error}</div>}
    {state.loading ? <div className="adm-loading">{t('common.loading')}</div> : <>
      <section className="adm-panel adm-section"><div className="adm-section-head"><h2>{t('administrative.movements')}</h2><span className="adm-badge">{movements.length}</span></div><div className="adm-table-wrap"><table className="adm-table"><thead><tr><th>ID</th><th>{t('administrative.time')}</th><th>{t('administrative.patient')}</th><th>{t('administrative.concept')}</th><th>{t('administrative.method')}</th><th>{t('administrative.amount')}</th></tr></thead><tbody>{movements.slice((movementPage - 1) * LIMIT, movementPage * LIMIT).map((item, index) => <tr key={item.id || index}><td>{item.id || '-'}</td><td>{item.time || item.date || '-'}</td><td>{item.patient || '-'}</td><td>{item.concept || item.description || '-'}</td><td>{item.method || '-'}</td><td>{currency(item.amount, i18n.language)}</td></tr>)}</tbody></table></div>{pager(movementPage, movements.length, setMovementPage)}</section>
      <section className="adm-panel adm-section"><div className="adm-section-head"><h2>{t('administrative.activeAccounts')}</h2><span className="adm-badge">{accounts.length}</span></div><div className="adm-table-wrap"><table className="adm-table"><thead><tr><th>{t('administrative.record')}</th><th>{t('administrative.patient')}</th><th>{t('administrative.area')}</th><th>{t('administrative.total')}</th><th>{t('administrative.balance')}</th><th>{t('common.actions')}</th></tr></thead><tbody>{accounts.slice((accountPage - 1) * LIMIT, accountPage * LIMIT).map((item, index) => <tr key={item.attention || index}><td>{item.record || '-'}</td><td>{item.patient || item.name || '-'}</td><td>{item.area || item.bed || '-'}</td><td>{currency(item.total, i18n.language)}</td><td>{currency(item.balance ?? Number(item.total || 0) - Number(item.advance || 0), i18n.language)}</td><td><button className="adm-button" onClick={() => navigate(`/pacientes/${item.Id_exp || item.record || 'cuenta'}`, { state: { patient: item } })}><FiEye />{t('common.view')}</button></td></tr>)}</tbody></table></div>{pager(accountPage, accounts.length, setAccountPage)}</section>
    </>}
  </AdminLayout>;
}
