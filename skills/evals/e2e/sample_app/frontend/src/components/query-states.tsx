'use client';

import { messageFor, requestIdOf } from '@/lib/messages';

export function ListSkeleton({ rows = 4 }: { rows?: number }) {
  return (
    <div aria-busy="true" aria-label="読み込み中" className="space-y-2">
      {Array.from({ length: rows }, (_, i) => (
        <div key={i} className="skeleton h-10" />
      ))}
    </div>
  );
}

/** Error state: message from the error code, support reference, and a retry action. */
export function ErrorState({ error, onRetry }: { error: unknown; onRetry: () => void }) {
  const requestId = requestIdOf(error);
  return (
    <div role="alert" className="rounded-md border p-4" style={{ borderColor: 'var(--color-danger)' }}>
      <p className="err">{messageFor(error)}</p>
      {requestId && <p className="text-xs">お問い合わせ番号: {requestId}</p>}
      <button type="button" className="btn mt-3" onClick={onRetry}>
        再試行
      </button>
    </div>
  );
}

export function EmptyState({ message, action }: { message: string; action?: { href: string; label: string } }) {
  return (
    <div className="rounded-md border border-dashed p-8 text-center" style={{ borderColor: 'var(--color-border)' }}>
      <p>{message}</p>
      {action && (
        <a className="btn btn-primary mt-3 inline-block" href={action.href}>
          {action.label}
        </a>
      )}
    </div>
  );
}
