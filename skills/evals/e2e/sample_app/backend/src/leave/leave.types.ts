export type RequestStatus = 'draft' | 'submitted' | 'approved' | 'rejected';

export interface ApprovalStep {
  stepNo: number;
  approverId: string; // the executor once decided (a delegate is recorded as the delegate)
  action: 'pending' | 'approved' | 'rejected';
  comment?: string;
  decidedAt?: string; // ISO 8601
}

export interface LeaveRequest {
  id: string; // uuid
  requesterId: string;
  approverId: string | null; // the requester's manager at creation time
  type: string; // leave_types.code
  dateFrom: string; // YYYY-MM-DD
  dateTo: string; // YYYY-MM-DD
  hours?: number;
  reason: string;
  status: RequestStatus;
  steps: ApprovalStep[];
  version: number; // optimistic lock
  createdAt: string; // ISO 8601
}

export interface Delegation {
  id: string; // uuid
  delegatorId: string;
  delegateId: string;
  validFrom: string; // YYYY-MM-DD
  validTo: string; // YYYY-MM-DD
}
