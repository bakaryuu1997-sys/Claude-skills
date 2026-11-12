import { INestApplication } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { Test } from '@nestjs/testing';
import { randomUUID } from 'node:crypto';
import request from 'supertest';
import { AppModule } from '../../src/app.module';
import { configureApp } from '../../src/app.setup';
import { AuthService } from '../../src/auth/auth.service';
import type { Role, User } from '../../src/auth/user.types';
import { UsersRepository, hashPassword } from '../../src/auth/users.repository';
import { AuditService } from '../../src/common/audit.service';
import { CLOCK } from '../../src/common/clock';
import { DepartmentsRepository } from '../../src/common/departments.repository';

/** Test credential only (12+ chars). Never a real password. */
export const TEST_PASSWORD = 'Test-Pass-0123';
/** 2027-01-15 10:00 JST. */
export const DEFAULT_NOW = '2027-01-15T01:00:00Z';

export interface TestEnv {
  app: INestApplication;
  api: () => ReturnType<typeof request>;
  setNow: (iso: string) => void;
  users: UsersRepository;
  auth: AuthService;
  audit: AuditService;
  deptId: string;
  /** seeded accounts */
  emp: User; // employee 100001, manager = mgr
  mgr: User; // manager 100002
  other: User; // employee 100003, manager = mgr2 (unrelated to emp)
  mgr2: User; // manager 100004 (delegate candidate)
  hr: User; // hr 100005
  peer: User; // employee 100006, manager = mgr
  tokenFor: (u: User) => string;
  bearer: (u: User) => { Authorization: string };
}

function makeUser(
  employeeId: string,
  name: string,
  role: Role,
  departmentId: string,
  managerId: string | null,
): User {
  return {
    id: randomUUID(),
    employeeId,
    name,
    role,
    departmentId,
    managerId,
    passwordHash: hashPassword(TEST_PASSWORD),
    tokenVersion: 1,
    failedLoginCount: 0,
    lockedUntil: null,
  };
}

export async function createTestEnv(): Promise<TestEnv> {
  let now = new Date(DEFAULT_NOW);
  const moduleRef = await Test.createTestingModule({ imports: [AppModule] })
    .overrideProvider(CLOCK)
    .useValue(() => now)
    .compile();
  const app = configureApp(moduleRef.createNestApplication());
  await app.init();

  const users = app.get(UsersRepository);
  const departments = app.get(DepartmentsRepository);
  const jwt = app.get(JwtService);
  const deptId = randomUUID();
  departments.add({ id: deptId, name: '開発部' });

  const mgr = makeUser('100002', '上長 太郎', 'manager', deptId, null);
  const mgr2 = makeUser('100004', '代理 次郎', 'manager', deptId, null);
  const emp = makeUser('100001', '社員 花子', 'employee', deptId, mgr.id);
  const other = makeUser('100003', '別部 三郎', 'employee', deptId, mgr2.id);
  const hr = makeUser('100005', '人事 四郎', 'hr', deptId, null);
  const peer = makeUser('100006', '同僚 五郎', 'employee', deptId, mgr.id);
  [mgr, mgr2, emp, other, hr, peer].forEach((u) => users.add(u));

  const tokenFor = (u: User): string => jwt.sign({ sub: u.id, tv: u.tokenVersion });
  return {
    app,
    api: () => request(app.getHttpServer()),
    setNow: (iso) => {
      now = new Date(iso);
    },
    users,
    auth: app.get(AuthService),
    audit: app.get(AuditService),
    deptId,
    emp,
    mgr,
    other,
    mgr2,
    hr,
    peer,
    tokenFor,
    bearer: (u) => ({ Authorization: `Bearer ${tokenFor(u)}` }),
  };
}

export function leaveBody(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    type: 'ANNUAL',
    dateFrom: '2027-02-01',
    dateTo: '2027-02-01',
    reason: 'family event',
    submit: true,
    ...overrides,
  };
}

/** Creates a request through the real endpoint and returns its id. */
export async function createRequest(
  env: TestEnv,
  as: User,
  overrides: Record<string, unknown> = {},
): Promise<string> {
  const res = await env.api().post('/api/v1/leave-requests').set(env.bearer(as)).send(leaveBody(overrides));
  if (res.status !== 201) throw new Error(`fixture create failed: ${res.status} ${JSON.stringify(res.body)}`);
  return (res.body as { data: { id: string } }).data.id;
}
