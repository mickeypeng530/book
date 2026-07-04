// 迷你離線外殼 service worker：讓閱讀器在飛機上打得開。
// 只快取「app 殼」：本站靜態檔 + Firebase SDK(gstatic) + Google Fonts。
// Firebase 的即時連線/認證/Storage(firebaseio.com、*.googleapis.com、firebasestorage)一律不攔。
// 章節內容不在這裡 —— 在 index.html 的 localStorage 快取（「⬇️ 離線預載」）。
// ⚠ 改版部署時把 CACHE 版本號 +1，舊快取會在 activate 時清掉。
const CACHE = 'book-shell-v1';

const PRECACHE = [
    './',
    './index.html',
    './manifest.json',
    './favicon-48.png',
    './icon-192.png',
    './icon-512.png',
    './apple-touch-icon.png',
    'https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js',
    'https://www.gstatic.com/firebasejs/10.7.1/firebase-database.js',
    'https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js',
    'https://www.gstatic.com/firebasejs/10.7.1/firebase-storage.js',
];

self.addEventListener('install', (e) => {
    e.waitUntil(
        caches.open(CACHE)
            // allSettled：單一資源失敗（例如icon還沒放）不要讓整個 SW 裝不起來
            .then(c => Promise.allSettled(PRECACHE.map(u => c.add(u))))
            .then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', (e) => {
    e.waitUntil(
        caches.keys()
            .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
            .then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (e) => {
    const req = e.request;
    if (req.method !== 'GET') return;

    const url = new URL(req.url);
    const sameOrigin = url.origin === location.origin;
    const cdnAsset = url.hostname === 'www.gstatic.com'
        || url.hostname === 'fonts.googleapis.com'
        || url.hostname === 'fonts.gstatic.com';
    if (!sameOrigin && !cdnAsset) return;   // firebaseio/googleapis 等一律放行不攔

    // 頁面（HTML）：網路優先拿最新版，離線退快取
    if (req.mode === 'navigate' || (sameOrigin && url.pathname.endsWith('.html'))) {
        e.respondWith(
            fetch(req).then(res => {
                const copy = res.clone();
                caches.open(CACHE).then(c => c.put(req, copy));
                return res;
            }).catch(() =>
                caches.match(req).then(hit => hit || caches.match('./index.html'))
            )
        );
        return;
    }

    // 靜態資產（SDK/字型/圖示）：快取優先，背景更新
    e.respondWith(
        caches.match(req).then(hit => {
            const refresh = fetch(req).then(res => {
                if (res.ok) {
                    const copy = res.clone();
                    caches.open(CACHE).then(c => c.put(req, copy));
                }
                return res;
            }).catch(() => hit);
            return hit || refresh;
        })
    );
});
