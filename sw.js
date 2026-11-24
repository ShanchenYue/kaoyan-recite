// 极简 Service Worker: 缓存核心文件
const CACHE = 'kaoyan-v1';
const FILES = [
  './',
  './index.html',
  './data.json',
  './manifest.json',
  './icon.svg'
];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).catch(() => {}));
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', e => {
  // 网络优先 + 离线回退缓存
  e.respondWith(
    fetch(e.request).then(r => {
      // 动态缓存
      if (r && r.status === 200) {
        const copy = r.clone();
        caches.open(CACHE).then(c => c.put(e.request, copy));
      }
      return r;
    }).catch(() => caches.match(e.request))
  );
});
