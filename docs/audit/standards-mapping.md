# Giai đoạn 2 — Đối chiếu tài liệu chuẩn công ty lớn với bộ skill (2026-11-11)

Mục tiêu: mỗi tài liệu mà một công ty phát triển phần mềm lớn (ISO/IEC/IEEE 12207, 29148, 25010, CMMI, ITIL, DORA, OWASP ASVS, 12-factor, Conventional Commits, Keep a Changelog, SemVer, ADR) thường yêu cầu phải có **chỗ đứng rõ ràng** trong pipeline: skill nào sinh, skill nào tiêu thụ, file nằm ở đâu, gate nào dùng nó.

Quy tắc đã chốt: **mở rộng skill/`references/` có sẵn thay vì tạo skill mới**. Tạo skill mới chỉ khi không có chỗ phù hợp và phải đăng ký đủ manifest + pipeline + menu + AGENTS + README + D08.

Ký hiệu: ✅ đã có · 🟡 có một phần · ❌ thiếu. "Chỗ đứng" = skill + file đề xuất.

| # | Tài liệu chuẩn | Chuẩn tham chiếu | Trạng thái trước | Chỗ đứng đề xuất (đã/đang làm ở Giai đoạn 1 hoặc 2) |
|---|---|---|---|---|
| 1 | BRD / PRD | ISO 29148 | 🟡 A2 Requirement Spec | A2 `Requirement_Specification.xlsx` (đã có 5 sheet) — thêm mục Business Goal, KPI đo được |
| 2 | SRS / Requirement Spec | ISO 29148 | ✅ A2 | giữ; chuỗi ID `FEAT-…` đã chốt (pipeline "Quy ước") |
| 3 | NFR spec (SLA, RTO/RPO, bảo mật, a11y, hiệu năng) | ISO 25010 | ❌ | A2 sheet mới `NFR` (mục tiêu đo được + cách kiểm) — A8 sinh test NFR từ đó |
| 4 | ADR (Architecture Decision Record) | Nygard / AWS | ❌ | `docs/<mã>/ADR-NNN-*.md` do **x2** và **b3** gọi; mẫu nằm ở `x2-project-architecture/references/adr-template.md` |
| 5 | HLD / LLD | CMMI TS | 🟡 b2 (basic) / b3 (detail) | giữ b2 = HLD (màn hình + luồng + API), b3 = LLD (class/sequence/DB) — đã chốt trong Basic/Detail design |
| 6 | Threat model (STRIDE) | OWASP / MS SDL | ❌ | `c4-trailofbits-security-skills/references/threat-model.md` — c4 đọc khi có auth/PII; A2 đưa vào NFR bảo mật |
| 7 | Test strategy (pyramid, môi trường, công cụ) | ISTQB / ISO 29119 | 🟡 a8 Test Plan | a8 sheet `Test_Strategy` (đã có theo báo cáo A); mục entry/exit lấy từ `settings.quality_gates` |
| 8 | RTM (ma trận truy vết) | ISO 29148 | 🟡 a8 Traceability | RTM đóng vòng: `FEAT → FN → SCR → ITM → B3 → TC-ID → kết quả C5 → D2 UAT` — chuỗi ID đã chốt ở pipeline |
| 9 | DoR / DoD | Scrum / CMMI | 🟡 b1 (có) · c1 (DoD 80%) | b1 charter là nguồn DoR/DoD; c1 và c5 đọc ngưỡng từ `quality_gates` (không tự đặt số) |
| 10 | Risk register (RAID) | PMI / CMMI RSKM | 🟡 b1 (4 rủi ro trên slide) | b1 sheet `RAID_Log` đầy đủ: Risk, Assumption, Issue, Dependency — x3 đọc để cảnh báo quá hạn |
| 11 | RACI | PMI | ✅ b1 | giữ; số dòng thống nhất 11 mục charter |
| 12 | Status report | PMI | 🟡 x3 (chat) · c6 (sprint) | x3 là dashboard chat; cần **Status Report tuần** (`docs/X3_project-status/Weekly_Status_YYYY-MM-DD.md`) để gửi khách |
| 13 | CHANGELOG / release notes | Keep a Changelog · SemVer | 🟡 `skills/CHANGELOG.md` (bộ skill) · ❌ cho dự án khách | c8 sinh `CHANGELOG.md` + Release Notes cho khách theo SemVer; `skill_self_update.py` ghi CHANGELOG của bộ |
| 14 | Runbook / SLO / on-call | Google SRE | 🟡 d1 Runbook | d1 thêm SLO/SLI, lịch on-call, escalation theo ca, DR runbook |
| 15 | Postmortem (blameless) | Google SRE | ❌ | d1 `references/postmortem-template.md` — `INC-NN` link từ `known_issues[]` |
| 16 | DR / BCP, backup & restore drill | ISO 22301 | ❌ | d1 mục DR; c8 yêu cầu restore drill trước go-live (PITR) |
| 17 | Data migration plan (cutover, rollback, đối soát) | ISO 27001 A.8 | 🟡 a5 migration.sql | c8 `Migration_Plan` (expand → migrate → contract, điểm không quay lại đánh dấu) |
| 18 | API versioning & deprecation policy | RFC 8594 / Stripe-style | ❌ | a4 sheet `Versioning` (chính sách `/v1`, sunset header, thời hạn deprecation) |
| 19 | CONTRIBUTING / PR template / issue template | GitHub best practice | 🟡 c1 (PR description) | c1 `assets/PULL_REQUEST_TEMPLATE.md` + `ISSUE_TEMPLATE/` (đã có assets của c1) |
| 20 | Branching strategy & release tag | trunk-based / GitFlow · SemVer | ❌ | x5 `ENGINEERING_STANDARDS.md` mục Git (trunk-based mặc định, tag `vX.Y.Z`, cấm force-push main) |
| 21 | CI/CD pipeline spec | 12-factor · DORA | 🟡 c8 (chỉ checklist) | c8 `references/cicd-spec.md`; .github/workflows/skill-lint.yml là mẫu cho dự án |
| 22 | Onboarding guide | Google eng practices | ❌ | x1 sinh `Onboarding_Guide.md` (cài đặt, chạy local, cấu trúc, người liên hệ từ `team[]`) |
| 23 | Tech-debt register | CMMI / Fowler | 🟡 c6 (nợ kỹ thuật ở retro) | `known_issues[]` với `type: tech-debt`; x5 quy định khi nào mở |
| 24 | Change request & baseline | CMMI CM | ✅ c7 | c7 + baseline `estimates.total_md` cập nhật sau khi ký (đã có C-44 trong fix-brief) |
| 25 | Meeting minutes / decision log | ISO 21500 | ✅ x4 / b1 | giữ; `DEC-NN` là ID chuẩn cho quyết định |
| 26 | Acceptance certificate (検収書) | JIS / hợp đồng JP | ❌ | d2 `references/acceptance-process.md` (thời hạn kiểm, từ chối, nghiệm thu mặc nhiên) |
| 27 | Definition of Done / Release readiness checklist | DORA | 🟡 c8 | c8 checklist gắn `check_gate.py` (Critical/High = 0) |

## Tóm tắt thiếu hụt → việc cần làm

- **Thêm vào `references/` (không tạo skill mới):** threat-model, adr-template, postmortem-template, acceptance-process, cicd-spec, migration plan, api versioning, onboarding guide, RAID log schema.
- **Mở rộng sheet có sẵn:** A2 (NFR, Business KPI), A8 (Test_Strategy, RTM đóng vòng), B1 (RAID_Log), A4 (Versioning), d1 (DR/BCP, on-call, postmortem).
- **Chưa đủ để gọi là chuẩn công ty lớn — ngoài phạm vi bộ skill:** ISO 27001 certification, ISO 22301 BCP đầy đủ, CMMI appraisal. Bộ skill chỉ sinh **tài liệu** và checklist; việc đạt chứng nhận cần quy trình tổ chức.

## Không tạo skill mới

Bảng trên không cần skill mới: mọi mục đã có chỗ đứng qua skill hiện có + `references/`. Nếu sau này cần "Security/Compliance pack" hoặc "Ops/SRE pack" riêng, đề xuất ở Giai đoạn 4 (cần người dùng duyệt).
