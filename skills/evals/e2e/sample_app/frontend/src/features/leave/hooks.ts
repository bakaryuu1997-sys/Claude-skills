import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useRef } from 'react';
import { apiFetch, newIdempotencyKey } from '@/lib/api-client';
import type { Envelope } from '@/lib/api-types';
import type { CreateLeaveInput } from './schemas';
import type { CreatedDto, LeaveListDto, LeaveRequestDto } from './types';

export interface ListParams {
  status?: string;
  from?: string;
  to?: string;
  page: number;
  pageSize: number;
}

export function useLeaveList(params: ListParams) {
  const qs = new URLSearchParams(
    Object.entries(params).filter(([, v]) => v !== undefined && v !== '').map(([k, v]) => [k, String(v)]),
  ).toString();
  return useQuery({
    queryKey: ['leave', 'list', params],
    queryFn: () => apiFetch<Envelope<LeaveListDto>>(`/leave-requests?${qs}`),
    staleTime: 30_000,
  });
}

export function useLeaveDetail(id: string) {
  return useQuery({
    queryKey: ['leave', 'detail', id],
    queryFn: () => apiFetch<Envelope<LeaveRequestDto>>(`/leave-requests/${id}`),
  });
}

export function useCreateLeave() {
  const qc = useQueryClient();
  const key = useRef(newIdempotencyKey()); // one key per form opening; replaced after success
  return useMutation({
    mutationFn: (input: CreateLeaveInput & { submit: boolean }) =>
      apiFetch<Envelope<CreatedDto>>('/leave-requests', {
        method: 'POST',
        body: JSON.stringify(input),
        headers: { 'x-idempotency-key': key.current },
      }),
    onSuccess: () => {
      key.current = newIdempotencyKey();
      void qc.invalidateQueries({ queryKey: ['leave'] });
    },
  });
}

export function useDecision(id: string) {
  const qc = useQueryClient();
  const key = useRef(newIdempotencyKey());
  const run = (action: 'approve' | 'reject', body: Record<string, unknown>) =>
    apiFetch<Envelope<{ id: string; status: string }>>(`/leave-requests/${id}/${action}`, {
      method: 'POST',
      body: JSON.stringify(body),
      headers: { 'x-idempotency-key': key.current },
    });
  return useMutation({
    mutationFn: ({ action, body }: { action: 'approve' | 'reject'; body: Record<string, unknown> }) => run(action, body),
    onSuccess: () => {
      key.current = newIdempotencyKey();
      void qc.invalidateQueries({ queryKey: ['leave'] });
    },
  });
}
