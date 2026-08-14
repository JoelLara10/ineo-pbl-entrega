import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { FiActivity, FiBarChart2, FiGitBranch, FiTrendingUp } from 'react-icons/fi';
import { sparkService } from '../../services/sparkService';
import './Spark.css';

export default function SparkDashboard() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [overview, setOverview] = useState({});
  const cards = [
    ['analytics', FiBarChart2, '/admin/spark/analytics'],
    ['met', FiTrendingUp, '/admin/spark/met'],
    ['clinical', FiActivity, '/admin/spark/clinical'],
    ['unsupervised', FiGitBranch, '/admin/spark/unsupervised'],
  ];

  useEffect(() => {
    sparkService.getOverview().then(setOverview).catch(() => setOverview({}));
  }, []);

  return (
    <main className="spark-page">
      <header className="spark-header">
        <span>{t('spark.eyebrow')}</span>
        <h1>{t('spark.title')}</h1>
        <p>{t('spark.description')}</p>
      </header>
      <section className="spark-cards">
        {cards.map(([type, CardIcon, path]) => (
          <button className="spark-module-card" key={type} onClick={() => navigate(path)}>
            <CardIcon size={30} />
            <h2>{t(`spark.types.${type}.title`)}</h2>
            <p>{t(`spark.types.${type}.description`)}</p>
            <span className={overview[type]?.available ? 'spark-ready' : 'spark-pending'}>
              {overview[type]?.available ? t('spark.resultsReady') : t('spark.noResults')}
            </span>
          </button>
        ))}
      </section>
    </main>
  );
}
