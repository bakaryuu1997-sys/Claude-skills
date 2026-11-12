export type Role = 'employee' | 'manager' | 'hr';

export interface User {
  id: string; // uuid
  employeeId: string; // 6 digits
  name: string;
  role: Role;
  departmentId: string;
  managerId: string | null;
  passwordHash: string;
  tokenVersion: number;
  failedLoginCount: number;
  lockedUntil: number | null; // epoch ms
}

/** manager covers hr ("manager or above"); hr-only operations require role === 'hr'. */
const RANK: Record<Role, number> = { employee: 0, manager: 1, hr: 2 };

export function hasRoleAtLeast(actual: Role, required: Role): boolean {
  return RANK[actual] >= RANK[required];
}
