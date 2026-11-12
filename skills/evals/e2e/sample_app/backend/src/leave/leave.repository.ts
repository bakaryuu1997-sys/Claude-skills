import { Injectable } from '@nestjs/common';
import { randomUUID } from 'node:crypto';
import type { Delegation, LeaveRequest } from './leave.types';

/** Active leave type codes (master data). OVERTIME_PRE is the prior-approval request for overtime. */
const ACTIVE_TYPES = ['ANNUAL', 'SICK', 'SPECIAL', 'OVERTIME_PRE', 'OVERTIME'] as const;

@Injectable()
export class LeaveRepository {
  private readonly requests = new Map<string, LeaveRequest>();
  private readonly delegations = new Map<string, Delegation>();

  isActiveType(code: string): boolean {
    return (ACTIVE_TYPES as readonly string[]).includes(code);
  }

  create(data: Omit<LeaveRequest, 'id' | 'version'>): LeaveRequest {
    const entity: LeaveRequest = { id: randomUUID(), version: 1, ...data };
    this.requests.set(entity.id, entity);
    return entity;
  }

  findById(id: string): LeaveRequest | undefined {
    return this.requests.get(id);
  }

  /** Optimistic lock: saves only when the stored version still equals `expectedVersion`. */
  saveIfVersion(entity: LeaveRequest, expectedVersion: number): boolean {
    const current = this.requests.get(entity.id);
    if (!current || current.version !== expectedVersion) return false;
    this.requests.set(entity.id, { ...entity, version: expectedVersion + 1 });
    return true;
  }

  listByRequester(requesterId: string): LeaveRequest[] {
    return [...this.requests.values()]
      .filter((r) => r.requesterId === requesterId)
      .sort((a, b) => b.createdAt.localeCompare(a.createdAt));
  }

  listApproved(): LeaveRequest[] {
    return [...this.requests.values()].filter((r) => r.status === 'approved');
  }

  upsertDelegation(d: Omit<Delegation, 'id'>): Delegation {
    const existing = this.delegations.get(d.delegatorId);
    const saved: Delegation = { id: existing?.id ?? randomUUID(), ...d };
    this.delegations.set(d.delegatorId, saved);
    return saved;
  }

  findDelegationByDelegator(delegatorId: string): Delegation | undefined {
    return this.delegations.get(delegatorId);
  }
}
