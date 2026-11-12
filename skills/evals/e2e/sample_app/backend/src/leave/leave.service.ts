import { Inject, Injectable } from '@nestjs/common';
import type { User } from '../auth/user.types';
import { CLOCK, businessDay, type Clock } from '../common/clock';
import { AppException, ERR } from '../common/errors';
import type { CreateLeaveRequestDto, ListQueryDto } from './leave.dto';
import { isRangeOrdered, isValidDate, isWithin, overlaps, transition } from './leave.engine';
import { LeaveRepository } from './leave.repository';
import type { LeaveRequest } from './leave.types';

@Injectable()
export class LeaveService {
  constructor(
    private readonly repo: LeaveRepository,
    @Inject(CLOCK) private readonly clock: Clock,
  ) {}

  create(user: User, dto: CreateLeaveRequestDto): LeaveRequest {
    if (!this.repo.isActiveType(dto.type)) {
      throw new AppException(ERR.VALIDATION, [{ field: 'type', issue: 'unknown or inactive leave type' }]);
    }
    for (const field of ['dateFrom', 'dateTo'] as const) {
      if (!isValidDate(dto[field])) {
        throw new AppException(ERR.VALIDATION, [{ field, issue: 'not a valid calendar date' }]);
      }
    }
    if (!isRangeOrdered(dto.dateFrom, dto.dateTo)) {
      throw new AppException(ERR.DATE_RANGE, [{ field: 'dateTo', issue: 'must be on or after dateFrom' }]);
    }
    if (dto.type === 'OVERTIME' && dto.hours === undefined) {
      throw new AppException(ERR.VALIDATION, [{ field: 'hours', issue: 'required for OVERTIME' }]);
    }
    const today = businessDay(this.clock());
    if (dto.submit && dto.dateFrom < today) {
      throw new AppException(ERR.DATE_RANGE, [
        { field: 'dateFrom', issue: 'past dates cannot be submitted' },
      ]);
    }

    const mine = this.repo.listByRequester(user.id);
    const clash = mine.some(
      (r) =>
        r.type === dto.type &&
        (r.status === 'approved' || r.status === 'submitted') &&
        overlaps(r.dateFrom, r.dateTo, dto.dateFrom, dto.dateTo),
    );
    if (clash) throw new AppException(ERR.OVERLAP);

    if (dto.submit && dto.type === 'OVERTIME') {
      const preApproved = mine.some(
        (r) =>
          r.type === 'OVERTIME_PRE' &&
          r.status === 'approved' &&
          overlaps(r.dateFrom, r.dateTo, dto.dateFrom, dto.dateTo),
      );
      if (!preApproved) throw new AppException(ERR.NO_PREAPPROVAL);
    }
    if (dto.submit && !user.managerId) {
      throw new AppException(ERR.VALIDATION, [{ field: 'approver', issue: 'no approver is assigned' }]);
    }

    const submitted = dto.submit ? transition('draft', 'submitted') : 'draft';
    return this.repo.create({
      requesterId: user.id,
      approverId: user.managerId,
      type: dto.type,
      dateFrom: dto.dateFrom,
      dateTo: dto.dateTo,
      hours: dto.hours,
      reason: dto.reason,
      status: submitted,
      steps:
        submitted === 'submitted' && user.managerId
          ? [{ stepNo: 1, approverId: user.managerId, action: 'pending' }]
          : [],
      createdAt: this.clock().toISOString(),
    });
  }

  list(user: User, q: ListQueryDto): { items: LeaveRequest[]; total: number } {
    for (const field of ['from', 'to'] as const) {
      const v = q[field];
      if (v !== undefined && !isValidDate(v)) {
        throw new AppException(ERR.VALIDATION, [{ field, issue: 'not a valid calendar date' }]);
      }
    }
    const page = q.page ?? 1;
    const pageSize = q.pageSize ?? 20;
    const all = this.repo
      .listByRequester(user.id)
      .filter((r) => !q.status || r.status === q.status)
      .filter((r) => !q.from || r.dateTo >= q.from)
      .filter((r) => !q.to || r.dateFrom <= q.to);
    return { items: all.slice((page - 1) * pageSize, page * pageSize), total: all.length };
  }

  /** The approver, or the delegate while the delegation covers today, may act on a request. */
  canDecide(user: User, req: LeaveRequest): boolean {
    if (!req.approverId) return false;
    if (req.approverId === user.id) return true;
    const d = this.repo.findDelegationByDelegator(req.approverId);
    return !!d && d.delegateId === user.id && isWithin(businessDay(this.clock()), d.validFrom, d.validTo);
  }

  get(user: User, id: string): LeaveRequest {
    const req = this.repo.findById(id);
    if (!req) throw new AppException(ERR.NOT_FOUND);
    if (req.requesterId !== user.id && !this.canDecide(user, req)) throw new AppException(ERR.FORBIDDEN);
    return req;
  }
}
