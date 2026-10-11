import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FiChevronLeft, FiChevronRight, FiEdit2, FiRefreshCw, FiSave, FiSearch, FiTrash2, FiUserPlus, FiX } from 'react-icons/fi';
import ConfigHeader from './ConfigHeader';
import api from '../../services/api';
import { getCache, setCache, paginate, pages } from './configCache';
import './ConfigStyles.css';

const CACHE_KEY = 'usuarios';
const ITEMS_PER_PAGE = 6;
const canonicalRole = (role) => role === 'enfermeria' ? 'enfermero' : role;
const dateForInput = (value) => {
  const match = String(value || '').match(/^(\d{4}-\d{2}-\d{2})/);
  return match ? match[1] : '';
};

const emptyForm = {
  curp: '', nombre: '', papell: '', sapell: '', fecnac: '', telefono: '', matricula: '', cedula: '',
  cargo: '', email: '', pregunta_seguridad: '', username: '', password: '', role: '', activo: true,
};

export default function UsuariosConfigScreen() {
  const { t } = useTranslation();
  const [usuarios, setUsuarios] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingUser, setEditingUser] = useState(null);
  const [changePassword, setChangePassword] = useState(false);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [msg, setMsg] = useState('');
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async (force = false) => {
    setLoading(true);
    setMsg('');
    if (!force) {
      const cached = getCache(CACHE_KEY);
      if (cached) {
        setUsuarios(cached);
        setLoading(false);
        return;
      }
    }
    try {
      const response = await api.get('/auth/users');
      const data = response.data?.data || response.data || [];
      const canonicalUsers = (Array.isArray(data) ? data : []).map((user) => ({ ...user, role: canonicalRole(user.role) }));
      setUsuarios(canonicalUsers);
      setCache(CACHE_KEY, canonicalUsers);
    } catch (error) {
      const cached = getCache(CACHE_KEY);
      if (cached) {
        setUsuarios(cached);
        setMsg(t('config.userOffline'));
      } else {
        setMsg(error.response?.data?.error || t('config.userLoadError'));
      }
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => { load(); }, [load]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return usuarios;
    return usuarios.filter((u) => `${u.nombre || ''} ${u.papell || ''} ${u.sapell || ''} ${u.username || ''} ${canonicalRole(u.role) || ''} ${u.email || ''}`.toLowerCase().includes(q));
  }, [usuarios, search]);

  const totalPages = pages(filtered, ITEMS_PER_PAGE);
  const list = paginate(filtered, page, ITEMS_PER_PAGE);

  const onRefresh = async () => {
    setRefreshing(true);
    setPage(1);
    await load(true);
    setRefreshing(false);
  };

  const resetForm = () => {
    setForm(emptyForm);
    setEditingUser(null);
    setChangePassword(false);
  };

  const startEdit = (user) => {
    setEditingUser(user);
    setChangePassword(false);
    setForm({
      ...emptyForm,
      curp: user.curp || '',
      nombre: user.nombre || '',
      papell: user.papell || '',
      sapell: user.sapell || '',
      fecnac: dateForInput(user.fecnac),
      telefono: user.telefono || '',
      matricula: user.matricula || '',
      cedula: user.cedula || '',
      cargo: user.cargo || '',
      email: user.email || '',
      pregunta_seguridad: user.pregunta_seguridad || user.preguntaSeguridad || '',
      username: user.username || '',
      role: canonicalRole(user.role) || '',
    });
    setMsg('');
  };

  const save = async (event) => {
    event.preventDefault();
    const username = form.username.trim();
    const nombre = form.nombre.trim();
    if (!username || !nombre || !form.role || (!editingUser && !form.password)) {
      setMsg(t('config.userRequired'));
      return;
    }
    if ((!editingUser || changePassword) && form.password && new TextEncoder().encode(form.password).length > 72) {
      setMsg(t('config.userPasswordTooLong'));
      return;
    }
    try {
      if (editingUser) {
        const id = editingUser.id || editingUser._id;
        if (!id) {
          setMsg(t('config.userIdNotFound'));
          return;
        }
        const payload = {
          curp: form.curp,
          nombre,
          papell: form.papell,
          sapell: form.sapell,
          telefono: form.telefono,
          matricula: form.matricula,
          cedula: form.cedula,
          cargo: form.cargo,
          email: form.email,
          pregunta_seguridad: form.pregunta_seguridad,
          username,
          role: canonicalRole(form.role),
        };
        if (form.fecnac || !editingUser.fecnac) payload.fecnac = form.fecnac;
        if (changePassword && form.password) payload.password = form.password;
        await api.put(`/auth/users/${id}`, payload);
        resetForm();
        await load(true);
        setMsg(t('config.userUpdated'));
      } else {
        const payload = { ...form, nombre, username, activo: true };
        await api.post('/auth/users', payload);
        resetForm();
        setSearch('');
        setPage(1);
        await load(true);
        setMsg(t('config.userSaved'));
      }
    } catch (error) {
      setMsg(error.response?.data?.error || (editingUser ? t('config.userUpdateError') : t('config.userSaveError')));
    }
  };

  const toggle = async (u) => {
    const id = u.id || u._id;
    if (!id) return setMsg(t('config.userIdNotFound'));
    try {
      await api.put(`/auth/users/${id}`, { activo: !u.activo });
      await load(true);
    } catch (error) {
      setMsg(error.response?.data?.error || t('config.userUpdateError'));
    }
  };

  const remove = async (u) => {
    const id = u.id || u._id;
    if (!id) return setMsg(t('config.userIdNotFound'));
    if (!window.confirm(t('config.userDeleteConfirm'))) return;
    try {
      await api.delete(`/auth/users/${id}`);
      await load(true);
      setMsg(t('config.userDeleted'));
    } catch (error) {
      setMsg(error.response?.data?.error || t('config.userDeleteError'));
    }
  };

  return (
    <main className="config-page">
      <ConfigHeader title={t('config.headerUsers')} right={<button className="config-refresh-btn" type="button" onClick={onRefresh}><FiRefreshCw className={refreshing ? 'spin' : ''} /></button>} />
      <section className="config-content">
        <form className="config-card config-main-card" onSubmit={save}>
          <div className="config-card-header"><FiUserPlus size={28} /><h2>{editingUser ? t('config.editUser') : t('config.registerUser')}</h2></div>
          <div className="config-card-body">
            <div className="config-section-box">
              <h3 className="config-subtitle">🪪 {t('config.personalData')}</h3>
              <label className="config-label">CURP</label>
              <input className="config-input" value={form.curp} onChange={(e) => setForm({ ...form, curp: e.target.value.toUpperCase() })} placeholder={t('config.curpPlaceholder')} />
              <label className="config-label">{t('config.userName')}</label>
              <input className="config-input" value={form.nombre} onChange={(e) => setForm({ ...form, nombre: e.target.value })} placeholder={t('config.userNamePlaceholder')} />
              <div className="config-grid-2">
                <div><label className="config-label">{t('config.firstName')}</label><input className="config-input" value={form.papell} onChange={(e) => setForm({ ...form, papell: e.target.value })} placeholder={t('config.firstNamePlaceholder')} /></div>
                <div><label className="config-label">{t('config.lastName')}</label><input className="config-input" value={form.sapell} onChange={(e) => setForm({ ...form, sapell: e.target.value })} placeholder={t('config.lastNamePlaceholder')} /></div>
              </div>
              <div className="config-grid-2">
                <div><label className="config-label">{t('config.birthDate')}</label><input className="config-input" type="date" value={form.fecnac} onChange={(e) => setForm({ ...form, fecnac: e.target.value })} /></div>
                <div><label className="config-label">{t('config.phone')}</label><input className="config-input" value={form.telefono} onChange={(e) => setForm({ ...form, telefono: e.target.value })} placeholder={t('config.phonePlaceholder')} /></div>
              </div>
              <div className="config-grid-2">
                <div><label className="config-label">{t('config.enrollment')}</label><input className="config-input" value={form.matricula} onChange={(e) => setForm({ ...form, matricula: e.target.value })} placeholder={t('config.enrollmentPlaceholder')} /></div>
                <div><label className="config-label">{t('config.license')}</label><input className="config-input" value={form.cedula} onChange={(e) => setForm({ ...form, cedula: e.target.value })} placeholder={t('config.licensePlaceholder')} /></div>
              </div>
            </div>

            <div className="config-section-box">
              <h3 className="config-subtitle">⚙️ {t('config.systemData')}</h3>
              <div className="config-grid-2">
                <div><label className="config-label">{t('config.position')}</label><input className="config-input" value={form.cargo} onChange={(e) => setForm({ ...form, cargo: e.target.value })} placeholder={t('config.positionPlaceholder')} /></div>
                <div><label className="config-label">{t('config.email')}</label><input className="config-input" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} placeholder={t('config.emailPlaceholder')} /></div>
              </div>
              <label className="config-label">{t('config.securityQuestion')}</label>
              <input className="config-input" value={form.pregunta_seguridad} onChange={(e) => setForm({ ...form, pregunta_seguridad: e.target.value })} placeholder={t('config.securityQuestionPlaceholder')} />
              <div className="config-grid-3">
                <div><label className="config-label">{t('config.username')}</label><input className="config-input" name="account-username" autoComplete="off" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} placeholder={t('config.usernamePlaceholder')} /></div>
                {editingUser && !changePassword ? (
                  <div>
                    <label className="config-label">{t('config.password')}</label>
                    <button className="config-btn secondary" type="button" onClick={() => setChangePassword(true)}>{t('config.changeUserPassword')}</button>
                  </div>
                ) : (
                  <div>
                    <label className="config-label">{t('config.password')}</label>
                    <input
                      className="config-input"
                      type="password"
                      name={editingUser ? 'new-account-password' : 'new-user-password'}
                      autoComplete="new-password"
                      value={form.password}
                      onChange={(e) => setForm({ ...form, password: e.target.value })}
                      placeholder={editingUser ? t('config.passwordOptionalPlaceholder') : t('config.passwordPlaceholder')}
                    />
                    {editingUser && <button className="config-btn secondary" type="button" onClick={() => { setChangePassword(false); setForm((current) => ({ ...current, password: '' })); }}>{t('config.cancelPasswordChange')}</button>}
                  </div>
                )}
                <div><label className="config-label">{t('config.role')}</label><select className="config-select" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}><option value="">{t('config.selectRole')}</option><option value="admin">{t('config.roleAdmin')}</option><option value="administrativo">{t('config.roleAdministrative')}</option><option value="medico">{t('config.roleMedical')}</option><option value="enfermero">{t('config.roleNurse')}</option><option value="estudios">{t('config.roleStudies')}</option></select></div>
              </div>
            </div>
            <div className="config-form-footer"><button className="config-btn secondary" type="button" onClick={resetForm}><FiX /> {t('config.cancel')}</button><button className="config-btn success" type="submit"><FiSave /> {editingUser ? t('config.updateUser') : t('config.saveUser')}</button></div>
            {msg && <div className="config-alert">{msg}</div>}
          </div>
        </form>

        <h2 className="config-section-title">{t('config.usersRegistered')}</h2>
        <div className="config-search"><FiSearch className="config-search-icon" /><input className="config-input" value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} placeholder={t('config.searchUser')} /></div>
        {loading ? <div className="config-card">{t('config.loadingUsers')}</div> : null}
        {!loading && list.map((u, index) => <article className="config-card" key={u.id || u._id || u.username || `user-${index}`}><div className="config-row"><div><h3>{u.nombre || t('config.noName')} {u.papell || ''} {u.sapell || ''}</h3><p>{t('config.username')}: {u.username || t('config.noUsername')} · {t('config.role')}: {canonicalRole(u.role) || t('config.noRole')}</p>{u.email && <p>{t('config.email')}: {u.email}</p>}</div><label className="config-row"><input className="config-switch" type="checkbox" checked={!!u.activo} onChange={() => toggle(u)} /><span className={`config-badge ${u.activo ? 'success' : 'danger'}`}>{u.activo ? t('config.activeStatus') : t('config.inactiveStatus')}</span></label></div><div className="config-actions"><button className="config-btn secondary" type="button" onClick={() => startEdit(u)}><FiEdit2 /> {t('config.edit')}</button><button className="config-btn danger" type="button" onClick={() => remove(u)}><FiTrash2 /> {t('config.delete')}</button></div></article>)}
        {!loading && filtered.length === 0 ? <div className="config-card">{t('config.noUsersRegistered')}</div> : null}
        {filtered.length > ITEMS_PER_PAGE && <div className="config-pagination"><button className="config-btn secondary" disabled={page === 1} onClick={() => setPage(page - 1)}><FiChevronLeft /></button><span className="config-page-pill">{page} / {totalPages}</span><button className="config-btn secondary" disabled={page === totalPages} onClick={() => setPage(page + 1)}><FiChevronRight /></button></div>}
      </section>
    </main>
  );
}
