# PIPELINE DỰ ÁN — NGUỒN SỰ THẬT DUY NHẤT (v3.17.0)

> File này là nơi DUY NHẤT định nghĩa thứ tự pipeline, hằng số chung và hợp đồng I/O giữa các skill.
> Mọi skill chỉ ghi "bước hiện tại + bước kế tiếp" và trỏ về đây. Nếu bất kỳ tài liệu/skill nào mô tả
> thứ tự khác với file này → **file này thắng**. Khi thêm skill mới: thêm vào đây + `assets/skills-manifest.json`, KHÔNG sửa các skill còn lại.

## Sơ đồ chuẩn (đánh số theo GIAI ĐOẠN — chèn thêm bước không phá số cũ)

```
GIAI ĐOẠN A — CHUẨN BỊ / PRE-SALE (chạy một lần)
  A1  /a1-project-init            ← CHẠY ĐẦU TIÊN, tạo project-context.json
  A2  /a2-requirement-analysis    ← làm rõ scope, Q&A P1/P2/P3
  A3  /a3-prototype-ui            ← (tùy chọn) demo UI, chạy song song lúc chờ trả lời Q&A
  A4  /a4-api-design ∥ /a5-db-design ← chạy song song; api-design trước thì tốt hơn (db đọc "DB Tables Affected")
  A5  /a5-db-design
  A6  /a6-estimate                ← GATE: >3 câu P1 chưa trả lời → dừng, cảnh báo sai >40%
  A7  /a7-estimate-template-fill  ← (tùy chọn) khi khách có template 見積書 riêng
  A8  /a8-test-plan
  A9  /a9-project-timeline

GIAI ĐOẠN B — HỢP ĐỒNG & KHỞI ĐỘNG (B0 tạo hồ sơ để ký hợp đồng; B1–B3 chạy sau khi hợp đồng được ký)
  B0  /b0-proposal-sow            ← Proposal kỹ thuật & SOW ký kết hợp đồng chốt phạm vi
  B1  /b1-project-kickoff         ← GATE: >3 câu P1 mở → hoãn kickoff
  B2  /b2-basic-design            ← khách ký duyệt TRƯỚC khi vào B3
  B3  /b3-detail-design           ← BẮT BUỘC có api-design + db-design (cập nhật) trước

GIAI ĐOẠN C — VẬN HÀNH (lặp lại trong suốt dự án)
  C0  /c0-frontend-dev            ← lập trình ứng dụng Web Frontend production (Next.js/React/Tailwind/shadcn), kết nối API trực tiếp (Zero-Mock)
  C1  /c1-dev-implement           ← dev viết code theo thiết kế (scaffold/feature/bugfix — mỗi task, TRƯỚC C3)
  C2  /c2-api-test-suite-generator← tự động sinh test suite API thực thi (8 mã HTTP + mock fixtures)
  C3  /c3-code-review             ← mỗi PR
  C4  /c4-trailofbits-security-skills ← kiểm toán bảo mật backend chuyên sâu (IDOR, JWT, injection, leak)
  C5  /c5-test-execution          ← mỗi phase test (UT/IT/ST/UAT)
  C6  /c6-sprint-review           ← cuối mỗi sprint
  C7  /c7-change-request          ← bất kỳ lúc nào scope thay đổi
  C8  /c8-release-deployment      ← kế hoạch phát hành, deploy production, smoke test & rollback

GIAI ĐOẠN D — KẾT THÚC & BÀN GIAO (thứ tự chốt: C5 chạy UAT → C8 phát hành → D1 → D2 → D3)
  D1  /d1-handover-doc            ← hồ sơ kỹ thuật & runbook vận hành; soạn sau C8, cập nhật sau go-live
  D2  /d2-uat-acceptance          ← nghiệm thu chính thức (検収) SAU khi bàn giao D1, ký Certificate giải ngân
  D3  /d3-user-guide-manual       ← tài liệu HDSD cho end-user và admin guide vận hành

GIAI ĐOẠN X — CROSS-CUTTING (chạy bất kỳ lúc nào, không thuộc chuỗi tuần tự)
  X1  /x1-acquire-codebase-knowledge ← khảo sát kiến trúc repo 4 tầng bằng Serena LSP trước khi code
  X2  /x2-project-architecture    ← HTML trực quan hóa toàn bộ kiến trúc + trạng thái tài liệu (tốt nhất sau A4; cập nhật sau mỗi thay đổi lớn)
  X3  /x3-project-status          ← dashboard hiện trạng trong chat: đang ở đâu, thiếu gì, gate nào chặn
  X4  /x4-meeting-minutes         ← biên bản họp + đổ ngược: câu hỏi mở → QA_Tracker, scope đổi → /c7-change-request
  X5  /x5-coding-standards        ← quy chuẩn kỹ thuật nội bộ, conventional commits, PR & self-improvement
  X6  /x6-skill-doctor            ← meta: lint chính bộ skill (cho người bảo trì, không thuộc pipeline dự án)
  X7  /x7-presentation-deck       ← tạo slide thuyết trình chuyên nghiệp (PowerPoint pptx / HTML Marp)
```

