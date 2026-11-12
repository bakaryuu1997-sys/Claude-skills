import { Injectable } from '@nestjs/common';
import { randomBytes, scryptSync, timingSafeEqual } from 'node:crypto';
import type { User } from './user.types';

export function hashPassword(password: string): string {
  const salt = randomBytes(16).toString('hex');
  return `${salt}:${scryptSync(password, salt, 32).toString('hex')}`;
}

export function verifyPassword(password: string, stored: string): boolean {
  const [salt, hash] = stored.split(':');
  if (!salt || !hash) return false;
  const expected = Buffer.from(hash, 'hex');
  const actual = scryptSync(password, salt, expected.length);
  return timingSafeEqual(expected, actual);
}

@Injectable()
export class UsersRepository {
  private readonly users = new Map<string, User>();

  add(user: User): void {
    this.users.set(user.id, user);
  }

  findById(id: string): User | undefined {
    return this.users.get(id);
  }

  findByEmployeeId(employeeId: string): User | undefined {
    return [...this.users.values()].find((u) => u.employeeId === employeeId);
  }

  listByDepartment(departmentId: string): User[] {
    return [...this.users.values()].filter((u) => u.departmentId === departmentId);
  }
}
