# PIPELINE DỰ ÁN — NGUỒN SỰ THẬT DUY NHẤT (v3.0.0)

> File này là nơi DUY NHẤT định nghĩa thứ tự pipeline, hằng số chung và hợp đồng I/O giữa các skill.
> Mọi skill chỉ ghi "bước hiện tại + bước kế tiếp" và trỏ về đây. Nếu bất kỳ tài liệu/skill nào mô tả
> thứ tự khác với file này → **file này thắng**. Khi thêm skill mới: thêm vào đây + `assets/skills-manifest.json`, KHÔNG sửa các skill còn lại.

## Sơ đồ chuẩn (đánh số theo GIAI ĐOẠN — chèn thêm bước không phá số cũ)

```
GIAI ĐOẠN A — CHUẨN BỊ / PRE-SALE (chạy một lần)
  A0  /project-init            ← CHẠY ĐẦU TIÊN, tạo project-context.json
  A1  /requirement-analysis    ← làm rõ scope, Q&A P1/P2/P3
  A2  /prototype-ui            ← (tùy chọn) demo UI, chạy song song lúc chờ trả lời Q&A
  A3  /api-design ∥ /db-design ← chạy song song; api-design trước thì tốt hơn (db đọc "DB Tables Affected")
  A4  /estimate                ← GATE: >3 câu P1 chưa trả lời → dừng, cảnh báo sai >40%
  A4b /estimate-template-fill  ← (tùy chọn) khi khách có template 見積書 riêng
  A5  /test-plan
  A6  /project-timeline

GIAI ĐOẠN B — KHỞI ĐỘNG (sau khi khách chốt báo giá / ký hợp đồng)
  B1  /project-kickoff         ← GATE: >3 câu P1 mở → hoãn kickoff
  B2  /basic-design            ← khách ký duyệt TRƯỚC khi vào B3
  B3  /detail-design           ← BẮT BUỘC có api-design + db-design (cập nhật) trước

GIAI ĐOẠN C — VẬN HÀNH (lặp lại trong suốt dự án)
  C0  /dev-implement           ← dev viết code theo thiết kế (scaffold/feature/bugfix — mỗi task, TRƯỚC C1)
  C0b /api-test-suite-generator← tự động sinh test suite API thực thi (8 mã HTTP + mock fixtures)
  C1  /code-review             ← mỗi PR
  C1b /trailofbits-security-skills ← kiểm toán bảo mật backend chuyên sâu (IDOR, JWT, injection, leak)
  C2  /test-execution          ← mỗi phase test (UT/IT/ST/UAT)
  C3  /sprint-review           ← cuối mỗi sprint
  C4  /change-request          ← bất kỳ lúc nào scope thay đổi

GIAI ĐOẠN D — KẾT THÚC
  D1  /handover-doc            ← sau go-live / ĐẠT UAT

GIAI ĐOẠN X — CROSS-CUTTING (chạy bất kỳ lúc nào, không thuộc chuỗi tuần tự)
  X0  /acquire-codebase-knowledge ← khảo sát kiến trúc repo 4 tầng bằng Serena LSP trước khi code
  X1  /project-architecture    ← HTML trực quan hóa toàn bộ kiến trúc + trạng thái tài liệu (tốt nhất sau A3; cập nhật sau mỗi thay đổi lớn)
  X2  /project-status          ← dashboard hiện trạng trong chat: đang ở đâu, thiếu gì, gate nào chặn
  X3  /skill-doctor            ← meta: lint chính bộ skill (cho người bảo trì, không thuộc pipeline dự án)
  X4  /meeting-minutes         ← biên bản họp + đổ ngược: câu hỏi mở → QA_Tracker, scope đổi → /change-request
  X5  /coding-standards        ← quy chuẩn kỹ thuật nội bộ, conventional commits, PR & self-improvement
```

