# CHANGELOG — Bộ skill quản trị dự án

> Các mục 3.7.0 → 3.16.0 được dựng lại ngày 2026-11-06 từ `git log` (repo chưa ghi changelog trong giai đoạn đó).
> Nhãn phiên bản có hai loại: **phiên bản bộ** (manifest + plugin, chỉ có 3.8.0 và 3.16.0 là bản phát hành toàn bộ) và **phiên bản từng skill**
> (3.9.0–3.14.0 chỉ xuất hiện ở một số skill trong `skills-manifest.json`). Mục nào "không có phát hành riêng" nghĩa là git log không có commit gắn nhãn đó.

## 3.17.4 — 2026-11-12
Mở rộng chuỗi E2E sang B0, B1, D1–D3, X1–X7 và các khoảng trống còn lại.

### Added
- B0: Đề xuất kỹ thuật (docx), SOW 16 điều (docx), SOW_Scope_Matrix (xlsx: In/Out Scope, mốc & % thanh toán = 100%, phụ thuộc phía khách).
- B1: Deck kickoff (pptx 9 slide, số liệu có nguồn), Project Charter (docx), Kickoff Workbook (RACI có kiểm 1 chữ A, RAID, Truyền thông, DoR/DoD, Action Items), mẫu biên bản.
- D1: Handover (docx, 12 mục + phụ lục postmortem), Handover_Workbook (Runbook_Matrix INC-01..06, SLO, Known_Issues), Runbook.md.
- D2: Chứng thư nghiệm thu (docx), UAT_SignOff_Workbook (sheet Punch_List_Minor_Defects), backlog JSON qua punch_list_to_backlog.py.
- D3: Hướng dẫn người dùng, hướng dẫn quản trị (docx), Quick Start (md).
- X1 onboarding (md), X2 kiến trúc (html, không CDN), X3 snapshot tiến độ (md, từ compute_status), X4 biên bản (docx + xlsx 4 sheet có lưới), X5 tiêu chuẩn kỹ thuật (md), X7 deck tiến độ (pptx).
- A4: sheet API詳細 (tham số, body, header, phản hồi kèm kiểu).
- C5–C8: báo cáo chuyển sang docx; báo cáo CR-001 bản tiếng Nhật cho khách.
- xlsx_build: tùy chọn "gridlines" (X4 yêu cầu lưới).

### Changed
- Kế hoạch mẫu có thêm công việc UAT và chuẩn bị release → 5 sprint (không còn M5/M6 trùng sprint cuối).
- B0, B1, D1, D2, D3, X4, X5 gắn bộ dựng dùng chung (bắt buộc).

### Fixed
- Ma trận RACI có dòng không có chữ A (phát hiện bởi kiểm 検算); đã sửa.
- Slide tiến độ ghi số case sai (38 thay vì số thực tế).
- Tài liệu API: kiểu dữ liệu phản hồi trống.

## 3.17.3 — 2026-11-12
Kiểm thử end-to-end trên một dự án mẫu (勤怠承認システム, hư cấu) và nâng cấp đầu ra.

### Added
- `a1/scripts/xlsx_build.py`: bộ dựng Excel dùng chung (excel-style: tiêu đề, subtitle, header, zebra, viền, freeze, công thức, danh sách thả xuống).
- `a1/scripts/xlsx_verify.py`: kiểm file Excel (tiêu đề, freeze, header, công thức lỗi, placeholder, tên bên thứ ba, mã bước nội bộ; `--eval` tính lại công thức).
- `a1/scripts/docx_build.py`: bộ dựng Word dùng chung (font ja = Yu Gothic cả eastAsia, bảng có header lặp, mục Heading thật).
- `skills/evals/e2e/`: chuỗi mẫu A4→A9, B3, C5, C6, C7, C8 chạy bằng các script thật của repo (tái lập được, không dữ liệu khách).
- Evals T14–T17: xlsx build/verify, docx build, gate với tiêu đề tiếng Nhật, E2E đầy đủ (21/21).
- Case E2E / SMK / REG và E2E cho luồng danh sách; ma trận phủ đủ 10 loại test.

### Changed
- `a1/scripts/check_gate.py`: nhận tiêu đề cột và trạng thái tiếng Nhật (優先度, ステータス, 未回答/回答済).
- `a5/scripts/health_check.py`: cột có FK tới bảng lookup không còn bị cảnh báo W08 nhầm.
- `a1/scripts/xlsx_verify.py`: không coi JSON lồng nhau là placeholder; số nguyên dạng chữ không bị cảnh báo.
- Skill A2, A4, A5, A6, A8, A9, B2, B3, C5, C6, C7, C8 gắn bộ dựng dùng chung (bắt buộc, không tự định nghĩa style).

