'use client';

import { useRouter } from 'next/navigation';
import { useRef, useState, type FormEvent } from 'react';
import { ApiError, apiFetch, newIdempotencyKey } from '@/lib/api-client';
import type { Envelope } from '@/lib/api-types';
import { loginSchema } from '@/features/leave/schemas';
import { messageFor, requestIdOf } from '@/lib/messages';

const HOME_BY_ROLE: Record<string, string> = { employee: '/requests', manager: '/requests', hr: '/reports' };

export default function LoginPage() {
  const router = useRouter();
  const [employeeId, setEmployeeId] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [banner, setBanner] = useState<string | null>(null);
  const [pending, setPending] = useState(false);
  const key = useRef(newIdempotencyKey());

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setBanner(null);
    const parsed = loginSchema.safeParse({ employeeId, password });
    if (!parsed.success) {
      setErrors(Object.fromEntries(parsed.error.issues.map((i) => [String(i.path[0]), i.message])));
      return;
    }
    setErrors({});
    setPending(true);
    try {
      const res = await apiFetch<Envelope<{ role: string }>>('/auth/login', {
        method: 'POST',
        body: JSON.stringify(parsed.data),
        headers: { 'x-idempotency-key': key.current },
      });
      router.push(HOME_BY_ROLE[res.data.role] ?? '/requests');
    } catch (err) {
      key.current = newIdempotencyKey();
      let text = messageFor(err);
      if (err instanceof ApiError && err.code === 'ERR-AUTH-002') {
        const until = err.details?.find((d) => d.field === 'lockedUntil')?.issue;
        if (until) text = `${text}（${new Date(until).toLocaleString('ja-JP')} 以降に再度お試しください）`;
      }
      const id = requestIdOf(err);
      setBanner(id ? `${text}（お問い合わせ番号: ${id}）` : text);
    } finally {
      setPending(false);
    }
  };

  return (
    <main className="mx-auto mt-16 max-w-sm p-4">
      <h1 className="mb-4 text-xl font-semibold">ログイン</h1>
      {new URLSearchParams(typeof window === 'undefined' ? '' : window.location.search).get('expired') && (
        <p role="status" className="mb-3 text-sm">
          ログインの有効期限が切れました。再度ログインしてください。
        </p>
      )}
      <form onSubmit={onSubmit} noValidate className="space-y-4">
        <div>
          <label htmlFor="employeeId">社員番号</label>
          <input id="employeeId" className="field" inputMode="numeric" maxLength={6} autoComplete="username" value={employeeId} onChange={(e) => setEmployeeId(e.target.value)} aria-invalid={!!errors.employeeId} />
          {errors.employeeId && <p className="err">{errors.employeeId}</p>}
        </div>
        <div>
          <label htmlFor="password">パスワード</label>
          <input id="password" type="password" className="field" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} aria-invalid={!!errors.password} />
          {errors.password && <p className="err">{errors.password}</p>}
        </div>
        {banner && (
          <p role="alert" className="err">
            {banner}
          </p>
        )}
        <button type="submit" className="btn btn-primary w-full" disabled={pending || !employeeId || !password}>
          {pending ? '送信中…' : 'ログイン'}
        </button>
      </form>
    </main>
  );
}
