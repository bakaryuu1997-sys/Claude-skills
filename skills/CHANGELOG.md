# CHANGELOG — Bộ skill quản trị dự án

## 3.5.0 — 2026-07-09
Nhóm Nice-to-have (N1/N2/N3/N5) — kết thúc toàn bộ roadmap audit.

### N1 — Decision tree sinh từ manifest
- Mỗi skill trong manifest có `intents[]` (cụm từ task tiếng Việt); `menu/scripts/match_intent.py` map mô tả task → top 3 skill (bỏ dấu, ngưỡng chống khớp rác, không đoán bừa khi ngoài phạm vi).
- menu/SKILL.md xóa bảng decision-tree hardcode — thêm skill mới chỉ khai intents trong manifest.
- skill-doctor rule **D12** (WARN): skill trong manifest thiếu intents.

### N2 — I18n policy
- `references/i18n-policy.md`: bảng doc-type → ngôn ngữ, nguồn `settings.languages` (client_facing/internal/code); thiếu → hỏi 1 lần rồi ghi vào context. Schema + project-init (Nhóm 4) + pipeline.md cập nhật tương ứng.

### N3 — Log rotation
- `update_context.py`: activity_log > 200 entry → 100 cũ nhất tự chuyển sang `project-context.archive.jsonl` (append-only) — context không phình vô hạn.

### N5 — Snapshot/Recovery (thay SQLite, có điều kiện chuyển)
- `update_context.py`: snapshot vào `.context-history/` trước MỖI lần ghi (giữ 20 bản) + lệnh `restore`.
- Quyết định SQLite HOÃN có điều kiện (ghi trong context-protocol.md): chỉ chuyển khi ≥2 agent ghi đồng thời thường xuyên hoặc context >1MB — khi đó bọc `context_store.py` cùng interface, 23 skill không phải đổi.

### Evals
- 3 test mới: T1b (rotation), T1c (snapshot/restore), T8 (match_intent đúng + từ chối task ngoài phạm vi) — tổng 12 test.

## 3.4.0 — 2026-07-09
Hoàn thành 2 hạng mục cuối của roadmap audit: H5 (eval harness) + M2 (script hóa Postman/OpenAPI).

### Added — M2
- `api-design/scripts/gen_postman.py` + `gen_openapi.py` — Postman/OpenAPI giờ là DẪN XUẤT TẤT ĐỊNH từ `*_api_spec.json` (nguồn trung gian mới, format: `api-design/references/api-spec-format.md`); cả 2 script tự verify (parse lại + đếm). CẤM viết 2 file này bằng tay.
- api-design/SKILL.md giảm 428 → 287 dòng (bỏ ~140 dòng template JSON/YAML tay).

### Added — H5
- `evals/run_evals.py` — eval TẦNG 1 tự động: 9 test cho toàn bộ lớp deterministic (update_context atomic/lock, check_gate 3 kịch bản, compute_status staleness, circular FK, gen Postman/OpenAPI golden, skill_doctor 0-FAIL, self-test checker). Exit code dùng được làm CI.
- `evals/checkers/check_xlsx.py` — checker cấu trúc Excel output: sheet/số cột/PHẢI có công thức (bắt hardcode tổng)/chuỗi cấm (bắt leak FPT/F-Pay/Lorem)/số dòng tối thiểu.
- `evals/golden/{estimate,test-plan,api-design}/` — 3 golden case TẦNG 2 (brief.md prompt chuẩn + expected_structure.json); quy trình: sửa prompt → chạy lại case → checker PASS mới được commit.
- Ghi nhận: ngay lần chạy đầu, T6 của harness đã bắt được 1 lệch version manifest thật — hệ thống hoạt động đúng thiết kế.

## 3.3.0 — 2026-07-09
Bản phát hành đồng bộ sau audit toàn hệ thống (chi tiết: `SKILLS_REVIEW_2026-07-08.md` trong workspace).

### Fixed
- **skill-doctor**: chỉ lint skill có trong manifest — hết 44 false-FAIL trên skill hệ thống (docx/pdf/pptx…); thêm rule **D11** (header "(N sheets)" phải khớp số `### Sheet` liệt kê); folder ngoài manifest trỏ pipeline.md → FAIL D08 (quên đăng ký).
- **pipeline.md**: hoàn thiện bảng Quality gates bị cụt file; bỏ hằng số "17 skill" lỗi thời; định nghĩa chính thức `<skills_dir>` / `<workspace_folder>`; thêm registry scripts dùng chung + quy ước kết thúc response (một nguồn).
- **db-design**: header "(5 sheets)" → 6. **project-timeline**: "(7 sheets)" → 8. **test-plan**: "(6 sheets)" → N + 6.
- **test-plan**: 17 cột → **14 cột** — bỏ Actual Result/Status/Bug Ticket ID; kết quả thực thi CHỈ sống ở tracker của /test-execution (xóa tình trạng 2 nguồn sự thật).
- **estimate**: khi không có context BẮT BUỘC hỏi `md_per_person_month` qua AskUserQuestion (hết nguy cơ lệch 22 vs 20 với /estimate-template-fill).
- **menu**: sửa tuyên bố "không hardcode" — decision-tree là fallback tĩnh, phải đối chiếu manifest lúc chạy; `check_menu_sync.py` bỏ phần tử trùng lặp.
- **project-init**: sửa "MỌI skill append activity_log" → chỉ skill tạo/sửa file (skill đọc-only không ghi).

### Added
- `project-init/scripts/update_context.py` — GHI context: atomic + lock + validate (thay snippet văn xuôi; mọi skill dùng script, không tự viết code ghi).
- `project-init/scripts/check_gate.py` — gate P1 / bug Critical / CR pending thi hành bằng code, exit ≠ 0 khi chặn.
- `project-init/scripts/compute_status.py` — quét tài liệu + staleness + gates, JSON; /project-status và /project-architecture dùng CHUNG (hết 2 bản cài đặt).
- `db-design/scripts/check_circular_fk.py` — thay code DFS nhúng trong prompt.
- `project-init/references/context-protocol.md` — giao thức "Bước -1" một nguồn duy nhất.
- **api-design**: thuật toán re-run merge CỐ ĐỊNH (khóa = METHOD + URL chuẩn hóa; diff NEW/CHANGED/nghi-xóa in ra TRƯỚC khi ghi; không tự deprecated).
- **basic-design / detail-design**: chế độ re-run versioning docx (`_v[N+1]`, Change History — không ghi đè bản có chỉnh sửa/chữ ký khách).
- **estimate**: quy tắc TẤT ĐỊNH chọn điểm trong khoảng tỷ lệ (CRUD → cận dưới; integration/unknown → cận trên; còn lại trung điểm, làm tròn 0.5 MD).
- Ngưỡng tự quyết thống nhất cho api-design/db-design/estimate: tác động < 3 MD và không đổi kiến trúc → tự quyết + ghi Assumption; ngược lại BẮT BUỘC hỏi.

### Changed
- Khối "Bước -1" trong mọi skill rút còn pointer 3 dòng → `context-protocol.md`; footer response rút gọn trỏ pipeline.md (giảm ~15% token nạp mỗi lần kích hoạt).
- Khử lặp Excel base style ở 6 skill (nguồn duy nhất: `excel-style.md`, skill chỉ giữ màu đặc thù).
- Toàn bộ skill bump **3.3.0** đồng bộ với manifest; xóa `__pycache__` khỏi source.

## 3.2.0 trở về trước
Xem lịch sử trong mô tả từng skill (chưa có changelog tập trung trước v3.3.0).
