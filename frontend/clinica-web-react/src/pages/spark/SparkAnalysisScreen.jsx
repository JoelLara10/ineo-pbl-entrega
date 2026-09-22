import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { FiArrowLeft, FiPlay, FiRefreshCw } from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';
import { sparkService } from '../../services/sparkService';
import './Spark.css';

const isSimple = (value) => value === null || ['string', 'number', 'boolean'].includes(typeof value);
const prettyKey = (key) => key.replaceAll('_', ' ').replace(/\b\w/g, (letter) => letter.toUpperCase());
const hasContent = (value) => {
  if (value === null || value === undefined) return false;
  if (Array.isArray(value)) return value.length > 0;
  if (typeof value === 'object') return Object.keys(value).length > 0;
  return value !== '';
};

function DataValue({ value }) {
  if (isSimple(value)) return <span>{value === null ? '—' : String(value)}</span>;
  if (Array.isArray(value)) {
    if (!value.length) return <span>—</span>;
    if (value.every(isSimple)) return <ul>{value.slice(0, 20).map((item, index) => <li key={index}>{String(item)}</li>)}</ul>;
    return <div className="spark-array">{value.slice(0, 12).map((item, index) => <DataObject key={index} data={item} />)}</div>;
  }
  return <DataObject data={value} />;
}

function DataObject({ data }) {
  if (!data || typeof data !== 'object') return <DataValue value={data} />;
  return (
    <div className="spark-data-grid">
      {Object.entries(data).map(([key, value]) => (
        <div className={isSimple(value) ? 'spark-datum' : 'spark-nested'} key={key}>
          <strong>{prettyKey(key)}</strong>
          <DataValue value={value} />
        </div>
      ))}
    </div>
  );
}

function VisualGallery({ images }) {
  const [sources, setSources] = useState({});
  useEffect(() => {
    let active = true;
    const urls = [];
    Promise.all((images || []).map(async (image) => {
      const url = await sparkService.getImage(image.url);
      urls.push(url);
      return [image.filename, url];
    })).then((entries) => active && setSources(Object.fromEntries(entries))).catch(() => {});
    return () => { active = false; urls.forEach(URL.revokeObjectURL); };
  }, [images]);
  if (!images?.length) return null;
  return <div className="spark-gallery">{images.map((image) => sources[image.filename] && (
    <figure key={image.filename}><img src={sources[image.filename]} alt={image.name} /><figcaption>{image.name}</figcaption></figure>
  ))}</div>;
}

/** Mapea status HTTP del API a una clave de estado de UI. */
function mapHttpError(requestError) {
  if (!requestError.response) return 'offline';
  const code = requestError.response.status;
  if (code === 401) return 'unauthorized';
  if (code === 403) return 'forbidden';
  if (code === 409) return 'conflict';
  return 'error';
}

