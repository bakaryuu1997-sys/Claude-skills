import type { RequestStatus } from './leave.types';

/** Pure date and state rules for leave/overtime requests and delegations (no I/O, time is injected). */

const DATE_RE = /^(\d{4})-(\d{2})-(\d{2})$/;

/** True only for real calendar dates (rejects 2026-02-30, 2026-13-01). */
export function isValidDate(value: string): boolean {
  const m = DATE_RE.exec(value);
  if (!m) return false;
  const [y, mo, d] = [Number(m[1]), Number(m[2]), Number(m[3])];
  const dt = new Date(Date.UTC(y, mo - 1, d));
  return dt.getUTCFullYear() === y && dt.getUTCMonth() === mo - 1 && dt.getUTCDate() === d;
}

function toDayNumber(value: string): number {
  const [y, m, d] = value.split('-').map(Number);
  return Date.UTC(y, m - 1, d) / 86_400_000;
}

/** Whole days from `from` to `to` (to - from). Same day = 0. */
export function daysBetween(from: string, to: string): number {
  return toDayNumber(to) - toDayNumber(from);
}

export function isRangeOrdered(from: string, to: string): boolean {
  return daysBetween(from, to) >= 0;
}

export function isWithin(day: string, from: string, to: string): boolean {
  return daysBetween(from, day) >= 0 && daysBetween(day, to) >= 0;
}

/** Two inclusive date ranges overlap. */
export function overlaps(aFrom: string, aTo: string, bFrom: string, bTo: string): boolean {
  return daysBetween(aFrom, bTo) >= 0 && daysBetween(bFrom, aTo) >= 0;
}

export class InvalidTransitionError extends Error {
  constructor(from: RequestStatus, to: RequestStatus) {
    super(`INVALID_TRANSITION: ${from} -> ${to}`);
    this.name = 'InvalidTransitionError';
  }
}

const ALLOWED: Record<RequestStatus, readonly RequestStatus[]> = {
  draft: ['submitted'],
  submitted: ['approved', 'rejected'],
  rejected: ['submitted'],
  approved: [], // cancellation is not designed yet (open question)
};

/** Transition table from the detail design (table 2-1). */
export function transition(from: RequestStatus, to: RequestStatus): RequestStatus {
  if (!ALLOWED[from].includes(to)) throw new InvalidTransitionError(from, to);
  return to;
}
