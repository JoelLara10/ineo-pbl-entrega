const xml = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;' }[char]));
const csvCell = (value) => {
  let text = String(value ?? '');
  if (typeof value === 'string' && /^[\s]*[=+@-]/.test(text)) text = "'" + text;
  return '"' + text.replaceAll('"', '""') + '"';
};
export const makeCsv = (rows) => '\uFEFF' + rows.map((row) => row.map(csvCell).join(',')).join('\r\n');
export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url; link.download = filename; document.body.append(link); link.click(); link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}
export const downloadCsv = (rows, filename) => downloadBlob(new Blob([makeCsv(rows)], { type: 'text/csv;charset=utf-8' }), filename);
const lines = (text, limit = 100) => String(text).split(/\s+/).flatMap((word) => word.match(new RegExp(`.{1,${limit}}`, 'g')) || ['']).reduce((result, word) => {
  const last = result.length - 1;
  if (result[last] && result[last].length + word.length > limit) result.push(word);
  else result[last] = result[last] ? result[last] + ' ' + word : word;
  return result;
}, ['']);
export function makeChartSvg({ title, hint, scope, source, unit, rows, mode, color = '#2563eb', reference, referenceLabel, format = String }) {
  const width = 1100;
  const head = [title, ...lines(hint), ...lines(scope), ...lines(source)];
  const top = 45 + head.length * 23;
  const line = mode === 'line' && rows.length > 1;
  const labelLines = rows.map((row) => lines(row.label, 27));
  const heights = labelLines.map((labels) => Math.max(54, labels.length * 17 + 12));
  const height = line ? top + 350 : top + Math.max(54, heights.reduce((sum, value) => sum + value, 0)) + 100;
  const min = Math.min(0, ...rows.map((row) => row.value));
  const max = Math.max(1, Number.isFinite(reference) ? reference : 0, ...rows.map((row) => row.value));
  const span = max - min; const left = 300; const right = 980;
  const px = (value) => left + (value - min) / span * (right - left);
  const parts = [`<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img"><title>${xml(title)}</title><desc>${xml(hint)}</desc><rect width="100%" height="100%" fill="white"/><g font-family="Arial,sans-serif" fill="#1e293b">`];
  head.forEach((text, i) => parts.push(`<text x="30" y="${32 + i * 23}" font-size="${i ? 15 : 22}" font-weight="${i ? 400 : 700}">${xml(text)}</text>`));
  if (line) {
    const times = rows.map((row) => Date.parse(row.rawLabel?.length === 7 ? row.rawLabel + '-01' : row.rawLabel));
    const elapsed = times[times.length - 1] - times[0];
    const x = (i) => 100 + (elapsed > 0 ? (times[i] - times[0]) / elapsed : i / (rows.length - 1)) * 880;
    const y = (value) => top + 230 - (value - min) / span * 200;
    for (const tick of [0, .25, .5, .75, 1]) parts.push(`<line x1="100" x2="980" y1="${y(min + span * tick)}" y2="${y(min + span * tick)}" stroke="#e2e8f0"/><text x="90" y="${y(min + span * tick) + 5}" text-anchor="end" font-size="14">${xml(format(min + span * tick))}</text>`);
    parts.push(`<text x="100" y="${top + 10}" font-size="14">${xml(unit)}</text><polyline fill="none" stroke="${xml(color)}" stroke-width="3" points="${rows.map((row, i) => `${x(i)},${y(row.value)}`).join(' ')}"/>`);
    for (const i of new Set([0, Math.floor((rows.length - 1) / 2), rows.length - 1])) parts.push(`<text x="${x(i)}" y="${top + 260}" font-size="14" text-anchor="${i === 0 ? 'start' : i === rows.length - 1 ? 'end' : 'middle'}">${xml(rows[i].label)}</text>`);
  } else {
    for (const tick of [0, .5, 1]) parts.push(`<text x="${px(min + span * tick)}" y="${top}" text-anchor="middle" font-size="14">${xml(format(min + span * tick))}</text>`);
    let offset = 0;
    rows.forEach((row, i) => {
      const y = top + 20 + offset;
      offset += heights[i];
      labelLines[i].forEach((label, index) => parts.push(`<text x="30" y="${y + 14 + index * 16}" font-size="14">${xml(label)}</text>`));
      parts.push(`<rect x="${left}" y="${y}" width="${right - left}" height="24" fill="#f1f5f9"/><rect x="${px(Math.min(0, row.value))}" y="${y}" width="${Math.abs(row.value) / span * (right - left)}" height="24" fill="${xml(color)}"/><text x="995" y="${y + 18}" font-size="14">${xml(format(row.value))}</text>`);
      if (Number.isFinite(reference)) parts.push(`<line x1="${px(reference)}" x2="${px(reference)}" y1="${y - 5}" y2="${y + 30}" stroke="#0f172a" stroke-width="2" stroke-dasharray="4 3"/>`);
    });
  }
  parts.push(`<text x="30" y="${height - 30}" font-size="14">${xml(unit)}${Number.isFinite(reference) ? ' · ' + xml(referenceLabel) + ': ' + xml(format(reference)) + ' ' + xml(unit) : ''}</text></g></svg>`);
  return parts.join('');
}
export async function downloadChartPng(svg, filename) {
  const url = URL.createObjectURL(new Blob([svg], { type: 'image/svg+xml;charset=utf-8' }));
  try {
    const image = new Image();
    await new Promise((resolve, reject) => { image.onload = resolve; image.onerror = reject; image.src = url; });
    const canvas = document.createElement('canvas'); canvas.width = image.width; canvas.height = image.height;
    const context = canvas.getContext('2d');
    if (!context) throw new Error('canvas_unavailable');
    context.drawImage(image, 0, 0);
    const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/png'));
    if (!blob) throw new Error('png_unavailable');
    downloadBlob(blob, filename);
  } finally { URL.revokeObjectURL(url); }
}
