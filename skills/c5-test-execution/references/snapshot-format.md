# Định dạng snapshot kết quả test (`<Project>_test_results_<PHASE>_<YYYYMMDD>.json`)

Snapshot là **nguồn sự thật** của một lần chạy/tổng hợp phase. Excel tracker và báo cáo Word phải đọc từ đây (hoặc sinh ra từ đây) — không nhập tay hai nơi.

Lưu tại `docs/C5_test-execution/`. Mỗi lần chạy một file mới (không ghi đè).

## Cấu trúc tối thiểu

```json
{
  "phase": "UT",
  "run_at": "2026-11-11T10:00:00+09:00",
  "environment": "CI / Node 20 / Ubuntu 22.04",
  "tests": [
    { "id": "AUTH-API-001", "module": "Auth", "viewpoint": "Security",
      "result": "pass", "bug_id": "", "duration_ms": 120, "evidence": "ci-run#123" }
  ],
  "defects": [
    { "id": "BUG-003", "title": "...", "severity": "High", "status": "closed",
      "found_in": "UT", "test_ids": ["AUTH-API-004"],
      "regression_test_id": "AUTH-API-004",
      "regression_impact_scope": "auth/login.service.ts, auth/refresh.ts",
      "required_regression_suites": "auth_api, session",
      "verified_commit": "9f3c2a1" }
  ],
  "coverage": { "line": 91.2, "branch": 74.0, "source": "coverage/coverage-summary.json" }
}
```

## Quy tắc giá trị

| Trường | Giá trị hợp lệ | Ghi chú |
|---|---|---|
| `tests[].result` | `pass` · `fail` · `blocked` · `na` · `notrun` | `notrun` = chưa chạy. Không có kết quả thì KHÔNG được ghi `pass`. |
| `tests[].id` | theo `<MODULE>-<TYPE>-<NNN>` của Test Plan (A8) | Giữ nguyên ID của Test Plan; test tự sinh (c2) dùng cùng ID. |
| `tests[].bug_id` | `BUG-<NNN>` | Bắt buộc khi `fail` (theo nguyên tắc: mọi fail có bug). |
| `defects[].severity` | `Critical` · `High` · `Medium` · `Low` | Thang chuẩn `pipeline.md` §1. |
| `defects[].status` | `open` · `in progress` · `fixed` · `retest` · `verified` · `closed` · `wontfix` | Gate coi mọi trạng thái trừ `verified`/`closed`/`wontfix` là **còn mở** — `fixed` chưa retest vẫn chặn. |
| `defects[]` regression | `regression_test_id`, `regression_impact_scope`, `required_regression_suites`, `verified_commit` | Bắt buộc khi `closed`/`verified`; thiếu → UNVERIFIED_FIX. `regression_impact_scope` có thể để trống nếu truyền `--repo` (script điền từ `git show --name-only <commit>`). |
| `coverage` | `line`, `branch` (%) | Nguồn: Jest `coverage-summary.json` (`json-summary`), pytest-cov. |

## Đồng bộ sang tracker (khi có openpyxl)

- Sheet UT/IT/ST/UAT ← `tests[]` (cột: Test ID, Mô tả, Phase, Requirement ref, Người thực thi, Ngày, Kết quả, Bug ID, Evidence, Ghi chú).
- Sheet Defects ← `defects[]`.
- Sheet Dashboard ← kết quả `scripts/test_metrics.py --format json` (không tự tính khác đi).

## Cập nhật context

Bug Critical/High còn mở đưa vào `known_issues[]` qua `update_context.py` (xem SKILL, mục "Ghi context"). Không sửa tay `project-context.json`.