### Fixed
- Test plan: công thức "自動化率" thiếu ngoặc (ra 31.15 thay vì 0.9); COUNTIF cả cột làm chậm; thiếu sheet bảo mật trong tổng số case.
- Thiết kế DB mẫu: thiếu index khóa ngoại, thiếu created_at/updated_at, thiếu bảng auth_sessions, SQL sinh ra có FK lạc chỗ (đã parse hợp lệ bằng PostgreSQL parser).
- Estimate mẫu: QA ghi 0 MD (đã thêm công thiết kế/tích hợp/UAT).

## 3.17.2 — 2026-11-11
Hoàn thiện các mục còn dở của đợt rà soát; gỡ dữ liệu khách/dự án cũ khỏi repo.

### Removed
- Template 見積書 `MPL-H12 App_IOS_見積書_template.xlsx` không còn được theo dõi bởi git (chứa tên, ngày, đơn giá của dự án cũ). Giữ bản cục bộ; truyền bằng `--template`.
- Email cá nhân trong `author`/`owner` của `plugin.json`, `marketplace.json`.

### Added
- `evals` T10–T13: golden tier-1 cho `test_metrics`, `cr_impact` (13.5 MD / 0.614 PM tính tay), `timeline_calc` (17 sprint, 6 VEVENT có UID), `smoke_test_runner` (GO/NO-GO với server HTTP cục bộ). Tổng 17 test.
- `c0/assets/theme-provider.tsx` và `c0/assets/command-palette.tsx` (đã kiểm cú pháp TypeScript).
- `c2/references/zengin-record-layout.md`: bố cục 120 byte, ghi rõ 1-based/0-based và mức xác minh từng trường.

### Changed
- `a7/fill_dev_estimate.py`: nếu không có template thì dừng với hướng dẫn `--template`, không dùng file mặc định trong repo.

## 3.17.1 — 2026-11-11
Bổ sung tài liệu chuẩn công ty lớn (Giai đoạn 2), không đổi hành vi script.

### Added
- `c4/references/threat-model.md` — STRIDE + ASVS, nối vào NFR và test bảo mật.
- `x2/references/adr-template.md` — ADR với vòng đời Proposed → Accepted → Superseded.
- `a4/references/api-versioning.md` — phân loại breaking change, chính sách Sunset/Deprecation.
- `x1/references/onboarding-guide.md` — mẫu onboarding 12 mục, chạy được trong 30 phút.
- `c8/references/cicd-spec.md` — stage, cổng theo `quality_gates`, DORA metrics.
- `b1/references/raid-log.md` — cột RAID, quy tắc phân loại, điểm rủi ro.
- `a2/references/nfr-spec.md` — NFR theo ISO 25010, cách kiểm, tiêu chí trước khi sang thiết kế.

## 3.17.0 — 2026-11-11
Phiên bản bộ 3.17.0: sửa toàn bộ lỗi của đợt rà soát 2026-11-06 (168 phát hiện gốc, gộp 44 nhóm nguyên nhân). Danh sách ID nằm ở `docs/audit/2026-11-06-phase1-findings.md`.

### Added
- Quy ước dùng chung trong `pipeline.md`: thang severity Critical/High/Medium/Low, error envelope duy nhất, chuỗi ID truy vết `FEAT→FN→SCR→ITM`, thư mục output `docs/<MÃ>_<tên>/`.
- `a1`: `update_context.py` có lệnh `patch` và `--file`/stdin; `check_gate.py` có exit 3 khi không kiểm được; schema có `quality_gates`, `release{}`, `team[].side`.
- Script mới đã chạy thử: `a5/health_check.py`, `a7` (điền 見積書 có đầu vào tham số hóa + quét sót), `a9/timeline_calc.py` (mốc theo tỷ lệ, ICS hợp lệ), `b3/check_crud_coverage.py`, `c3/coverage_summary.py`, `c4/parse_npm_audit.py`, `c5/test_metrics.py`, `c6/sprint_metrics.py`, `c7/cr_impact.py`, `c8/smoke_test_runner.py`, `d2/punch_list_to_backlog.py`, `x2/gen_architecture_html.py`, `x7/build_deck.py`, `menu/scripts/test_intents.py`.
- Tài liệu mới trong `references/`: `sow-clauses` (b0), `ops-readiness` và `hosting-variants` (d1), `acceptance-process` (d2), `release-practices` (c8), `self-improvement.md` (a1), `domain-fintech-jp` (c0–c4, nạp theo điều kiện), `viewpoints` (a8).
- x6: rule D13 (mục Self-Improvement đúng 1 lần, ≤ 8 dòng, trỏ về nguồn) và D14–D17 đã có từ đợt này; lint tối thiểu cho skill ngoài manifest.
- `.github/workflows/skill-lint.yml`: chạy skill_doctor, evals và biên dịch mọi script trên mỗi push.
- `scripts/skill_self_update.py`: tự sửa + push một cải tiến nhỏ, có rào an toàn (xem `a1-project-init/references/self-improvement.md`).

