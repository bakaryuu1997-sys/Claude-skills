'use client';

import Link from 'next/link';
import { useState } from 'react';
import { AppShell } from '@/components/app-shell';
import { EmptyState, ErrorState, ListSkeleton } from '@/components/query-states';
import { LEAVE_TYPES, STATUS_LABELS } from '@/config/leave-types';
import { useLeaveList } from '@/features/leave/hooks';

const PAGE_SIZE = 20;

export default function RequestListPage() {
  const [status, setStatus] = useState('');
  const [from, setFrom] = useState('');
  const [to, setTo] = useState('');
  const [page, setPage] = useState(1);
  const query = useLeaveList({ status: status || undefined, from: from || undefined, to: to || undefined, page, pageSize: PAGE_SIZE });
  const total = query.data?.data.total ?? 0;
  const lastPage = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const typeLabel = (code: string) => LEAVE_TYPES.find((t) => t.code === code)?.label ?? code;

  return (
    <AppShell title="申請一覧">
      <div className="mb-4 flex flex-wrap items-end gap-3">
        <label className="text-sm">
          状態
          <select className="field" value={status} onChange={(e) => { setStatus(e.target.value); setPage(1); }}>
            <option value="">すべて</option>
            {Object.entries(STATUS_LABELS).map(([v, l]) => (
              <option key={v} value={v}>{l}</option>
            ))}
          </select>
        </label>
        <label className="text-sm">
          期間（開始）
          <input type="date" className="field" value={from} onChange={(e) => { setFrom(e.target.value); setPage(1); }} />
        </label>
        <label className="text-sm">
          期間（終了）
          <input type="date" className="field" value={to} onChange={(e) => { setTo(e.target.value); setPage(1); }} />
        </label>
        <Link href="/requests/new" className="btn btn-primary ml-auto">新規作成</Link>
      </div>

      {query.isPending && <ListSkeleton />}
      {query.isError && <ErrorState error={query.error} onRetry={() => void query.refetch()} />}
      {query.isSuccess && query.data.data.items.length === 0 && (
        <EmptyState message="該当する申請はありません。" action={{ href: '/requests/new', label: '新規申請を作成' }} />
      )}
      {query.isSuccess && query.data.data.items.length > 0 && (
        <>
          <table className="w-full text-left text-sm">
            <thead>
              <tr>
                <th className="py-2">種別</th>
                <th>期間</th>
                <th>状態</th>
                <th>詳細</th>
              </tr>
            </thead>
            <tbody>
              {query.data.data.items.map((r) => (
                <tr key={r.id} className="border-t" style={{ borderColor: 'var(--color-border)' }}>
                  <td className="py-2">{typeLabel(r.type)}</td>
                  <td>{r.dateFrom} 〜 {r.dateTo}</td>
                  <td>{STATUS_LABELS[r.status] ?? r.status}</td>
                  <td><Link href={`/requests/${r.id}`} className="underline">開く</Link></td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="mt-4 flex items-center gap-3 text-sm">
            <button type="button" className="btn" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>前へ</button>
            <span>{page} / {lastPage}（全 {total} 件）</span>
            <button type="button" className="btn" disabled={page >= lastPage} onClick={() => setPage((p) => p + 1)}>次へ</button>
          </div>
        </>
      )}
    </AppShell>
  );
}
