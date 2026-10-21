import { useId, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FiChevronDown, FiChevronUp, FiClock, FiUser } from 'react-icons/fi';
import './NursingSections.css';

export function NursingPatientCard({ title, label, theme }) {
  return <section className={`nursing-patient nursing-theme-${theme}`}>
    <div className="nursing-patient-avatar"><FiUser size={30} aria-hidden="true" /></div>
    <div><h2>{title}</h2><p>{label}</p></div>
  </section>;
}

export function NursingFormCard({ title, icon, theme, children }) {
  const titleId = useId();
  return <section className={`nursing-section nursing-theme-${theme}`} aria-labelledby={titleId}>
    <h2 id={titleId} className="nursing-section-title">{icon}{title}</h2>
    <div className="nursing-form-body">{children}</div>
  </section>;
}

export function NursingHistoryCard({ title, count, theme, children }) {
  const [expanded, setExpanded] = useState(true);
  const bodyId = useId();
  const { t } = useTranslation();
  return <section className={`nursing-section nursing-theme-${theme}`}>
    <h2 className="nursing-history-heading">
      <button type="button" className="nursing-history-toggle" aria-expanded={expanded}
        aria-controls={bodyId} onClick={() => setExpanded((value) => !value)}>
        <span className="nursing-history-title"><FiClock size={18} aria-hidden="true" />
          <strong>{title}</strong><span className="nursing-history-count">{t('nursingAssessment.records', { count })}</span>
        </span>
        {expanded ? <FiChevronUp size={18} aria-hidden="true" /> : <FiChevronDown size={18} aria-hidden="true" />}
      </button>
    </h2>
    <div id={bodyId} className="nursing-history-body" hidden={!expanded}>{children}</div>
  </section>;
}
