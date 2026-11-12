import { NextRequest, NextResponse } from 'next/server';
import { ACCESS_COOKIE, BACKEND_URL, csrfRejected, missingCsrfHeader } from '@/lib/bff';

// Generic proxy: attaches the bearer token from the HttpOnly cookie. Only API paths the design defines are allowed.
const ALLOWED = [
  /^leave-requests(\/[0-9a-f-]{36}(\/(approve|reject))?)?$/,
  /^approver-delegations$/,
  /^reports\/monthly-attendance\.csv$/,
];

async function proxy(req: NextRequest, ctx: { params: Promise<{ path: string[] }> }): Promise<NextResponse> {
  const { path } = await ctx.params;
  const joined = path.join('/');
  if (!ALLOWED.some((re) => re.test(joined))) {
    return NextResponse.json({ error: { code: 'ERR-SYS-404', message: 'Target not found' } }, { status: 404 });
  }
  if (missingCsrfHeader(req.method, req.headers)) return csrfRejected();

  const headers = new Headers({ Accept: req.headers.get('accept') ?? 'application/json' });
  const token = req.cookies.get(ACCESS_COOKIE)?.value;
  if (token) headers.set('Authorization', `Bearer ${token}`);
  const contentType = req.headers.get('content-type');
  if (contentType) headers.set('Content-Type', contentType);

  const hasBody = !['GET', 'HEAD'].includes(req.method);
  const upstream = await fetch(`${BACKEND_URL}/api/v1/${joined}${req.nextUrl.search}`, {
    method: req.method,
    headers,
    body: hasBody ? await req.text() : undefined,
    cache: 'no-store',
  });

  const out = new Headers();
  for (const name of ['content-type', 'content-disposition', 'retry-after']) {
    const v = upstream.headers.get(name);
    if (v) out.set(name, v);
  }
  return new NextResponse(await upstream.arrayBuffer(), { status: upstream.status, headers: out });
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
