'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import { AppShell } from '@/components/app-shell';
import { LEAVE_TYPES } from '@/config/leave-types';
import { useCreateLeave } from '@/features/leave/hooks';
import { createLeaveSchema } from '@/features/leave/schemas';
import { ApiError } from '@/lib/api-client';
import { fieldErrors, messageFor, requestIdOf } from '@/lib/messages';

// Business day in Japan (the backend compares dates in JST), as YYYY-MM-DD.
const today = () => new Date().toLocaleDateString('sv-SE', { timeZone: 'Asia/Tokyo' });
const MAX_REASON = 500;

export default function NewRequestPage() {
  const router = useRouter();
  const create = useCreateLeave();
  const [type, setType] = useState('');
  const [dateFrom, setDateFrom] = useState(today());
  const [dateTo, setDateTo] = useState(today());
  const [hours, setHours] = useState('');
  const [reason, setReason] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [banner, setBanner] = useState<string | null>(null);
  const [overlap, setOverlap] = useState(false);

  const send = (submit: boolean) => {
    setBanner(null);
    setOverlap(false);
    const parsed = createLeaveSchema.safeParse({
      type,
      dateFrom,
      dateTo,
      hours: hours === '' ? undefined : Number(hours),
      reason,
    });
    if (!parsed.success) {
      // A draft may be saved with validation errors only for the fields the server accepts; here we require a valid form.
      setErrors(Object.fromEntries(parsed.error.issues.map((i) => [String(i.path[0]), i.message])));
      return;
    }
    setErrors({});
    create.mutate(
      { ...parsed.data, submit },
      {
        onSuccess: () => router.push('/requests'),
        onError: (err) => {
          const code = err instanceof ApiError ? err.code : '';
          const detail = fieldErrors(err);
          if (code === 'ERR-VAL-002') setErrors({ dateTo: messageFor(err) });
          else if (code === 'ERR-LEAVE-001') {
            setErrors({ dateTo: messageFor(err) });
            setOverlap(true);
          } else if (code === 'ERR-LEAVE-002') setErrors({ hours: messageFor(err) });
          else if (Object.keys(detail).length > 0) setErrors(detail);
          else {
            const id = requestIdOf(err);
            setBanner(id ? `${messageFor(err)}（お問い合わせ番号: ${id}）` : messageFor(err));
          }
        },
      },
    );
  };

  const remaining = MAX_REASON - reason.length;

  return (
    <AppShell title="休暇・残業申請">
      <form className="max-w-xl space-y-4" noValidate onSubmit={(e) => e.preventDefault()}>
        <div>
          <label htmlFor="type">休暇種別</label>
          <select id="type" className="field" value={type} onChange={(e) => setType(e.target.value)} aria-invalid={!!errors.type}>
            <option value="">選択してください</option>
            {LEAVE_TYPES.map((t) => (
              <option key={t.code} value={t.code}>{t.label}</option>
            ))}
          </select>
          {errors.type && <p className="err">{errors.type}</p>}
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label htmlFor="dateFrom">開始日</label>
            <input id="dateFrom" type="date" className="field" value={dateFrom} onChange={(e) => { setDateFrom(e.target.value); if (dateTo < e.target.value) setDateTo(e.target.value); }} />
            {errors.dateFrom && <p className="err">{errors.dateFrom}</p>}
          </div>
          <div>
            <label htmlFor="dateTo">終了日</label>
            <input id="dateTo" type="date" className="field" value={dateTo} min={dateFrom} onChange={(e) => setDateTo(e.target.value)} aria-invalid={!!errors.dateTo} />
            {errors.dateTo && (
              <p className="err">
                {errors.dateTo}
                {overlap && <> <Link href="/requests" className="underline">申請一覧を見る</Link></>}
              </p>
            )}
          </div>
        </div>
        {type === 'OVERTIME' && (
          <div>
            <label htmlFor="hours">残業時間（0.00〜24.00）</label>
            <input id="hours" type="number" step="0.01" min={0} max={24} className="field" value={hours} onChange={(e) => setHours(e.target.value)} aria-invalid={!!errors.hours} />
            {errors.hours && <p className="err">{errors.hours}</p>}
          </div>
        )}
        <div>
          <label htmlFor="reason">理由</label>
          <textarea id="reason" className="field" rows={4} value={reason} maxLength={MAX_REASON} onChange={(e) => setReason(e.target.value)} />
          <p className="text-sm" style={{ color: 'var(--color-muted)' }}>残り {remaining} 文字</p>
          {errors.reason && <p className="err">{errors.reason}</p>}
        </div>
        {banner && <p role="alert" className="err">{banner}</p>}
        <div className="flex gap-3">
          <button type="button" className="btn" disabled={create.isPending} onClick={() => send(false)}>下書き保存</button>
          <button type="button" className="btn btn-primary" disabled={create.isPending || !type} onClick={() => send(true)}>
            {create.isPending ? '送信中…' : '提出'}
          </button>
        </div>
      </form>
    </AppShell>
  );
}
