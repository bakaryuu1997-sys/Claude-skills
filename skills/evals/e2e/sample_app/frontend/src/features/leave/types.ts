export type RequestStatus = 'draft' | 'submitted' | 'approved' | 'rejected';

export interface ApprovalStepDto {
  stepNo: number;
  approverId: string;
  action: 'pending' | 'approved' | 'rejected';
  comment?: string;
  decidedAt?: string;
}

export interface LeaveRequestDto {
  id: string;
  type: string;
  dateFrom: string;
  dateTo: string;
  hours?: number;
  reason: string;
  status: RequestStatus;
  steps: ApprovalStepDto[];
}

export interface LeaveListDto {
  items: LeaveRequestDto[];
  total: number;
}

export interface CreatedDto {
  id: string;
  status: RequestStatus;
  createdAt: string;
}