Ánh xạ số cũ sang chuẩn mới: A0→A1, A1→A2, A2→A3, A3(api)→A4, A3(db)→A5, A4→A6, A4b→A7, A5→A8, A6→A9, C0→C1, C0b→C2, C1→C3, C1b→C4, C2→C5, C3→C6, C4→C7, X0→X1, X1→X2, X2→X3, X3→X6.

## Quy ước dùng chung — NGUỒN DUY NHẤT (skill chỉ trỏ về đây, KHÔNG định nghĩa lại)

### 1. Thang severity chuẩn: `Critical` > `High` > `Medium` > `Low`

| Nguồn | Ánh xạ về thang chuẩn |
|---|---|
| c3 code review | BLOCKER→Critical · CRITICAL→High · MAJOR→Medium · MINOR→Low |
| c4 security audit | BLOCKER→Critical · CRITICAL→High · MEDIUM→Medium · LOW→Low |
| c6 sprint / backlog | P1→Critical · P2→High · P3→Medium · P4→Low |
| d1 sự cố vận hành | P1→Critical · P2→High · P3→Medium |
| d2 UAT | Sev1→Critical · Sev2→High · Sev3→Medium · Sev4→Low |

- Verdict: còn **Critical hoặc High mở** ⇒ chặn merge/release/nghiệm thu (đếm bằng `check_gate.py`). Medium ⇒ sửa trước release kế tiếp hoặc ghi `known_issues[]`. Low ⇒ backlog.
- Trạng thái bug (`known_issues[].status`): `open → in progress → fixed → retest → verified → closed` (+ `wontfix`, `reopened`). Gate coi MỌI trạng thái trừ `verified`/`closed`/`wontfix` là **còn mở** (Fixed chưa retest vẫn chặn).
- `P1/P2/P3` của Q&A (A2) là **mức ưu tiên câu hỏi**, không phải severity. Trạng thái câu hỏi chuẩn: `Open` / `Answered`.

### 2. Hợp đồng API dùng chung (a4 là nguồn; c0, c1, c2, c3 chỉ trỏ về đây)

- Thành công: `{ "data": <payload>, "meta": { … } }` (`meta` tùy chọn: phân trang, requestId).
- Lỗi: `{ "error": { "code": "ERR-<DOMAIN>-<NNN>", "message": "…", "details": [ { "field": "…", "issue": "…" } ], "requestId": "…" } }` — `details`/`requestId` tùy chọn. HTTP status đúng ngữ nghĩa (400 validation, 401, 403, 404, 409, 429, 5xx).
- Mã lỗi `ERR-<DOMAIN>-<NNN>` (vd `ERR-AUTH-001`, `ERR-VAL-001`, `ERR-SYS-001`). Nguồn thật là **Error Map của b3 / code của dự án** — test và FE đọc từ đó, không tự bịa mã.