export default function SparkAnalysisScreen({ type }) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [status, setStatus] = useState({ state: 'idle', running: false });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [errorKind, setErrorKind] = useState('error');

  const load = useCallback(async () => {
    setLoading(true); setError(''); setErrorKind('error');
    try {
      const [results, currentStatus] = await Promise.all([
        sparkService.getResults(type), sparkService.getStatus(type),
      ]);
      setData(results); setStatus(currentStatus);
    } catch (requestError) {
      const kind = mapHttpError(requestError);
      setErrorKind(kind);
      setError(
        requestError.response?.data?.error
        || t(`spark.states.${kind}.hint`, { defaultValue: t('spark.loadError') }),
      );
    } finally { setLoading(false); }
  }, [t, type]);

  useEffect(() => { load(); }, [load]);
  useEffect(() => {
    if (!status.running) return undefined;
    const timer = window.setInterval(async () => {
      try {
        const next = await sparkService.getStatus(type);
        setStatus(next);
        if (!next.running) load();
      } catch {
        // Si el polling falla, el usuario puede usar Actualizar.
      }
    }, 3000);
    return () => window.clearInterval(timer);
  }, [load, status.running, type]);

  const sections = useMemo(
    () => Object.entries(data || {}).filter(
      ([key, value]) =>
        !['available', 'timestamp', 'visualizations', 'type'].includes(key) &&
        hasContent(value)
    ),
    [data]
  );

  const run = async () => {
    setError(''); setErrorKind('error');
    try {
      const response = await sparkService.run(type);
      setStatus(response.status);
    } catch (requestError) {
      const kind = mapHttpError(requestError);
      // 409: el job ya corre; refrescar estado en vez de bloquear.
      if (requestError.response?.status === 409) {
        setErrorKind('conflict');
        setError(requestError.response?.data?.error || t('spark.states.conflict.hint'));
        load();
        return;
      }
      setErrorKind(kind);
      setError(
        requestError.response?.data?.error
        || t(`spark.states.${kind}.hint`, { defaultValue: t('spark.runError') }),
      );
    }
  };

  const isProcessing = status.running || status.state === 'processing';
  const isPending = !data?.available && (status.state === 'idle' || status.state === 'pending');
  const isCompleted = data?.available && (status.state === 'completed' || status.state === 'idle' || !status.running);

  return <main className="spark-page">
    <div className="spark-toolbar">
      <button type="button" onClick={() => navigate('/admin/spark')}><FiArrowLeft /> {t('common.back', 'Volver')}</button>
      <div>
        <button type="button" onClick={load} disabled={loading}><FiRefreshCw /> {t('spark.refresh')}</button>
        <button type="button" className="spark-primary" onClick={run} disabled={status.running}>
          <FiPlay /> {status.running ? t('spark.running') : t('spark.run')}
        </button>
      </div>
    </div>
    <header className="spark-header">
      <span>{t('spark.eyebrow')}</span>
      <h1>{t(`spark.types.${type}.title`)}</h1>
      <p>{t(`spark.types.${type}.description`)}</p>
      {isCompleted && !error && !loading && (
        <p className="spark-status-badge" role="status">{t('spark.states.completed.title')}</p>
      )}
    </header>
    {error && (
      <div className="spark-state spark-state-error" role="alert">
        <h2>{t(`spark.states.${errorKind}.title`, { defaultValue: t('spark.states.error.title') })}</h2>
        <p>
          {['offline', 'forbidden', 'unauthorized', 'conflict'].includes(errorKind)
            ? t(`spark.states.${errorKind}.hint`)
            : error}
        </p>
        <button type="button" onClick={errorKind === 'forbidden' || errorKind === 'unauthorized' ? () => navigate('/') : load}>
          {errorKind === 'forbidden' || errorKind === 'unauthorized'
            ? t('common.back', 'Volver')
            : t('common.retry')}
        </button>
      </div>
    )}
    {!error && loading ? (
      <div className="spark-state" role="status">
        <h2>{t('spark.states.loading.title')}</h2>
        <p>{t('spark.states.loading.hint')}</p>
        <button type="button" onClick={load}>{t('spark.refresh')}</button>
      </div>
    ) : !error && isProcessing ? (
      <div className="spark-state spark-state-processing" role="status">
        <h2>{t('spark.states.processing.title')}</h2>
        <p>{t('spark.states.processing.hint')}</p>
        <button type="button" onClick={load}>{t('spark.refresh')}</button>
      </div>
    ) : !error && status.state === 'failed' ? (
      <div className="spark-state spark-state-error" role="alert">
        <h2>{t('spark.states.failed.title')}</h2>
        <p>{t('spark.states.failed.hint')}</p>
        <button type="button" onClick={run}>{t('spark.states.failed.action')}</button>
      </div>
    ) : !error && isPending ? (
      <div className="spark-state">
        <h2>{t('spark.states.pending.title')}</h2>
        <p>{t('spark.states.pending.hint')}</p>
        <button type="button" className="spark-primary" onClick={run}>{t('spark.states.pending.action')}</button>
      </div>
    ) : !error && !data?.available ? (
      <div className="spark-state">
        <h2>{t('spark.states.empty.title')}</h2>
        <p>{t('spark.states.empty.hint')}</p>
        <button type="button" onClick={load}>{t('spark.states.empty.action')}</button>
      </div>
    ) : (
      <>
        {sections.map(([key, value]) => (
          <section className="spark-panel" key={key}>
            <h2>{t(`spark.sections.${key}`, prettyKey(key))}</h2>
            <DataValue value={value} />
          </section>
        ))}
        <VisualGallery images={data?.visualizations} />
      </>
    )}
    {status.state === 'failed' && status.log && (
      <details className="spark-log">
        <summary>{t('spark.executionFailed')}</summary>
        <pre>{status.log}</pre>
      </details>
    )}
  </main>;
}
