# E2E — chuỗi thử nghiệm đầu-cuối trên dự án MẪU

Dự án mẫu: **勤怠承認システム（サンプル）**, khách **架空** (không liên quan khách thật). Dùng để kiểm tra bộ skill sinh đúng tài liệu trước khi dùng cho dự án thật.

## Chạy

```bash
python skills/evals/e2e/build_all.py          # output: $E2E_WS (mặc định: thư mục tạm)
E2E_WS=./out python skills/evals/e2e/build_all.py   # chọn thư mục đầu ra
```

Yêu cầu: `openpyxl`, `python-docx`, `pglast` (kiểm SQL, tùy chọn), `formulas` (tính lại công thức, tùy chọn). Cài bằng `python -m pip install openpyxl python-docx`. **Không** chạy `python -I` (user-site bị bỏ qua).

## Chuỗi chạy (mỗi bước gọi script THẬT của repo)

| Bước | Output | Script / bộ dựng |
|---|---|---|
| A1 | `project-context.json` | `validate_context.py` |
| A2 | Requirement Specification + QA Tracker | `xlsx_build.py`, `check_gate.py` (đếm P1 mở) |
| A4 | API Design (xlsx), `api_spec.json`, OpenAPI, Postman | `xlsx_build.py`, `gen_openapi.py`, `gen_postman.py` |
| A5 | DB Design (xlsx), migration SQL, ERD, FK graph | `xlsx_build.py`, `health_check.py`, `check_circular_fk.py` |
| A6 | Estimate (công thức tham chiếu sheet Assumptions) | `xlsx_build.py` |
| A8 | Test Plan (10 loại test, 14 cột, ma trận phủ, dashboard) | `xlsx_build.py` |
| A9 | Project Timeline (xlsx, ICS, JSON) | `timeline_calc.py`, `xlsx_build.py` |
| B2 | 基本設計書 (docx) | `docx_build.py` |
| B3 | 詳細設計書 (docx) + CRUD Matrix | `docx_build.py`, `check_crud_coverage.py` |
| C5 | Snapshot ST × 2 lần (lần 1 bị chặn, lần 2 đạt) | `test_metrics.py` |
| C6 | Sprint 2 review | `sprint_metrics.py` |
| C7 | CR-001 impact | `cr_impact.py` |
| C8 | Smoke test trên stub staging | `smoke_test_runner.py` |

## Kiểm tra tự động (run_evals T14–T17)

- Mọi xlsx phải `xlsx_verify.py --client-facing` ĐẠT (0 FAIL).
- Ma trận CRUD phủ 100% bảng.
- Cổng chất lượng: snapshot lần 1 → NOT QUALIFIED (exit 1), lần 2 → QUALIFIED (exit 0).

## Giới hạn đã biết

- Chưa render hình ảnh (không có LibreOffice/Excel). Kiểm tra ở mức cấu trúc và công thức.
- Sơ đồ Mermaid không được render thành hình (không có `mmdc`); tài liệu Word dùng bảng thay thế.
- Mẫu chưa có bảng "API詳細" (bóc tách từng tham số) — A4 yêu cầu, sẽ bổ sung.
- Stub staging trong C8 chỉ mô phỏng hợp đồng API, không phải hệ thống thật.

## Giai đoạn 3 — C0, C1, C2, C3, C4 trên mã nguồn thật

`phase3_code.py` cần Node ≥ 20 và mã mẫu `sample_app/` (backend NestJS, frontend Next.js; dự án 勤怠承認 khớp spec A4/B3/A8). Không nằm trong `run_evals.py` vì phải `npm install`.

```bash
cp -r skills/evals/e2e/sample_app /tmp/att/app && cd /tmp/att/app
git init -b main && git add backend/package.json backend/tsconfig*.json backend/eslint.config.mjs backend/.prettierrc backend/.gitignore \
  && git commit -m scaffold && git checkout -b feature/leave-approval && git add -A && git commit -m "feat: leave approval API"
(cd backend && npm install && npm run build)
(cd backend && npx jest --coverage --json --outputFile=tests/results/all.results.json)
for m in auth leave appr report; do (cd backend && npx jest tests/api/${m}_api.test.ts --json --outputFile=tests/results/${m}_api.results.json); done
(cd frontend && npm install && npx next build)
# npm audit --json > $E2E_WS/docs/C4_trailofbits-security-skills/npm_audit_{backend,frontend}.json (sau khi chạy build_all.py)
E2E_WS=<ws> E2E_APP=/tmp/att/app PYTHONUTF8=1 python -B skills/evals/e2e/phase3_code.py
```

Kết quả thực đã đo (2026-11-12): 125/126 test pass (1 todo vì A4 thiếu endpoint submit), coverage 99% dòng / 90.9% nhánh, kiểm tra đột biến 4/4, E2E Playwright (Edge, `E2E_CHANNEL=msedge`, tài khoản kiểm thử do bên chạy seed) 7/7.

Giới hạn: backend dùng repository trong bộ nhớ (không PostgreSQL); `phase3_code.py` đọc các kết luận review/audit đã kiểm chứng bằng PoC (FINDINGS) và tra lại file:dòng bằng regex — nếu sửa mã mẫu để khắc phục các lỗi đó thì phải cập nhật FINDINGS. Chưa chạy: semgrep/gitleaks, kiểm tra hiển thị màn Delegation/CSV trên trình duyệt.