### Changed
- Mục Self-Improvement ở 33 skill thay bằng khối 5 dòng trỏ về `self-improvement.md` (thay cho bản cũ yêu cầu người dùng duyệt tay).
- Các skill nội dung: nội dung dự án mẫu (ứng dụng ghi chú, canteen, 電帳法, Personal_Vault…) không còn là deliverable bắt buộc; chuyển sang `references/example-*` và nạp theo điều kiện.
- x7: engine duy nhất là PPTX 16:9 (bỏ Marp/HTML).
- x5: stack chuyển sang `references/stack-*.md`; ngưỡng đọc từ `settings.quality_gates`.
- c0–c8 và d1–d3: thang severity chuẩn, envelope chung trỏ về `pipeline.md`, thư mục output `docs/<MÃ>_…/`, `_v1` ngay từ bản đầu.
- menu: sinh bảng từ manifest kèm nhóm "BỔ TRỢ"; intent matcher có stopword tiếng Việt, IDF, bigram; test 155/155 cụm.
- README, AGENTS.md (35 skill), rules/AGENTS.md và SOUL.md đồng bộ với bản gốc.

### Removed
- 5 skill trùng với plugin claude-mem: `handoff`, `learn-codebase`, `mem-search`, `smart-explore`, `timeline-report`. Cài plugin `claude-mem` để dùng bản chính thức.
- `skills/ui-ux-pro-max/scripts/tests/` (fixture của repo upstream, lỗi import khi chạy độc lập).
- Phụ thuộc vào MCP `playwright` và `claude-mem` trong skill c3/c5.

### Fixed
- `check_gate.py` đọc sai dòng header nên gate P1 có thể qua nhầm; nay quét 10 dòng đầu và báo "không kiểm được" thay vì "đạt".
- `check_circular_fk.py` crash khi có vòng FK; self-reference không còn bị báo sai.
- `patch_archify_legibility.py` crash `cp932` sau khi đã ghi file; nay không vá file không phải sơ đồ Archify.
- `verify_fe_scaffold.py` báo ĐẠT khi có mock trong `src/` hoặc khi chỉ có file trong `node_modules`.
- `fill_dev_estimate.py` trộn 人日/人時 (BrSE/PM sai) và chia sai khi chạy chế độ MH.
- `compute_status.py` ghép `docs/**/` vào pattern đã có `docs/` (lỗi `ValueError`) và tạo `**` từ `[N]*`.
- `run_evals.py` không còn fail khi chạy `python -I`.

