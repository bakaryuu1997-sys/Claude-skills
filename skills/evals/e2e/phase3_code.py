# -*- coding: utf-8 -*-
"""phase3_code.py — Giai đoạn 3 của E2E: các bước làm việc trên MÃ NGUỒN (C0, C1, C2, C3, C4).

Khác build_all.py (chỉ cần Python), bước này cần mã nguồn mẫu đã cài phụ thuộc:
    sample_app/backend  (NestJS)   →  npm install ; npx jest --coverage --json --outputFile=tests/results/all.results.json
    sample_app/frontend (Next.js)  →  npm install ; npx next build ; (tùy chọn) npx playwright test
Quy trình đầy đủ và cách dựng thư mục làm việc: xem README.md (mục "Giai đoạn 3").

Usage:
    E2E_APP=<thư mục đã npm install, chứa backend/ frontend/, là git repo có nhánh main + nhánh PR> \
    E2E_WS=<workspace> PYTHONUTF8=1 python -B phase3_code.py

Script KHÔNG tự chạy jest/next/playwright: nó đọc kết quả thật đã sinh ra (jest JSON, coverage-summary, e2e-results.json,
npm audit JSON) và gọi các script thật của skill (verify_fe_scaffold, coverage_summary, parse_npm_audit, update_context,
check_gate, xlsx_build, xlsx_verify). Thiếu đầu vào nào → dừng và nói rõ thiếu gì (exit 2), không bịa số.

Các phát hiện review/audit (FINDINGS) là kết luận của người review đã kiểm chứng bằng PoC khi chạy mẫu; file:dòng được
tra lại bằng regex tại thời điểm sinh báo cáo để không lệch khi mã nguồn đổi.
"""
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_sample as S  # noqa: E402

REPO = S.REPO
SK = REPO / "skills"
WS = S.WS
DOCS = WS / "docs"
APP = Path(os.environ.get("E2E_APP", WS.parent / "app"))
BE, FE = APP / "backend", APP / "frontend"
PY = [sys.executable, "-B"]
TODAY = date.today().isoformat()
PROJ = S.PROJ
sys.path.insert(0, str(SK / "a1-project-init" / "scripts"))
from xlsx_build import build as xbuild  # noqa: E402


def need(path: Path, hint: str) -> Path:
    if not path.exists():
        print(f"THIẾU {path}\n  → {hint}")
        raise SystemExit(2)
    return path


def sh(args, cwd=None):
    r = subprocess.run(PY + [str(a) for a in args], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=cwd, env=dict(os.environ, PYTHONUTF8="1"))
    print(f"$ {Path(str(args[0])).name} → exit {r.returncode}")
    return r


def out(folder: str, name: str) -> Path:
    p = DOCS / folder / name
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def loc(rel: str, pattern: str) -> str:
    """'<đường dẫn>:<dòng>' của dòng đầu tiên khớp regex; không khớp → báo lỗi to (tránh trích dẫn sai)."""
    f = APP / rel
    for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
        if re.search(pattern, line):
            return f"{rel}:{i}"
    raise SystemExit(f"Không tìm thấy /{pattern}/ trong {rel} — cập nhật FINDINGS")


# ------------------------------------------------------------------ đầu vào thật
need(BE / "tests/results/all.results.json", "chạy: cd backend && npx jest --coverage --json --outputFile=tests/results/all.results.json")
need(BE / "coverage/coverage-summary.json", "chạy jest với --coverage (reporter json-summary)")
need(DOCS / "C4_trailofbits-security-skills/npm_audit_backend.json", "npm audit --json > …/npm_audit_backend.json (trong backend)")
need(DOCS / "C4_trailofbits-security-skills/npm_audit_frontend.json", "npm audit --json > …/npm_audit_frontend.json (trong frontend)")
need(WS / "project-context.json", "chạy build_all.py trước")
git = ["git", "-C", str(APP)]


def git_out(*a):
    return subprocess.run(git + list(a), capture_output=True, text=True, encoding="utf-8", errors="replace").stdout


jest = json.loads((BE / "tests/results/all.results.json").read_text(encoding="utf-8"))
cov = json.loads((BE / "coverage/coverage-summary.json").read_text(encoding="utf-8"))["total"]
gates = json.loads((WS / "project-context.json").read_text(encoding="utf-8"))["settings"]["quality_gates"]
branch_name = git_out("rev-parse", "--abbrev-ref", "HEAD").strip()
commit = git_out("rev-parse", "--short", "HEAD").strip()
PR = "PR1"

# ================================================================== tài liệu theo từng bước

# ---- C0 -------------------------------------------------------------------------------------------------
v = sh([SK / "c0-frontend-dev/scripts/verify_fe_scaffold.py", FE])
e2e_json = FE / "test-results/e2e-results.json"
e2e = json.loads(e2e_json.read_text(encoding="utf-8"))["stats"] if e2e_json.exists() else None
smoke_log = DOCS / "C0_frontend-dev/integration_smoke_log.txt"
fe_report = f"""# Frontend implementation report — {PROJ} — {TODAY}

> Stack: Next.js 15 (App Router) · React 19 · TanStack Query · Zod · Tailwind CSS 4. Backend commit `{commit}` on `{branch_name}`.

## 1. Screens implemented
| Screen | Route | Roles | API used | Live against the real backend |
|---|---|---|---|---|
| SCR-01 Login | `/login` | all | `POST /auth/login` (through the BFF) | Yes (E2E + smoke) |
| SCR-02 Create request | `/requests/new` | employee | `POST /leave-requests` | Yes (E2E) |
| SCR-03 Request list | `/requests` | employee | `GET /leave-requests` | Yes (E2E) |
| SCR-04 Request detail | `/requests/[id]` | owner, approver | `GET /leave-requests/{{id}}`, `POST .../approve`, `POST .../reject` | Yes (E2E approve path); reject path **not exercised** end to end |
| SCR-06 Delegation | `/delegations` | manager | `PUT /approver-delegations` | Backend contract verified by API tests; screen **not exercised** in the browser |
| SCR-07 Monthly CSV | `/reports` | hr | `GET /reports/monthly-attendance.csv` | CSV through the BFF verified (smoke); download button **not exercised** in the browser |
| SCR-05 Pending approvals | — | manager | **none defined** | **Not implemented**: the API design has no endpoint that lists requests waiting for an approver |

## 2. Live API Adherence Matrix
| Action | Endpoint | Status |
|---|---|---|
| Sign in | `POST /api/auth/login` (BFF) → `/api/v1/auth/login` | live, cookies are HttpOnly |
| Silent refresh | `POST /api/auth/refresh` (BFF) | live; the refresh token is single-use and the contract returns no replacement, so a second expiry sends the user to login |
| Submit / save draft | `POST /leave-requests` | live |
| List with filters and paging | `GET /leave-requests` | live |
| Detail with history | `GET /leave-requests/{{id}}` | live |
| Approve | `POST /leave-requests/{{id}}/approve` | live |
| Reject | `POST /leave-requests/{{id}}/reject` | wired; not exercised end to end |
| Set delegation | `PUT /approver-delegations` | wired; not exercised in the browser |
| CSV download | `GET /reports/monthly-attendance.csv` | proxied and verified with curl; browser download not exercised |

No mock data exists in `src/`. `NEXT_PUBLIC_API_MODE=contract-mock` is rejected by `next.config.ts` for production builds.

## 3. Connection state
- Environment variables: `BACKEND_URL` (server side, BFF target), `NEXT_PUBLIC_API_MODE` (`live` default). See `.env.example`.
- `verify_fe_scaffold.py`: exit {v.returncode} — {"OK, no violations" if v.returncode == 0 else "violations, see log"}.
- Production build: `next build` succeeded (12 routes; first-load JS 103–136 kB). Budget targets are not yet enforced in CI (open item).
- E2E (Playwright, installed Edge, live backend, sequential): {f"{e2e['expected']} passed, {e2e['unexpected']} failed, {e2e['flaky']} flaky" if e2e else "not run"}.
- Integration smoke log with the BFF cookie flags and CSV check: `integration_smoke_log.txt` in this folder.

## 4. Deviations and open items
1. SCR-05 cannot be built: no list endpoint for approvers. Managers can only act by opening a request URL. Needs an API design change.
2. No master-data endpoints: leave types are a configuration list in `src/config/leave-types.ts`; delegate and department are entered as IDs (no lookup endpoints).
3. Content-Security-Policy keeps `'unsafe-inline'` for scripts because Next injects inline bootstrap scripts; a nonce-based CSP is the follow-up.
4. Not covered: the delegation and CSV screens in a browser, visual layout review, accessibility audit, performance budget in CI.
5. Backend defect found while integrating: the login rate limit is shared by every user behind the BFF (see the code review report).

## 5. Run locally
```
cd frontend && npm install && cp .env.example .env.local
npm run build && npm run start          # http://localhost:3001
E2E_CHANNEL=msedge E2E_EMPLOYEE_ID=… E2E_EMPLOYEE_PASSWORD=… E2E_MANAGER_ID=… E2E_MANAGER_PASSWORD=… E2E_HR_ID=… E2E_HR_PASSWORD=… npx playwright test --workers 1
```
"""
out("C0_frontend-dev", "FE_IMPLEMENTATION_REPORT.md").write_text(fe_report, encoding="utf-8")
if e2e_json.exists():
    out("C0_frontend-dev", "e2e_results.json").write_text(e2e_json.read_text(encoding="utf-8"), encoding="utf-8")

