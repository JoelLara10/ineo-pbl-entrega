import { createHash } from 'node:crypto';

export function workerSource(files, version) {
  return `const CACHE = 'ineo-shell-${version}';
const FILES = ${JSON.stringify(files)};
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(FILES)));
});
self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key.startsWith('ineo-shell-') && key !== CACHE).map(key => caches.delete(key)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== 'GET' || url.origin !== self.location.origin || url.search || url.pathname.startsWith('/api/')) return;
  if (request.mode === 'navigate' && !url.pathname.match(/\\.[^/]+$/)) {
    event.respondWith(fetch(request).catch(() => caches.open(CACHE).then(cache => cache.match('/index.html'))));
  } else if (FILES.includes(url.pathname)) {
    event.respondWith(caches.open(CACHE).then(cache => cache.match(url.pathname)).then(cached => cached || fetch(request)));
  }
});`;
}

export default function offlineShell() {
  return {
    name: 'ineo-offline-shell', apply: 'build', enforce: 'post',
    generateBundle(_options, bundle) {
      const files = ['/index.html', '/manifest.webmanifest', '/icon.svg',
        ...Object.keys(bundle).filter(name => name.startsWith('assets/') && /\.(js|css|woff2?|svg|png)$/.test(name)).map(name => '/' + name)];
      const hash = createHash('sha256');
      for (const item of Object.values(bundle)) hash.update(item.type === 'chunk' ? item.code : item.source);
      this.emitFile({ type: 'asset', fileName: 'sw.js', source: workerSource(files, hash.digest('hex').slice(0, 16)) });
    },
  };
}
