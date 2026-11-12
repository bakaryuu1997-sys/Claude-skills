'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import type { ReactNode } from 'react';
import { apiFetch } from '@/lib/api-client';
import { ErrorBoundary } from './shared/error-boundary';
import { useTheme } from './shared/theme-provider';

const NAV = [
  { href: '/requests', label: '申請一覧' },
  { href: '/requests/new', label: '新規申請' },
  { href: '/delegations', label: '承認者代理設定' },
  { href: '/reports', label: '月次勤怠CSV' },
];

/** Header, navigation and a fault-isolating boundary around the page content. All surfaces share one theme. */
export function AppShell({ title, children }: { title: string; children: ReactNode }) {
  const router = useRouter();
  const { choice, setChoice } = useTheme();

  const logout = async () => {
    await apiFetch('/auth/logout', { method: 'POST' }).catch(() => undefined);
    router.push('/login');
  };

  return (
    <div className="min-h-screen">
      <header className="flex flex-wrap items-center gap-4 border-b px-4 py-3" style={{ borderColor: 'var(--color-border)', background: 'var(--color-surface)' }}>
        <strong>勤怠承認システム</strong>
        <nav aria-label="メインメニュー" className="flex flex-wrap gap-3 text-sm">
          {NAV.map((n) => (
            <Link key={n.href} href={n.href} className="underline-offset-4 hover:underline">
              {n.label}
            </Link>
          ))}
        </nav>
        <div className="ml-auto flex items-center gap-2 text-sm">
          <label className="flex items-center gap-1">
            表示
            <select
              className="field w-auto py-1"
              value={choice}
              onChange={(e) => setChoice(e.target.value as 'light' | 'dark' | 'system')}
              aria-label="テーマ"
            >
              <option value="system">システム</option>
              <option value="light">ライト</option>
              <option value="dark">ダーク</option>
            </select>
          </label>
          <button type="button" className="btn py-1" onClick={logout}>
            ログアウト
          </button>
        </div>
      </header>
      <main className="mx-auto max-w-4xl p-4">
        <h1 className="mb-4 text-xl font-semibold">{title}</h1>
        <ErrorBoundary label={title} message="この領域を読み込めませんでした。" retryLabel="再試行">
          {children}
        </ErrorBoundary>
      </main>
    </div>
  );
}
