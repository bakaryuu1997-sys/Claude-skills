# Claude Skills & Antigravity Suite 🚀

Kho kỹ năng (Skills) và công cụ mở rộng (MCP Servers) toàn diện cho quy trình phát triển phần mềm chuẩn doanh nghiệp (hỗ trợ Claude Code, Codex, Cursor và Antigravity).

---

## 📑 Mục Lục Nhanh
1. [📦 Giai Đoạn A — Chuẩn Bị & Thiết Kế (A1 → A9)](#-giai-đoạn-a--chuẩn-bị--thiết-kế-a1--a9)
2. [🚀 Giai Đoạn B — Khởi Động & Đặc Tả Chi Tiết (B0 → B3)](#-giai-đoạn-b--khởi-động--đặc-tả-chi-tiết-b0--b3)
3. [🔄 Giai Đoạn C — Vận Hành, Phát Triển & Kiểm Thử (C1 → C8)](#-giai-đoạn-c--vận-hành-phát-triển--kiểm-thử-c1--c8)
4. [🏁 Giai Đoạn D — Kết Thúc & Bàn Giao Dự Án (D1 → D3)](#-giai-đoạn-d--kết-thúc--bàn-giao-dự-án-d1--d3)
5. [🛠️ Giai Đoạn X — Cross-Cutting & Tiêu Chuẩn Kỹ Thuật (X1 → X7)](#️-giai-đoạn-x--cross-cutting--tiêu-chuẩn-kỹ-thuật-x1--x7)
6. [🧭 Meta — Điều Hướng Hệ Thống (/menu)](#-meta--điều-hướng-hệ-thống)
7. [🧠 Kỹ Năng Bộ Nhớ AI & Khảo Sát Codebase (Claude-Mem Skills)](#-kỹ-năng-bộ-nhớ-ai--khảo-sát-codebase)
8. [🎨 Kỹ Năng Thiết Kế Giao Diện Đẳng Cấp (UI/UX Pro Max)](#-kỹ-năng-thiết-kế-giao-diện-đẳng-cấp-uiux-pro-max)
9. [⚡ Kỹ Năng Đặc Nhiệm & Lập Trình Tự Trị (Superpowers Skills)](#-kỹ-năng-đặc-nhiệm--lập-trình-tự-trị-superpowers)
10. [🔌 Hệ Thống Công Cụ Mở Rộng MCP (Model Context Protocol)](#-hệ-thống-công-cụ-mở-rộng-mcp-servers)
11. [⚙️ Hướng Dẫn Cài Đặt & Đồng Bộ Tự Động](#️-hướng-dẫn-cài-đặt--đồng-bộ-tự-động)

---

## 📦 GIAI ĐOẠN A — CHUẨN BỊ & THIẾT KẾ (A1 → A9)
*Chạy tuần tự một lần ở đầu dự án / giai đoạn Pre-sale & Solution Architecture.*

| Bước | Lệnh Skill | Tác dụng & Thời điểm dùng | Đầu ra chính |
|:---:|---|---|---|
| **A1** | `/a1-project-init` | **Khởi tạo dự án**: Tạo nguồn sự thật chung `project-context.json` (tech stack, team, settings, links). Chạy đầu tiên. | `project-context.json` |
| **A2** | `/a2-requirement-analysis` | **Phân tích yêu cầu**: Bóc tách scope, phân loại yêu cầu chức năng/phi chức năng, lập bảng Q&A P1–P3 kèm tác động rủi ro. | `*_Requirement_Specification.xlsx`<br>`*_QA_Tracker.xlsx` |
| **A3** | `/a3-prototype-ui` | **Dựng prototype UI click được**: Tạo file HTML tự vận hành (self-contained) tương tác trực quan để khách nghiệm thu giao diện sớm. | `*_Prototype_v[N].html` |
| **A4** | `/a4-api-design` | **Thiết kế API**: Đặc tả endpoints, method, request/response, middleware, lỗi, xuất Excel, Postman Collection và OpenAPI YAML. | `*_API_Design.xlsx`<br>`*_Postman_Collection.json`<br>`*_openapi.yaml` |
| **A5** | `/a5-db-design` | **Thiết kế Database**: Data dictionary, kiểm tra 10 quy tắc DB Health Check, sinh migration SQL và sơ đồ Mermaid ERD. | `*_DB_Design.xlsx`<br>`*_migration.sql`<br>`*_ERD.md` |
| **A6** | `/a6-estimate` | **Báo giá & WBS man-day**: Bóc tách công số chi tiết theo role (Excel 6 sheet). Có Gate chặn: >3 câu P1 chưa trả lời → cảnh báo dừng. | `*_Estimate.xlsx` |
| **A7** | `/a7-estimate-template-fill` | **Điền báo giá vào mẫu có sẵn**: Điền task và công số dev trực tiếp vào file template 見積書 có sẵn của khách hàng Nhật. | `<template-filled>.xlsx` |
| **A8** | `/a8-test-plan` | **Lập kế hoạch kiểm thử**: Sinh danh sách test cases chi tiết (17 cột, bao phủ 6 viewpoints), ma trận truy xuất Traceability Matrix. | `*_Test_Plan.xlsx` |
| **A9** | `/a9-project-timeline` | **Lập lịch tiến độ dự án**: Sprint plan, biểu đồ Gantt, đường găng Critical Path từ estimate; xuất file lịch `.ics`. | `*_Project_Timeline.xlsx`<br>`*_Milestones.ics` |

---

## 🚀 GIAI ĐOẠN B — KHỞI ĐỘNG & ĐẶC TẢ CHI TIẾT (B0 → B3)
*Thực hiện sau khi ký hợp đồng và chốt phạm vi dự án.*

| Bước | Lệnh Skill | Tác dụng & Thời điểm dùng | Đầu ra chính |
|:---:|---|---|---|
| **B0** | `/b0-proposal-sow` | **Biên soạn Proposal & SOW**: Đề xuất giải pháp kỹ thuật, phạm vi In/Out scope, cam kết SLA, mốc nghiệm thu và điều khoản thanh toán để khách hàng ký chốt hợp đồng. | `*_Technical_Proposal.docx`<br>`*_Statement_Of_Work.docx`<br>`*_SOW_Scope_Matrix.xlsx` |
| **B1** | `/b1-project-kickoff` | **Họp khởi động**: Chuẩn bị kickoff deck (pptx), Project Charter (docx), ma trận RACI, kế hoạch truyền thông, tiêu chuẩn DoR/DoD. | `*_Kickoff_Deck.pptx`<br>`*_Project_Charter.docx`<br>`*_Kickoff_Workbook.xlsx` |
| **B2** | `/b2-basic-design` | **Thiết kế cơ bản (基本設計)**: Screen list, sơ đồ chuyển màn hình (screen flow), đặc tả I/O UI để khách hàng ký duyệt. | `*_Basic_Design.docx`<br>`*_BasicDesign_Workbook.xlsx` |
| **B3** | `/b3-detail-design` | **Thiết kế chi tiết (詳細設計)**: Sequence diagrams, class/module design, CRUD matrix, logic xử lý nội bộ cho dev code. | `*_Detail_Design.docx`<br>`*_DetailDesign_Workbook.xlsx` |

---

## 🔄 GIAI ĐOẠN C — VẬN HÀNH, PHÁT TRIỂN & KIỂM THỬ (C1 → C8)
*Vòng lặp phát triển lặp lại liên tục trong mỗi Sprint.*

| Bước | Lệnh Skill | Tác dụng & Thời điểm dùng | Đầu ra chính |
|:---:|---|---|---|
| **C1** | `/c1-dev-implement` | **Lập trình viên viết code**: 3 chế độ (SCAFFOLD khởi tạo repo/Docker/CI, FEATURE code tính năng theo spec, BUGFIX sửa lỗi). | Code `src/`, `tests/`<br>`docs/C0_dev-implement/PR_*.md` |
| **C2** | `/c2-api-test-suite-generator` | **Tự động sinh test suite API**: Sinh mã integration test thực thi được (Jest/Supertest/Pytest) bao phủ 8 mã HTTP + mock DB fixtures. | `tests/api/*_api.test.ts`<br>`tests/fixtures/*_fixture.ts` |
| **C3** | `/c3-code-review` | **Review code & PR**: Đối chiếu spec api/db design, kiểm tra chuẩn kỹ thuật, xuất báo cáo checklist Excel 5 sheet và Markdown. | `*_Code_Review_Report.xlsx`<br>`*_Code_Review_Report.md` |
| **C4** | `/c4-trailofbits-security-skills` | **Kiểm toán bảo mật (Security Audit)**: Rà soát 7 vector lỗ hổng nghiêm trọng (IDOR, JWT flaws, bypass schema, rò rỉ credential/log, SQLi, ReDoS). | `docs/C1_security-audit/Security_Audit_Report.md` |
| **C5** | `/c5-test-execution` | **Quản lý thực thi kiểm thử**: Theo dõi kết quả UT/IT/ST/UAT, danh sách defect, tính tỷ lệ pass/fail theo viewpoint, xuất báo cáo nghiệm thu. | `docs/C2_test-execution/*_Execution.xlsx`<br>`*_Report.docx` |
| **C6** | `/c6-sprint-review` | **Tổng kết Sprint & Retrospective**: Đối chiếu Planned vs Actual, đo đạc velocity trend, phân tích bug health, retro 4L và ghi Sprint Log tích lũy. | `docs/C3_sprint-review/*_Review.xlsx`<br>`*_Sprint_Log.xlsx` |
| **C7** | `/c7-change-request` | **Quản lý yêu cầu thay đổi (CR)**: Phân tích phạm vi ảnh hưởng (Impact Analysis), tính toán lại công số man-day khi scope thay đổi sau khi chốt. | `*_CR[N]_Change_Request.xlsx`<br>`*_Impact_Summary.md` |
| **C8** | `/c8-release-deployment` | **Kế hoạch phát hành & Deploy Production**: Checklist pre/post deploy đa tầng, quản lý migration DB an toàn, kịch bản smoke test và phương án rollback dự phòng ≤ 15 phút. | `Release_Plan_v[N].docx`<br>`Deployment_Checklist.xlsx`<br>`Smoke_Test_Runbook.md` |

---

## 🏁 GIAI ĐOẠN D — KẾT THÚC & BÀN GIAO DỰ ÁN (D1 → D3)
*Thực hiện khi dự án hoàn thành nghiệm thu UAT và chuẩn bị bàn giao vận hành.*

| Bước | Lệnh Skill | Tác dụng & Thời điểm dùng | Đầu ra chính |
|:---:|---|---|---|
| **D1** | `/d1-handover-doc` | **Tài liệu bàn giao toàn diện**: Biên soạn Handover 12 mục Docx + Workbook Excel 7 sheet (Tech stack, Envs, DB, APIs, Runbook, Known issues) + Runbook.md. | `*_Handover.docx`<br>`*_Handover_Workbook.xlsx`<br>`*_Runbook.md` |
| **D2** | `/d2-uat-acceptance` | **Quản lý nghiệm thu UAT**: Kiểm tra tiêu chuẩn chấp nhận (Acceptance Criteria), biên bản bàn giao ký duyệt (Acceptance Certificate) để khách hàng giải ngân thanh toán, punch list bảo hành. | `*_UAT_Acceptance_Certificate.docx`<br>`*_UAT_SignOff_Workbook.xlsx` |
| **D3** | `/d3-user-guide-manual` | **Sổ tay hướng dẫn sử dụng (User Manual) & Admin Guide**: Hướng dẫn thao tác từng bước cho người dùng cuối và quản trị viên kèm ảnh chụp màn hình UI và FAQ xử lý sự cố. | `*_User_Manual_EndUser.docx`<br>`*_Admin_Guide.docx`<br>`*_Quick_Start_Guide.md` |

---

## 🛠️ GIAI ĐOẠN X — CROSS-CUTTING & TIÊU CHUẨN KỸ THUẬT (X1 → X7)
*Bộ công cụ dùng bất kỳ thời điểm nào trong dự án.*

| Bước | Lệnh Skill | Tác dụng & Thời điểm dùng | Đầu ra chính |
|:---:|---|---|---|
| **X1** | `/x1-acquire-codebase-knowledge` | **Khảo sát kiến trúc repo 4 tầng**: Phân tích Router → Middleware → Service → Repository bằng AST Serena LSP siêu tiết kiệm token trước khi code/sửa lỗi. | `docs/X0_codebase-knowledge/Architecture_Survey.md` |
| **X2** | `/x2-project-architecture` | **Trực quan hóa kiến trúc hệ thống**: Tạo trang HTML self-contained vẽ toàn bộ kiến trúc module, API map, ERD và tiến độ bằng sơ đồ Code-Backed (Archify). | `*_Architecture_v[N].html` |
| **X3** | `/x3-project-status` | **Dashboard hiện trạng dự án**: Hiển thị nhanh ngay trong chat vị trí hiện tại trong pipeline, tài liệu đã có / còn thiếu, gate nào đang chặn. | *(Trực tiếp trong chat)* |
| **X4** | `/x4-meeting-minutes` | **Biên bản cuộc họp**: Chuyển transcript/notes họp thành biên bản Docx ký duyệt + Excel 4 sheet; tự động đẩy câu hỏi mở vào QA Tracker. | `*_Minutes_[date].docx`<br>`*_Minutes_[date].xlsx` |
| **X5** | `/x5-coding-standards` | **Hiến pháp kỹ thuật nội bộ**: Ép chuẩn Strict TypeScript, Prisma Transactions, Git Conventional Commits, checklist PR 7 mục & Self-Improvement Loop. | `docs/X5_coding-standards/ENGINEERING_STANDARDS.md` |
| **X6** | `/x6-skill-doctor` | **Linter kiểm định chính bộ skill**: Quét 12 quy tắc chống regression, kiểm tra frontmatter, độ dài mô tả, anti-pattern công thức Excel và tính đồng bộ manifest. | *(Trực tiếp trong chat)* |
| **X7** | `/x7-presentation-deck` | **Tạo slide thuyết trình chuyên nghiệp**: Xuất slide PowerPoint (`.pptx`) 16:9 thiết kế dạng thẻ hiện đại + file HTML interactive slide tự chạy trên trình duyệt web cho pitch, demo, kickoff, sprint review. | `*_Presentation_Deck.pptx`<br>`*_Slide_Deck.html` |

---

## 🧭 META — ĐIỀU HƯỚNG HỆ THỐNG
| Lệnh Skill | Tác dụng | Đầu ra |
|---|---|---|
| `/menu` | **Menu điều hướng động thông minh**: Tra cứu toàn bộ kỹ năng hoặc tự động map intent người dùng với skill phù hợp nhất. | *(Trực tiếp trong chat)* |

---

## 🧠 KỸ NĂNG BỘ NHỚ AI & KHẢO SÁT CODEBASE
*Bộ kỹ năng tối ưu ngữ cảnh, lưu trữ ký ức làm việc dài hạn xuyên session kết hợp với Claude-Mem MCP.*

| Lệnh Skill | Tác dụng & Trường hợp sử dụng | Cơ chế hoạt động |
|---|---|---|
| `/handoff` | **Bàn giao phiên làm việc khi context dài**: Tạo file `HANDOFF.md` tóm tắt mục tiêu, tiến độ, những phương án đã thử thất bại và bước kế tiếp để mở session mới mượt mà. | Đóng gói context sang session kế tiếp mà không làm giảm sút chất lượng suy luận. |
| `/learn-codebase` | **Đọc hiểu sâu toàn bộ mã nguồn**: Yêu cầu AI đọc và phân tích cấu trúc từng file source code để nắm vững logic nền tảng của dự án mới. | Xây dựng corpus kiến thức nền cho toàn bộ dự án. |
| `/mem-search` | **Tìm kiếm ký ức các phiên trước**: Tra cứu xem những bài toán, lỗi hoặc quyết định kỹ thuật nào đã từng được giải quyết trong các phiên làm việc cũ. | Truy vấn database bộ nhớ persistent của `claude-mem`. |
| `/smart-explore` | **Khám phá mã nguồn theo cấu trúc AST**: Thay vì đọc toàn bộ file tốn token, skill sử dụng Tree-sitter AST để đọc outline, chữ ký hàm và cấu trúc lớp. | Tiết kiệm đến 80% token khi tìm hiểu luồng code phức tạp. |
| `/timeline-report` | **Xuất báo cáo hành trình phát triển**: Tạo bài phân tích tường thuật (narrative analysis) toàn bộ lịch sử xây dựng và cải tiến dự án từ timeline bộ nhớ. | Trích xuất báo cáo từ timeline của `claude-mem`. |

---

## 🎨 KỸ NĂNG THIẾT KẾ GIAO DIỆN ĐẲNG CẤP (UI/UX PRO MAX)
*Kho tri thức thiết kế giao diện thông minh cho Web, Mobile và Desktop.*

| Lệnh Skill | Tác dụng & Tài nguyên tích hợp |
|---|---|
| `/ui-ux-pro-max` | **Cẩm nang thiết kế UI/UX đỉnh cao** tích hợp sẵn cơ sở dữ liệu tra cứu offline:<br>• **79 phong cách thiết kế UI** (Minimalism, Neumorphism, Glassmorphism, Brutalism, Bento Grid, Cyberpunk, Apple Design...)<br>• **192 bảng màu chuyên nghiệp** (palette theo ngữ cảnh ngành hàng, độ tương phản WCAG)<br>• **74 cặp phông chữ (font pairings)** chuẩn typography<br>• **119 nguyên lý trải nghiệm người dùng (UX Guidelines)**<br>• **105 bộ biểu tượng (curated icon sets)**<br>• **17 cấu hình hiệu ứng mượt mà (GSAP presets)**<br>• **25 mẫu biểu đồ trực quan hóa dữ liệu (charts)**<br>• **22 công nghệ giao diện** (React, Next.js, Vue, Tailwind CSS, Flutter, Svelte, Angular...). |

---

## ⚡ KỸ NĂNG ĐẶC NHIỆM & LẬP TRÌNH TỰ TRỊ (SUPERPOWERS)
*Quy chuẩn quy trình kỹ nghệ phần mềm cấp cao, vận hành subagents và kiểm thử chuyên sâu.*

| Nhóm Kỹ Năng | Lệnh Skill | Mô tả & Nguyên tắc vận hành |
|---|---|---|
| **Khởi tạo & Lập Kế Hoạch** | `/brainstorming`<br>`/writing-plans`<br>`/executing-plans` | • Khám phá yêu cầu, thảo luận giải pháp kiến trúc trước khi code.<br>• Viết kế hoạch thực thi từng bước rõ ràng, có điểm kiểm tra.<br>• Thực thi kế hoạch có checkpoint nghiêm ngặt, chỉ tiến hành khi bước trước hoàn tất. |
| **Điều Phối Tự Trị (Agents)** | `/subagent-driven-development`<br>`/dispatching-parallel-agents` | • Phân công các subagent chuyên trách độc lập xử lý từng phần việc trong phiên.<br>• Khởi chạy song song 2+ agent cho các task không phụ thuộc trạng thái, tăng tốc gấp nhiều lần. |
| **Kỹ Thuật Lập Trình & Sửa Lỗi** | `/test-driven-development`<br>`/systematic-debugging`<br>`/using-git-worktrees` | • **TDD**: Viết unit test trước, ép code pass test sau.<br>• **Gỡ lỗi khoa học**: 4 bước tìm root cause, giả thuyết thực nghiệm, không đoán mò sửa bừa.<br>• Sử dụng Git Worktree để cô lập không gian làm việc giữa các nhánh tính năng. |
| **Đảm Bảo Chất Lượng & Hoàn Thành** | `/requesting-code-review`<br>`/receiving-code-review`<br>`/verification-before-completion`<br>`/finishing-a-development-branch` | • Tạo yêu cầu review code với đầy đủ ngữ cảnh và checklist.<br>• Tiếp nhận phản biện kỹ thuật với tư duy phản biện, kiểm chứng trước khi sửa.<br>• **Evidence before assertions**: Bắt buộc chạy test thực tế và có log bằng chứng trước khi khẳng định hoàn tất.<br>• Lựa chọn giải pháp hoàn thiện nhánh: merge, squash hay tạo PR chuẩn mực. |

---

## 🔌 HỆ THỐNG CÔNG CỤ MỞ RỘNG MCP (SERVERS)
*Bộ 3 máy chủ Model Context Protocol cung cấp siêu năng lực tương tác sâu với hệ thống, trình duyệt và mã nguồn.*

```
┌────────────────────────────────────────────────────────────────────────┐
│                        AI ASSISTANT (ANTIGRAVITY / CLAUDE)              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│    SERENA MCP    │       │  PLAYWRIGHT MCP  │       │  CLAUDE-MEM MCP  │
│  AST Code Intel  │       │ Browser & Web E2E│       │ Persistent Memory│
└──────────────────┘       └──────────────────┘       └──────────────────┘
```

### 1. Serena MCP (`serena`) — AST & Semantic Code Intelligence
*Trợ lý thấu hiểu cấu trúc code thông qua Abstract Syntax Tree (AST) và LSP:*
* **Đọc hiểu cấu trúc**: `get_symbols_overview`, `find_symbol`, `find_declaration`, `find_implementations` — tìm chính xác định nghĩa class, hàm, biến trong toàn bộ dự án mà không cần đọc từng file.
* **Quan hệ phụ thuộc**: `find_referencing_symbols` — tìm mọi nơi gọi đến hàm/module cần sửa, tránh sửa sót gây break code.
* **Chỉnh sửa chính xác**: `replace_symbol_body`, `insert_after_symbol`, `insert_before_symbol` — thay thế đúng thân hàm ở cấp độ AST, triệt tiêu lỗi format thụt lề hay mất code ngoài ý muốn.
* **Bắt lỗi theo thời gian thực**: `get_diagnostics_for_file` — phát hiện lỗi cú pháp và linter ngay khi vừa chỉnh sửa.
* **Bộ nhớ ngữ cảnh dự án**: `write_memory`, `read_memory`, `list_memories` — lưu lại các quy ước đặc biệt của dự án để AI luôn tuân thủ.

### 2. Playwright MCP (`playwright`) — Browser Automation & E2E Testing
*Trình duyệt tự động hóa kiểm thử giao diện thực tế:*
* **Tương tác trang web**: `browser_navigate`, `browser_click`, `browser_type`, `browser_fill_form`, `browser_select_option`, `browser_press_key` — thao tác như người dùng thật.
* **Chụp ảnh & Trực quan hóa**: `browser_take_screenshot`, `browser_snapshot` — chụp lại kết quả hiển thị của trang web để kiểm tra layout và giao diện.
* **Giám sát mạng & Lỗi**: `browser_network_requests`, `browser_console_messages` — theo dõi API network gọi đi, mã phản hồi HTTP và log lỗi console trình duyệt.
* **Xử lý kịch bản nâng cao**: `browser_file_upload`, `browser_hover`, `browser_drag`, `browser_evaluate` — thực thi script JS trực tiếp trên context trang.

### 3. Claude-Mem MCP (`claude-mem`) — Persistent Memory & Tree-Sitter Search
*Động cơ bộ nhớ dài hạn và tìm kiếm code tốc độ cao:*
* **Bộ nhớ xuyên session**: `work_state_write`, `work_state_read`, `session_start_context` — giữ mạch suy nghĩ và tiến độ dự án khi bắt đầu phiên làm việc mới.
* **Truy vấn lịch sử**: `search`, `timeline`, `get_observations` — tra cứu lại các quyết định kỹ thuật và lỗi đã từng gặp.
* **Tree-Sitter Structural Search**: `smart_search`, `smart_outline`, `smart_unfold` — tìm kiếm logic code bằng parser AST Tree-sitter, siêu tiết kiệm context window.
* **Quản lý Corpus dự án**: `build_corpus`, `prime_corpus`, `query_corpus` — lập chỉ mục tri thức mã nguồn phục vụ trả lời nhanh.

---

## ⚙️ HƯỚNG DẪN CÀI ĐẶT & ĐỒNG BỘ TỰ ĐỘNG

### 1. Cài đặt trên máy khác (Claude Code / Codex / Antigravity)
* Mở menu Plugin trên công cụ làm việc → **Marketplaces** → **Add Marketplace** → Dán link:
  ```text
  https://github.com/bakaryuu1997-sys/Claude-skills
  ```
* Chọn cài đặt gói **`dev-lifecycle-skills`** và chuyển trạng thái sang **Enable Auto Update**.

### 2. Tự động Kiểm Tra & Cập Nhật Lên GitHub
* Khi có bất kỳ thay đổi nào trong bộ kỹ năng, chỉ cần nhấp đúp vào:
  ```text
  scripts/auto-commit-push.bat
  ```
* Script sẽ tự động:
  1. Chạy linter kiểm định **`x6-skill-doctor`** (bảo đảm 100% không có lỗi regression).
  2. Tạo commit và push thẳng lên nhánh `main` của GitHub repository.
  3. Tất cả các máy khác có bật chế độ Auto-Update sẽ tự động tải bản mới nhất về ngay lập tức!
