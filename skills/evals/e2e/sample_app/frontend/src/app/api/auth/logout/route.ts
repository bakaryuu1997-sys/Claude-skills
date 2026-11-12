import { NextRequest, NextResponse } from 'next/server';
import { ACCESS_COOKIE, REFRESH_COOKIE, ROLE_COOKIE, csrfRejected, missingCsrfHeader } from '@/lib/bff';

export async function POST(req: NextRequest) {
  if (missingCsrfHeader('POST', req.headers)) return csrfRejected();
  const res = NextResponse.json({ data: { ok: true } });
  res.cookies.delete({ name: ACCESS_COOKIE, path: '/' });
  res.cookies.delete({ name: REFRESH_COOKIE, path: '/api/auth' });
  res.cookies.delete({ name: ROLE_COOKIE, path: '/' });
  return res;
}
