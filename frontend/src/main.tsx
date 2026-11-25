import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

// Configure Production API Base URL & Single Authoritative Session + Refresh Token Interceptor
const API_BASE_URL = (((import.meta as any).env?.VITE_API_BASE_URL as string) || '').replace(/\/+$/, '');
const originalFetch = window.fetch.bind(window);

let inflightRefreshPromise: Promise<string | null> | null = null;

async function attemptSilentSessionRefresh(): Promise<string | null> {
  if (inflightRefreshPromise) return inflightRefreshPromise;
  inflightRefreshPromise = (async () => {
    try {
      let storedRefresh: string | null = null;
      let storedAccess: string | null = null;
      try {
        storedRefresh = window.localStorage.getItem('sparkminds_refresh_token');
        storedAccess = window.localStorage.getItem('sparkminds_auth_token');
      } catch {
        storedRefresh = null;
        storedAccess = null;
      }
      const refreshUrl = API_BASE_URL
        ? `${API_BASE_URL}/api/auth/session/refresh`
        : '/api/auth/session/refresh';
      const headers = new Headers({ 'Content-Type': 'application/json' });
      if (storedRefresh) {
        headers.set('X-SparkMinds-Refresh-Token', storedRefresh);
      }
      const res = await originalFetch(refreshUrl, {
        method: 'POST',
        credentials: 'include',
        headers,
        body: JSON.stringify({
          refresh_token: storedRefresh || undefined,
          session_token: storedAccess || undefined,
        }),
      });
      if (!res.ok) return null;
      const data = await res.json().catch(() => null);
      if (data && data.session_token) {
        try {
          window.localStorage.setItem('sparkminds_auth_token', data.session_token);
          if (data.refresh_token) {
            window.localStorage.setItem('sparkminds_refresh_token', data.refresh_token);
          }
          if (data.student_id) {
            window.localStorage.setItem('sparkminds_student_id', data.student_id);
          }
        } catch {
          // Ignore storage errors
        }
        return String(data.session_token);
      }
      return null;
    } catch {
      return null;
    } finally {
      inflightRefreshPromise = null;
    }
  })();
  return inflightRefreshPromise;
}

window.fetch = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
  let targetInput = input;
  let urlStr = typeof input === 'string' ? input : input instanceof URL ? input.toString() : input.url;

  if (API_BASE_URL && urlStr.startsWith('/api/')) {
    urlStr = `${API_BASE_URL}${urlStr}`;
    targetInput = urlStr;
  }

  const isApiCall =
    urlStr.startsWith('/api/') || (Boolean(API_BASE_URL) && urlStr.startsWith(API_BASE_URL));

  const nextInit: RequestInit = { ...(init || {}) };
  const headers = new Headers(nextInit.headers || {});
  let attachedToken: string | null = null;
  if (isApiCall) {
    // Always include HttpOnly auth & refresh cookies cleanly
    if (!nextInit.credentials) {
      nextInit.credentials = 'include';
    }
    try {
      attachedToken = window.localStorage.getItem('sparkminds_auth_token');
    } catch {
      attachedToken = null;
    }
    if (attachedToken) {
      if (!headers.has('Authorization')) {
        headers.set('Authorization', `Bearer ${attachedToken}`);
      }
      if (!headers.has('X-SparkMinds-Token')) {
        headers.set('X-SparkMinds-Token', attachedToken);
      }
    }
  }
  nextInit.headers = headers;

  const response = await originalFetch(targetInput, nextInit);

  const isAuthLifecyclePath =
    urlStr.includes('/api/auth/login') ||
    urlStr.includes('/api/auth/register') ||
    urlStr.includes('/api/auth/recover') ||
    urlStr.includes('/api/auth/logout') ||
    urlStr.includes('/api/auth/session/refresh') ||
    urlStr.includes('/api/auth/email/');

  // On 401 for protected API calls: transparently attempt a single silent token refresh
  // using the HttpOnly refresh cookie / stored refresh token before ever expiring the UI session.
  if (isApiCall && response.status === 401 && !isAuthLifecyclePath) {
    const newAccessToken = await attemptSilentSessionRefresh();
    if (newAccessToken) {
      const retryHeaders = new Headers(init?.headers || {});
      retryHeaders.set('Authorization', `Bearer ${newAccessToken}`);
      retryHeaders.set('X-SparkMinds-Token', newAccessToken);
      const retryInit: RequestInit = {
        ...(init || {}),
        credentials: init?.credentials || 'include',
        headers: retryHeaders,
      };
      return originalFetch(targetInput, retryInit);
    }
    // Only notify session expiration if user had an active token and refresh genuinely failed
    if (attachedToken && !urlStr.includes('/api/auth/session')) {
      window.dispatchEvent(
        new CustomEvent('sparkminds-session-expired', {
          detail: { url: urlStr, status: 401 },
        })
      );
    }
  }

  return response;
};

// Register Progressive Web App (PWA) Service Worker with Automatic Update Detection & Controller Reload
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/sw.js')
      .then((registration) => {
        registration.update();
        if (registration.waiting) {
          registration.waiting.postMessage({ type: 'SKIP_WAITING' });
        }
        registration.addEventListener('updatefound', () => {
          const installingWorker = registration.installing;
          if (!installingWorker) return;
          installingWorker.addEventListener('statechange', () => {
            if (
              installingWorker.state === 'installed' &&
              navigator.serviceWorker.controller
            ) {
              installingWorker.postMessage({ type: 'SKIP_WAITING' });
            }
          });
        });
      })
      .catch(() => {
        // Ignore service worker registration errors in unsupported environments
      });
  });

  let refreshing = false;
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (!refreshing) {
      refreshing = true;
      window.location.reload();
    }
  });
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
