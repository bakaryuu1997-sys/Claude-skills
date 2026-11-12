import { HttpException } from '@nestjs/common';

export interface ErrorDetail {
  field: string;
  issue: string;
}

/** Codes and HTTP statuses come from the Error Map of the detail design (table 5-1). */
export const ERR = {
  VALIDATION: { code: 'ERR-VAL-001', status: 400, message: 'Invalid input' },
  DATE_RANGE: { code: 'ERR-VAL-002', status: 400, message: 'Invalid date range' },
  AUTH_INVALID: { code: 'ERR-AUTH-001', status: 401, message: 'Employee ID or password is incorrect' },
  AUTH_LOCKED: { code: 'ERR-AUTH-002', status: 423, message: 'Account is locked after repeated failures' },
  AUTH_TOKEN: { code: 'ERR-AUTH-003', status: 401, message: 'Access token is missing, expired or invalid' },
  OVERLAP: { code: 'ERR-LEAVE-001', status: 409, message: 'The period overlaps an existing request' },
  NO_PREAPPROVAL: { code: 'ERR-LEAVE-002', status: 422, message: 'Overtime requires prior approval' },
  FORBIDDEN: { code: 'ERR-APPR-001', status: 403, message: 'Not allowed to perform this operation' },
  STATE_CONFLICT: {
    code: 'ERR-APPR-002',
    status: 409,
    message: 'The request state does not allow this operation',
  },
  NOT_FOUND: { code: 'ERR-SYS-404', status: 404, message: 'Target not found' },
  SYSTEM: { code: 'ERR-SYS-500', status: 500, message: 'Internal server error' },
  /** Not in the Error Map yet: the rate-limit code is an open gap reported to the design owner. */
  RATE_LIMIT: { code: 'ERR-SYS-429', status: 429, message: 'Too many requests' },
} as const;

export type ErrDef = (typeof ERR)[keyof typeof ERR];

export class AppException extends HttpException {
  constructor(
    public readonly def: ErrDef,
    public readonly details?: ErrorDetail[],
    public readonly extraHeaders?: Record<string, string>,
  ) {
    super({ code: def.code, message: def.message, details }, def.status);
  }
}
