'use client';

import { useParams } from 'next/navigation';
import { useState } from 'react';
import { AppShell } from '@/components/app-shell';
import { ErrorState, ListSkeleton } from '@/components/query-states';
import { LEAVE_TYPES, STATUS_LABELS } from '@/config/leave-types';
import { useDecision, useLeaveDetail } from '@/features/leave/hooks';
import { rejectSchema } from '@/features/leave/schemas';
import { ApiError } from '@/lib/api-client';
import { messageFor } from '@/lib/messages';

const ACTION_LABELS = { pending: '承認待ち', approved: '承認', rejected: '差戻し' } as const;

export default function RequestDetailPage() {
  const { id } = useParams<{ id: string }>();
  const detail = useLeaveDetail(id);
  const decision = useDecision(id);
  const [reason, setReason] = useState('');
  const [reasonError, setReasonError] = useState<string | null>(null);
  const [banner, setBanner] = useState<{ text: string; refresh: boolean } | null>(null);

  const onError = (err: unknown) => {
    const stale = err instanceof ApiError && err.code === 'ERR-APPR-002';
    setBanner({ text: messageFor(err), refresh: stale });
  };

  const approve = () => {
    setBanner(null);
    decision.mutate({ action: 'approve', body: {} }, { onError });
  };
  const reject = () => {
    setBanner(null);
    const parsed = rejectSchema.safeParse({ reason });
    if (!parsed.success) {
      setReasonError(parsed.error.issues[0]?.message ?? null);
      return;
    }
    setReasonError(null);
    decision.mutate({ action: 'reject', body: parsed.data }, { onError });
  };

  return (
    <AppShell title="申請詳細">
      {detail.isPending && <ListSkeleton rows={3} />}
      {detail.isError && <ErrorState error={detail.error} onRetry={() => void detail.refetch()} />}
      {detail.isSuccess && (
        <div className="space-y-6">
          {banner && (
            <div role="alert" className="rounded-md border p-3" style={{ borderColor: 'var(--color-danger)' }}>
              <p className="err">{banner.text}</p>
              {banner.refresh && (
                <button type="button" className="btn mt-2" onClick={() => { setBanner(null); void detail.refetch(); }}>
                  更新
                </button>
              )}
            </div>
          )}
          <dl className="grid grid-cols-[8rem_1fr] gap-2">
            <dt>種別</dt>
            <dd>{LEAVE_TYPES.find((t) => t.code === detail.data.data.type)?.label ?? detail.data.data.type}</dd>
            <dt>期間</dt>
            <dd>{detail.data.data.dateFrom} 〜 {detail.data.data.dateTo}</dd>
            {detail.data.data.hours !== undefined && (<><dt>残業時間</dt><dd>{detail.data.data.hours}</dd></>)}
            <dt>理由</dt>
            <dd className="whitespace-pre-wrap">{detail.data.data.reason}</dd>
            <dt>状態</dt>
            <dd>{STATUS_LABELS[detail.data.data.status] ?? detail.data.data.status}</dd>
          </dl>

          <section aria-label="承認履歴">
            <h2 className="mb-2 font-semibold">承認履歴</h2>
            {detail.data.data.steps.length === 0 ? (
              <p>履歴はありません。</p>
            ) : (
              <ol className="space-y-1">
                {detail.data.data.steps.map((s) => (
                  <li key={s.stepNo}>
                    {s.stepNo}. {ACTION_LABELS[s.action]}
                    {s.decidedAt && <> ／ {new Date(s.decidedAt).toLocaleString('ja-JP')}</>}
                    {s.comment && <> ／ {s.comment}</>}
                  </li>
                ))}
              </ol>
            )}
          </section>

          {detail.data.data.status === 'submitted' && (
            <section aria-label="承認操作" className="space-y-3">
              <div>
                <label htmlFor="reason">差戻し理由</label>
                <textarea id="reason" className="field" rows={3} maxLength={500} value={reason} onChange={(e) => setReason(e.target.value)} aria-invalid={!!reasonError} />
                {reasonError && <p className="err">{reasonError}</p>}
              </div>
              <div className="flex gap-3">
                <button type="button" className="btn btn-primary" disabled={decision.isPending} onClick={approve}>承認</button>
                <button type="button" className="btn" disabled={decision.isPending} onClick={reject}>差戻し</button>
              </div>
            </section>
          )}
        </div>
      )}
    </AppShell>
  );
}
