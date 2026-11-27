// 极简 Service Worker: 只缓存页面壳，音频一律直连，避免缓存卡顿
const CACHE = 'kaoyan-v6';
const FILES = [
  './',
  './index.html',
  './quiz.html',
  './plan.html',
  './plan_data.js',
  './manifest.json',
  './icon.svg'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  // 音频、数据、跨域请求不经过缓存，直接走网络
  if (e.request.destination === 'audio' || url.pathname.includes('/audios/') ||
      url.pathname.endsWith('data.json') || url.origin !== location.origin) {
    return;
  }
  e.respondWith(
    fetch(e.request).then(r => {
      if (r && r.status === 200 && e.request.method === 'GET') {
        const copy = r.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy)).catch(() => {});
      }
      return r;
    }).catch(() => caches.match(e.request))
  );
});
