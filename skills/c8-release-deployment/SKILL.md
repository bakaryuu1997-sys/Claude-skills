---
name: c8-release-deployment
version: "3.6.0"
description: >-
  Kế hoạch phát hành & triển khai Production an toàn: checklist pre/post deploy, quản lý
  migration DB, kịch bản smoke test và phương án rollback dự phòng khi có sự cố. Trigger:
  "release", "deployment", "deploy production", "kế hoạch phát hành", "checklist deploy",
  "smoke test", "rollback plan". Bước C8 — cuối mỗi chu kỳ release trước bàn giao D1.
---

# Release & Deployment — Kế Hoạch Phát Hành & Triển Khai Production

## Mục tiêu

Xây dựng quy trình phát hành phần mềm chuyên nghiệp, đảm bảo tính sẵn sàng và ổn định cao cho hệ thống khi đưa lên môi trường Staging/Production. Triệt tiêu rủi ro gián đoạn dịch vụ thông qua checklist kiểm tra đa tầng, kịch bản di chuyển dữ liệu (DB Migration) an toàn và kế hoạch khôi phục khẩn cấp (Rollback Plan).

Nguyên tắc triển khai:
- **Zero Surprise:** Mọi câu lệnh, migration script và biến môi trường phải được kiểm thử thành công trên Staging trước khi chạm vào Production.
- **Always have a Rollback:** Không bao giờ triển khai phiên bản mới nếu chưa có kịch bản và script rollback khả thi trong vòng ≤ 15 phút.
- **Rõ người rõ việc:** Định rõ vai trò Release Lead, Ops/DevOps Lead, DB Admin, QA Lead và thời gian trực hỗ trợ (War Room).

---

## Bước -1 — Đọc Project Context (nếu có)

> **Giao thức chuẩn — chi tiết: `a1-project-init/references/context-protocol.md`** (KHÔNG chép lại vào skill):
> đọc bằng `load_context.py` + `cget()`; ghi bằng `update_context.py`; gate bằng `check_gate.py`.
> `NO_CONTEXT` → chạy chế độ hỏi/suy luận thủ công.

**Nếu có context** → tự động trích xuất:
- `tech_stack.database`, `tech_stack.hosting` (hạ tầng triển khai).
- `team.devops`, `team.lead_dev` (nhân sự vận hành).
- `links.repo`, `links.ci_cd` (pipeline triển khai tự động).

---

## Bước 0 — Thu thập thông tin đầu vào

Đọc kết quả từ các bước trước:
1. `docs/C0_dev-implement/` & Git Release Tag → Danh sách commit, PRs, tính năng mới và bugfixes.
2. `*_DB_Design.xlsx` & migration scripts (từ /a5-db-design) → Các migration SQL cần chạy.
3. `*_Code_Review_Report.xlsx` (từ /c3-code-review) & `Security_Audit_Report.md` (từ /c4-trailofbits-security-skills) → Đảm bảo không còn defect Critical/High chặn release.
4. `*_Test_Execution.xlsx` (từ /c5-test-execution) → Tỷ lệ Pass rate kiểm thử đạt tiêu chuẩn Release Gate (100% pass trên Staging).

---

## Tiêu chí Chất lượng & Chống Sơ sài (Anti-Superficiality Checklist)

Bộ tài liệu phát hành gồm **3 file hoàn chỉnh**:

| STT | File Deliverable | Định dạng | Tiêu chuẩn chất lượng tối thiểu |
|---|---|---|---|
| 1 | `Release_Plan_v[N].docx` | Word Document | Tối thiểu **8 mục chuẩn**: Thông tin phiên bản & Release Notes, Lịch trình & Khung giờ bảo trì (Maintenance Window), Đội ngũ trực chiến (War Room & Contacts), Rủi ro & Giải pháp phòng ngừa, Quy trình Go/No-Go Decision, Kịch bản truyền thông người dùng |
| 2 | `Deployment_Checklist.xlsx` | Excel Workbook | Đủ **4 sheets**: `Pre_Deployment`, `DB_Migration`, `Smoke_Verification`, `Rollback_Plan` |
| 3 | `Smoke_Test_Runbook.md` | Markdown | Hướng dẫn kiểm thử nhanh (Sanity/Smoke Check) sau khi hệ thống vừa bật lại: Endpoint kiểm tra, Luồng thanh toán/đăng nhập then chốt, Tiêu chí đạt |

---

## Cấu trúc file Excel (4 sheets)

### Sheet 1: Pre_Deployment
- Cột A: STT
- Cột B: Hạng mục kiểm tra trước giờ G
- Cột C: Lệnh / Thao tác thực hiện
- Cột D: Người phụ trách
- Cột E: Trạng thái (Pending / Done / Blocked)
- Cột F: Ghi chú bằng chứng (Backup snapshot, SSL cert, DNS TTL...)

### Sheet 2: DB_Migration
- Cột A: Thứ tự chạy migration
- Cột B: Tên file SQL migration
- Cột C: Loại migration (Schema / Data seeding / Index)
- Cột D: Thời gian chạy dự kiến
- Cột E: Kịch bản kiểm tra toàn vẹn dữ liệu sau khi chạy
- Cột F: Script rollback tương ứng (Down migration)

### Sheet 3: Smoke_Verification
- Cột A: Mã kiểm tra (`SMK-01` ..)
- Cột B: Tính năng / Luồng nghiệp vụ cốt lõi
- Cột C: Thao tác kiểm thử
- Cột D: Kết quả kỳ vọng
- Cột E: Kết quả thực tế
- Cột F: Đánh giá (PASS / FAIL)

### Sheet 4: Rollback_Plan
- Cột A: Điều kiện kích hoạt Rollback (Trigger criteria: Lỗi 5xx > 5%, migration thất bại...)
- Cột B: Bước thực hiện rollback (Revert container image, restore DB snapshot, clear CDN cache...)
- Cột C: Thời gian tối đa cho phép thực hiện (RTO)
- Cột D: Người có quyền ra quyết định Rollback
- Cột E: Thông báo sự cố cho khách hàng / người dùng

---

## 🔗 Workflow Integration

**Nguồn sự thật pipeline: `<skills_dir>/a1-project-init/references/pipeline.md`** — KHÔNG vẽ lại pipeline trong response; nếu nơi khác mô tả thứ tự lệch, pipeline.md thắng.

- **Bước hiện tại:** C8 — Release & Deployment (Kiểm soát chất lượng phát hành lên Production)
- **Input từ:** /c1-dev-implement · /c3-code-review · /c4-trailofbits-security-skills · /c5-test-execution
- **Output cho:** Phiên bản hoạt động ổn định trên Production → /d1-handover-doc
- **Bước kế tiếp:** /d1-handover-doc (Bàn giao tài liệu vận hành và hệ thống hoàn chỉnh)

**Kết thúc response:** theo quy ước chung trong `pipeline.md` (≤ 6 dòng ✅→▶; skill tạo/sửa file append `activity_log[]` bằng `update_context.py`).

---

## Self-Improvement Loop

Trước khi kết thúc tác vụ, hãy tự đánh giá lại quá trình thực hiện theo 3 câu hỏi:
1. Có bước nào thất bại, gặp lỗi hoặc phải dùng cách xử lý tạm (workaround) không?
2. Người dùng có phải đính chính, chỉnh sửa hoặc từ chối kết quả nào đáng chú ý không?
3. Có phát hiện thêm ngữ cảnh hay quy tắc mới nào giúp các lần chạy sau làm tốt hơn không?