# ---- tập hợp số liệu test dùng chung ---------------------------------------------------------------------
cs = sh([SK / "c3-code-review/scripts/coverage_summary.py", "--repo", APP, "--coverage", "backend/coverage/coverage-summary.json",
         "--tests", BE / "tests/results/all.results.json", "--base", "main", "--format", "json"])
evidence = json.loads(cs.stdout)
tst, covt, diff = evidence["tests"], evidence["coverage"], evidence["diff"]
line_ok = covt["lines"] >= gates["ut_coverage_line"]
branch_ok = covt["branches"] >= gates["ut_coverage_branch"]

# ---- C1 -------------------------------------------------------------------------------------------------
files = [l.split("\t") for l in git_out("diff", "--name-status", "main...HEAD").splitlines() if l.strip()]
tree = "\n".join(f"- `{f[1]}`" for f in files if f[1].startswith("backend/src"))
matrix = [
    ("POST /auth/login", "200 {accessToken, refreshToken, expiresIn=900, role}; 401/423/400", loc("backend/src/auth/auth.service.ts", r"async login"), "✅"),
    ("POST /auth/refresh", "200 {accessToken, expiresIn}; single use", loc("backend/src/auth/auth.service.ts", r"async refresh"), "✅ (no new refresh token: contract gap)"),
    ("POST /leave-requests", "201 {id,status,createdAt}; 400/409/422", loc("backend/src/leave/leave.service.ts", r"create\(user"), "✅"),
    ("GET /leave-requests", "200 {items,total}; pageSize 1–100; newest first", loc("backend/src/leave/leave.service.ts", r"list\(user"), "✅"),
    ("GET /leave-requests/{id}", "200 detail+steps; 403 other user; 404", loc("backend/src/leave/leave.service.ts", r"get\(user"), "✅"),
    ("POST …/approve", "200 {id,status}; 403; 409; audit LEAVE_APPROVED", loc("backend/src/approval/approval.service.ts", r"private decide"), "✅ (see review: self-approval)"),
    ("POST …/reject", "reason 1–500; 400 empty", loc("backend/src/approval/approval.service.ts", r"reject\(user"), "✅"),
    ("PUT /approver-delegations", "≤ 30 days; past date 400; 404 unknown delegate", loc("backend/src/approval/approval.service.ts", r"setDelegation\("), "✅"),
    ("GET …/monthly-attendance.csv", "Shift_JIS, CRLF, hr only", loc("backend/src/report/report.service.ts", r"iconv.encode"), "✅ (column order provisional)"),
    ("State table 2-1", "draft→submitted→approved/rejected; approved is final", loc("backend/src/leave/leave.engine.ts", r"export function transition"), "✅"),
    ("Persistence (PostgreSQL, 1 transaction, version column)", "Detail design §1", loc("backend/src/leave/leave.repository.ts", r"new Map<string, LeaveRequest>"), "❌ in-memory repositories only"),
]
pr = f"""# PR: {PR} — leave and overtime approval API (backend)

> Branch `{branch_name}` · commit `{commit}` · mode FEATURE · written in English (code language).

## 1. Summary
- Implements authentication, leave/overtime requests, approval and delegation, and the monthly CSV report from the API Design and Detail Design.
- Assumptions (the design was silent or ambiguous; each needs an owner decision):
  1. Prior approval for overtime (open question on overtime) is modelled as an approved request of type `OVERTIME_PRE` that overlaps the overtime dates.
  2. "Today" is the Japan business day (UTC+9) for the past-date rule and delegation validity.
  3. Delegation period is `validTo − validFrom ≤ 30 days` (difference, not inclusive count), as the test cases require (a 30-day delegation is `today … today+30`).
  4. Account lock is checked before the rate limiter, so the 6th attempt reports the lock (423) instead of 429.
  5. Every 403 uses `ERR-APPR-001` because the Error Map has no other permission code; the rate-limit code `ERR-SYS-429` is not in the Error Map (gap).
  6. Persistence is **not** implemented: repositories are in memory behind the repository classes. Data is lost on restart.

## 2. Directory tree
{tree}

## 3. Spec Adherence Matrix
| Endpoint / rule | Spec | Code | Matches |
|---|---|---|---|
""" + "\n".join(f"| {a} | {b} | `{c}` | {d} |" for a, b, c, d in matrix) + f"""

## 4. Test verification and coverage
- Command: `npx jest --coverage --json --outputFile=tests/results/all.results.json` → {tst['passed']}/{tst['total']} passed, {tst['failed']} failed, {tst.get('skipped', 0)} todo.
- Coverage: lines {covt['lines']}% (gate {gates['ut_coverage_line']}% → {"met" if line_ok else "NOT met"}), branches {covt['branches']}% (gate {gates['ut_coverage_branch']}% → {"met" if branch_ok else "NOT met"}).
- Pre-flight: `npm run format`, `npm run lint -- --max-warnings 0`, `npm run type-check` all clean.
- Unit tests cover the date engine (leap years, month ends, ranges), the state table (allowed and forbidden moves), config fail-fast, CSV escaping, the rate limiter, the refresh-token store and role order.

## 5. Security and guardrails checklist
- [x] No secret in code or `.env.example` (but see review: a development fallback secret exists)
- [x] Validation by schema (class-validator, whitelist + forbidNonWhitelisted)
- [x] AuthN/AuthZ with ownership checks
- [x] No sensitive data in logs or responses
- [ ] Dependency audit: 0 vulnerabilities in production dependencies; 14 in dev tooling
- [ ] Config fail-fast in production: only when `NODE_ENV=production` is set explicitly

## 6. Local run guide
```
cd backend && npm install
cp .env.example .env        # set JWT_SECRET (>= 32 random bytes) for any non-local use
npm run build && npm start
npm test                    # unit + API tests
```

## 7. Reviewer notes
- The review found five High items; see the code review report for this PR.
- Mutation check on the test suite: 4 of 4 deliberate defects were caught (see the API test suite report).
"""
out("C1_dev-implement", f"PR_{PR}.md").write_text(pr, encoding="utf-8")

