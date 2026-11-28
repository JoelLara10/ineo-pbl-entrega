import api from './api';
export async function downloadMedicalPdf(path, attention) {
  const response = await api.get(path, {params:{id_atencion:attention}, responseType:'blob'});
  const blob = response.data;
  if (!(blob instanceof Blob) || !blob.size || !blob.type.includes('pdf')) throw new Error('Invalid PDF');
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url; link.download = path.split('/').slice(-2).join('_') + '.pdf';
  document.body.appendChild(link); link.click(); link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 60000);
  return true;
}
