import type { ApiErrorBody } from './api-types';

// '/api' = BFF route handlers on the same origin. The browser never sees an access or refresh token.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? '/api';

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
    public readonly details?: ApiErrorBody['error']['details'],
    public readonly requestId?: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

const MUTATING = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);
let refreshInFlight: Promise<boolean> | null = null; // single-flight: N parallel 401s => one refresh

async function refreshSession(): Promise<boolean> {
  refreshInFlight ??= fetch(`${API_BASE_URL}/auth/refresh`, {
    method: 'POST',
    credentials: 'include',
    headers: { 'x-idempotency-key': newIdempotencyKey() },
  })
    .then((r) => r.ok)
    .catch(() => false)
    .finally(() => {
      refreshInFlight = null;
    });
  return refreshInFlight;
}

export function newIdempotencyKey(): string {
  return `idemp-${Date.now()}-${crypto.randomUUID()}`;
}

export async function apiFetch<T>(path: string, init: RequestInit = {}, retried = false): Promise<T> {
  const method = (init.method ?? 'GET').toUpperCase();
  const headers = new Headers(init.headers);
  headers.set('Accept', 'application/json');
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
  // One key per user operation; callers pass their own key so a retry reuses it.
  if (MUTATING.has(method) && !headers.has('x-idempotency-key')) headers.set('x-idempotency-key', newIdempotencyKey());

  const res = await fetch(`${API_BASE_URL}${path}`, { ...init, method, headers, credentials: 'include' });

  if (res.status === 401 && !retried && !path.startsWith('/auth/')) {
    if (await refreshSession()) return apiFetch<T>(path, init, true);
    if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/login')) {
      window.location.assign('/login?expired=1');
    }
  }
  if (!res.ok) {
    const body = (await res.json().catch(() => null)) as ApiErrorBody | null;
    throw new ApiError(
      res.status,
      body?.error?.code ?? 'ERR-NET-000',
      body?.error?.message ?? res.statusText,
      body?.error?.details,
      body?.error?.requestId,
    );
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

/** Binary download through the BFF (CSV). Same auth and error handling as apiFetch. */
export async function apiDownload(path: string): Promise<Blob> {
  const res = await fetch(`${API_BASE_URL}${path}`, { credentials: 'include' });
  if (!res.ok) {
    const body = (await res.json().catch(() => null)) as ApiErrorBody | null;
    throw new ApiError(res.status, body?.error?.code ?? 'ERR-NET-000', body?.error?.message ?? res.statusText, body?.error?.details, body?.error?.requestId);
  }
  return res.blob();
}