# ---- C2 -------------------------------------------------------------------------------------------------
MODULES = {"auth": "AUTH", "leave": "LEAVE", "appr": "APPR", "report": "REPORT"}
SPEC_GAPS = [
    ("LEAVE-CON-001 / APPR-E2E-001", "`POST /leave-requests/{id}/submit` is referenced by the test plan but absent from the API design (resubmission after rejection and double-submit control cannot be tested)."),
    ("AUTH-SEC-001", "The refresh response defines only `accessToken` and `expiresIn`, so single-use rotation leaves the client without a refresh token."),
    ("APPR-CON-001", "Concurrent approval by approver and delegate is specified (optimistic lock) but cannot be tested with in-memory storage; needs the database implementation."),
]
MUTATIONS = [
    ("Delegation limit 30 → 31", "caught (APPR2-BND-001)"),
    ("Account lock threshold 5 → 50", "caught (AUTH-API-003)"),
    ("Ownership check removed from GET /leave-requests/{id}", "caught (LEAVE2-SEC-001, LEAVE2-SEC-004)"),
    ("Overlap check removed", "caught (LEAVE-BIZ-002)"),
]
c2_summary = {}
for key, mod in MODULES.items():
    rj = need(BE / f"tests/results/{key}_api.results.json", f"jest tests/api/{key}_api.test.ts --json --outputFile=tests/results/{key}_api.results.json")
    data = json.loads(rj.read_text(encoding="utf-8"))
    rows = []
    for suite in data["testResults"]:
        for t in suite["assertionResults"]:
            m = re.match(r"\[([A-Z0-9]+-[A-Z]+-\d{3})\](\s+NEW)?\s*(.*)", t["title"])
            tid = m.group(1) if m else "?"
            rows.append((tid, "NEW" if m and m.group(2) else "", m.group(3) if m else t["title"], t["status"]))
    n = {s: sum(1 for r in rows if r[3] == s) for s in ("passed", "failed", "todo", "pending")}
    c2_summary[mod] = (len(rows), n)
    table = "\n".join(f"| {a} | {b} | {c.replace('|', '/')} | {d} |" for a, b, c, d in rows)
    gaps = "\n".join(f"- **{a}** — {b}" for a, b in SPEC_GAPS if a.split("-")[0] in (mod, "LEAVE" if mod == "APPR" and False else mod) or (mod == "AUTH" and a.startswith("AUTH")) or (mod == "LEAVE" and a.startswith("LEAVE")) or (mod == "APPR" and a.startswith("APPR")))
    rep = f"""# API test suite — {mod} — v1 ({TODAY})

- Test file: `tests/api/{key}_api.test.ts` · fixtures: `tests/fixtures/app.fixture.ts` · results: `tests/results/{key}_api.results.json`
- Command: `npx jest tests/api/{key}_api.test.ts --json --outputFile=tests/results/{key}_api.results.json`
- **Result: {n['passed']} passed, {n['failed']} failed, {n['todo'] + n['pending']} todo** of {len(rows)} (real run, backend commit `{commit}`).
- Bootstrap parity: the test app uses the same `configureApp()` as `main.ts` (prefix, validation pipe, exception filter, envelope interceptor); time is an injected clock; the database is the in-memory repository (no external service to mock).

## Test cases (Test ID from the test plan; `NEW` = not in the plan yet, to be added by the test-plan owner)
| Test ID | | Case | Status |
|---|---|---|---|
{table}

## Spec Mismatch (code differs from the contract)
None found by this suite: every test that encodes the contract passes. This is not a statement of "no defects"; the code review and security audit found defects the contract tests do not cover.

## Spec Gap (the design is silent or inconsistent)
{gaps or "None for this module."}

## HTTP code matrix
The matrix of status codes per endpoint is encoded in the test titles above (200/201, 400, 401, 403, 404, 409, 422, 423, 429, 500). Codes marked N/A: 500 is covered once for the whole API (`AUTH-SYS-003`, database failure injected, no SQL or stack trace in the body).

## Mutation check (does the suite fail when the code is wrong?)
""" + "\n".join(f"- {a}: {b}" for a, b in MUTATIONS) + "\n"
    out("C2_api-test-suite-generator", f"API_TEST_SUITE_{mod}_v1.md").write_text(rep, encoding="utf-8")

