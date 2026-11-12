import { createRequest, createTestEnv, leaveBody, type TestEnv } from '../fixtures/app.fixture';

const BASE = '/api/v1/leave-requests';

describe('LEAVE API', () => {
  let env: TestEnv;

  beforeEach(async () => {
    env = await createTestEnv();
  });
  afterEach(async () => {
    await env.app.close();
  });

  const post = (as = env.emp, body: Record<string, unknown> = leaveBody()) =>
    env.api().post(BASE).set(env.bearer(as)).send(body);
  const detail = (id: string, as = env.emp) => env.api().get(`${BASE}/${id}`).set(env.bearer(as));
  const list = (query: Record<string, unknown> = {}, as = env.emp) =>
    env.api().get(BASE).query(query).set(env.bearer(as));

  describe('POST /leave-requests', () => {
    it('[LEAVE-API-001] 201 submit=true -> status submitted and an approval step for the manager', async () => {
      const res = await post();
      expect(res.status).toBe(201);
      expect(res.body.data).toEqual({
        id: expect.any(String),
        status: 'submitted',
        createdAt: expect.any(String),
      });
      const d = (await detail(res.body.data.id)).body.data;
      expect(d.steps).toEqual([{ stepNo: 1, approverId: env.mgr.id, action: 'pending' }]);
    });

    it('[LEAVE-API-002] 201 submit=false -> status draft and no approval step', async () => {
      const res = await post(env.emp, leaveBody({ submit: false }));
      expect(res.status).toBe(201);
      expect(res.body.data.status).toBe('draft');
      expect((await detail(res.body.data.id)).body.data.steps).toEqual([]);
    });

    it('[LEAVE-VAL-001] 400 ERR-VAL-002 when dateTo is before dateFrom', async () => {
      const res = await post(env.emp, leaveBody({ dateFrom: '2027-02-05', dateTo: '2027-02-01' }));
      expect(res.status).toBe(400);
      expect(res.body.error.code).toBe('ERR-VAL-002');
    });

    it('[LEAVE-VAL-002] reason of 500 characters is accepted (201), 501 characters is rejected (400)', async () => {
      expect((await post(env.emp, leaveBody({ reason: 'あ'.repeat(500) }))).status).toBe(201);
      const res = await post(
        env.emp,
        leaveBody({ dateFrom: '2027-03-01', dateTo: '2027-03-01', reason: 'あ'.repeat(501) }),
      );
      expect(res.status).toBe(400);
      expect(res.body.error.code).toBe('ERR-VAL-001');
    });

    it('[LEAVE-VAL-003] NEW 400 ERR-VAL-001 for an unknown leave type, an impossible date and a missing submit flag', async () => {
      for (const body of [
        leaveBody({ type: 'NOPE' }),
        leaveBody({ dateFrom: '2027-02-30', dateTo: '2027-02-30' }),
        { type: 'ANNUAL', dateFrom: '2027-02-01', dateTo: '2027-02-01', reason: 'x' },
      ]) {
        const res = await post(env.emp, body);
        expect(res.status).toBe(400);
        expect(res.body.error.code).toBe('ERR-VAL-001');
      }
    });

    it('[LEAVE-VAL-004] NEW a past start date cannot be submitted (400 ERR-VAL-002) but can be saved as a draft', async () => {
      const past = { dateFrom: '2027-01-10', dateTo: '2027-01-10' };
      const submitted = await post(env.emp, leaveBody(past));
      expect(submitted.status).toBe(400);
      expect(submitted.body.error.code).toBe('ERR-VAL-002');
      expect((await post(env.emp, leaveBody({ ...past, submit: false }))).status).toBe(201);
    });

    it('[LEAVE-BIZ-001] 422 ERR-LEAVE-002 for OVERTIME without prior approval', async () => {
      const res = await post(env.emp, leaveBody({ type: 'OVERTIME', hours: 2 }));
      expect(res.status).toBe(422);
      expect(res.body.error.code).toBe('ERR-LEAVE-002');
    });

    it('[LEAVE-BIZ-003] NEW OVERTIME is accepted once an OVERTIME_PRE request for that day has been approved', async () => {
      const preId = await createRequest(env, env.emp, { type: 'OVERTIME_PRE' });
      await env.api().post(`${BASE}/${preId}/approve`).set(env.bearer(env.mgr)).send({}).expect(200);
      const res = await post(env.emp, leaveBody({ type: 'OVERTIME', hours: 2 }));
      expect(res.status).toBe(201);
    });

    it('[LEAVE-BIZ-004] NEW 400 ERR-VAL-001 when OVERTIME has no hours', async () => {
      const res = await post(env.emp, leaveBody({ type: 'OVERTIME', submit: false }));
      expect(res.status).toBe(400);
      expect(res.body.error.code).toBe('ERR-VAL-001');
    });

    it('[LEAVE-BIZ-002] 409 ERR-LEAVE-001 for an overlapping period and no row is added', async () => {
      await post();
      const before = (await list()).body.data.total;
      const res = await post(env.emp, leaveBody({ dateFrom: '2027-02-01', dateTo: '2027-02-03' }));
      expect(res.status).toBe(409);
      expect(res.body.error.code).toBe('ERR-LEAVE-001');
      expect((await list()).body.data.total).toBe(before);
    });

    it('[LEAVE-BIZ-005] NEW adjacent periods do not overlap, and another employee can use the same dates', async () => {
      await post();
      expect((await post(env.emp, leaveBody({ dateFrom: '2027-02-02', dateTo: '2027-02-02' }))).status).toBe(
        201,
      );
      expect((await post(env.peer)).status).toBe(201);
    });

    it('[LEAVE-BIZ-006] NEW an employee without an assigned approver cannot submit (400) but can save a draft', async () => {
      expect((await post(env.mgr)).status).toBe(400);
      expect((await post(env.mgr, leaveBody({ submit: false }))).status).toBe(201);
    });

    it.each([
      [0, 201],
      [24, 201],
      [24.01, 400],
      [-1, 400],
      [1.234, 400],
    ])('[LEAVE-BND-001] hours=%s -> %s', async (hours, expected) => {
      const res = await post(env.emp, leaveBody({ type: 'OVERTIME', hours, submit: false }));
      expect(res.status).toBe(expected);
    });

    it('[LEAVE-SEC-001] NEW 401 without a token', async () => {
      expect((await env.api().post(BASE).send(leaveBody())).status).toBe(401);
    });

    it.todo(
      '[LEAVE-CON-001] two tabs submit the same draft: only one wins (409). Blocked: POST /leave-requests/{id}/submit is not defined in the API design',
    );
  });

  describe('GET /leave-requests', () => {
    it('[LEAVE2-API-001] 200 items are newest first and total counts only my requests', async () => {
      const ids: string[] = [];
      for (const [i, day] of ['2027-02-01', '2027-02-02', '2027-02-03'].entries()) {
        env.setNow(`2027-01-15T0${i + 1}:00:00Z`);
        ids.push(await createRequest(env, env.emp, { dateFrom: day, dateTo: day }));
      }
      const res = await list();
      expect(res.status).toBe(200);
      expect(res.body.data.total).toBe(3);
      expect(res.body.data.items.map((r: { id: string }) => r.id)).toEqual([...ids].reverse());
    });

    it('[LEAVE2-API-002] status filter returns only matching requests', async () => {
      const a = await createRequest(env, env.emp, { dateFrom: '2027-02-01', dateTo: '2027-02-01' });
      await createRequest(env, env.emp, { dateFrom: '2027-02-02', dateTo: '2027-02-02' });
      await env.api().post(`${BASE}/${a}/approve`).set(env.bearer(env.mgr)).send({}).expect(200);
      const res = await list({ status: 'approved' });
      expect(res.body.data.total).toBe(1);
      expect(res.body.data.items[0].id).toBe(a);
    });

    it('[LEAVE2-API-003] NEW from/to filter keeps requests whose period intersects the window', async () => {
      await createRequest(env, env.emp, { dateFrom: '2027-02-01', dateTo: '2027-02-03' });
      await createRequest(env, env.emp, { dateFrom: '2027-03-01', dateTo: '2027-03-01' });
      expect((await list({ from: '2027-02-03', to: '2027-02-28' })).body.data.total).toBe(1);
      expect((await list({ from: '2027-04-01' })).body.data.total).toBe(0);
    });

    it.each([
      [1, 200],
      [100, 200],
      [101, 400],
      [0, 400],
    ])('[LEAVE2-BND-001] pageSize=%s -> %s', async (pageSize, expected) => {
      expect((await list({ pageSize })).status).toBe(expected);
    });

    it('[LEAVE2-BND-002] NEW page=0 and an unknown status are rejected with 400; paging slices the result', async () => {
      expect((await list({ page: 0 })).status).toBe(400);
      expect((await list({ status: 'weird' })).status).toBe(400);
      await createRequest(env, env.emp, { dateFrom: '2027-02-01', dateTo: '2027-02-01' });
      await createRequest(env, env.emp, { dateFrom: '2027-02-02', dateTo: '2027-02-02' });
      const p2 = await list({ page: 2, pageSize: 1 });
      expect(p2.body.data.items).toHaveLength(1);
      expect(p2.body.data.total).toBe(2);
    });

    it('[LEAVE2-SEC-002] only my own requests are listed', async () => {
      await createRequest(env, env.emp);
      await createRequest(env, env.peer);
      const res = await list();
      expect(res.body.data.total).toBe(1);
    });

    it('[LEAVE2-SEC-003] NEW 401 without a token', async () => {
      expect((await env.api().get(BASE)).status).toBe(401);
    });
  });

  describe('GET /leave-requests/{id}', () => {
    it('[LEAVE2-API-004] NEW 200 for the owner with all documented fields', async () => {
      const id = await createRequest(env, env.emp, { reason: 'trip' });
      const res = await detail(id);
      expect(res.status).toBe(200);
      expect(res.body.data).toMatchObject({
        id,
        type: 'ANNUAL',
        dateFrom: '2027-02-01',
        dateTo: '2027-02-01',
        reason: 'trip',
        status: 'submitted',
      });
      expect(Array.isArray(res.body.data.steps)).toBe(true);
    });

    it('[LEAVE2-API-005] NEW 200 for the approver', async () => {
      const id = await createRequest(env, env.emp);
      expect((await detail(id, env.mgr)).status).toBe(200);
    });

    it('[LEAVE2-SEC-001] 403 for another employee and the body leaks no request content', async () => {
      const id = await createRequest(env, env.emp, { reason: 'secret-medical-reason' });
      const res = await detail(id, env.other);
      expect(res.status).toBe(403);
      expect(res.body.error.code).toBe('ERR-APPR-001');
      expect(JSON.stringify(res.body)).not.toContain('secret-medical-reason');
    });

    it('[LEAVE2-SEC-004] NEW 403 for a manager who is not the approver of that request', async () => {
      const id = await createRequest(env, env.emp);
      expect((await detail(id, env.mgr2)).status).toBe(403);
    });

    it('[LEAVE2-API-006] NEW 404 for an unknown id and 400 for a non-UUID id', async () => {
      expect((await detail('6f1c2c0e-1b1a-4a44-9d0e-2f4d2a2f0c11')).status).toBe(404);
      expect((await detail('not-a-uuid')).status).toBe(400);
    });
  });
});
