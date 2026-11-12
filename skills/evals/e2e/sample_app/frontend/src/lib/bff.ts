import { NextResponse } from 'next/server';

export const BACKEND_URL = process.env.BACKEND_URL ?? 'http://localhost:3000';
export const ACCESS_COOKIE = 'at';
export const REFRESH_COOKIE = 'rt';
export const ROLE_COOKIE = 'app_role'; // readable by the UI for navigation only; the backend enforces permissions

const isProd = process.env.NODE_ENV === 'production';

export function sessionCookieOptions(maxAgeSeconds: number, path = '/') {
  return { httpOnly: true, secure: isProd, sameSite: 'lax' as const, path, maxAge: maxAgeSeconds };
}

/** Mutating browser calls must carry a custom header (CSRF defence on top of SameSite). */
export function missingCsrfHeader(method: string, headers: Headers): boolean {
  return ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method) && !headers.get('x-idempotency-key');
}

export function csrfRejected(): NextResponse {
  return NextResponse.json({ error: { code: 'ERR-NET-403', message: 'Missing required header' } }, { status: 403 });
}
