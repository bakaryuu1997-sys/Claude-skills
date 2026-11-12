'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { useEffect, useMemo, useState, type ReactNode } from 'react';
import { ApiError } from '@/lib/api-client';
import { CommandPalette, type PaletteCommand } from './shared/command-palette';
import { ThemeProvider, useTheme } from './shared/theme-provider';

function Palette() {
  const router = useRouter();
  const { setChoice } = useTheme();
  const [open, setOpen] = useState(false);
  const commands = useMemo<PaletteCommand[]>(
    () => [
      { id: 'list', label: '申請一覧', group: '移動', keywords: ['requests', 'list'], run: () => router.push('/requests') },
      { id: 'new', label: '新規申請', group: '移動', keywords: ['new', 'create'], run: () => router.push('/requests/new') },
      { id: 'deleg', label: '承認者代理設定', group: '移動', keywords: ['delegation'], run: () => router.push('/delegations') },
      { id: 'report', label: '月次勤怠CSV', group: '移動', keywords: ['csv', 'report'], run: () => router.push('/reports') },
      { id: 'light', label: 'ライトテーマ', group: '表示', run: () => setChoice('light') },
      { id: 'dark', label: 'ダークテーマ', group: '表示', run: () => setChoice('dark') },
      { id: 'system', label: 'システム設定に合わせる', group: '表示', run: () => setChoice('system') },
    ],
    [router, setChoice],
  );
  return (
    <CommandPalette
      commands={commands}
      open={open}
      onOpenChange={setOpen}
      placeholder="コマンドを入力…"
      emptyText="該当するコマンドがありません"
      dialogLabel="コマンドパレット"
    />
  );
}

function OfflineBanner() {
  const [offline, setOffline] = useState(false);
  useEffect(() => {
    const update = () => setOffline(!navigator.onLine);
    update();
    window.addEventListener('online', update);
    window.addEventListener('offline', update);
    return () => {
      window.removeEventListener('online', update);
      window.removeEventListener('offline', update);
    };
  }, []);
  if (!offline) return null;
  return (
    <div role="status" className="bg-amber-100 px-4 py-2 text-center text-sm text-amber-900">
      オフラインです。接続が回復すると自動的に再読み込みします。
    </div>
  );
}

export function Providers({ children }: { children: ReactNode }) {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            refetchOnReconnect: true,
            retry: (count, err) => !(err instanceof ApiError && err.status < 500) && count < 2,
          },
        },
      }),
  );
  return (
    <ThemeProvider>
      <QueryClientProvider client={client}>
        <OfflineBanner />
        {children}
        <Palette />
      </QueryClientProvider>
    </ThemeProvider>
  );
}