# ---- findings (dùng chung C3/C4) ----------------------------------------------------------------------------
L = {
    "self": loc("backend/src/leave/leave.service.ts", r"canDecide\(user: User"),
    "secret": loc("backend/src/config/index.ts", r"jwtSecret: env\.JWT_SECRET"),
    "env": loc("backend/src/config/index.ts", r"const nodeEnv"),
    "limiter": loc("backend/src/auth/auth.service.ts", r"this\.limiter\.hit"),
    "ip": loc("backend/src/auth/auth.controller.ts", r"req\.ip"),
    "persist": loc("backend/src/leave/leave.repository.ts", r"private readonly requests = new Map"),
    "audit_mem": loc("backend/src/common/audit.service.ts", r"private readonly log"),
    "refresh": loc("backend/src/auth/auth.service.ts", r"async refresh"),
    "lock": loc("backend/src/auth/auth.service.ts", r"AUTH_LOCKED"),
    "timing": loc("backend/src/auth/auth.service.ts", r"verifyPassword\(password"),
    "login": loc("backend/src/auth/auth.service.ts", r"async login"),
    "refresh_route": loc("backend/src/auth/auth.controller.ts", r"@Post\('refresh'\)"),
    "csv": loc("backend/src/report/report.service.ts", r"iconv\.encode"),
    "verify": loc("backend/src/common/auth.guard.ts", r"verifyAsync"),
    "reqid": loc("backend/src/common/http-exception.filter.ts", r"const requestId"),
    "cast": loc("backend/src/approval/approval.service.ts", r"as LeaveRequest"),
    "scrypt": loc("backend/src/auth/users.repository.ts", r"scryptSync\(password, salt, 32\)"),
    "setup": loc("backend/src/app.setup.ts", r"export function configureApp"),
    "csp": loc("frontend/next.config.ts", r"Content-Security-Policy"),
    "bff_login": loc("frontend/src/app/api/auth/login/route.ts", r"x-forwarded-for"),
    "con_test": loc("backend/tests/api/leave_api.test.ts", r"LEAVE-CON-001"),
    "clock": loc("backend/src/common/clock.ts", r"export function businessDay"),
    "rt_store": loc("backend/src/auth/refresh-token.store.ts", r"export class RefreshTokenStore"),
    "occ": loc("backend/src/leave/leave.repository.ts", r"saveIfVersion"),
    "trans": loc("backend/src/leave/leave.engine.ts", r"export function transition"),
    "fixture": loc("backend/tests/fixtures/app.fixture.ts", r"export async function createTestEnv"),
}
# (id, severity, category, where, problem, why, current, fix, R-id, bug_id or None, kind) — kind: code | spec
FINDINGS = [
    ("F-PR1-01", "High", "Security/Logic", L["self"],
     "canDecide() lets a delegate act on a request they filed themselves.",
     "PoC (probe test, then deleted): manager B reports to manager A; A delegates to B; B submits leave and approves it → HTTP 200 approved. Self-approval defeats separation of duties.",
     "if (req.approverId === user.id) return true; … d.delegateId === user.id && isWithin(...)",
     "Return false when req.requesterId === user.id (also for the direct approver) and add API tests for both cases.", "R03, R13", "BUG-001", "code"),
    ("F-PR1-02", "High", "Security", L["secret"],
     "Fail-open JWT secret: NODE_ENV defaults to 'development' when unset and a public fallback secret is used.",
     "A deployment that forgets NODE_ENV=production starts with the publicly known secret; anyone can forge tokens for any user (including hr).",
     "const nodeEnv = env.NODE_ENV ?? 'development'; jwtSecret: env.JWT_SECRET ?? 'dev-only-secret-…'",
     "Allow the fallback only when NODE_ENV is explicitly 'development' or 'test'; otherwise require JWT_SECRET of >= 32 bytes and abort startup.", "R10, R02", "BUG-002", "code"),
    ("F-PR1-03", "High", "Security/Availability", L["limiter"],
     "Login rate limit (5 per 10 min) is keyed by req.ip; behind the BFF every user shares the BFF's IP.",
     "PoC through the real BFF: employee, manager and HR logins, then more logins with different X-Forwarded-For values → 429 after the 6th. A few valid logins lock the whole organisation out for 10 minutes; an attacker only needs 5 requests.",
     "const retryAfter = this.limiter.hit(callerKey, now) with callerKey = req.ip ?? 'unknown'",
     "Configure trust proxy for the real infrastructure and key the limiter by (employeeId, client IP); keep a separate global ceiling. Add an integration test with ≥ 6 logins from different accounts.", "R07, R02", "BUG-003", "code"),
    ("F-PR1-04", "High", "Logic/Database", L["persist"],
     "All state is in memory (users, requests, delegations, refresh tokens, audit log); there is no PostgreSQL implementation.",
     "The Detail Design requires one transaction per decision, a version column and an append-only audit_logs table. Today a restart loses every request, delegation, session and audit entry, and the concurrency tests (APPR-CON-001) cannot be automated.",
     "private readonly requests = new Map<string, LeaveRequest>()",
     "Implement repositories on PostgreSQL from the DB Design (migrations, UPDATE … WHERE version = :v, audit table without UPDATE/DELETE grants) and run the existing API tests against it.", "R12, R15, R13", "BUG-004", "code"),
    ("F-PR1-05", "High", "API Contract (spec gap)", L["con_test"],
     "The API design defines no way to resubmit a rejected request and no list of requests waiting for an approver.",
     "Test plan and screen design need POST /leave-requests/{id}/submit (resubmit) and a pending-approvals list (SCR-05). Without them a rejected request is a dead end and a manager can only approve by guessing a request URL.",
     "(absent) — LEAVE-CON-001 is an it.todo; the frontend has no SCR-05",
     "Owner of the API design: add the two endpoints (and their error codes) or change the flow; then implement and test.", "R16, R13", "BUG-005", "spec"),
    ("F-PR1-06", "Medium", "API Contract (spec gap)", L["refresh"],
     "Refresh is single-use but the response contains no new refresh token.",
     "After one silent refresh the session cannot be refreshed again; users are sent to login at the next expiry (15 min later). Rotation without reissue defeats the purpose.",
     "async refresh(refreshToken: string): Promise<{ accessToken; expiresIn }>",
     "Return a new refreshToken (rotation) or define a sliding session; update the API design and the BFF.", "R16, R02", "BUG-006", "spec"),
    ("F-PR1-07", "Medium", "Security", L["lock"],
     "423 'account locked' is returned only for existing employee IDs.",
     "PoC: 6 failed logins for an existing ID end with 423; for an unknown ID the 6th is still 401. Attackers can enumerate valid employee numbers. The spec requires 423, so the design needs a countermeasure.",
     "if (user?.lockedUntil && user.lockedUntil > now) throw new AppException(ERR.AUTH_LOCKED …)",
     "Count failures per submitted employeeId whether or not it exists and lock the identifier the same way, or return the same response for both.", "R02", "BUG-007", "code"),
    ("F-PR1-08", "Medium", "Security", L["timing"],
     "Password hashing runs only when the user exists.",
     "Measured on the test machine: about 65 ms per request for an existing ID versus about 7 ms for an unknown ID — a timing oracle that also enumerates employee numbers.",
     "if (!user || !verifyPassword(password, user.passwordHash))",
     "Always verify against a dummy hash when the user is not found.", "R02", "BUG-008", "code"),
    ("F-PR1-09", "Medium", "Logic (spec adherence)", L["login"],
     "Login, failed login and lockout are not written to the audit log.",
     "The CRUD matrix marks POST /auth/login as creating audit_logs rows; nothing is written, so there is no trail for brute-force investigation.",
     "async login(…) — no AuditService call",
     "Append LOGIN_SUCCESS, LOGIN_FAILED and ACCOUNT_LOCKED entries (no password, no raw employee number in free text).", "R13, R05", "BUG-009", "code"),
    ("F-PR1-10", "Medium", "Security", L["refresh_route"],
     "RateLimit middleware listed in the API design is missing on refresh (20/min), create (30/min), list (60/min), delegation (10/min) and CSV (5/min).",
     "Spec parity gap; the CSV export (all approved requests of a department) and refresh endpoints can be hammered.",
     "only the login path calls the limiter",
     "Add a guard/interceptor with per-user limits taken from the design; test the 429 and Retry-After for each.", "R07, R17", "BUG-010", "code"),
    ("F-PR1-11", "Medium", "Logic", L["csv"],
     "Characters outside Shift_JIS are silently replaced by '?' in the CSV.",
     "PoC: a name containing 𠮷 and an emoji produced '?' bytes with no warning. HR receives wrong names without any signal; the replacement rule is an open design question.",
     "return iconv.encode(text, 'Shift_JIS')",
     "Decide the rule (reject, transliterate or mark) and surface a count of replaced characters; add a test for the chosen rule.", "R13", "BUG-011", "code"),
    ("F-PR1-12", "Medium", "Security", L["verify"],
     "JWT verification does not pin algorithms, issuer or audience, and the secret length is not enforced.",
     "Defaults of the library currently accept only HMAC algorithms, but this relies on library behaviour. A short secret can be brute-forced offline.",
     "await this.jwt.verifyAsync<TokenPayload>(token)",
     "Pass { algorithms: ['HS256'], issuer, audience } and reject secrets shorter than 32 bytes at startup.", "R02", "BUG-012", "code"),
    ("F-PR1-13", "Low", "API Contract", L["reqid"],
     "requestId is an empty string when the client sends no x-request-id, and a client-supplied value is echoed unvalidated.",
     "Error responses cannot be correlated with server logs; arbitrary client text is reflected into the JSON.",
     "const requestId = String(req.headers['x-request-id'] ?? '')",
     "Generate a UUID in a middleware when absent, validate the format when present, and log it.", "R16, R06", None, "code"),
    ("F-PR1-14", "Low", "Maintainability", L["cast"],
     "Type assertion after a successful save.",
     "The cast hides a missing return value; a future change could return undefined to the controller.",
     "return this.repo.findById(id) as LeaveRequest;",
     "Make saveIfVersion return the saved entity (or undefined) and handle it.", "R24", None, "code"),
    ("F-PR1-15", "Low", "Security", L["scrypt"],
     "scrypt uses Node defaults (N=16384), below the current OWASP minimum (N=2^17).",
     "Cheaper offline cracking if the hashes leak.",
     "scryptSync(password, salt, 32)",
     "Use Argon2id or scrypt with N=2^17, r=8, p=1 (async version to avoid blocking the event loop).", "R02", None, "code"),
    ("F-PR1-16", "Low", "Security", L["setup"],
     "No security headers on the API (no helmet) and X-Powered-By is exposed.",
     "Hardening only; the API sits behind the BFF.",
     "configureApp() sets prefix, pipe, filter and interceptor only",
     "Add helmet and disable x-powered-by.", "R06", None, "code"),
    ("F-PR1-17", "Low", "Security", L["csp"],
     "Frontend CSP allows 'unsafe-inline' scripts.",
     "Weakens XSS defence; needed today for Next's inline bootstrap scripts.",
     "script-src 'self' 'unsafe-inline'",
     "Move to a nonce-based CSP through middleware.", "R23", None, "code"),
    ("F-PR1-18", "Low", "Dependency", "backend/package.json:1",
     "Development dependencies carry 14 advisories (7 low, 7 moderate), all in the jest and eslint toolchains.",
     "Not shipped to production; production dependencies report 0.",
     "npm audit: jest / ts-jest / typescript-eslint chains",
     "Upgrade the toolchain with the next maintenance window; keep the production audit in CI.", "R09", None, "code"),
]
BUGS = [f for f in FINDINGS if f[9]]
PRAISES = [
    ("Time is injected (Clock + businessDay), so all date rules are tested without waiting or mocking global time.", L["clock"], "Deterministic tests for the delegation window and the past-date rule."),
    ("The test app is built with the same configureApp() as main.ts, so tests run with the production pipes, filter and interceptor.", L["setup"], "No bypass of validation or error formatting in tests."),
    ("Refresh tokens are opaque, stored only as SHA-256 hashes, and consumed once.", L["rt_store"], "A leaked store does not leak usable tokens."),
    ("The state table is a pure function with allowed and forbidden moves covered by tests; decisions use a version check.", L["trans"], "The approval rules are easy to audit and change."),
    ("Every API test carries the test-plan ID, and a mutation check proved that the suite fails when the code is wrong.", L["fixture"], "Traceability into test execution and evidence that the tests are not vacuous."),
]
CHECK = [  # (R-id, group, criterion, risk, files, result, note)
    ("R01", "Security", "Injection", "Cao", "backend/src", "N/A", "No SQL, shell or template use; re-audit when the PostgreSQL repositories land."),
    ("R02", "Security", "Authentication", "Cao", "auth.service.ts, auth.guard.ts, config", "FAIL", "F-PR1-02, -03, -07, -08, -12 (secret fallback, shared limiter, enumeration, timing, JWT options)."),
    ("R03", "Security", "Authorization / IDOR", "Cao", "leave.service.ts", "FAIL", "Ownership checks and UUID validation present; self-approval via delegation (F-PR1-01)."),
    ("R04", "Security", "Input validation / mass assignment", "TB", "*.dto.ts, app.setup.ts", "PASS", "whitelist + forbidNonWhitelisted; boundaries tested (hours, reason, pageSize, dates)."),
    ("R05", "Security", "Sensitive data in log/response", "TB", "audit.service.ts", "REC", "Responses map fields explicitly (no passwordHash). Audit entries lack login events (F-PR1-09)."),
    ("R06", "Security", "Internal error exposure", "TB", "http-exception.filter.ts", "PASS", "Test AUTH-SYS-003 proves no SQL or stack trace; requestId gaps are Low (F-PR1-13)."),
    ("R07", "Security", "Rate limiting", "Cao", "auth.service.ts, auth.controller.ts", "FAIL", "F-PR1-03 (shared key), F-PR1-10 (missing limits)."),
    ("R08", "Security", "File upload", "Thấp", "-", "N/A", "No upload endpoint."),
    ("R09", "Security", "Dependency / CVE", "TB", "package.json", "REC", "0 production advisories; 14 dev-tooling advisories (F-PR1-18). Frontend: zod and next advisories triaged Unreachable (see audit report)."),
    ("R10", "Security", "Secrets", "Cao", "config/index.ts", "FAIL", "F-PR1-02."),
    ("R11", "Performance", "N+1, index, pagination, pool", "TB", "leave.repository.ts", "REC", "Pagination capped at 100. CSV loads all approved requests in memory; re-check with the database."),
    ("R12", "Logic", "Transaction / concurrency / idempotency", "Cao", "approval.service.ts", "FAIL", "Optimistic lock exists in memory only (F-PR1-04); idempotency keys are sent by the frontend but not honoured by the API."),
    ("R13", "Logic", "Business rules, edge cases, status codes", "Cao", "leave.service.ts, approval.service.ts", "FAIL", "Rules match the design (overlap, overtime pre-approval, 30-day delegation); F-PR1-01, -09, -11."),
    ("R14", "Logic", "Error handling / no swallowed errors / no any", "TB", "src", "PASS", "No empty catch except the JWT verify (maps to 401); no `any`."),
    ("R15", "Database", "Migration safety", "Cao", "-", "FAIL", "No persistence layer (F-PR1-04)."),
    ("R16", "API", "Contract, envelope, error codes", "Cao", "controllers, errors.ts", "FAIL", "Field names, envelope and codes match; gaps in the contract itself (F-PR1-05, -06) and the missing rate-limit code in the Error Map."),
    ("R17", "API", "Status / decorator parity", "TB", "controllers", "REC", "Statuses match; RateLimit middleware from the design missing (F-PR1-10)."),
    ("R18", "Test", "Happy / unhappy / boundary tests", "TB", "tests/", "PASS", f"{tst['passed']} passing tests, line coverage {covt['lines']}%, branch {covt['branches']}%."),
    ("R19", "Test", "Negative tests for guards, throws, locks", "TB", "tests/api", "PASS", "403/409/423/429 paths covered; mutation check 4/4."),
    ("R20", "Test", "Isolation, no time dependence", "TB", "tests/fixtures", "PASS", "Injected clock; one app per test."),
    ("R21", "IaC", "Dockerfile", "TB", "-", "N/A", "No container files in this PR (scaffold templates not applied)."),
    ("R22", "IaC", "CI/CD", "TB", "-", "N/A", "No pipeline in this PR."),
    ("R23", "Frontend", "Token storage, XSS/CSRF, offline, a11y", "TB", "frontend/", "REC", "Tokens only in HttpOnly cookies; custom-header CSRF rule; CSP keeps unsafe-inline (F-PR1-17)."),
    ("R24", "Maintainability", "Layering, strict TS, naming", "Thấp", "src", "REC", "Clear layers, strict TS; one cast (F-PR1-14)."),
    ("R25", "Domain", "Domain rules (finance)", "-", "-", "N/A", "Not a finance domain."),
]
SEV_FILL = {"Critical": "FFE0E0", "High": "FCE4D6", "Medium": "FFF2CC", "Low": "DDEEFF"}
cnt = {s: sum(1 for f in FINDINGS if f[1] == s) for s in ("Critical", "High", "Medium", "Low")}

