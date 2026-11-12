import { Injectable } from '@nestjs/common';
import iconv from 'iconv-lite';
import { UsersRepository } from '../auth/users.repository';
import { DepartmentsRepository } from '../common/departments.repository';
import { AppException, ERR } from '../common/errors';
import { LeaveRepository } from '../leave/leave.repository';

/** Column list is provisional until the character-set / column-order question is decided. */
const HEADER = ['employeeId', 'name', 'department', 'type', 'dateFrom', 'dateTo', 'hours', 'approvedAt'];

/** Neutralises spreadsheet formula injection and quotes fields containing separators. */
export function csvField(value: string): string {
  const safe = /^[=+\-@\t\r]/.test(value) ? `'${value}` : value;
  return /[",\n\r]/.test(safe) ? `"${safe.replace(/"/g, '""')}"` : safe;
}

@Injectable()
export class ReportService {
  constructor(
    private readonly repo: LeaveRepository,
    private readonly users: UsersRepository,
    private readonly departments: DepartmentsRepository,
  ) {}

  /** Approved requests of the department whose period starts in `yearMonth`, as Shift_JIS CSV with CRLF. */
  monthlyCsv(departmentId: string, yearMonth: string): Buffer {
    const dept = this.departments.findById(departmentId);
    if (!dept) throw new AppException(ERR.NOT_FOUND);

    const rows = this.repo
      .listApproved()
      .filter((r) => r.dateFrom.startsWith(yearMonth))
      .flatMap((r) => {
        const u = this.users.findById(r.requesterId);
        if (!u || u.departmentId !== departmentId) return [];
        const decided = r.steps.find((s) => s.action === 'approved');
        return [
          [
            u.employeeId,
            u.name,
            dept.name,
            r.type,
            r.dateFrom,
            r.dateTo,
            r.hours === undefined ? '' : String(r.hours),
            decided?.decidedAt ?? '',
          ]
            .map(csvField)
            .join(','),
        ];
      });

    const text = [HEADER.join(','), ...rows].join('\r\n') + '\r\n';
    return iconv.encode(text, 'Shift_JIS');
  }
}