### 3. Chuỗi ID truy vết (đứt chuỗi = không truy vết được)

`FEAT-<MODULE>-<NN>` (A2 Functional Scope) → `FN-<NN>` (B2 sheet `Function_List`, cột *FEAT ref*) → `SCR-<NN>` (B2 `Screen_List`, cột *Prototype id* khớp slug A3) → `ITM-<SCR>-<NN>` (B2 `Screen_Items`) → B3 tham chiếu FN/SCR/ITM.
Test case (A8): `<MODULE>-<TYPE>-<NNN>`, cột *Requirement Ref* = ID `FEAT-…`. Khác: `BUG-<NNN>`, `CR-<NNN>`, `ACT-<NN>`, `DEC-<NN>`, `INC-<NN>` (D1 Runbook), mốc `M1..MN`.

### 4. Thư mục xuất file

`<workspace_folder>/docs/<MÃ BƯỚC>_<tên-skill-bỏ-tiền-tố>/` — ví dụ `docs/A2_requirement-analysis/`, `docs/C4_trailofbits-security-skills/`, `docs/D2_uat-acceptance/`. Skill nào sinh file PHẢI ghi đúng thư mục này (chi tiết: `context-protocol.md` §7). Tài liệu sinh lại nhiều lần đặt tên `…_v[N]` kể cả bản đầu (`_v1`); skill chạy mỗi PR/sprint thêm `_PR<id>` / `_Sprint<N>` vào tên để không ghi đè lịch sử.

### 5. Định dạng & ngôn ngữ

Excel: `excel-style.md` (màu, font, freeze, công thức thay cho số cứng). Ngôn ngữ deliverable + font tiếng Nhật/Việt: `i18n-policy.md`. Số liệu trong tài liệu gửi khách phải trích từ file/context thật; không có nguồn thì bỏ khối đó (cấm số mẫu "100%", "<50ms"…).

## Hợp đồng I/O giữa các skill

