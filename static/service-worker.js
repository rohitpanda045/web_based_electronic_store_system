const CACHE_NAME = 'techmart-v4';
const ASSETS = [
    '/',
    '/login',
    '/registration',
    '/products',
    '/cart',
    '/static/css/style.css',
    '/static/js/common.js',
    '/static/js/products.js',
    '/static/js/cart.js',
    '/static/js/admin.js',
    '/static/images/20260128190942_s25_ultra.jpg'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(ASSETS))
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        fetch(event.request).catch(() => caches.match(event.request))
    );
});
