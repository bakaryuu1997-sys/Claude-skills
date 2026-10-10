---
name: b0-proposal-sow
version: "3.8.0"
description: >-
  Biên soạn Proposal kỹ thuật & Statement of Work (SOW) chuyên nghiệp cho khách ký chốt hợp
  đồng: bối cảnh, giải pháp kiến trúc, phạm vi In/Out scope, mốc nghiệm thu, cam kết SLA &
  điều khoản thanh toán. Trigger: "proposal", "sow", "statement of work", "đề xuất kỹ thuật",
  "soạn proposal", "chốt hợp đồng". Bước B0 — tiền đề kickoff B1.
---

# Proposal & Statement of Work (SOW) — Đề Xuất Kỹ Thuật & Phạm Vi Hợp Đồng

> ⚠️ **Mọi tên riêng trong ví dụ của skill này (FPT, F-Pay, canteen…) chỉ là VÍ DỤ MINH HỌA** — khi làm dự án thực phải thay bằng dữ liệu của dự án đó.

## Mục tiêu

Tổng hợp toàn bộ kết quả phân tích yêu cầu, thiết kế kiến trúc, báo giá công số và tiến độ thành **Bộ hồ sơ Đề xuất Kỹ thuật (Technical Proposal) và Phạm vi công việc (Statement of Work - SOW)** chuẩn mực doanh nghiệp để khách hàng ký duyệt hợp đồng.

Nguyên tắc cốt lõi:
- **Ranh giới trách nhiệm rõ ràng (Clear Boundary):** Định nghĩa rạch ròi In-Scope và Out-of-Scope để ngăn ngừa tình trạng phình scope (Scope Creep) trong quá trình thực thi.
- **Mốc bàn giao gắn liền nghiệm thu & thanh toán:** Mỗi mốc (Milestone) phải gắn với tiêu chí bàn giao định lượng đo đếm được.
- **Khả thi về kỹ thuật & cam kết SLA:** Nêu rõ kiến trúc giải pháp, công nghệ sử dụng, ràng buộc môi trường và cam kết bảo hành hỗ trợ sau bàn giao.
- **Đồng nhất ngôn ngữ 100% (Zero Language Leak):** Nếu proposal/SOW cho khách hàng Nhật (`client_facing = ja`), toàn bộ tài liệu (Docx + Excel) phải 100% bằng tiếng Nhật chuẩn, không lẫn tiếng Việt hay metadata rác từ template cũ.
- **Cấm rò rỉ thương hiệu bên thứ ba & mã nội bộ:** Tuyệt đối không để tên nhà thầu cũ (`Rikkei`, `Rikkeisoft`, `FPT`...) hay mã bước nội bộ (`A1`, `A2`, `B0`...) xuất hiện trong tài liệu giao cho khách. Thông tin các bên phải lấy chính xác từ `project-context.json`.

---

## Bước -1 — Đọc Project Context (nếu có)

> **Giao thức chuẩn — chi tiết: `a1-project-init/references/context-protocol.md`** (KHÔNG chép lại vào skill):
> đọc bằng `load_context.py` + `cget()`; ghi bằng `update_context.py`; gate bằng `check_gate.py`.
> `NO_CONTEXT` → chạy chế độ hỏi/suy luận thủ công.

**Nếu có context** → tự động trích xuất:
- `project.name`, `client`, `tech_stack`, `integrations` (giải pháp kiến trúc).
- `estimates.total_md`, `estimates.role_breakdown` (công số và chi phí).
- `sprint_count`, `milestones`, `target_dates` (tiến độ thực hiện).

---

## Bước 0 — Thu thập thông tin đầu vào

Đọc kết quả từ các bước trước:
1. `*_Requirement_Specification.xlsx` (từ /a2-requirement-analysis) → Scope chức năng/phi chức năng, assumptions.
2. `*_API_Design.xlsx` (từ /a4-api-design) & `*_DB_Design.xlsx` (từ /a5-db-design) → Phạm vi kỹ thuật & thực thể dữ liệu.
3. `*_Estimate.xlsx` (từ /a6-estimate) → Bóc tách man-day, chi phí, nhân sự.
4. `*_Project_Timeline.xlsx` (từ /a9-project-timeline) → Lịch trình, mốc bàn giao.

