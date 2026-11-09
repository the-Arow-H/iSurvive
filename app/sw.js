/* iSurvive field guide service worker. Cache-first. Generated. */
const CACHE = "isurvive-guide-4e2d940ca7fc";
const PRECACHE = [
  "/LICENSE",
  "/css/guide.css",
  "/data/pages.json",
  "/icons/icon-192.png",
  "/icons/icon-512.png",
  "/index.html",
  "/js/guide.js",
  "/manifest.webmanifest",
  "/offline.html",
  "/vendor/MINISEARCH-LICENSE.txt",
  "/vendor/minisearch.js"
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(PRECACHE)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) {
    return;
  }
  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      return fetch(event.request)
        .then((response) => {
          if (response && response.ok && event.request.method === "GET") {
            const copy = response.clone();
            caches.open(CACHE).then((cache) => cache.put(event.request, copy));
          }
          return response;
        })
        .catch(() => caches.match("/index.html"));
    })
  );
});
