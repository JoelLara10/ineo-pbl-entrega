import { FiArrowLeft, FiRefreshCw } from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import './Administrativo.css';

export default function AdminLayout({ title, subtitle, children, onRefresh, refreshing, updatedAt, actions }) {
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  return (
    <main className="adm-page">
      <header className="adm-header">
        <button className="adm-icon-button" onClick={() => navigate(-1)} aria-label={t('common.back', 'Back')}>
          <FiArrowLeft />
        </button>
        <div>
          <h1>{title}</h1>
          {subtitle && <p>{subtitle}</p>}
        </div>
        <div className="adm-header-actions">
          {actions}
          {onRefresh && (
            <button className="adm-button adm-button-light" onClick={onRefresh} disabled={refreshing}>
              <FiRefreshCw className={refreshing ? 'spin' : ''} />
              {t('administrative.refresh')}
            </button>
          )}
        </div>
      </header>
      {updatedAt && (
        <p className="adm-updated">
          {t('administrative.updated')}: {new Intl.DateTimeFormat(i18n.language, { dateStyle: 'short', timeStyle: 'short' }).format(updatedAt)}
        </p>
      )}
      {children}
    </main>
  );
}
