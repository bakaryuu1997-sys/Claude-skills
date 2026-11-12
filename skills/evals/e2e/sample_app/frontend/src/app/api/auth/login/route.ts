import { NextRequest, NextResponse } from 'next/server';
import { ACCESS_COOKIE, BACKEND_URL, REFRESH_COOKIE, ROLE_COOKIE, csrfRejected, missingCsrfHeader, sessionCookieOptions } from '@/lib/bff';

interface LoginData {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  role: string;
}

export async function POST(req: NextRequest) {
  if (missingCsrfHeader('POST', req.headers)) return csrfRejected();
  const upstream = await fetch(`${BACKEND_URL}/api/v1/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'x-forwarded-for': req.headers.get('x-forwarded-for') ?? '' },
    body: await req.text(),
    cache: 'no-store',
  });
  const body: unknown = await upstream.json().catch(() => null);
  if (!upstream.ok) return NextResponse.json(body, { status: upstream.status });

  const { accessToken, refreshToken, expiresIn, role } = (body as { data: LoginData }).data;
  // Tokens only ever live in HttpOnly cookies; the browser receives the role for navigation.
  const res = NextResponse.json({ data: { role } });
  res.cookies.set(ACCESS_COOKIE, accessToken, sessionCookieOptions(expiresIn));
  res.cookies.set(REFRESH_COOKIE, refreshToken, sessionCookieOptions(7 * 24 * 60 * 60, '/api/auth'));
  res.cookies.set(ROLE_COOKIE, role, { sameSite: 'lax', path: '/', maxAge: 7 * 24 * 60 * 60 });
  return res;
}
