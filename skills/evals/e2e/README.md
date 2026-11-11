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
