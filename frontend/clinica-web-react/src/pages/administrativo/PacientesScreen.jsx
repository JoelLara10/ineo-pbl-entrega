import { useCallback, useMemo, useState } from 'react';
import { FiEdit2, FiEye, FiPlus, FiSearch } from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import adminService from '../../services/adminService';
import AdminLayout from './AdminLayout';
import useAdminData from './useAdminData';

const LIMIT = 5;
const groupsFrom = (value) => Array.isArray(value)
  ? [{ key: 'activos', patients: value, pagination: { total: value.length } }]
  : value?.groups || value?.data || [];
const keyOf = (patient, index) => patient.id_atencion || patient.idAtencion || patient.attention || patient.Id_exp || patient.id_exp || index;

export default function PacientesScreen() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [pages, setPages] = useState({});
  const loader = useCallback(() => adminService.getPatients(''), []);
  const state = useAdminData('patients:all:complete', loader, { groups: [], summary: {} });
  const groups = groupsFrom(state.data);

  const filtered = useMemo(() => groups.map((group) => {
    const query = search.trim().toLowerCase();
    const patients = (group.patients || []).filter((patient) => !query || Object.values(patient).join(' ').toLowerCase().includes(query));
    return { ...group, patients };
  }), [groups, search]);

  const open = (patient) => navigate(`/pacientes/${patient.Id_exp || patient.id_exp || patient.record || 'cuenta'}`, { state: { patient } });
  const edit = (patient) => navigate(`/pacientes/${patient.Id_exp || patient.id_exp}/editar`, { state: { patient } });

  return (
    <AdminLayout
      title={t('administrative.patientManagement')}
      subtitle={t('administrative.patientManagementDesc')}
      onRefresh={state.reload}
      refreshing={state.refreshing}
      updatedAt={state.updatedAt}
      actions={<button className="adm-button adm-button-success" onClick={() => navigate('/nuevo-paciente')}><FiPlus />{t('administrative.newPatient')}</button>}
    >
      <div className="adm-summary">
        {['activos', 'expedientes', 'altas'].map((item, index) => (
          <div className="adm-stat" style={{ '--accent': ['#667eea', '#ed8936', '#48bb78'][index] }} key={item}>
            <span>{t(`administrative.${item}`)}</span>
            <strong>{state.data?.summary?.[item] ?? groups.find((group) => group.key === item)?.patients?.length ?? 0}</strong>
          </div>
        ))}
      </div>
      <div className="adm-toolbar">
        <div className="adm-search"><FiSearch /><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder={t('administrative.searchPatients')} /></div>
      </div>
      {state.error && <div className="adm-alert">{t('administrative.apiError')}: {state.error}</div>}
      {state.loading ? <div className="adm-loading">{t('common.loading')}</div> : filtered.map((group) => {
        const page = pages[group.key] || 1;
        const totalPages = Math.max(1, Math.ceil(group.patients.length / LIMIT));
        const visible = group.patients.slice((page - 1) * LIMIT, page * LIMIT);
        return (
          <section className="adm-panel adm-section" key={group.key}>
            <div className="adm-section-head"><h2>{t(`administrative.group_${group.key}`, group.title || group.key)}</h2><span className="adm-badge">{group.patients.length}</span></div>
            <div className="adm-table-wrap"><table className="adm-table"><thead><tr>
              <th>{t('administrative.record')}</th><th>{t('administrative.patient')}</th><th>{t('administrative.age')}</th><th>{t('administrative.phone')}</th><th>{t('administrative.area')}</th><th>{t('administrative.bed')}</th><th>{t('common.actions')}</th>
            </tr></thead><tbody>{visible.map((patient, index) => <tr key={keyOf(patient, index)}>
              <td>{patient.record || patient.Id_exp || patient.id_exp || '-'}</td><td>{patient.name || patient.patient || [patient.nom_pac, patient.papell, patient.sapell].filter(Boolean).join(' ')}</td>
              <td>{patient.age ?? '-'}</td><td>{patient.phone || patient.tel || '-'}</td><td>{patient.area || '-'}</td><td>{patient.bed || patient.cama || '-'}</td>
              <td><div className="adm-actions"><button className="adm-button" onClick={() => open(patient)}><FiEye />{t('common.view')}</button><button className="adm-button adm-button-light" onClick={() => edit(patient)}><FiEdit2 />{t('common.edit')}</button></div></td>
            </tr>)}</tbody></table></div>
            {!visible.length && <div className="adm-empty">{t('administrative.noPatients')}</div>}
            <div className="adm-pagination"><button disabled={page === 1} onClick={() => setPages({ ...pages, [group.key]: page - 1 })}>‹</button><span>{page} / {totalPages}</span><button disabled={page === totalPages} onClick={() => setPages({ ...pages, [group.key]: page + 1 })}>›</button></div>
          </section>
        );
      })}
    </AdminLayout>
  );
}
