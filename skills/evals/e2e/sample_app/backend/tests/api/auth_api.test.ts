import { Logger } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { TEST_PASSWORD, createTestEnv, type TestEnv } from '../fixtures/app.fixture';

const LOGIN = '/api/v1/auth/login';
const REFRESH = '/api/v1/auth/refresh';

describe('AUTH API', () => {
  let env: TestEnv;

  beforeEach(async () => {
    env = await createTestEnv();
    env.auth.limiter.reset();
  });
  afterEach(async () => {
    jest.restoreAllMocks();
    await env.app.close();
  });

  const login = (employeeId: string, password: string) =>
    env.api().post(LOGIN).send({ employeeId, password });

  describe('POST /auth/login', () => {
    it('[AUTH-API-001] 200 returns accessToken, refreshToken, expiresIn=900 and role', async () => {
      const res = await login('100001', TEST_PASSWORD);
      expect(res.status).toBe(200);
      expect(res.body.data).toEqual({
        accessToken: expect.any(String),
        refreshToken: expect.any(String),
        expiresIn: 900,
        role: 'employee',
      });
    });

    it('[AUTH-API-002] 401 for a wrong password and the body does not reveal which field was wrong', async () => {
      const wrongPassword = await login('100001', 'Wrong-Pass-0123');
      const unknownUser = await login('999999', 'Wrong-Pass-0123');
      expect(wrongPassword.status).toBe(401);
      expect(wrongPassword.body.error.code).toBe('ERR-AUTH-001');
      expect(unknownUser.status).toBe(401);
      expect(unknownUser.body.error.code).toBe(wrongPassword.body.error.code);
      expect(unknownUser.body.error.message).toBe(wrongPassword.body.error.message);
    });

    it('[AUTH-API-003] 401 for the first five failures, then 423 even with the right password (failedLoginCount=5)', async () => {
      for (let i = 0; i < 5; i++) {
        const r = await login('100001', 'Wrong-Pass-0123');
        expect(r.status).toBe(401);
      }
      const sixth = await login('100001', TEST_PASSWORD);
      expect(sixth.status).toBe(423);
      expect(sixth.body.error.code).toBe('ERR-AUTH-002');
      expect(env.emp.failedLoginCount).toBe(5);
    });

    it('[AUTH-API-006] NEW the lock is released after 10 minutes and a correct login resets the counter', async () => {
      for (let i = 0; i < 5; i++) await login('100001', 'Wrong-Pass-0123');
      env.setNow('2027-01-15T01:10:01Z'); // 10 min 1 s later
      env.auth.limiter.reset();
      const res = await login('100001', TEST_PASSWORD);
      expect(res.status).toBe(200);
      expect(env.emp.failedLoginCount).toBe(0);
    });

    it('[AUTH-API-005] NEW 429 with Retry-After when more than 5 attempts arrive from one caller in 10 minutes', async () => {
      const statuses: number[] = [];
      let last = await login('999999', 'Wrong-Pass-0123');
      statuses.push(last.status);
      for (let i = 0; i < 5; i++) {
        last = await login('999999', 'Wrong-Pass-0123');
        statuses.push(last.status);
      }
      expect(statuses.slice(0, 5)).toEqual([401, 401, 401, 401, 401]);
      expect(last.status).toBe(429);
      expect(last.headers['retry-after']).toBeDefined();
      expect(last.body.error.code).toBe('ERR-SYS-429');
    });

    it.each([
      ['5 digits', '12345'],
      ['7 digits', '1234567'],
      ['non-digit', '12A456'],
    ])('[AUTH-VAL-001] 400 ERR-VAL-001 for employeeId (%s)', async (_label, employeeId) => {
      const res = await login(employeeId, TEST_PASSWORD);
      expect(res.status).toBe(400);
      expect(res.body.error.code).toBe('ERR-VAL-001');
      expect(res.body.error.details[0].field).toBe('employeeId');
    });

    it('[AUTH-VAL-002] password of 11 characters is rejected (400) and 12 characters passes validation', async () => {
      expect((await login('100001', 'a'.repeat(11))).status).toBe(400);
      expect((await login('100001', 'a'.repeat(12))).status).not.toBe(400);
    });

    it('[AUTH-VAL-003] NEW 400 for a missing body and for unknown properties', async () => {
      expect((await env.api().post(LOGIN).send({})).status).toBe(400);
      expect(
        (await env.api().post(LOGIN).send({ employeeId: '100001', password: TEST_PASSWORD, admin: true }))
          .status,
      ).toBe(400);
    });
  });

  describe('POST /auth/refresh', () => {
    it('[AUTH-API-004] NEW 200 returns a new accessToken and expiresIn', async () => {
      const { refreshToken } = (await login('100001', TEST_PASSWORD)).body.data;
      const res = await env.api().post(REFRESH).send({ refreshToken });
      expect(res.status).toBe(200);
      expect(res.body.data).toEqual({ accessToken: expect.any(String), expiresIn: 900 });
    });

    it('[AUTH-SEC-001] the refresh token is single-use: second use returns 401', async () => {
      const { refreshToken } = (await login('100001', TEST_PASSWORD)).body.data;
      expect((await env.api().post(REFRESH).send({ refreshToken })).status).toBe(200);
      const second = await env.api().post(REFRESH).send({ refreshToken });
      expect(second.status).toBe(401);
      expect(second.body.error.code).toBe('ERR-AUTH-003');
    });

    it('[AUTH-SEC-006] NEW 401 for an unknown token and 400 when the token is missing', async () => {
      expect((await env.api().post(REFRESH).send({ refreshToken: 'not-a-real-token' })).status).toBe(401);
      expect((await env.api().post(REFRESH).send({})).status).toBe(400);
    });

    it('[AUTH-SEC-007] NEW 401 after the refresh token lifetime (7 days)', async () => {
      const { refreshToken } = (await login('100001', TEST_PASSWORD)).body.data;
      env.setNow('2027-01-22T01:00:01Z');
      expect((await env.api().post(REFRESH).send({ refreshToken })).status).toBe(401);
    });
  });

  describe('access token handling (any protected endpoint)', () => {
    const protectedCall = (headers: Record<string, string>) =>
      env.api().get('/api/v1/leave-requests').set(headers);

    it('[AUTH-SEC-002] 403 when an employee calls the HR-only CSV endpoint', async () => {
      const res = await env
        .api()
        .get('/api/v1/reports/monthly-attendance.csv')
        .query({ departmentId: env.deptId, yearMonth: '2027-02' })
        .set(env.bearer(env.emp));
      expect(res.status).toBe(403);
      expect(res.body.error.code).toBe('ERR-APPR-001');
    });

    it('[AUTH-SEC-003] NEW 401 ERR-AUTH-003 when the header is missing, malformed or the token is garbage', async () => {
      const cases: Record<string, string>[] = [
        {},
        { Authorization: 'Token abc' },
        { Authorization: 'Bearer garbage' },
      ];
      for (const headers of cases) {
        const res = await protectedCall(headers);
        expect(res.status).toBe(401);
        expect(res.body.error.code).toBe('ERR-AUTH-003');
      }
    });

    it('[AUTH-SEC-004] NEW 401 when the token has been revoked (tokenVersion changed)', async () => {
      const headers = env.bearer(env.emp);
      env.emp.tokenVersion += 1;
      expect((await protectedCall(headers)).status).toBe(401);
    });

    it('[AUTH-SEC-005] NEW 401 for an expired token', async () => {
      const jwt = env.app.get(JwtService);
      const expired = jwt.sign({ sub: env.emp.id, tv: env.emp.tokenVersion }, { expiresIn: -10 });
      expect((await protectedCall({ Authorization: `Bearer ${expired}` })).status).toBe(401);
    });

    it('[AUTH-SEC-008] NEW 401 for a token signed with another secret', async () => {
      const jwt = env.app.get(JwtService);
      const forged = jwt.sign({ sub: env.mgr.id, tv: 1 }, { secret: 'attacker-secret' });
      expect((await protectedCall({ Authorization: `Bearer ${forged}` })).status).toBe(401);
    });
  });

  describe('platform behaviour', () => {
    it('[AUTH-SMK-001] GET /health is 200 and login works for a test account', async () => {
      expect((await env.api().get('/health')).status).toBe(200);
      expect((await login('100001', TEST_PASSWORD)).status).toBe(200);
    });

    it('[AUTH-SYS-001] NEW 404 uses the error envelope for unknown routes', async () => {
      const res = await env.api().get('/api/v1/does-not-exist');
      expect(res.status).toBe(404);
      expect(res.body.error.code).toBe('ERR-SYS-404');
    });

    it('[AUTH-SYS-002] NEW 400 ERR-VAL-001 for malformed JSON', async () => {
      const res = await env.api().post(LOGIN).set('Content-Type', 'application/json').send('{"employeeId":');
      expect(res.status).toBe(400);
      expect(res.body.error.code).toBe('ERR-VAL-001');
    });

    it('[AUTH-SYS-003] NEW 500 hides internals: no SQL, stack trace or file paths in the body', async () => {
      jest.spyOn(Logger.prototype, 'error').mockImplementation(() => undefined);
      jest.spyOn(env.users, 'findByEmployeeId').mockImplementation(() => {
        throw new Error('connection to db failed: SELECT * FROM users WHERE password=...');
      });
      const res = await login('100001', TEST_PASSWORD);
      expect(res.status).toBe(500);
      expect(res.body.error.code).toBe('ERR-SYS-500');
      const text = JSON.stringify(res.body);
      expect(text).not.toMatch(/SELECT|password=|at .*\.ts|node_modules/i);
    });
  });
});
