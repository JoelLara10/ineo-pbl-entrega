import { useCallback, useMemo, useState } from 'react';
import { FiSearch } from 'react-icons/fi';
import { useTranslation } from 'react-i18next';
import adminService from '../../services/adminService';
import AdminLayout from './AdminLayout';
import useAdminData from './useAdminData';

const LIMIT = 5;
export default function CensoScreen() {
  const { t } = useTranslation();
  const [search, setSearch] = useState('');
  const [pages, setPages] = useState({});
  const loader = useCallback(() => adminService.getCensus(''), []);
  const state = useAdminData('census:all:complete', loader, { sections: [], summary: {} });
  const sections = useMemo(() => state.data?.sections || state.data?.data || [], [state.data]);
  const filtered = useMemo(() => sections.map((section) => ({ ...section, data: (section.data || section.patients || []).filter((patient) => !search || Object.values(patient).join(' ').toLowerCase().includes(search.toLowerCase())) })), [sections, search]);
  return <AdminLayout title={t('administrative.census')} subtitle={t('administrative.censusDesc')} onRefresh={state.reload} refreshing={state.refreshing} updatedAt={state.updatedAt}>
    <div className="adm-summary">{['activos', 'areas', 'avisos'].map((key, index) => <div className="adm-stat" style={{ '--accent': ['#667eea', '#38b2ac', '#ed8936'][index] }} key={key}><span>{t(`administrative.${key}`)}</span><strong>{state.data?.summary?.[key] || 0}</strong></div>)}</div>
    <div className="adm-toolbar"><div className="adm-search"><FiSearch /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder={t('administrative.searchCensus')} /></div></div>
    {state.error && <div className="adm-alert">{state.error}</div>}
    {state.loading ? <div className="adm-loading">{t('common.loading')}</div> : filtered.map((section) => {
      const page = pages[section.key] || 1; const totalPages = Math.max(1, Math.ceil(section.data.length / LIMIT)); const visible = section.data.slice((page - 1) * LIMIT, page * LIMIT);
      return <section className="adm-panel adm-section" key={section.key}><div className="adm-section-head"><h2>{t(`administrative.census_${section.key}`, section.title || section.key)}</h2><span className="adm-badge">{section.data.length}</span></div>
        <div className="adm-table-wrap"><table className="adm-table"><thead><tr><th>{t('administrative.account')}</th><th>{t('administrative.patient')}</th><th>{t('administrative.record')}</th><th>{t('administrative.area')}</th><th>{t('administrative.doctor')}</th><th>{t('administrative.reason')}</th><th>{t('administrative.notice')}</th></tr></thead>
          <tbody>{visible.map((patient, index) => <tr key={patient.attention || patient.account || index}><td>{patient.account || patient.attention || '-'}</td><td>{patient.patient || patient.name || '-'}</td><td>{patient.record || '-'}</td><td>{patient.room || patient.area || '-'}</td><td>{patient.doctor || '-'}</td><td>{patient.reason || '-'}</td><td>{patient.notice || '-'}</td></tr>)}</tbody></table></div>
        {!visible.length && <div className="adm-empty">{t('administrative.noPatients')}</div>}<div className="adm-pagination"><button disabled={page === 1} onClick={() => setPages({ ...pages, [section.key]: page - 1 })}>‹</button><span>{page} / {totalPages}</span><button disabled={page === totalPages} onClick={() => setPages({ ...pages, [section.key]: page + 1 })}>›</button></div>
      </section>;
    })}
  </AdminLayout>;
}