# ---- C3 -------------------------------------------------------------------------------------------------
numstat = [l.split("\t") for l in git_out("diff", "--numstat", "main...HEAD").splitlines() if l.strip()]


def layer(p):
    for k, v in (("/auth/", "auth"), ("/approval/", "approval"), ("/leave/", "leave"), ("/report/", "report"), ("/common/", "common"),
                 ("/config/", "config"), ("tests/", "test"), ("frontend", "frontend")):
        if k in p:
            return v
    return "app"


HIGH_RISK = ("/auth/", "/approval/", "/config/", "auth.guard")
files_rows = []
for a, d, p in numstat:
    if not p.startswith("backend/src") and not p.startswith("backend/tests"):
        continue
    risk = "Cao" if any(k in p for k in HIGH_RISK) else ("Thấp" if p.endswith((".dto.ts", ".module.ts", ".types.ts")) or "tests/" in p else "TB")
    files_rows.append([p, layer(p), "TypeScript", f"+{a} / -{d}", risk, "", "Reviewed"])

R_FILL = {"PASS": "E2EFDA", "FIXED": "E2EFDA", "REC": "FFF2CC", "FAIL": "FCE4D6", "N/A": "F2F2F2"}


def cell(v, fill=None):
    return {"value": v, "fill": fill} if fill else v


