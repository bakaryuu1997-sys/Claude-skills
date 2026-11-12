import { NextRequest, NextResponse } from 'next/server';
import { ACCESS_COOKIE, BACKEND_URL, REFRESH_COOKIE, csrfRejected, missingCsrfHeader, sessionCookieOptions } from '@/lib/bff';

export async function POST(req: NextRequest) {
  if (missingCsrfHeader('POST', req.headers)) return csrfRejected();
  const refreshToken = req.cookies.get(REFRESH_COOKIE)?.value;
  if (!refreshToken) {
    return NextResponse.json({ error: { code: 'ERR-AUTH-003', message: 'Session expired' } }, { status: 401 });
  }
  const upstream = await fetch(`${BACKEND_URL}/api/v1/auth/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refreshToken }),
    cache: 'no-store',
  });
  const body: unknown = await upstream.json().catch(() => null);
  if (!upstream.ok) {
    const res = NextResponse.json(body, { status: upstream.status });
    res.cookies.delete({ name: REFRESH_COOKIE, path: '/api/auth' });
    return res;
  }
  const { accessToken, expiresIn } = (body as { data: { accessToken: string; expiresIn: number } }).data;
  const res = NextResponse.json({ data: { ok: true } });
  res.cookies.set(ACCESS_COOKIE, accessToken, sessionCookieOptions(expiresIn));
  // The refresh token is single-use and the API contract returns no replacement, so it is dropped here:
  // the next expiry sends the user back to the login screen (open item for the API design).
  res.cookies.delete({ name: REFRESH_COOKIE, path: '/api/auth' });
  return res;
}
