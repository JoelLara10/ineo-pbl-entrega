import { FiArrowLeft } from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import './ConfigStyles.css';

export default function ConfigHeader({ title, right = null, showBack = true }) {
  const navigate = useNavigate();
  const { t } = useTranslation();

  return (
    <header className="config-header-modern">
      <div className="config-header-left">
        {showBack && (
          <button className="config-back-btn" type="button" onClick={() => navigate(-1)}>
            <FiArrowLeft />
          </button>
        )}
      </div>
      <h1 className="config-title">{title || t('config.title')}</h1>
      <div>{right}</div>
    </header>
  );
}