verdict = "🔴 REQUEST CHANGES" if cnt["Critical"] + cnt["High"] else ("⚠️ APPROVE WITH COMMENTS" if cnt["Medium"] + cnt["Low"] else "✅ APPROVE")
spec = {"title": "Code Review Report", "language": "vi", "sheets": [
    {"name": "Review_Summary", "title": f"Review Summary — {PROJ} — {PR}", "subtitle": f"Nhánh {branch_name} · commit {commit} · {TODAY}",
     "columns": [{"key": "k", "header": "Mục", "width": 34}, {"key": "v", "header": "Giá trị", "width": 70, "wrap": True}],
     "rows": [
         ["Stack", "NestJS 11 / TypeScript (backend) + Next.js 15 (frontend, xem báo cáo C0)"],
         ["Phạm vi", f"{len(files_rows)} file backend (src + tests), +{diff['total_added']} / -{diff['total_deleted']} dòng so với main"],
         ["Tác giả / Reviewer", "[CẦN ĐIỀN] / [CẦN ĐIỀN]"],
         ["Critical", '=COUNTIF(Findings_Defects!$B$4:$B$200,"Critical")'],
         ["High", '=COUNTIF(Findings_Defects!$B$4:$B$200,"High")'],
         ["Medium", '=COUNTIF(Findings_Defects!$B$4:$B$200,"Medium")'],
         ["Low", '=COUNTIF(Findings_Defects!$B$4:$B$200,"Low")'],
         ["Tổng finding", "=COUNTA(Findings_Defects!$A$4:$A$200)"],
         ["Test evidence (jest)", f"{tst['passed']}/{tst['total']} pass, {tst['failed']} fail, {tst.get('skipped', 0)} todo — nguồn coverage_summary.py"],
         ["Coverage dòng / nhánh", f"{covt['lines']}% / {covt['branches']}% (gate {gates['ut_coverage_line']}% / {gates['ut_coverage_branch']}%: {'đạt' if line_ok and branch_ok else 'KHÔNG đạt'})"],
         ["Verdict", cell(verdict, "FCE4D6")],
         ["Điều kiện merge", "Sửa BUG-001, BUG-002, BUG-003; BUG-004 và BUG-005 cần quyết định thiết kế/lập kế hoạch trước; Medium vào known_issues."],
     ]},
    {"name": "Review_Checklist", "title": "Review Checklist R01–R25", "subtitle": "PASS / FIXED / REC / FAIL / N/A",
     "columns": [{"key": "a", "header": "ID", "width": 7}, {"key": "b", "header": "Nhóm", "width": 15}, {"key": "c", "header": "Tiêu chí", "width": 34, "wrap": True},
                 {"key": "d", "header": "Mức rủi ro", "width": 10}, {"key": "e", "header": "File liên quan", "width": 30, "wrap": True},
                 {"key": "f", "header": "Kết quả", "width": 9}, {"key": "g", "header": "Ghi chú kỹ thuật", "width": 70, "wrap": True}],
     "rows": [[r[0], r[1], r[2], r[3], r[4], cell(r[5], R_FILL[r[5]]), r[6]] for r in CHECK]},
    {"name": "Files_Reviewed", "title": "Files Reviewed", "subtitle": "Số dòng lấy từ git diff --numstat main...HEAD",
     "columns": [{"key": "a", "header": "Đường dẫn", "width": 52}, {"key": "b", "header": "Layer", "width": 11}, {"key": "c", "header": "Ngôn ngữ", "width": 12},
                 {"key": "d", "header": "LOC (+/−)", "width": 12}, {"key": "e", "header": "Rủi ro", "width": 8}, {"key": "f", "header": "Hàm/lớp trọng tâm", "width": 28},
                 {"key": "g", "header": "Trạng thái", "width": 11}], "rows": files_rows},
    {"name": "Findings_Defects", "title": "Findings / Defects", "subtitle": "Severity theo thang chuẩn; BUG-ID = đã ghi vào known_issues",
     "columns": [{"key": "a", "header": "ID", "width": 11}, {"key": "b", "header": "Severity", "width": 9}, {"key": "c", "header": "Category", "width": 18, "wrap": True},
                 {"key": "d", "header": "File:dòng", "width": 38, "wrap": True}, {"key": "e", "header": "Problem", "width": 44, "wrap": True},
                 {"key": "f", "header": "Why (tác động)", "width": 60, "wrap": True}, {"key": "g", "header": "Code hiện tại", "width": 40, "wrap": True},
                 {"key": "h", "header": "Đề xuất", "width": 50, "wrap": True}, {"key": "i", "header": "Tiêu chí", "width": 10},
                 {"key": "j", "header": "Trạng thái", "width": 10}, {"key": "k", "header": "BUG-ID", "width": 10}],
     "rows": [[f[0], cell(f[1], SEV_FILL[f[1]]), f[2], f[3], f[4], f[5], f[6], f[7], f[8], "Open", f[9] or ""] for f in FINDINGS]},
    {"name": "Key_Praises", "title": "Key Praises", "subtitle": "Điểm tốt có thật trong PR",
     "columns": [{"key": "a", "header": "Điểm tốt", "width": 70, "wrap": True}, {"key": "b", "header": "File:dòng", "width": 40}, {"key": "c", "header": "Vì sao tốt", "width": 60, "wrap": True}],
     "rows": [[cell(p[0], "E2EFDA"), p[1], p[2]] for p in PRAISES]},
]}
xl = out("C3_code-review", f"{PROJ}_{PR}_Code_Review_Report.xlsx")
xbuild(spec, xl)
vx = sh([SK / "a1-project-init/scripts/xlsx_verify.py", xl])
assert vx.returncode == 0, vx.stdout[-400:]

