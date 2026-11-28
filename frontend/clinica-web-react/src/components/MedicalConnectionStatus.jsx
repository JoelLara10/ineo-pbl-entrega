import { FiCloud, FiCloudOff } from 'react-icons/fi';
import { useTranslation } from 'react-i18next';
export default function MedicalConnectionStatus({ status, message }) {
  const { t } = useTranslation();
  if (!['remote', 'cache', 'error'].includes(status)) return null;
  const remote = status === 'remote';
  const Icon = remote ? FiCloud : FiCloudOff;
  return <div role={remote ? 'status' : 'alert'} style={{display:'flex', alignItems:'center', gap:8, marginTop:12, padding:'10px 14px', borderRadius:10, border:'1px solid', borderColor: remote ? '#9ae6b4' : status === 'cache' ? '#fbd38d' : '#feb2b2', backgroundColor:remote ? '#f0fff4' : status === 'cache' ? '#fffaf0' : '#fff5f5', color:'#2d3748', fontSize:12}}>
    <Icon size={18} style={{flexShrink:0}} />
    <span>{remote ? t('common.remoteDataLoaded') : status === 'cache' ? t('common.cachedDataWarning') : message}</span>
  </div>;
}
