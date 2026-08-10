/**
 * Service Worker for Berlin Gigs PWA
 * - Caches the app shell (index.html, app.js) on install
 * - Caches events.json with a network-first strategy (fresh data if online)
 * - Falls back to cached data when offline
 */

const CACHE = "berlin-gigs-v1";
const APP_SHELL = ["/", "/index.html", "/app.js"];
const EVENTS_URL = "/events.json";

// Install: cache the app shell
self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(APP_SHELL))
  );
  self.skipWaiting();
});

// Activate: delete old caches
self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// Fetch: network-first for events.json, cache-first for app shell
self.addEventListener("fetch", (e) => {
  const { request } = e;
  const url = new URL(request.url);

  // events.json: try network first (fresh data), fall back to cache
  if (url.pathname.endsWith("events.json")) {
    e.respondWith(
      fetch(request)
        .then((resp) => {
          const clone = resp.clone();
          caches.open(CACHE).then((c) => c.put(request, clone));
          return resp;
        })
        .catch(() => caches.match(request))
    );
    return;
  }

  // App shell: cache-first
  e.respondWith(
    caches.match(request).then((cached) => cached || fetch(request))
  );
});