md = [f"# Code Review Report — {PROJ} — {PR}", "",
      f"**CODE REVIEW REPORT** — PR: `{branch_name}` ({commit}) · Stack: NestJS 11 / TypeScript · Files: {len(files_rows)}",
      f"**VERDICT: {verdict}**",
      f"Critical {cnt['Critical']} · High {cnt['High']} · Medium {cnt['Medium']} · Low {cnt['Low']} · Praise {len(PRAISES)}",
      f"Test evidence: {tst['passed']}/{tst['total']} pass ({tst.get('skipped', 0)} todo) · coverage line {covt['lines']}% / branch {covt['branches']}% (nguồn: coverage_summary.py)", ""]
for sev in ("Critical", "High", "Medium", "Low"):
    items = [f for f in FINDINGS if f[1] == sev]
    if not items:
        continue
    md.append(f"## {sev} ({len(items)})")
    for f in items:
        md += [f"### {f[0]} — {f[4]}", f"- **Vị trí:** `{f[3]}` · **Category:** {f[2]} · **Tiêu chí:** {f[8]}" + (f" · **{f[9]}**" if f[9] else ""),
               f"- **Tác động:** {f[5]}", f"- **Code hiện tại:** `{f[6]}`", f"- **Đề xuất:** {f[7]}", ""]
md += ["## Praise"] + [f"- {p[0]} (`{p[1]}`) — {p[2]}" for p in PRAISES]
md += ["", "## Giới hạn của lần review này",
       "- Không có semgrep/ocr: kết quả công cụ tự động không được dùng; review là đọc mã + PoC bằng test tạm (đã xóa) và gọi API qua BFF.",
       "- Chưa review: lớp persistence (chưa tồn tại), bố cục giao diện trên trình duyệt, màn Delegation/CSV.",
       "", "## Lesson",
       "Khi một thành phần đứng giữa (BFF/proxy), mọi giới hạn theo IP ở phía sau phải được kiểm bằng một lần chạy tích hợp thật — test đơn vị với `supertest` không thấy được lỗi này."]
out("C3_code-review", f"{PROJ}_{PR}_Code_Review_Report.md").write_text("\n".join(md) + "\n", encoding="utf-8")

# ---- C4 -------------------------------------------------------------------------------------------------
C4 = DOCS / "C4_trailofbits-security-skills"


def audit_table(name, pkgjson):
    r = sh([SK / "c4-trailofbits-security-skills/scripts/parse_npm_audit.py", C4 / name, "--package-json", pkgjson, "--fail-on", "high"])
    return r.stdout.strip(), r.returncode


tb_be, rc_be = audit_table("npm_audit_backend.json", BE / "package.json")
tb_fe, rc_fe = audit_table("npm_audit_frontend.json", FE / "package.json")
fe_triage = ("\n**Reachability (đọc mã):** `zod` GHSA-mrhx-c7xc-m3w5 (bộ nhớ khi validate collection cực lớn): Unreachable — zod chỉ chạy trong component client "
             "(`frontend/src/features/leave/schemas.ts`, `reports/page.tsx`) trên chuỗi/số do chính người dùng nhập, không có schema mảng; không dùng ở server. "
             "`postcss` (bản lồng trong `next`, 4 advisory về sourceMappingURL/`</style>`): Unreachable — chỉ chạy lúc build trên CSS của dự án, không xử lý CSS do người dùng cung cấp. "
             "`next` Medium chỉ là phụ thuộc vào postcss. Đã chọn không nâng lên bản major (breaking) trong PR này; theo dõi trong known_issues nếu nâng cấp bị hoãn.")
vectors = [
    ("V1 IDOR/BOLA", "Đạt một phần", "UUID kiểm bằng ParseUUIDPipe; GET theo id kiểm chủ sở hữu hoặc người duyệt; approve/reject kiểm canDecide. Lỗi: người được ủy quyền tự duyệt đơn của mình (BUG-001). 403 (không phải 404) theo spec nên lộ sự tồn tại id."),
    ("V2 Auth, JWT, phiên", "Không đạt", "BUG-002 (secret mặc định, NODE_ENV mặc định development), BUG-012 (không ghim thuật toán/iss/aud), BUG-007/008 (liệt kê tài khoản qua 423 và thời gian), BUG-006 (refresh không cấp token mới), scrypt dưới mức khuyến nghị (Low). Tốt: token ở cookie HttpOnly qua BFF, refresh băm SHA-256 dùng một lần, tokenVersion thu hồi."),
    ("V3 Mass assignment", "Đạt", "ValidationPipe whitelist + forbidNonWhitelisted; controller ánh xạ trường trả về tường minh, không trả passwordHash."),
    ("V4 Rò rỉ thông tin / log", "Đạt (Low còn lại)", "Không log body; lỗi không lộ SQL/stack (test AUTH-SYS-003). requestId rỗng/phản chiếu giá trị client (Low)."),
    ("V5 Injection", "Chưa áp dụng", "Chưa có truy vấn DB/shell/file. CSV đã vô hiệu công thức (`=`,`+`,`-`,`@`). Phải kiểm lại khi có repository PostgreSQL."),
    ("V6 DoS / rate limit", "Không đạt", "BUG-003 (khóa giới hạn dùng chung sau BFF — PoC), BUG-010 (thiếu RateLimit theo spec ở 5 endpoint), CSV nạp toàn bộ bản ghi vào bộ nhớ. Body parser giữ mặc định 100 kB; phân trang tối đa 100."),
    ("V7 Headers / CORS", "Một phần", "Frontend có CSP/X-Frame-Options/nosniff/Referrer-Policy, không X-Powered-By; CSP còn 'unsafe-inline'. API chưa có helmet (Low). Không bật CORS (cùng origin qua BFF) — đúng thiết kế."),
    ("V8 Chuỗi cung ứng", "Đạt có điều kiện", "Backend: 0 lỗ hổng ở production dependencies, 14 ở dev tooling. Frontend: 6 (3 High) — đã triage Unreachable; lockfile đã commit."),
    ("V9 SSRF", "Không áp dụng", "Server không gọi URL do client cung cấp; BFF proxy chỉ cho đường dẫn trong allow-list và đích cố định BACKEND_URL."),
    ("V10 Secrets", "Không đạt", "BUG-002. `.env.example` không có giá trị thật; `.env` được ignore. gitleaks/trufflehog không có trên máy: chỉ quét thủ công bằng grep."),
]
sev_c4 = {s: sum(1 for f in FINDINGS if f[1] == s and f[10] == "code" or (f[1] == s and f[10] == "spec")) for s in ("Critical", "High", "Medium", "Low")}
security_rows = [f for f in FINDINGS if f[8].split(",")[0].strip() in ("R02", "R03", "R07", "R10", "R06", "R23", "R09", "R05")]
vec_of = {"F-PR1-01": "V1", "F-PR1-02": "V2/V10", "F-PR1-03": "V6", "F-PR1-07": "V2", "F-PR1-08": "V2", "F-PR1-10": "V6", "F-PR1-12": "V2",
          "F-PR1-13": "V4", "F-PR1-15": "V2", "F-PR1-16": "V7", "F-PR1-17": "V7", "F-PR1-18": "V8"}
