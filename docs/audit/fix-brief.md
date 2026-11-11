# Brief sửa lỗi Giai đoạn 1 — áp dụng cho MỌI agent sửa (2026-11-06)

Người dùng đã DUYỆT phạm vi sửa: gói S (script), C (hợp đồng/số liệu), G (bổ sung nội dung skill), D (gỡ nội dung dự án mẫu), O (trigger chồng chéo). Bảng gộp: `docs/audit/2026-11-06-phase1-findings.md`. Mỗi agent sửa phát hiện CỦA NHÓM MÌNH (ID gốc trong báo cáo bạn đã viết).

## Đã làm xong ở lõi (KHÔNG làm lại, KHÔNG sửa các file này)
- `skills/a1-project-init/scripts/{check_gate,update_context,validate_context,compute_status}.py`, `assets/context-schema.json`, `assets/skills-manifest.json`, `references/{pipeline,context-protocol,i18n-policy,excel-style}.md`. Skill trỏ về chúng, không chép lại.
- `pipeline.md` mục **"Quy ước dùng chung"** là luật mới — ĐỌC TRƯỚC KHI SỬA: thang severity Critical/High/Medium/Low + bảng ánh xạ, hợp đồng API (`{data,meta}` / `{error:{code,message,details,requestId}}`, mã `ERR-<DOMAIN>-<NNN>`), chuỗi ID truy vết (`FEAT→FN→SCR→ITM`, `BUG-/CR-/ACT-/DEC-/INC-`), thư mục `docs/<MÃ BƯỚC>_<tên-skill-bỏ-tiền-tố>/`, tên file `_v1` ngay từ bản đầu, thứ tự C5→C8→D1→D2→D3.
- `update_context.py` có thêm lệnh `patch <mảng> <id> '<json>'`, `--file <json>`, stdin `-`; mảng object CHỈ nhận JSON object. `check_gate.py` exit 3 = không kiểm được (không coi là "đã qua"); bug `Fixed` chưa `verified`/`closed` vẫn tính là mở. Schema có `settings.quality_gates`, `release{}`, `team[].side` (vendor|client), `links.*` (chuỗi), `known_issues[]`/`change_requests[]` có schema item.
- 5 skill claude-mem đã xóa (handoff, learn-codebase, mem-search, smart-explore, timeline-report). Bộ còn 35 skill = 33 trong manifest + `ui-ux-pro-max` + `product-teardown`. Nếu skill của bạn nhắc tới 5 skill đó / claude-mem / Playwright MCP → gỡ hoặc thay bằng cơ chế còn tồn tại.

## Luật làm việc
1. **Phạm vi file**: chỉ sửa trong thư mục skill của nhóm bạn (và file được giao rõ). KHÔNG sửa: manifest, pipeline, context-protocol, schema, 4 script lõi nói trên, README.md, AGENTS.md, rules/, CHANGELOG, `.github/`, và đặc biệt KHÔNG đụng mục `## Self-Improvement Loop` (cuối SKILL.md) — Giai đoạn 3 sẽ thay hàng loạt. Cần đổi file dùng chung → ghi vào mục "Đề nghị sửa file chung" của báo cáo cuối, tôi sẽ làm.
2. **KHÔNG** git commit / push / tạo nhánh. **KHÔNG** bump version (tôi bump theo từng skill đã đổi ở cuối). **KHÔNG** xóa skill, **KHÔNG** tạo skill mới, **KHÔNG** đổi tên thư mục skill.
3. **Giữ**: frontmatter hợp lệ (name khớp thư mục, `description` ≤ 700 ký tự, trigger không chồng), mục Workflow Integration trỏ `pipeline.md` (không chép lại pipeline), mỗi SKILL.md ≤ 500 dòng — nội dung dài/ví dụ/domain chuyển sang `references/*.md` hoặc `assets/` và nạp theo điều kiện.
4. **Nội dung dự án mẫu** (ứng dụng ghi chú, canteen/FPT, 電帳法/Zengin, `Personal_Vault_*`, số liệu mẫu "100%/<50ms/0 Defect"…): KHÔNG để trong phần "bắt buộc". Viết lại thành quy tắc theo DỮ LIỆU (đọc từ context / tài liệu bước trước); ví dụ mẫu chuyển sang `references/example-*.md` ghi rõ "chỉ minh họa"; thiếu dữ liệu → `[CẦN ĐIỀN]`, không bịa.
5. **Tài liệu gửi khách**: cấm lộ mã bước nội bộ/nhãn nội bộ (Gate A, `/a7-…`), cấm số liệu không có nguồn, cấm tên khách/email/đường dẫn cá nhân/token trong skill.
6. **Script**: Windows-safe — `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` đầu file, `pathlib`, `open(..., encoding="utf-8")`, không `/tmp`, không lệnh POSIX-only, không `python3` cứng trong ví dụ mới (ghi `python`). Thư viện ngoài (openpyxl, python-docx…) phải được kiểm `ImportError` và báo lỗi rõ. Ghi chú: trong shell của người dùng `python -I` KHÔNG thấy openpyxl (user-site) và console mặc định cp932. Mỗi script sửa/tạo phải `compile()` được và CHẠY THỬ trên dữ liệu mẫu (dựng ở thư mục tạm, KHÔNG ghi vào repo; dùng `python -B` để khỏi sinh `__pycache__`).
7. **Giữ kiểu xuống dòng** của file (nhiều file CRLF): ưu tiên công cụ Edit; nếu viết lại bằng Python thì đọc bytes, nhận diện CRLF và ghi lại đúng kiểu.
8. Ưu tiên theo mức: HIGH → MED → LOW. Làm xong thì dừng ở điểm ngắt sạch; không để file dở dang. Mục không làm được/không nên làm → nêu lý do trong báo cáo, không lờ đi.
9. Cuối cùng chạy `python -B -I skills/x6-skill-doctor/scripts/skill_doctor.py skills` và chỉ xét FAIL/WARN thuộc skill của bạn (agent khác đang sửa song song).

## Báo cáo cuối (≤ 45 dòng, tiếng Việt)
(a) Đã sửa: theo ID gốc → file đã đổi, 1 dòng/ID. (b) Chưa sửa + lý do. (c) Đề nghị sửa file chung (manifest/DEPS/pipeline/…) cho lõi. (d) Lệnh kiểm đã chạy + kết quả thật.
