import { Inject, Injectable } from '@nestjs/common';
import { UsersRepository } from '../auth/users.repository';
import type { User } from '../auth/user.types';
import { AuditService } from '../common/audit.service';
import { CLOCK, businessDay, type Clock } from '../common/clock';
import { AppException, ERR } from '../common/errors';
import { CONFIG, type AppConfig } from '../config';
import { daysBetween, isRangeOrdered, isValidDate, transition } from '../leave/leave.engine';
import { LeaveRepository } from '../leave/leave.repository';
import { LeaveService } from '../leave/leave.service';
import type { Delegation, LeaveRequest } from '../leave/leave.types';

@Injectable()
export class ApprovalService {
  constructor(
    private readonly repo: LeaveRepository,
    private readonly leave: LeaveService,
    private readonly users: UsersRepository,
    private readonly audit: AuditService,
    @Inject(CLOCK) private readonly clock: Clock,
    @Inject(CONFIG) private readonly config: AppConfig,
  ) {}

  private load(user: User, id: string): LeaveRequest {
    const req = this.repo.findById(id);
    if (!req) throw new AppException(ERR.NOT_FOUND);
    if (!this.leave.canDecide(user, req)) throw new AppException(ERR.FORBIDDEN);
    return req;
  }

  /** Applies a decision with an optimistic-lock check; a lost race is reported as a state conflict. */
  private decide(user: User, id: string, to: 'approved' | 'rejected', comment?: string): LeaveRequest {
    const req = this.load(user, id);
    if (req.status !== 'submitted') throw new AppException(ERR.STATE_CONFLICT);
    const decidedAt = this.clock().toISOString();
    const steps = req.steps.map((s) =>
      s.action === 'pending' ? { ...s, approverId: user.id, action: to, comment, decidedAt } : s,
    );
    const next: LeaveRequest = { ...req, status: transition(req.status, to), steps };
    if (!this.repo.saveIfVersion(next, req.version)) throw new AppException(ERR.STATE_CONFLICT);
    this.audit.append(to === 'approved' ? 'LEAVE_APPROVED' : 'LEAVE_REJECTED', user.id, req.id);
    return this.repo.findById(id) as LeaveRequest;
  }

  approve(user: User, id: string, comment?: string): { id: string; status: string } {
    const r = this.decide(user, id, 'approved', comment);
    return { id: r.id, status: r.status };
  }

  reject(user: User, id: string, reason: string): { id: string; status: string } {
    const r = this.decide(user, id, 'rejected', reason);
    return { id: r.id, status: r.status };
  }

  setDelegation(user: User, delegateId: string, validFrom: string, validTo: string): Delegation {
    for (const [field, value] of [
      ['validFrom', validFrom],
      ['validTo', validTo],
    ] as const) {
      if (!isValidDate(value))
        throw new AppException(ERR.VALIDATION, [{ field, issue: 'not a valid calendar date' }]);
    }
    if (!isRangeOrdered(validFrom, validTo)) {
      throw new AppException(ERR.DATE_RANGE, [{ field: 'validTo', issue: 'must be on or after validFrom' }]);
    }
    if (validFrom < businessDay(this.clock())) {
      throw new AppException(ERR.DATE_RANGE, [{ field: 'validFrom', issue: 'must not be in the past' }]);
    }
    if (daysBetween(validFrom, validTo) > this.config.delegationMaxDays) {
      throw new AppException(ERR.VALIDATION, [
        { field: 'validTo', issue: `period must not exceed ${this.config.delegationMaxDays} days` },
      ]);
    }
    const delegate = this.users.findById(delegateId);
    if (!delegate) throw new AppException(ERR.NOT_FOUND);
    if (delegate.role === 'employee' || delegate.id === user.id) {
      throw new AppException(ERR.VALIDATION, [{ field: 'delegateId', issue: 'must be another manager' }]);
    }
    const saved = this.repo.upsertDelegation({ delegatorId: user.id, delegateId, validFrom, validTo });
    this.audit.append('DELEGATION_SET', user.id, saved.id);
    return saved;
  }
}