cwe = {"F-PR1-01": "CWE-863 / API5:2023", "F-PR1-02": "CWE-1188 / API8:2023", "F-PR1-03": "CWE-770 / API4:2023", "F-PR1-07": "CWE-204",
       "F-PR1-08": "CWE-208", "F-PR1-10": "CWE-770 / API4:2023", "F-PR1-12": "CWE-347", "F-PR1-13": "CWE-117", "F-PR1-15": "CWE-916",
       "F-PR1-16": "CWE-200", "F-PR1-17": "CWE-79", "F-PR1-18": "CWE-1104"}
audit_findings = [f for f in FINDINGS if f[0] in vec_of]
c4_cnt = {s: sum(1 for f in audit_findings if f[1] == s) for s in ("Critical", "High", "Medium", "Low")}
sec = [f"# Security Audit Report — {PROJ} — {PR} — {TODAY}", "",
       "## 1. Phạm vi & phương pháp",
       f"- Phạm vi: nhánh `{branch_name}` ({commit}): backend NestJS (auth, leave, approval, report) + frontend Next.js (BFF, đăng nhập, phiên). Ngoài phạm vi: hạ tầng, CI/CD, DB (chưa có).",
       "- Phương pháp: đọc mã theo 10 vector; `npm audit --json` (npm " + (subprocess.run(["npm", "-v"], capture_output=True, text=True, shell=(os.name == "nt")).stdout.strip() or "?") + ") cho backend và frontend, bóc bằng `parse_npm_audit.py`.",
       "- Không chạy được: `semgrep`, `gitleaks`, `trufflehog`, `trivy`, `osv-scanner` không có trên máy; không cài mới khi chưa được cho phép. Quét secret chỉ bằng grep thủ công.",
       "- Kiểm thử động: **Có** — PoC bằng test tạm (đã xóa) trên backend chạy cục bộ và các lệnh `curl` qua BFF với tài khoản kiểm thử (nhật ký: `docs/C0_frontend-dev/integration_smoke_log.txt`). Không phải pentest.", "",
       "## 2. Tóm tắt",
       "| Critical | High | Medium | Low |", "|---|---|---|---|",
       f"| {c4_cnt['Critical']} | {c4_cnt['High']} | {c4_cnt['Medium']} | {c4_cnt['Low']} |", "",
       f"Kết luận phát hành: **CHẶN** — còn {c4_cnt['High']} High về bảo mật chưa xử lý (BUG-001, BUG-002, BUG-003). Các High không thuộc bảo mật (BUG-004, BUG-005) ở báo cáo review mã.", "",
       "## 3. Kết quả theo vector", "| Vector | Kết quả | Ghi chú |", "|---|---|---|"]
sec += [f"| {a} | {b} | {c} |" for a, b, c in vectors]
sec += ["", "## 4. Findings", "| ID | Severity | Vector | CWE/OWASP | Vị trí | Mô tả & tác động | Bằng chứng / PoC | Khuyến nghị | Owner | Hạn | Trạng thái |", "|---|---|---|---|---|---|---|---|---|---|---|"]
for f in audit_findings:
    sec.append(f"| {f[9] or f[0]} | {f[1]} | {vec_of[f[0]]} | {cwe[f[0]]} | `{f[3]}` | {f[4]} | {f[5]} | {f[7]} | [CẦN ĐIỀN] | [CẦN ĐIỀN] | open |")
sec += ["", "## 5. Bảng triage dependency",
        "### Backend (`npm audit`, tất cả)", tb_be, f"\nExit `--fail-on high`: {rc_be}. Production-only (`npm audit --omit=dev`): 0 lỗ hổng.", "",
        "### Frontend", tb_fe, f"\nExit `--fail-on high`: {rc_fe} (3 High).", fe_triage, "",
        "## 6. Bằng chứng test auth/IDOR",
        "- `tests/api/auth_api.test.ts`: AUTH-API-002/003/005/006, AUTH-SEC-001…008 (khóa tài khoản, giới hạn tốc độ, refresh dùng một lần, token hết hạn/thu hồi/ký sai).",
        "- `tests/api/leave_api.test.ts`: LEAVE2-SEC-001/002/004 (IDOR, phạm vi danh sách, người duyệt không liên quan).",
        "- `tests/api/appr_api.test.ts`: APPR-SEC-001/002/003, APPR2-SEC-001, APPR2-BIZ-001…003 (quyền duyệt, ủy quyền theo ngày). **Chưa có test cho ca tự duyệt (BUG-001)** — phải thêm khi sửa.",
        "- `tests/api/report_api.test.ts`: REPORT-SEC-001/002/003 (chỉ hr, 401, vô hiệu công thức CSV).", "",
        "## 7. Điểm tốt đã xác nhận"] + [f"- {p[0]} (`{p[1]}`)" for p in PRAISES[:4]] + [
        "", "## 8. Việc còn lại / Giới hạn",
        "- Kiểm lại V1, V5, V6 khi có lớp PostgreSQL (BUG-004).",
        "- Chưa kiểm: cấu hình proxy/TLS/cookie `Secure` trên môi trường thật; CSRF với trình duyệt thật ngoài quy tắc header tùy biến; quét secret trong lịch sử git bằng công cụ.",
        "- Findings Medium/Low của review mã không thuộc 10 vector không lặp lại ở đây."]
out("C4_trailofbits-security-skills", f"Security_Audit_Report_{PR}.md").write_text("\n".join(sec) + "\n", encoding="utf-8")

# ---- known_issues + gate ----------------------------------------------------------------------------------
ctxp = WS / "project-context.json"
existing = {k["id"] for k in json.loads(ctxp.read_text(encoding="utf-8")).get("known_issues", [])}
for f in BUGS:
    if f[9] in existing:
        continue
    item = {"id": f[9], "title": f[4][:140], "severity": f[1], "status": "open", "found_in": f"C3/C4 {PR}", "ref": f[0]}
    tmp = WS / f".{f[9]}.json"
    tmp.write_text(json.dumps(item, ensure_ascii=False), encoding="utf-8")
    r = sh([SK / "a1-project-init/scripts/update_context.py", WS, "append", "known_issues", "--file", tmp])
    tmp.unlink(missing_ok=True)
    assert r.returncode == 0, r.stdout + r.stderr
gate = sh([SK / "a1-project-init/scripts/check_gate.py", WS, "go-live"])
print(gate.stdout.strip()[-400:])
assert gate.returncode != 0, "known_issues có High mở thì cổng go-live phải CHẶN"

print(f"\nOK Giai đoạn 3: C0–C4 đã sinh vào {DOCS}")
print(f"   jest {tst['passed']}/{tst['total']} · coverage {covt['lines']}%/{covt['branches']}% · findings C:{cnt['Critical']} H:{cnt['High']} M:{cnt['Medium']} L:{cnt['Low']}")
