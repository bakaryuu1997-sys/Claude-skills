import { createRequest, createTestEnv, type TestEnv } from '../fixtures/app.fixture';

const BASE = '/api/v1/leave-requests';
const DELEG = '/api/v1/approver-delegations';

describe('APPR API', () => {
  let env: TestEnv;

  beforeEach(async () => {
    env = await createTestEnv();
  });
  afterEach(async () => {
    await env.app.close();
  });

  const approve = (id: string, as = env.mgr, body: Record<string, unknown> = {}) =>
    env.api().post(`${BASE}/${id}/approve`).set(env.bearer(as)).send(body);
  const reject = (id: string, reason: unknown, as = env.mgr) =>
    env.api().post(`${BASE}/${id}/reject`).set(env.bearer(as)).send({ reason });
  const status = async (id: string) =>
    (await env.api().get(`${BASE}/${id}`).set(env.bearer(env.emp))).body.data.status;
  const putDelegation = (body: Record<string, unknown>, as = env.mgr) =>
    env.api().put(DELEG).set(env.bearer(as)).send(body);
  const delegationBody = (validFrom: string, validTo: string, delegateId = env.mgr2.id) => ({
    delegateId,
    validFrom,
    validTo,
  });

  describe('POST /leave-requests/{id}/approve', () => {
    it('[APPR-API-001] 200 approved, the step records the approver and an audit entry LEAVE_APPROVED is written', async () => {
      const id = await createRequest(env, env.emp);
      const res = await approve(id, env.mgr, { comment: 'ok' });
      expect(res.status).toBe(200);
      expect(res.body.data).toEqual({ id, status: 'approved' });
      const steps = (await env.api().get(`${BASE}/${id}`).set(env.bearer(env.emp))).body.data.steps;
      expect(steps).toEqual([
        expect.objectContaining({ approverId: env.mgr.id, action: 'approved', comment: 'ok' }),
      ]);
      expect(env.audit.entries()).toEqual([
        expect.objectContaining({ action: 'LEAVE_APPROVED', actorId: env.mgr.id, targetId: id }),
      ]);
    });

    it('[APPR-BIZ-001] 409 ERR-APPR-002 when the request is already approved', async () => {
      const id = await createRequest(env, env.emp);
      await approve(id).expect(200);
      const again = await approve(id);
      expect(again.status).toBe(409);
      expect(again.body.error.code).toBe('ERR-APPR-002');
      expect(env.audit.entries()).toHaveLength(1);
    });

    it('[APPR-BIZ-002] NEW 409 when the request is still a draft or was already rejected', async () => {
      const draft = await createRequest(env, env.emp, { submit: false });
      expect((await approve(draft)).status).toBe(409);
      const rejected = await createRequest(env, env.emp, { dateFrom: '2027-03-01', dateTo: '2027-03-01' });
      await reject(rejected, 'check dates').expect(200);
      expect((await approve(rejected)).status).toBe(409);
    });

    it('[APPR-SEC-001] 403 for an unrelated manager and for an employee; state does not change', async () => {
      const id = await createRequest(env, env.emp);
      const unrelated = await approve(id, env.mgr2);
      expect(unrelated.status).toBe(403);
      expect(unrelated.body.error.code).toBe('ERR-APPR-001');
      expect((await approve(id, env.peer)).status).toBe(403);
      expect(await status(id)).toBe('submitted');
    });

    it('[APPR-SEC-003] NEW 401 without a token; 404 for an unknown id; 400 for a non-UUID id', async () => {
      const id = await createRequest(env, env.emp);
      expect((await env.api().post(`${BASE}/${id}/approve`).send({})).status).toBe(401);
      expect((await approve('6f1c2c0e-1b1a-4a44-9d0e-2f4d2a2f0c11')).status).toBe(404);
      expect((await approve('not-a-uuid')).status).toBe(400);
    });

    it('[APPR-SEC-004] NEW an approval comment containing markup is stored as plain text and returned JSON-encoded', async () => {
      const id = await createRequest(env, env.emp);
      await approve(id, env.mgr, { comment: '<script>alert(1)</script>' }).expect(200);
      const res = await env.api().get(`${BASE}/${id}`).set(env.bearer(env.emp));
      expect(res.headers['content-type']).toMatch(/application\/json/);
      expect(res.body.data.steps[0].comment).toBe('<script>alert(1)</script>');
    });
  });

  describe('POST /leave-requests/{id}/reject', () => {
    it.each([[''], [undefined], ['x'.repeat(501)]])(
      '[APPR-API-002] 400 for an invalid reason (%j) and the state stays submitted',
      async (reason) => {
        const id = await createRequest(env, env.emp);
        const res = await reject(id, reason);
        expect(res.status).toBe(400);
        expect(res.body.error.code).toBe('ERR-VAL-001');
        expect(await status(id)).toBe('submitted');
      },
    );

    it('[APPR-API-003] 200 rejected with a reason; the reason is kept on the step and LEAVE_REJECTED is audited', async () => {
      const id = await createRequest(env, env.emp);
      const res = await reject(id, '日付を確認してください');
      expect(res.status).toBe(200);
      expect(res.body.data).toEqual({ id, status: 'rejected' });
      const steps = (await env.api().get(`${BASE}/${id}`).set(env.bearer(env.emp))).body.data.steps;
      expect(steps[0]).toMatchObject({ action: 'rejected', comment: '日付を確認してください' });
      expect(env.audit.entries()[0].action).toBe('LEAVE_REJECTED');
    });

    it('[APPR-SEC-002] NEW 403 when an unrelated manager rejects', async () => {
      const id = await createRequest(env, env.emp);
      expect((await reject(id, 'no', env.mgr2)).status).toBe(403);
      expect(await status(id)).toBe('submitted');
    });
  });

  describe('PUT /approver-delegations', () => {
    it('[APPR2-API-001] 200 saves a 30-day delegation and writes an audit entry', async () => {
      const res = await putDelegation(delegationBody('2027-01-15', '2027-02-14'));
      expect(res.status).toBe(200);
      expect(res.body.data).toEqual({
        id: expect.any(String),
        delegateId: env.mgr2.id,
        validFrom: '2027-01-15',
        validTo: '2027-02-14',
      });
      expect(env.audit.entries()[0].action).toBe('DELEGATION_SET');
    });

    it.each([
      ['2027-02-14', 200], // today + 30
      ['2027-02-15', 400], // today + 31
    ])('[APPR2-BND-001] validTo=%s -> %s', async (validTo, expected) => {
      expect((await putDelegation(delegationBody('2027-01-15', validTo))).status).toBe(expected);
    });

    it('[APPR2-VAL-001] 400 when validTo is before validFrom', async () => {
      const res = await putDelegation(delegationBody('2027-01-20', '2027-01-19'));
      expect(res.status).toBe(400);
      expect(res.body.error.code).toBe('ERR-VAL-002');
    });

    it('[APPR2-VAL-002] NEW 400 for a past validFrom, a non-UUID delegateId and a bad date', async () => {
      expect((await putDelegation(delegationBody('2027-01-14', '2027-01-20'))).status).toBe(400);
      expect((await putDelegation(delegationBody('2027-01-15', '2027-01-20', 'nope'))).status).toBe(400);
      expect((await putDelegation(delegationBody('2027-02-30', '2027-03-01'))).status).toBe(400);
    });

    it('[APPR2-VAL-003] NEW 404 for an unknown delegate; 400 when the delegate is an employee or yourself', async () => {
      expect(
        (
          await putDelegation(
            delegationBody('2027-01-15', '2027-01-20', '6f1c2c0e-1b1a-4a44-9d0e-2f4d2a2f0c11'),
          )
        ).status,
      ).toBe(404);
      expect((await putDelegation(delegationBody('2027-01-15', '2027-01-20', env.peer.id))).status).toBe(400);
      expect((await putDelegation(delegationBody('2027-01-15', '2027-01-20', env.mgr.id))).status).toBe(400);
    });

    it('[APPR2-SEC-001] 403 when an employee tries to set a delegation', async () => {
      expect((await putDelegation(delegationBody('2027-01-15', '2027-01-20'), env.emp)).status).toBe(403);
    });

    it('[APPR2-API-002] NEW setting a delegation again replaces the previous one and keeps its id', async () => {
      const first = await putDelegation(delegationBody('2027-01-15', '2027-01-20'));
      const second = await putDelegation(delegationBody('2027-01-16', '2027-01-25'));
      expect(second.body.data.id).toBe(first.body.data.id);
      expect(second.body.data.validTo).toBe('2027-01-25');
    });
  });

  describe('delegation effect on approval', () => {
    it('[APPR2-BIZ-001] 200 the delegate approves inside the period and is recorded as the approver', async () => {
      const id = await createRequest(env, env.emp);
      await putDelegation(delegationBody('2027-01-15', '2027-01-20')).expect(200);
      const res = await approve(id, env.mgr2);
      expect(res.status).toBe(200);
      const steps = (await env.api().get(`${BASE}/${id}`).set(env.bearer(env.emp))).body.data.steps;
      expect(steps[0].approverId).toBe(env.mgr2.id);
    });

    it('[APPR2-BIZ-002] 403 the day after validTo', async () => {
      const id = await createRequest(env, env.emp);
      await putDelegation(delegationBody('2027-01-15', '2027-01-20')).expect(200);
      env.setNow('2027-01-21T01:00:00Z');
      expect((await approve(id, env.mgr2)).status).toBe(403);
    });

    it('[APPR2-BIZ-003] NEW the last day of the delegation is still valid (inclusive) and the day before validFrom is not', async () => {
      const id = await createRequest(env, env.emp);
      await putDelegation(delegationBody('2027-01-16', '2027-01-20')).expect(200);
      expect((await approve(id, env.mgr2)).status).toBe(403); // 2027-01-15 is before validFrom
      env.setNow('2027-01-20T14:59:00Z'); // 23:59 JST on the last day
      expect((await approve(id, env.mgr2)).status).toBe(200);
    });
  });
});
