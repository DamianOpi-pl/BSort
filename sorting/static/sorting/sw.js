// Service Worker for BSort PWA
const CACHE_NAME = 'bsort-v1';
const STATIC_CACHE_NAME = 'bsort-static-v1';

// Files to cache for offline functionality
const STATIC_FILES = [
    '/',
    '/static/sorting/css/styles.css',
    '/static/sorting/manifest.json',
    '/static/sorting/icons/icon-192x192.png',
    '/static/sorting/icons/icon-512x512.png',
    // Bootstrap CSS
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css',
    // Font Awesome
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css',
    // Google Fonts
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap',
    // jQuery and Bootstrap JS
    'https://code.jquery.com/jquery-3.6.4.min.js',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js'
];

// API endpoints to cache
const API_CACHE_PATTERNS = [
    '/sorting/',
    '/admin/',
];

// Install event - cache static files
self.addEventListener('install', event => {
    console.log('Service Worker: Install');
    event.waitUntil(
        caches.open(STATIC_CACHE_NAME)
            .then(cache => {
                console.log('Service Worker: Caching static files');
                return cache.addAll(STATIC_FILES);
            })
            .catch(err => {
                console.log('Service Worker: Cache failed', err);
            })
    );
    self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('Service Worker: Activate');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cache => {
                    if (cache !== CACHE_NAME && cache !== STATIC_CACHE_NAME) {
                        console.log('Service Worker: Clearing old cache', cache);
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Handle API requests with network-first strategy
    if (API_CACHE_PATTERNS.some(pattern => url.pathname.startsWith(pattern))) {
        event.respondWith(
            fetch(request)
                .then(response => {
                    // Clone response to cache it
                    const responseClone = response.clone();
                    if (response.status === 200) {
                        caches.open(CACHE_NAME).then(cache => {
                            cache.put(request, responseClone);
                        });
                    }
                    return response;
                })
                .catch(() => {
                    // If network fails, try to serve from cache
                    return caches.match(request);
                })
        );
        return;
    }

    // Handle static files with cache-first strategy
    if (request.destination === 'style' || 
        request.destination === 'script' || 
        request.destination === 'font' ||
        request.destination === 'image' ||
        STATIC_FILES.includes(url.pathname)) {
        
        event.respondWith(
            caches.match(request).then(response => {
                if (response) {
                    return response;
                }
                return fetch(request).then(response => {
                    if (response.status === 200) {
                        const responseClone = response.clone();
                        caches.open(STATIC_CACHE_NAME).then(cache => {
                            cache.put(request, responseClone);
                        });
                    }
                    return response;
                });
            })
        );
        return;
    }

    // For all other requests, try network first, then cache
    event.respondWith(
        fetch(request)
            .then(response => {
                // Cache successful responses
                if (response.status === 200 && request.method === 'GET') {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(request, responseClone);
                    });
                }
                return response;
            })
            .catch(() => {
                // If network fails, try to serve from cache
                return caches.match(request).then(response => {
                    if (response) {
                        return response;
                    }
                    // Return offline page for navigation requests
                    if (request.destination === 'document') {
                        return caches.match('/');
                    }
                });
            })
    );
});

// Background sync for form submissions when offline
self.addEventListener('sync', event => {
    console.log('Service Worker: Background sync', event.tag);
    
    if (event.tag === 'bag-form-sync') {
        event.waitUntil(syncBagForms());
    }
});

// Sync bag forms stored in IndexedDB when connection is restored
async function syncBagForms() {
    try {
        // This would integrate with IndexedDB to sync offline form submissions
        console.log('Service Worker: Syncing bag forms');
        // Implementation would depend on the specific offline storage strategy
    } catch (error) {
        console.error('Service Worker: Sync failed', error);
    }
}

// Push notification support (for future features)
self.addEventListener('push', event => {
    if (event.data) {
        const data = event.data.json();
        const options = {
            body: data.body,
            icon: '/static/sorting/icons/icon-192x192.png',
            badge: '/static/sorting/icons/icon-192x192.png',
            data: data.data || {}
        };
        
        event.waitUntil(
            self.registration.showNotification(data.title, options)
        );
    }
});

// Handle notification clicks
self.addEventListener('notificationclick', event => {
    event.notification.close();
    
    event.waitUntil(
        clients.openWindow('/')
    );
});