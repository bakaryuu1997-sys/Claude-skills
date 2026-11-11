# PR: <TICKET/SPRINT> — <tiêu đề ngắn>

> Lưu tại `docs/C1_dev-implement/PR_<TICKET_OR_SPRINT>.md`. Viết bằng ngôn ngữ `settings.languages.code` (mặc định en) — không ghi mã bước nội bộ của pipeline (`A4`, `B3`, `C1`…): dùng tên tài liệu thật (API Design, Detail Design…).

## 1. Summary
- Mục tiêu / phạm vi (1–3 dòng). Mode: SCAFFOLD | FEATURE | BUGFIX. `Fixes: BUG-xxx` (nếu BUGFIX) + root cause 2 câu.
- Assumptions (bắt buộc nếu code không đủ spec): `[CẦN ĐIỀN]` hoặc liệt kê.

## 2. Directory Tree
(Cây file thêm/sửa, 1 dòng mô tả mỗi file.)

## 3. Spec Adherence Matrix
| Endpoint / Rule | Spec (API Design / Detail Design / DB Design) | Code (file:dòng) | Khớp? |
|---|---|---|---|
| `POST /…` | status, DTO, error code `ERR-<DOMAIN>-<NNN>` | `src/…` | ✅/❌ + lý do |

## 4. Test Verification & Coverage
- Lệnh đã chạy + kết quả thật (pass/fail, số test). Coverage line/branch so với `settings.quality_gates` (`ut_coverage_line`, `ut_coverage_branch`).
- Happy path + ≥ 2 unhappy path mỗi endpoint; test hồi quy cho BUGFIX (đỏ trước fix, xanh sau fix).

## 5. Security & Guardrails Checklist
- [ ] Không secret trong code/config · [ ] Validation theo schema · [ ] AuthN/AuthZ (ownership) · [ ] Không log dữ liệu nhạy cảm · [ ] Dependency mới đã audit
- [ ] Dockerfile non-root + HEALTHCHECK (nếu đụng hạ tầng) · [ ] Config fail-fast ở production

## 6. Local Run Guide
(Lệnh cài đặt, env cần thiết từ `.env.example`, migrate, chạy, chạy test.)

## 7. Reviewer Notes
(Điểm khó, quyết định thiết kế, rủi ro, việc để PR sau.)