| Skill | Input chính (từ đâu) | Output chính (cho ai) |
|---|---|---|
| project-init | người dùng | project-context.json → MỌI skill |
| requirement-analysis | tài liệu khách / folder | *_Requirement_Specification.xlsx (5 sheet, có Functional Scope với ID `FEAT-…`), *_QA_Tracker.xlsx (+ `*_Requirement_Analysis.docx` tùy chọn) → A3, A4, A8, B2, gate A6/B1 |
| prototype-ui | Functional Scope (mục 3 của A2) | *_Prototype_v[N].html → B2, A4, A6 |
| api-design | scope + roles (A2), screens (A3) | *_API_Design.xlsx (cột DB Tables Affected → db-design; Test Cases/Errors → test-plan), *_api_spec.json, Postman, OpenAPI → B3 THAM CHIẾU |
| db-design | DB Tables Affected (api-design) | *_DB_Design.xlsx, *_migration.sql, *_ERD.md → B3, A8 |
| estimate | A4 outputs + A5 outputs + A3 screens | *_Estimate.xlsx (Role Breakdown → A9); ghi estimates.* vào context |
| estimate-template-fill | cột Dev của estimate | file 見積書 đã điền → gửi khách |
| test-plan | api-design (Test Cases/Errors), db-design (schema), A2 (Q&A ref) | *_Test_Plan.xlsx → C5, A9 |
| project-timeline | estimate (BẮT BUỘC), test-plan | *_Project_Timeline.xlsx, .ics → B1, C6; ghi current_sprint, capacity vào context |
| proposal-sow | A2 + A4 + A5 + A6 + A9 outputs | Proposal.docx, SOW.docx → ký kết hợp đồng chốt phạm vi (tiền đề B1) |
| project-kickoff | A2 + A6 + A9 outputs | Deck.pptx, Charter.docx, Workbook.xlsx, Minutes → B2 |
| basic-design | A2, A3, api-design | Basic_Design.docx + Workbook.xlsx + Diagrams.md → B3 |
| detail-design | B2 + api-design + db-design | Detail_Design.docx + Workbook + Diagrams → coding, C3 đối chiếu, A8 bổ sung |
| frontend-dev | B2 screens + A4 API DTO + A3 UI layout + tech_stack | frontend/ app code + FE_IMPLEMENTATION_REPORT.md → /c3-code-review, /c5-test-execution (E2E do c0 tự sinh theo mẫu) |
| dev-implement | detail-design + api-design + db-design (FEATURE) · bug entry test-execution (BUGFIX) · tech_stack (SCAFFOLD) | code + unit test + PR description → /c3-code-review (bắt buộc trước merge) |
| api-test-suite-generator | api-design + detail-design + routes | tests/api/*_api.test.ts + fixtures → /c3-code-review, /c5-test-execution |
| code-review | diff/PR + spec (api/db design) | Code_Review_Report.xlsx + Report.md (kèm chat) → merge/fix |
| trailofbits-security-skills | code PR / routes / middlewares | Security_Audit_Report.md; finding Critical/High → `known_issues[]` → /c1-dev-implement (sửa bug), /c3-code-review |
| test-execution | test-plan + kết quả chạy | Test_Execution.xlsx + Test_Report.docx; ghi known_issues[] → D1 |
| sprint-review | sprint plan (A9) + actual | Sprint[N]_Review.xlsx + Sprint_Log.xlsx (append); current_sprint++ |
| change-request | mô tả CR + estimate gốc + sprint hiện tại | CR xlsx + summary md; append change_requests[]; APPROVED → cập nhật A9/A4/A5 |
| release-deployment | C1 + C3 + C4 + C5 outputs + `known_issues[]` (chạy `check_gate.py`) | Release_Plan_v[N].docx, Deployment_Checklist.xlsx, Smoke_Test_Runbook.md; ghi `release{}` vào context → D1 |
| handover-doc | toàn bộ pipeline + C8 (Release_Plan, Smoke_Test_Runbook) + C4/C5 reports + known_issues[] | Handover.docx + Handover_Workbook.xlsx + Runbook.md (mỗi sự cố có ID `INC-<NN>`); ghi links.production_url/staging_url → D2, D3 |
| uat-acceptance | D1 hồ sơ + A8 UAT cases + C5 test results + B0 SOW (`Milestone_Deliverables`) + `known_issues[]` (chạy `check_gate.py`) | *_UAT_Acceptance_Certificate.docx, *_UAT_SignOff_Workbook.xlsx (Punch List là sheet trong workbook) → khách hàng ký |
| user-guide-manual | B2 screens + A3 flows + D1 Runbook (`INC-xx`) + D2 UAT_SignOff_Workbook | *_User_Manual_EndUser.docx, *_Admin_Guide.docx, *_Quick_Start_Guide.md → bàn giao người dùng cuối & admin |
| acquire-codebase-knowledge | mã nguồn repo + Serena LSP | Architecture_Survey.md → /c1-dev-implement, /x2-project-architecture |
| project-architecture | context + output MỌI skill đã chạy | *_Architecture_v[N].html (view tổng hợp chỉ-đọc); ghi links.architecture_file |
| project-status | manifest patterns + activity_log + files | dashboard trong chat (đọc-only, không tạo file, không ghi context) |
| meeting-minutes | notes/transcript họp | biên bản Minutes.docx + Minutes.xlsx + md; câu hỏi mở → QA_Tracker; scope change → cảnh báo /c7-change-request |
| coding-standards | project-context.json (tech_stack) | ENGINEERING_STANDARDS.md → mọi skill thực thi |
| skill-doctor | thư mục skills + manifest | báo cáo lint PASS/WARN/FAIL trong chat |
| presentation-deck | bất kỳ tài liệu nào cần trình chiếu (số liệu PHẢI trích từ file thật) | Deck.pptx (16:9) hoặc HTML slide → khách hàng, BOD, team |

## Hằng số chung — NGUỒN DUY NHẤT là `project-context.json → settings`

| Hằng số | Key | Mặc định | Ai dùng |
|---|---|---|---|
| MD / Person-Month | `settings.md_per_person_month` | 22 | estimate, estimate-template-fill, change-request — **PHẢI cùng một giá trị**, không skill nào tự đặt số riêng |
| Buffer % | `settings.buffer_percent` | 15 | estimate, change-request |
| Sprint duration | `settings.sprint_duration_weeks` | 2 | project-timeline, sprint-review |
| Capacity/role/sprint | `team[].md_per_sprint` | BE/FE/Mobile 8 · QA 7 · PM 5 · DevOps 6 | project-timeline, sprint-review, change-request |
| Ngôn ngữ deliverable | `settings.languages` | client_facing=vi · internal=vi · code=en — quy tắc đầy đủ: `references/i18n-policy.md` | mọi skill sinh file |
| Quality gates | `settings.quality_gates` | `ut_pass_rate` 95 · `ut_coverage_line` 80 · `ut_coverage_branch` 70 · `it_pass_rate` 95 · `st_pass_rate` 98 · `open_critical_high_max` 0 (schema: `context-schema.json`) | c1, c5, c8, d2 — chỉ đọc từ context, không tự đặt ngưỡng |

## Placeholder chuẩn (mọi skill dùng — KHÔNG định nghĩa lại)

- `<skills_dir>` = thư mục cha chứa toàn bộ skill folder (thư mục có `a1-project-init/`, `a4-api-design/`…). Xác định từ vị trí SKILL.md đang được nạp; trong shell dùng đường dẫn tuyệt đối tương ứng của môi trường đang chạy.
- `<workspace_folder>` = thư mục làm việc người dùng đã chọn — nơi chứa `project-context.json` và mọi deliverable.

## Scripts dùng chung (nguồn logic — KHÔNG mô tả lại thuật toán bằng văn xuôi trong skill)

| Script | Việc | Ai gọi |
|---|---|---|
| `a1-project-init/scripts/load_context.py` | đọc context + `cget()` | mọi skill |
| `a1-project-init/scripts/update_context.py` | GHI context (atomic + lock + validate); lệnh `set`/`append`/`patch`/`restore`; PowerShell dùng `--file` hoặc stdin | mọi skill tạo/sửa file |
| `a1-project-init/scripts/check_gate.py` | đếm gate P1 / bug Critical / CR — exit 1 = chặn, exit 3 = KHÔNG kiểm được (không coi là đã qua) | estimate, project-kickoff, test-execution, release-deployment, uat-acceptance |
| `a1-project-init/scripts/compute_status.py` | quét tài liệu + staleness + gates → JSON | project-status, project-architecture |
| `a1-project-init/scripts/validate_context.py` | validate schema context | project-init, update_context |
| `a5-db-design/scripts/check_circular_fk.py` | phát hiện chu trình FK | db-design |
| `a4-api-design/scripts/gen_postman.py` | sinh Postman Collection từ api_spec.json | api-design |
| `a4-api-design/scripts/gen_openapi.py` | sinh OpenAPI YAML từ api_spec.json | api-design |
| `evals/run_evals.py` + `evals/checkers/*` | eval harness 2 tầng (xem evals/README.md) | người bảo trì skill |
| `a7-estimate-template-fill/scripts/fill_dev_estimate.py` | điền block 開発 template 見積書 | estimate-template-fill |
| `x6-skill-doctor/scripts/skill_doctor.py` + `menu/scripts/*` | lint bộ skill, sinh/kiểm menu | skill-doctor, menu |

## Quy ước kết thúc response (mọi skill — nguồn duy nhất)

Tối đa 6 dòng: `✅ Vừa xong <bước> + số liệu chính → ▶ Bước kế /<skill> — lấy gì từ output`. KHÔNG ASCII box dài.
Skill TẠO/SỬA file: append `{skill, date, outputs[]}` vào `activity_log[]` bằng `update_context.py`.
Skill đọc-only (project-status, menu, skill-doctor): KHÔNG ghi context.