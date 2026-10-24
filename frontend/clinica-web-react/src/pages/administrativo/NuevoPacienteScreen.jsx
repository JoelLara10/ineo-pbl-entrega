import { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { FiSearch } from 'react-icons/fi';
import adminService from '../../services/adminService';
import { clearAdminCache } from '../../services/adminCache';
import AdminLayout from './AdminLayout';

const defaults = { curp: '', papell: '', sapell: '', nom_pac: '', fecnac: '', tel: '', area: 'Consulta', cama: '', motivo: 'Consulta', especialidad: 'Oftalmologia', alergias: '', fam_nombre: '', fam_parentesco: '', fam_tel: '' };

const optionValue = (option) => {
  if (option == null) return '';
  if (typeof option !== 'object') return String(option);
  return String(
    option.id ??
    option.value ??
    option.id_cama ??
    option.id_medico ??
    option.id_serv ??
    option.numero ??
    option.nombre ??
    option.username ??
    '',
  );
};

const optionLabel = (option) => {
  if (option == null) return '';
  if (typeof option !== 'object') return String(option);
  return String(
    option.label ??
    option.nombre ??
    option.name ??
    option.numero ??
    option.descripcion ??
    option.especialidad ??
    option.area ??
    option.motivo ??
    option.username ??
    optionValue(option),
  );
};

export default function NuevoPacienteScreen() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const { id } = useParams();
  const source = location.state?.patient || {};
  const editMode = Boolean(id);
  const [form, setForm] = useState({ ...defaults, ...source, curp: source.curp || source.rawPatient?.curp || '', nom_pac: source.nom_pac || source.name || '' });
  const [options, setOptions] = useState({ areas: [], motivos: [], especialidades: [], camas: [], medicos: [] });
  const [doctors, setDoctors] = useState(source.doctors || []);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [patientSearch, setPatientSearch] = useState('');
  const [patientMatches, setPatientMatches] = useState([]);
  const [searchingPatients, setSearchingPatients] = useState(false);
  const [patientSearchError, setPatientSearchError] = useState('');

  useEffect(() => {
    Promise.all([adminService.getOptions(source.id_cama), editMode ? adminService.getPatient(id) : null])
      .then(([opts, detail]) => {
        const availableOptions = opts || {};
        setOptions(availableOptions);
        if (detail) {
          const raw = detail.rawPatient || detail.patient || detail;
          const active = detail.activeAppointment || {};
          const family = detail.family || {};
          const area = active.area || '';
          const formArea = Object.keys(availableOptions.areaMap || {}).find(
            (key) => availableOptions.areaMap[key] === area,
          ) || area;
          setForm((current) => ({
            ...current,
            curp: raw.curp || '',
            papell: raw.papell || '',
            sapell: raw.sapell || '',
            nom_pac: raw.nom_pac || '',
            fecnac: raw.fecnac?.slice?.(0, 10) || '',
            tel: raw.tel || '',
            area: formArea || (active.id_atencion ? '' : defaults.area),
            cama: active.id_cama || active.cama || '',
            motivo: active.motivo || active.reason || (active.id_atencion ? '' : defaults.motivo),
            especialidad: active.especialidad || active.specialty || (active.id_atencion ? '' : defaults.especialidad),
            alergias: active.alergias || active.allergies || '',
            fam_nombre: family.nombre || '',
            fam_parentesco: family.parentesco || '',
            fam_tel: family.telefono || '',
          }));
          setDoctors(active.doctors || []);
        }
      })
      .catch((requestError) => setError(requestError.response?.data?.error || requestError.message))
      .finally(() => setLoading(false));
  }, [editMode, id, source.id_cama]);

  useEffect(() => {
    const query = patientSearch.trim();
    if (editMode || query.length < 2) {
      setPatientMatches([]);
      setPatientSearchError('');
      setSearchingPatients(false);
      return undefined;
    }

    let cancelled = false;
    const timer = setTimeout(async () => {
      setSearchingPatients(true);
      setPatientSearchError('');
      try {
        const results = await adminService.searchPatients(query, 8);
        if (!cancelled) setPatientMatches(Array.isArray(results) ? results : results?.data || []);
      } catch (requestError) {
        if (!cancelled) {
          setPatientMatches([]);
          setPatientSearchError(requestError.response?.data?.error || requestError.message);
        }
      } finally {
        if (!cancelled) setSearchingPatients(false);
      }
    }, 250);

    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [editMode, patientSearch]);

  const doctorOptions = useMemo(() => (options.medicos || []).map((doctor) => ({
    id: optionValue(doctor),
    label: typeof doctor === 'object'
      ? [doctor.nombre, doctor.papell, doctor.sapell].filter(Boolean).join(' ') || optionLabel(doctor)
      : optionLabel(doctor),
  })), [options.medicos]);
  const update = (key, value) => setForm((current) => ({ ...current, [key]: value }));
  const toggleDoctor = (doctorId) => setDoctors((current) => current.includes(doctorId) ? current.filter((value) => value !== doctorId) : current.length < 5 ? [...current, doctorId] : current);
  const submit = async (event) => {
    event.preventDefault();
    setSaving(true); setError('');
    try {
      const payload = { ...form, assignedDoctors: doctors };
      if (editMode) await adminService.updatePatient(id, payload);
      else await adminService.createPatient(payload);
      clearAdminCache();
      navigate('/pacientes');
    } catch (requestError) {
      setError(requestError.response?.data?.error || requestError.message);
    } finally { setSaving(false); }
  };
  const input = (key, type = 'text', required = false) => <input type={type} value={form[key] || ''} required={required} onChange={(event) => update(key, event.target.value)} />;
  const select = (key, values = []) => (
    <select value={form[key] || ''} onChange={(event) => update(key, event.target.value)}>
      <option value="">{t('common.select')}</option>
      {values.map((value, index) => {
        const normalizedValue = optionValue(value);
        return (
          <option key={`${key}-${normalizedValue}-${index}`} value={normalizedValue}>
            {optionLabel(value)}
          </option>
        );
      })}
    </select>
  );

  return <AdminLayout title={t(editMode ? 'administrative.editPatient' : 'administrative.registerPatient')} subtitle={t('administrative.patientFormDesc')}>
    {!editMode && <section className="adm-panel adm-form-section">
      <h2>{t('administrative.searchPreviousPatients')}</h2>
      <div className="adm-search"><FiSearch /><input value={patientSearch} onChange={(event) => setPatientSearch(event.target.value)} placeholder={t('administrative.searchPatients')} aria-label={t('administrative.searchPreviousPatients')} /></div>
      {searchingPatients && <div className="adm-loading">{t('common.loading')}</div>}
      {patientSearchError && <div className="adm-alert" role="alert">{patientSearchError}</div>}
      {patientMatches.length > 0 && <div className="adm-actions">{patientMatches.map((patient, index) => {
        const patientId = patient.Id_exp || patient.id_exp || patient.record;
        const name = patient.name || patient.patient || [patient.nom_pac, patient.papell, patient.sapell].filter(Boolean).join(' ');
        const active = Boolean(patient.hasActiveAttention);
        return <button key={patientId || index} type="button" className="adm-button adm-button-light" disabled={active || !patientId} onClick={() => navigate(`/pacientes/${patientId}/editar`, { state: { patient, reactivation: true } })}>
          {name} · {patient.record || `OFTALCORE-${patientId}`} · {active ? t('administrative.patientAlreadyActive') : t('administrative.reactivatePatient')}
        </button>;
      })}</div>}
      {patientSearch.trim().length >= 2 && !searchingPatients && !patientSearchError && patientMatches.length === 0 && <div className="adm-empty">{t('administrative.noPatients')}</div>}
    </section>}
    {loading ? <div className="adm-loading">{t('common.loading')}</div> : <form onSubmit={submit}>
      {error && <div className="adm-alert">{error}</div>}
      <section className="adm-panel adm-form-section"><h2>{t('administrative.personalData')}</h2><div className="adm-form-grid">
        <div className="adm-field"><label>CURP</label>{input('curp', 'text', true)}</div>
        <div className="adm-field"><label>{t('administrative.firstSurname')}</label>{input('papell', 'text', true)}</div>
        <div className="adm-field"><label>{t('administrative.secondSurname')}</label>{input('sapell')}</div>
        <div className="adm-field"><label>{t('administrative.names')}</label>{input('nom_pac', 'text', true)}</div>
        <div className="adm-field"><label>{t('administrative.birthDate')}</label>{input('fecnac', 'date', true)}</div>
        <div className="adm-field"><label>{t('administrative.phone')}</label>{input('tel')}</div>
      </div></section>
      <section className="adm-panel adm-form-section"><h2>{t('administrative.attentionData')}</h2><div className="adm-form-grid">
        <div className="adm-field"><label>{t('administrative.area')}</label>{select('area', options.areas || [])}</div>
        <div className="adm-field"><label>{t('administrative.bed')}</label>{select('cama', options.camas || [])}</div>
        <div className="adm-field"><label>{t('administrative.reason')}</label>{select('motivo', options.motivos || [])}</div>
        <div className="adm-field"><label>{t('administrative.specialty')}</label>{select('especialidad', options.especialidades || [])}</div>
        <div className="adm-field" style={{ gridColumn: '1/-1' }}><label>{t('administrative.allergies')}</label><textarea value={form.alergias || ''} onChange={(event) => update('alergias', event.target.value)} /></div>
      </div></section>
      <section className="adm-panel adm-form-section"><h2>{t('administrative.assignedDoctors')}</h2><div className="adm-actions">{doctorOptions.map((doctor) => <label className="adm-document" key={doctor.id}><input type="checkbox" checked={doctors.includes(doctor.id)} onChange={() => toggleDoctor(doctor.id)} /> {doctor.label}</label>)}</div></section>
      <section className="adm-panel adm-form-section"><h2>{t('administrative.familyData')}</h2><div className="adm-form-grid">
        <div className="adm-field"><label>{t('administrative.familyName')}</label>{input('fam_nombre')}</div><div className="adm-field"><label>{t('administrative.relationship')}</label>{input('fam_parentesco')}</div><div className="adm-field"><label>{t('administrative.phone')}</label>{input('fam_tel')}</div>
      </div></section>
      <div className="adm-toolbar"><button type="button" className="adm-button adm-button-light" onClick={() => navigate(-1)}>{t('common.cancel')}</button><button className="adm-button adm-button-success" disabled={saving}>{saving ? t('common.loading') : t('common.save')}</button></div>
    </form>}
  </AdminLayout>;
}