## 3.16.0 — 2026-11-06
Phiên bản bộ đồng bộ 3.16.0 ở `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `marketplace.json`, `plugin.json` và `manifest_version`.
- `0cfb51b` (2026-11-06): đồng bộ version 3.16.0 ở 4 file plugin/marketplace và manifest; thêm `c0-frontend-dev` vào README/AGENTS.
- `859d822` (2026-11-06): bỏ MCP `playwright` (timeout kết nối) và `claude-mem` (trùng plugin claude-mem riêng) khỏi `.claude-plugin/plugin.json`; xóa `scripts/fix_skills.py` (ghi cứng version 3.8.0 vào mọi skill). `mcp_config.json` (Antigravity) giữ nguyên.
- `02c37c3` (2026-10-21): thêm skill độc lập `/product-teardown` (scanner mã nguồn + benchmark tier-1) và dòng intent tương ứng trong AGENTS.md.
- `d994dbb` (2026-10-13): chỉnh `plugin.json` theo schema Antigravity.
- `ff07ec3` (2026-10-10): thêm `c0-frontend-dev` v3.16.0 (frontend production Next.js/React, `verify_fe_scaffold.py`, 2 file references).

## 3.15.0
Không có phát hành riêng trong git log.

## 3.14.0
- `c6-sprint-review` v3.14.0 (`ff07ec3`, 2026-10-10): cập nhật theo bộ lifecycle 3.9.0.

## 3.13.0
- `c1-dev-implement`, `c2-api-test-suite-generator`, `c3-code-review`, `c4-trailofbits-security-skills`, `c5-test-execution` lên v3.13.0 (`ff07ec3`, 2026-10-10).

## 3.12.0
Không có phát hành riêng trong git log.

## 3.11.0 — 2026-10-09
- `d7434d2`: nâng `c1`–`c6` lên v3.11.0; đồng bộ quy tắc chống lộ mã bước nội bộ và manifest; cập nhật `excel-style.md`, `i18n-policy.md`, `a3-prototype-ui`, `a6-estimate`, `a7-estimate-template-fill` (`fill_dev_estimate.py`) và template.
- `23efec8`: cập nhật tài liệu và `mcp_config.json` thành bộ 7 MCP server (cấu hình Antigravity).

## 3.10.0
- `c7-change-request` v3.10.0 (`d7434d2`, 2026-10-09): mở rộng phân tích tác động và re-estimate.

## 3.9.0 — 2026-10-10
- `ff07ec3`: nâng `c8-release-deployment`, `d1-handover-doc`, `d2-uat-acceptance`, `d3-user-guide-manual` lên v3.9.0; đồng bộ manifest và `pipeline.md` (thêm C0).

## 3.8.0 — 2026-10-04 → 2026-10-07
Bản phát hành bộ đầu tiên có manifest, marketplace và version thống nhất.
- `6b750cb` (2026-10-04): đánh số bước, references, test plan 14 cột, `claude-mem` MCP, version hợp nhất 3.8.0.
- `96b3334`, `4521e36` (2026-10-04): thêm `.claude-plugin/marketplace.json`, chỉnh schema (owner, metadata, `source: ./`).
- `15ae75f`, `a5d5169` (2026-10-04): `compute_status` và `run_evals` hỗ trợ skill có tiền tố; sửa đồ thị DEPS, đường dẫn script, MCP config, tham số CLI.
- `8ee328c` (2026-10-04): README tách hai sơ đồ SDLC.
- `9b398fc` (2026-10-04): `x7` bản thiết kế "human-centric".
- `4c6182e`, `74dcc8a`, `a09ede6`, `2ecc068`, `96db096`, `89867d1` (2026-10-07): thêm `AGENTS.md`/`SOUL.md`, intent classifier, tích hợp Impeccable, Hallmark, Alibaba `ocr`, kiến trúc Slidev, guardrails ECC, Hindsight, Firecrawl; sửa thư mục output C3 và C2.
- `12dc364`, `65211fb` (2026-10-07): thêm rồi bỏ khỏi git các deck mẫu SenseiHub.

## 3.7.0 — 2026-10-04
- `3f3c0d9`: `x7-presentation-deck` v3.7.0 (bố cục Asymmetric Hero, Segoe UI, khoảng trắng chống "void").
- `edf6d3b`, `bc28595`: `x7` deck-as-code, 3 nguyên tắc, anti-slop; thêm deck mẫu.

## 3.6.0 — 2026-10-04
> Ghi chú 2026-11-06: các số liệu trong mục này là số liệu tại thời điểm 2026-10-04 và không còn đúng — hiện bộ có 35 skill (33 trong manifest gồm `menu`, cộng `ui-ux-pro-max` và `product-teardown`; 5 skill claude-mem đã gỡ), plugin Claude Code chỉ khai báo MCP `serena` (bộ 7 MCP là cấu hình riêng của Antigravity trong `mcp_config.json`).
Chuẩn hóa tiền tố liên tiếp (Consecutive Numbering), bổ sung 5 kỹ năng mới & Tài liệu hóa toàn diện hệ sinh thái:
- **Chuẩn hóa số thứ tự liên tiếp**: Xóa bỏ hoàn toàn các hậu tố chữ cái (`A4b`, `C0b`, `C1b`), đổi sang số nguyên liên tiếp theo từng giai đoạn.
- **Bổ sung 5 kỹ năng chuyên nghiệp mới**:
  - `B0` — `b0-proposal-sow`: Biên soạn Đề xuất kỹ thuật & SOW (Statement of Work) chốt hợp đồng.
  - `C8` — `c8-release-deployment`: Kế hoạch phát hành, deploy production, checklist, smoke test & rollback.
  - `D2` — `d2-uat-acceptance`: Quản lý nghiệm thu UAT với khách hàng, ký biên bản bàn giao giải ngân.
  - `D3` — `d3-user-guide-manual`: Sổ tay hướng dẫn sử dụng (User Manual) cho người dùng cuối và Admin Guide kèm FAQ.
  - `X7` — `x7-presentation-deck`: Tạo slide thuyết trình chuyên nghiệp (PowerPoint pptx + HTML interactive slide Marp).
- **Tài liệu hóa toàn diện README.md**: Ghi đầy đủ 50 skills (32 Lifecycle, Claude-Mem, UI/UX Pro Max, Superpowers) và 3 MCP Servers (Serena AST, Playwright E2E, Claude-Mem Memory).
- **Cập nhật Linter `x6-skill-doctor`**: Bảo đảm 100% 32 skills đạt chuẩn (0 FAIL | 0 WARN).

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
- `a4-api-design/scripts/gen_postman.py` + `gen_openapi.py` — Postman/OpenAPI giờ là DẪN XUẤT TẤT ĐỊNH từ `*_api_spec.json` (nguồn trung gian mới, format: `a4-api-design/references/api-spec-format.md`); cả 2 script tự verify (parse lại + đếm). CẤM viết 2 file này bằng tay.
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
- **test-plan**: 17 cột → **14 cột** — bỏ Actual Result/Status/Bug Ticket ID; kết quả thực thi CHỈ sống ở tracker của /c5-test-execution (xóa tình trạng 2 nguồn sự thật).
- **estimate**: khi không có context BẮT BUỘC hỏi `md_per_person_month` qua AskUserQuestion (hết nguy cơ lệch 22 vs 20 với /a7-estimate-template-fill).
- **menu**: sửa tuyên bố "không hardcode" — decision-tree là fallback tĩnh, phải đối chiếu manifest lúc chạy; `check_menu_sync.py` bỏ phần tử trùng lặp.
- **project-init**: sửa "MỌI skill append activity_log" → chỉ skill tạo/sửa file (skill đọc-only không ghi).

### Added
- `a1-project-init/scripts/update_context.py` — GHI context: atomic + lock + validate (thay snippet văn xuôi; mọi skill dùng script, không tự viết code ghi).
- `a1-project-init/scripts/check_gate.py` — gate P1 / bug Critical / CR pending thi hành bằng code, exit ≠ 0 khi chặn.
- `a1-project-init/scripts/compute_status.py` — quét tài liệu + staleness + gates, JSON; /x3-project-status và /x2-project-architecture dùng CHUNG (hết 2 bản cài đặt).
- `a5-db-design/scripts/check_circular_fk.py` — thay code DFS nhúng trong prompt.
- `a1-project-init/references/context-protocol.md` — giao thức "Bước -1" một nguồn duy nhất.
- **api-design**: thuật toán re-run merge CỐ ĐỊNH (khóa = METHOD + URL chuẩn hóa; diff NEW/CHANGED/nghi-xóa in ra TRƯỚC khi ghi; không tự deprecated).
- **basic-design / detail-design**: chế độ re-run versioning docx (`_v[N+1]`, Change History — không ghi đè bản có chỉnh sửa/chữ ký khách).
- **estimate**: quy tắc TẤT ĐỊNH chọn điểm trong khoảng tỷ lệ (CRUD → cận dưới; integration/unknown → cận trên; còn lại trung điểm, làm tròn 0.5 MD).
- Ngưỡng tự quyết thống nhất cho api-design/a5-db-design/a6-estimate: tác động < 3 MD và không đổi kiến trúc → tự quyết + ghi Assumption; ngược lại BẮT BUỘC hỏi.

### Changed
- Khối "Bước -1" trong mọi skill rút còn pointer 3 dòng → `context-protocol.md`; footer response rút gọn trỏ pipeline.md (giảm ~15% token nạp mỗi lần kích hoạt).
- Khử lặp Excel base style ở 6 skill (nguồn duy nhất: `excel-style.md`, skill chỉ giữ màu đặc thù).
- Toàn bộ skill bump **3.3.0** đồng bộ với manifest; xóa `__pycache__` khỏi source.

## 3.2.0 trở về trước
Xem lịch sử trong mô tả từng skill (chưa có changelog tập trung trước v3.3.0).