---

## Tiêu chí Chất lượng & Chống Sơ sài (Anti-Superficiality Checklist)

Bộ tài liệu Proposal & SOW bắt buộc gồm **3 file hoàn chỉnh**:

| STT | File Deliverable | Định dạng | Tiêu chuẩn chất lượng tối thiểu |
|---|---|---|---|
| 1 | `[TênDựÁn]_Technical_Proposal.docx` | Word Document | Tối thiểu **8 mục chuẩn quốc tế**: Bối cảnh & Mục tiêu, Kiến trúc giải pháp kỹ thuật, Luồng người dùng, Bảo mật & Hiệu năng, Đội ngũ triển khai, Tiến độ tổng thể, Cam kết chất lượng, Phụ lục |
| 2 | `[TênDựÁn]_Statement_Of_Work.docx` | Word Document | Tối thiểu **10 điều khoản pháp lý & kỹ thuật**: Mục tiêu, Phạm vi bàn giao, Mốc nghiệm thu (Milestones & Payment terms), Trách nhiệm 2 bên, Quản lý thay đổi (Change Control), Quyền sở hữu trí tuệ, SLA bảo hành |
| 3 | `[TênDựÁn]_SOW_Scope_Matrix.xlsx` | Excel Workbook | Đủ **3 sheets**: `In_Scope`, `Out_Of_Scope`, `Milestone_Deliverables` |

---

## Cấu trúc file Excel (3 sheets)

### Sheet 1: In_Scope
- Cột A: STT
- Cột B: Module / Phân hệ
- Cột C: Tính năng chi tiết
- Cột D: Mô tả nghiệp vụ
- Cột E: Vai trò người dùng (Roles)
- Cột F: Mức độ ưu tiên (Must / Should / Could)
- Cột G: Deliverable nghiệm thu

### Sheet 2: Out_Of_Scope
- Cột A: STT
- Cột B: Hạng mục loại trừ (Feature / Service)
- Cột C: Lý do loại trừ (Pha 2 / Phía khách tự thực hiện / Bên thứ ba)
- Cột D: Rủi ro giả định nếu khách yêu cầu thêm
- Cột E: Cơ chế xử lý nếu phát sinh (Đưa vào Change Request /a7-change-request)

### Sheet 3: Milestone_Deliverables
- Cột A: Mã mốc (`M1` .. `MN`)
- Cột B: Tên mốc giai đoạn
- Cột C: Thời gian dự kiến (Tuần/Ngày)
- Cột D: Sản phẩm bàn giao cụ thể
- Cột E: Tiêu chí nghiệm thu hoàn thành (Acceptance Criteria)
- Cột F: Tỷ lệ thanh toán đề xuất (%)

---

## 🔗 Workflow Integration

**Nguồn sự thật pipeline: `<skills_dir>/a1-project-init/references/pipeline.md`** — KHÔNG vẽ lại pipeline trong response; nếu nơi khác mô tả thứ tự lệch, pipeline.md thắng.

- **Bước hiện tại:** B0 — Proposal & SOW (Chốt hợp đồng & phạm vi cam kết với khách hàng)
- **Input từ:** /a2-requirement-analysis · /a4-api-design · /a5-db-design · /a6-estimate · /a9-project-timeline
- **Output cho:** Hợp đồng và SOW đã ký duyệt → /b1-project-kickoff
- **Bước kế tiếp:** /b1-project-kickoff (Họp khởi động dự án chính thức)

**Kết thúc response:** theo quy ước chung trong `pipeline.md` (≤ 6 dòng ✅→▶; skill tạo/sửa file append `activity_log[]` bằng `update_context.py`).

---

## Self-Improvement Loop

Trước khi kết thúc tác vụ, hãy tự đánh giá lại quá trình thực hiện theo 3 câu hỏi:
1. Có bước nào thất bại, gặp lỗi hoặc phải dùng cách xử lý tạm (workaround) không?
2. Người dùng có phải đính chính, chỉnh sửa hoặc từ chối kết quả nào đáng chú ý không?
3. Có phát hiện thêm ngữ cảnh hay quy tắc mới nào giúp các lần chạy sau làm tốt hơn không?
