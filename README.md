# Claude Skills Suite 🚀

Kho kỹ năng và công cụ tự động hóa toàn diện cho quy trình phát triển phần mềm (Claude Code, Codex, Antigravity).

---

## 📦 GIAI ĐOẠN A — CHUẨN BỊ & THIẾT KẾ (A0 → A6, Chạy 1 lần đầu dự án)

| Bước | Lệnh Skill | Tác dụng & Thời điểm dùng | Đầu ra chính |
|---|---|---|---|
| **A0** | `/project-init` | Chạy đầu tiên: Khởi tạo nguồn sự thật chung (tech stack, team, settings, links). | `project-context.json` |
| **A1** | `/requirement-analysis` | Phân tích yêu cầu mơ hồ, bóc tách scope, chuẩn bị bảng Q&A P1–P3 kèm impact. | `*_Requirement_Specification.xlsx`<br>`*_QA_Tracker.xlsx` |
| **A2** | `/prototype-ui` | (Tùy chọn) Dựng prototype HTML click được (1 file self-contained) demo khách duyệt. | `*_Prototype_v[N].html` |
| **A3** | `/api-design` | Thiết kế API endpoints, xuất spec Excel, Postman Collection và OpenAPI YAML. | `*_API_Design.xlsx`<br>`*_Postman_Collection.json` |
| **A3** | `/db-design` | Thiết kế DB schema: Data dictionary, kiểm tra 10 health check rules, migration SQL, ERD. | `*_DB_Design.xlsx`<br>`*_migration.sql`, `*_ERD.md` |
| **A4** | `/estimate` | Báo giá/WBS man-day (Excel 6 sheet). Có Gate chặn: >3 câu P1 mở → dừng. | `*_Estimate.xlsx` |
| **A4b**| `/estimate-template-fill` | (Tùy chọn) Điền task và công số dev vào file template 見積書 có sẵn của khách Nhật. | `<template-filled>.xlsx` |
| **A5** | `/test-plan` | Lập kế hoạch kiểm thử, sinh test cases (Excel 17 cột, 6 viewpoints), Traceability Matrix. | `*_Test_Plan.xlsx` |
| **A6** | `/project-timeline` | Lập lịch tiến độ dự án từ estimate: Sprint plan, Gantt, Critical Path, xuất file calendar. | `*_Project_Timeline.xlsx`<br>`*_Milestones.ics` |

---

## 🚀 GIAI ĐOẠN B — KHỞI ĐỘNG & ĐẶC TẢ CHI TIẾT (B1 → B3, Sau khi ký hợp đồng)

| Bước | Lệnh Skill | Tác dụng & Thời điểm dùng | Đầu ra chính |
|---|---|---|---|
| **B1** | `/project-kickoff` | Họp khởi động: Kickoff deck (pptx), Charter (docx), RACI, Communication plan, DoR/DoD. | `*_Kickoff_Deck.pptx`<br>`*_Project_Charter.docx` |
| **B2** | `/basic-design` | Thiết kế cơ bản (基本設計): Screen list, Screen flow, UI I/O spec để khách ký duyệt. | `*_Basic_Design.docx`<br>`*_BasicDesign_Workbook.xlsx` |
| **B3** | `/detail-design` | Thiết kế chi tiết (詳細設計) cho dev: Sequence diagrams, class design, CRUD matrix, logic xử lý. | `*_Detail_Design.docx`<br>`*_DetailDesign_Workbook.xlsx` |

---

## 🔄 GIAI ĐOẠN C — VẬN HÀNH, PHÁT TRIỂN & KIỂM THỬ (C0 → C4, Lặp lại trong Sprint)

