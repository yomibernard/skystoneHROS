var CACHE = 'people-os-shell-1';
self.addEventListener('install', function (event) { self.skipWaiting(); event.waitUntil(caches.open(CACHE)); });
self.addEventListener('activate', function (event) { event.waitUntil(self.clients.claim()); });
self.addEventListener('fetch', function (event) {
  var req = event.request;
  if (req.method !== 'GET' || req.url.indexOf('/api/') >= 0) return;
  event.respondWith(fetch(req).then(function (res) {
    var copy = res.clone();
    caches.open(CACHE).then(function (cache) { cache.put(req, copy); });
    return res;
  }).catch(function () { return caches.match(req); }));
});