Ánh xạ số cũ (tài liệu cũ có thể còn dùng): `[0]`=A0, `[1]`=A1, `[1.5]`=A2, `[2]`=A3(api), `[3]`=A3(db), `[4]`=A4, `[4.5]`=A4b, `[5]`=A5, `[6]`=A6, `[K]`=B1, `[BD]`=B2, `[DD]`=B3, `[7]`=C1, `[TE]`=C2, `[8]`=C3, `[9]`=C4, `[10]`=D1.

## Hợp đồng I/O giữa các skill

| Skill | Input chính (từ đâu) | Output chính (cho ai) |
|---|---|---|
| project-init | người dùng | `project-context.json` → MỌI skill |
| requirement-analysis | tài liệu khách / folder | `*_Requirement_Analysis.docx`, `*_QA_Tracker.xlsx` → A2, A3, gate A4/B1 |
| prototype-ui | Functional Scope (mục 3 của A1) | `*_Prototype_v[N].html` → B2, A3, A4 |
| api-design | scope + roles (A1), screens (A2) | `*_API_Design.xlsx` (cột DB Tables Affected → db-design; Test Cases/Errors → test-plan), Postman, OpenAPI → B3 THAM CHIẾU |
| db-design | DB Tables Affected (api-design) | `*_DB_Design.xlsx`, `*_migration.sql`, `*_ERD.md` → B3, A5 |
| estimate | A3 outputs + A2 screens | `*_Estimate.xlsx` (Role Breakdown → A6); ghi `estimates.*` vào context |
| estimate-template-fill | cột Dev của estimate | file 見積書 đã điền → gửi khách |
| test-plan | api-design (Test Cases/Errors), db-design (schema), A1 (Q&A ref) | `*_Test_Plan.xlsx` → C2, A6 |
| project-timeline | estimate (BẮT BUỘC), test-plan | `*_Project_Timeline.xlsx`, `.ics` → B1, C3; ghi `current_sprint`, capacity vào context |
| project-kickoff | A1 + A4 + A6 outputs | Deck.pptx, Charter.docx, Workbook.xlsx, Minutes → B2 |
| basic-design | A1, A2, api-design | Basic_Design.docx + Workbook.xlsx + Diagrams.md → B3 |
| detail-design | B2 + api-design + db-design | Detail_Design.docx + Workbook + Diagrams → coding, C1 đối chiếu, A5 bổ sung |
| code-review | diff/PR + spec (api/db design) | Code_Review_Report.xlsx + Report.md (kèm chat) → merge/fix |
| test-execution | test-plan + kết quả chạy | Test_Execution.xlsx + Test_Report.docx; ghi `known_issues[]` → D1 |
| sprint-review | sprint plan (A6) + actual | Sprint[N]_Review.xlsx + Sprint_Log.xlsx (append); `current_sprint`++ |
| change-request | mô tả CR + estimate gốc + sprint hiện tại | CR xlsx + summary md; append `change_requests[]`; APPROVED → cập nhật A6/A3/A5 |
| handover-doc | toàn bộ pipeline + `known_issues[]` | Handover.docx + Handover_Workbook.xlsx + Runbook.md; ghi `links.production_url/staging_url` |
| project-architecture | context + output MỌI skill đã chạy | `*_Architecture_v[N].html` (view tổng hợp chỉ-đọc); ghi `links.architecture_file` |
| project-status | manifest patterns + activity_log + files | dashboard trong chat (đọc-only, không tạo file, không ghi context) |
| skill-doctor | thư mục skills + manifest | báo cáo lint PASS/WARN/FAIL trong chat |
| dev-implement | detail-design + api-design + db-design (FEATURE) · bug entry test-execution (BUGFIX) · tech_stack (SCAFFOLD) | code + unit test + PR description → /code-review (bắt buộc trước merge) |
| api-test-suite-generator | api-design + detail-design + routes | tests/api/*_api.test.ts + fixtures → /code-review, /test-execution |
| trailofbits-security-skills | code PR / routes / middlewares | Security_Audit_Report.md → /dev-implement (sửa bug), /code-review |
| acquire-codebase-knowledge | mã nguồn repo + Serena LSP | Architecture_Survey.md → /dev-implement, /project-architecture |
| coding-standards | project-context.json (tech_stack) | ENGINEERING_STANDARDS.md → mọi skill thực thi |
| meeting-minutes | notes/transcript họp | biên bản Minutes.docx + Minutes.xlsx + md; câu hỏi mở → QA_Tracker; scope change → cảnh báo /change-request |

## Hằng số chung — NGUỒN DUY NHẤT là `project-context.json → settings`

| Hằng số | Key | Mặc định | Ai dùng |
|---|---|---|---|
| MD / Person-Month | `settings.md_per_person_month` | 22 | estimate, estimate-template-fill, change-request — **PHẢI cùng một giá trị**, không skill nào tự đặt số riêng |
| Buffer % | `settings.buffer_percent` | 15 | estimate, change-request |
| Sprint duration | `settings.sprint_duration_weeks` | 2 | project-timeline, sprint-review |
| Capacity/role/sprint | `team[].md_per_sprint` | BE/FE/Mobile 8 · QA 7 · PM 5 · DevOps 6 | project-timeline, sprint-review, change-request |
| Ngôn ngữ deliverable | `settings.languages` | client_facing=vi · internal=vi · code=en — quy tắc đầy đủ: `references/i18n-policy.md` | mọi skill sinh file |
| Quality gates | `settings.quality_gates` | UT pass ≥95 · UT coverage ≥80 · IT pass ≥95 · ST pass ≥98 · 0 Critical/High mở | test-execution, dev-implement |

## Placeholder chuẩn (mọi skill dùng — KHÔNG định nghĩa lại)

- `<skills_dir>` = thư mục cha chứa toàn bộ skill folder (thư mục có `project-init/`, `api-design/`…). Xác định từ vị trí SKILL.md đang được nạp; trong shell dùng đường dẫn tuyệt đối tương ứng của môi trường đang chạy.
- `<workspace_folder>` = thư mục làm việc người dùng đã chọn — nơi chứa `project-context.json` và mọi deliverable.

## Scripts dùng chung (nguồn logic — KHÔNG mô tả lại thuật toán bằng văn xuôi trong skill)

| Script | Việc | Ai gọi |
|---|---|---|
| `project-init/scripts/load_context.py` | đọc context + `cget()` | mọi skill |
| `project-init/scripts/update_context.py` | GHI context (atomic + lock + validate) | mọi skill tạo/sửa file |
| `project-init/scripts/check_gate.py` | đếm gate P1 / bug Critical / CR — exit ≠ 0 khi chặn | estimate, project-kickoff, test-execution |
| `project-init/scripts/compute_status.py` | quét tài liệu + staleness + gates → JSON | project-status, project-architecture |
| `project-init/scripts/validate_context.py` | validate schema context | project-init, update_context |
| `db-design/scripts/check_circular_fk.py` | phát hiện chu trình FK | db-design |
| `api-design/scripts/gen_postman.py` | sinh Postman Collection từ api_spec.json | api-design |
| `api-design/scripts/gen_openapi.py` | sinh OpenAPI YAML từ api_spec.json | api-design |
| `evals/run_evals.py` + `evals/checkers/*` | eval harness 2 tầng (xem evals/README.md) | người bảo trì skill |
| `estimate-template-fill/scripts/fill_dev_estimate.py` | điền block 開発 template 見積書 | estimate-template-fill |
| `skill-doctor/scripts/skill_doctor.py` + `menu/scripts/*` | lint bộ skill, sinh/kiểm menu | skill-doctor, menu |

## Quy ước kết thúc response (mọi skill — nguồn duy nhất)

Tối đa 6 dòng: `✅ Vừa xong <bước> + số liệu chính → ▶ Bước kế /<skill> — lấy gì từ output`. KHÔNG ASCII box dài.
Skill TẠO/SỬA file: append `{skill, date, outputs[]}` vào `activity_log[]` bằng `update_context.py`.
Skill đọc-only (project-status, menu, skill-doctor): KHÔNG ghi context.