| Bước | Lệnh Skill | Tác dụng & Thời điểm dùng | Đầu ra chính |
|---|---|---|---|
| **C0** | `/dev-implement` | Dev viết code: Chế độ SCAFFOLD (repo/Docker/CI), FEATURE (theo spec), hoặc BUGFIX (kèm regression test). | Code `src/`, `tests/`<br>`docs/C0_dev-implement/PR_*.md` |
| **C0b**| `/api-test-suite-generator` | Tự động sinh test suite API: Bao phủ 8 mã HTTP (200, 422, 401, 403, 404, 409, 429, 500) + mock DB/Auth fixtures. | `tests/api/*_api.test.ts`<br>`tests/fixtures/*_fixture.ts` |
| **C1** | `/code-review` | Review code/PR theo chuẩn dự án nội bộ, đối chiếu spec api/db design, xuất checklist 5 sheet. | `*_Code_Review_Report.xlsx`<br>`*_Code_Review_Report.md` |
| **C1b**| `/trailofbits-security-skills` | Kiểm toán bảo mật (Red Team): Rà soát 7 vector (IDOR, JWT flaw, Mass Assignment, rò rỉ log/credential, SQLi, ReDoS). | `docs/C1_security-audit/Security_Audit_Report.md` |
| **C2** | `/test-execution` | Quản lý & báo cáo chạy test UT/IT/ST/UAT: Tracker pass/fail, defect list, tỷ lệ đạt theo viewpoint. | `docs/C2_test-execution/*_Execution.xlsx`<br>`*_Report.docx` |
| **C3** | `/sprint-review` | Tổng kết sprint: Planned vs actual, velocity trend, bug health, retrospective 4L, Sprint Log tích lũy. | `docs/C3_sprint-review/*_Review.xlsx`<br>`*_Sprint_Log.xlsx` |
| **C4** | `/change-request` | Phân tích tác động (Impact Analysis) + re-estimate man-day khi phạm vi dự án thay đổi. | `*_CR[N]_Change_Request.xlsx`<br>`*_Impact_Summary.md` |

---

## 🏁 GIAI ĐOẠN D — KẾT THÚC DỰ ÁN

| Bước | Lệnh Skill | Tác dụng & Thời điểm dùng | Đầu ra chính |
|---|---|---|---|
| **D1** | `/handover-doc` | Tài liệu bàn giao sau go-live: Handover 12 mục Docx + Workbook Excel 7 sheet + Runbook vận hành. | `*_Handover.docx`<br>`*_Handover_Workbook.xlsx`<br>`*_Runbook.md` |

---

## 🛠️ GIAI ĐOẠN X — CROSS-CUTTING (Chạy bất kỳ lúc nào khi cần)

| Bước | Lệnh Skill | Tác dụng & Thời điểm dùng | Đầu ra chính |
|---|---|---|---|
| **X0** | `/acquire-codebase-knowledge` | Khảo sát kiến trúc repo 4 tầng kết hợp Serena LSP (AST) tiết kiệm token trước khi code hoặc sửa bug. | `docs/X0_codebase-knowledge/Architecture_Survey.md` |
| **X1** | `/project-architecture` | Sinh file HTML self-contained trực quan hóa toàn bộ kiến trúc hệ thống (SVG + Code-Backed Archify). | `*_Architecture_v[N].html` |
| **X2** | `/project-status` | Dashboard hiện trạng dự án ngay trong chat: Bước hiện tại, tài liệu có/thiếu/lỗi thời, gate chặn. | *(Trực tiếp trong chat)* |
| **X3** | `/skill-doctor` | Linter kiểm định chính bộ skill (12 rule chống regression, kiểm tra frontmatter, độ dài, manifest). | *(Trực tiếp trong chat)* |
| **X4** | `/meeting-minutes` | Chuyển notes/transcript cuộc họp thành biên bản Docx + Excel 4 sheet; tự động đổ ngược Q&A vào pipeline. | `*_Minutes_[date].docx`<br>`*_Minutes_[date].xlsx` |
| **X5** | `/coding-standards` | "Hiến pháp kỹ thuật": Strict TypeScript, Prisma transactions, Git Conventional Commits, PR 7 mục. | `docs/X5_coding-standards/ENGINEERING_STANDARDS.md` |

---

## 🧭 META — ĐIỀU HƯỚNG TỔNG

| Bước | Lệnh Skill | Tác dụng | Đầu ra |
|---|---|---|---|
| **-** | `/menu` | Menu điều hướng toàn bộ skill — sinh động từ `skills-manifest.json` và intent matching. | *(Trực tiếp trong chat)* |

---

## ⚙️ Hướng Dẫn Cài Đặt & Sử Dụng

### 1. Cài đặt trên máy khác (Claude Code / Codex / Antigravity)
* Mở menu Plugin → **Marketplaces** → **Add Marketplace** → Dán link:
  ```text
  https://github.com/bakaryuu1997-sys/Claude-skills
  ```
* Chọn cài đặt gói **`dev-lifecycle-skills`** và bật **Enable Auto Update**.

### 2. Tự động commit & push khi chỉnh sửa skill tại máy chính
* Nhấp đúp chuột vào file:
  `scripts/auto-commit-push.bat`
* Script sẽ tự động chạy linter `skill-doctor.py`, tạo commit và push thẳng lên nhánh `main` của GitHub. Mọi máy khác có bật Auto-Update sẽ tự động kéo bản mới nhất về.
