import iconv from 'iconv-lite';
import { createRequest, createTestEnv, type TestEnv } from '../fixtures/app.fixture';

const CSV = '/api/v1/reports/monthly-attendance.csv';
const BASE = '/api/v1/leave-requests';

describe('REPORT API', () => {
  let env: TestEnv;

  beforeEach(async () => {
    env = await createTestEnv();
  });
  afterEach(async () => {
    await env.app.close();
  });

  const get = (query: Record<string, unknown>, as = env.hr) =>
    env
      .api()
      .get(CSV)
      .query(query)
      .set(env.bearer(as))
      .buffer(true)
      .parse((res, cb) => {
        const chunks: Buffer[] = [];
        res.on('data', (c: Buffer) => chunks.push(c));
        res.on('end', () => cb(null, Buffer.concat(chunks)));
      });
  const decode = (body: unknown): string => iconv.decode(body as Buffer, 'cp932');
  const approve = (id: string) =>
    env.api().post(`${BASE}/${id}/approve`).set(env.bearer(env.mgr)).send({}).expect(200);

  it('[REPORT-API-001] 200 text/csv in Shift_JIS with CRLF line ends and a header row', async () => {
    const id = await createRequest(env, env.emp);
    await approve(id);
    const res = await get({ departmentId: env.deptId, yearMonth: '2027-02' });
    expect(res.status).toBe(200);
    expect(res.headers['content-type']).toMatch(/^text\/csv/);
    expect(res.headers['content-type'].toLowerCase()).toContain('shift_jis');
    const text = decode(res.body);
    expect(text.split('\r\n')[0]).toBe('employeeId,name,department,type,dateFrom,dateTo,hours,approvedAt');
    expect(text.endsWith('\r\n')).toBe(true);
    expect(text).toContain('100001,社員 花子,開発部,ANNUAL,2027-02-01,2027-02-01');
  });

  it.each([
    ['2027-13', 400],
    ['2027-1', 400],
    ['2027-02', 200],
  ])('[REPORT-VAL-001] yearMonth=%s -> %s', async (yearMonth, expected) => {
    expect((await get({ departmentId: env.deptId, yearMonth })).status).toBe(expected);
  });

  it('[REPORT-BIZ-001] only approved requests are counted; rejected and draft are excluded', async () => {
    const approved = await createRequest(env, env.emp, { dateFrom: '2027-02-01', dateTo: '2027-02-01' });
    const rejected = await createRequest(env, env.emp, { dateFrom: '2027-02-02', dateTo: '2027-02-02' });
    await createRequest(env, env.emp, { dateFrom: '2027-02-03', dateTo: '2027-02-03', submit: false });
    await approve(approved);
    await env
      .api()
      .post(`${BASE}/${rejected}/reject`)
      .set(env.bearer(env.mgr))
      .send({ reason: 'no' })
      .expect(200);
    const lines = decode((await get({ departmentId: env.deptId, yearMonth: '2027-02' })).body)
      .trim()
      .split('\r\n');
    expect(lines).toHaveLength(2); // header + 1 approved row
  });

  it('[REPORT-BIZ-002] NEW requests of other months are excluded', async () => {
    await approve(await createRequest(env, env.emp, { dateFrom: '2027-03-01', dateTo: '2027-03-01' }));
    const lines = decode((await get({ departmentId: env.deptId, yearMonth: '2027-02' })).body)
      .trim()
      .split('\r\n');
    expect(lines).toHaveLength(1);
  });

  it('[REPORT-SEC-001] 403 for an employee and for a manager (HR only)', async () => {
    expect((await get({ departmentId: env.deptId, yearMonth: '2027-02' }, env.emp)).status).toBe(403);
    expect((await get({ departmentId: env.deptId, yearMonth: '2027-02' }, env.mgr)).status).toBe(403);
  });

  it('[REPORT-SEC-002] NEW 401 without a token', async () => {
    expect((await env.api().get(CSV).query({ departmentId: env.deptId, yearMonth: '2027-02' })).status).toBe(
      401,
    );
  });

  it('[REPORT-SEC-003] NEW formula injection: a name starting with "=" is neutralised in the CSV', async () => {
    env.emp.name = '=HYPERLINK("http://x")';
    await approve(await createRequest(env, env.emp));
    const text = decode((await get({ departmentId: env.deptId, yearMonth: '2027-02' })).body);
    expect(text).not.toMatch(/^=/m);
    expect(text).toContain(`"'=HYPERLINK(""http://x"")"`);
  });

  it('[REPORT-API-002] NEW 404 for an unknown department and 400 for a non-UUID department', async () => {
    expect(
      (await get({ departmentId: '6f1c2c0e-1b1a-4a44-9d0e-2f4d2a2f0c11', yearMonth: '2027-02' })).status,
    ).toBe(404);
    expect((await get({ departmentId: 'x', yearMonth: '2027-02' })).status).toBe(400);
  });

  it('[REPORT-ENC-001] names with environment-dependent characters (髙, 﨑) survive Shift_JIS encoding', async () => {
    env.emp.name = '髙橋 﨑山';
    await approve(await createRequest(env, env.emp));
    const text = decode((await get({ departmentId: env.deptId, yearMonth: '2027-02' })).body);
    expect(text).toContain('髙橋 﨑山');
    expect(text).not.toContain('?');
  });
});
