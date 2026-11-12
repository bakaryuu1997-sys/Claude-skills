import { Inject, Injectable } from '@nestjs/common';
import { CLOCK, type Clock } from './clock';

export type AuditAction = 'LEAVE_APPROVED' | 'LEAVE_REJECTED' | 'DELEGATION_SET';

export interface AuditEntry {
  action: AuditAction;
  actorId: string;
  targetId: string;
  at: string; // ISO 8601
}

/** Append-only audit trail: there is deliberately no update or delete method. Entries carry no personal data. */
@Injectable()
export class AuditService {
  private readonly log: AuditEntry[] = [];

  constructor(@Inject(CLOCK) private readonly clock: Clock) {}

  append(action: AuditAction, actorId: string, targetId: string): void {
    this.log.push({ action, actorId, targetId, at: this.clock().toISOString() });
  }

  entries(): readonly AuditEntry[] {
    return this.log;
  }
}
