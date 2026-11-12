'use client';

import { useMutation } from '@tanstack/react-query';
import { useRef, useState } from 'react';
import { AppShell } from '@/components/app-shell';
import { delegationSchema } from '@/features/leave/schemas';
import { apiFetch, newIdempotencyKey } from '@/lib/api-client';
import type { Envelope } from '@/lib/api-types';
import { messageFor } from '@/lib/messages';

interface DelegationDto {
  id: string;
  delegateId: string;
  validFrom: string;
  validTo: string;
}

export default function DelegationPage() {
  const [delegateId, setDelegateId] = useState('');
  const [validFrom, setValidFrom] = useState('');
  const [validTo, setValidTo] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [banner, setBanner] = useState<string | null>(null);
  const key = useRef(newIdempotencyKey());

  const save = useMutation({
    mutationFn: (body: { delegateId: string; validFrom: string; validTo: string }) =>
      apiFetch<Envelope<DelegationDto>>('/approver-delegations', {
        method: 'PUT',
        body: JSON.stringify(body),
        headers: { 'x-idempotency-key': key.current },
      }),
    onSuccess: () => {
      key.current = newIdempotencyKey();
    },
  });

  const submit = () => {
    setBanner(null);
    const parsed = delegationSchema.safeParse({ delegateId, validFrom, validTo });
    if (!parsed.success) {
      setErrors(Object.fromEntries(parsed.error.issues.map((i) => [String(i.path[0]), i.message])));
      return;
    }
    setErrors({});
    save.mutate(parsed.data, { onError: (err) => setBanner(messageFor(err)) });
  };

  return (
    <AppShell title="承認者代理設定">
      <form className="max-w-xl space-y-4" noValidate onSubmit={(e) => e.preventDefault()}>
        <p className="text-sm">不在期間中の代理承認者を設定します（最大30日）。</p>
        <div>
          <label htmlFor="delegateId">代理承認者のID</label>
          <input id="delegateId" className="field" value={delegateId} onChange={(e) => setDelegateId(e.target.value)} aria-invalid={!!errors.delegateId} />
          {errors.delegateId && <p className="err">{errors.delegateId}</p>}
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label htmlFor="validFrom">開始日</label>
            <input id="validFrom" type="date" className="field" value={validFrom} onChange={(e) => setValidFrom(e.target.value)} />
            {errors.validFrom && <p className="err">{errors.validFrom}</p>}
          </div>
          <div>
            <label htmlFor="validTo">終了日</label>
            <input id="validTo" type="date" className="field" value={validTo} min={validFrom} onChange={(e) => setValidTo(e.target.value)} />
            {errors.validTo && <p className="err">{errors.validTo}</p>}
          </div>
        </div>
        {banner && <p role="alert" className="err">{banner}</p>}
        {save.isSuccess && <p role="status">代理承認者を設定しました。</p>}
        <button type="button" className="btn btn-primary" disabled={save.isPending} onClick={submit}>
          {save.isPending ? '送信中…' : '設定する'}
        </button>
      </form>
    </AppShell>
  );
}
