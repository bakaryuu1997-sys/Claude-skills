---
name: d2-uat-acceptance
version: "3.6.0"
description: >-
  Quản lý nghiệm thu UAT với khách hàng: kiểm tra tiêu chuẩn nghiệm thu (Acceptance Criteria),
  biên bản bàn giao tính năng ký duyệt (Sign-Off) và danh mục punch list bảo hành. Trigger:
  "nghiệm thu", "uat acceptance", "biên bản nghiệm thu", "sign-off", "acceptance criteria",
  "bàn giao thanh toán". Bước D2 — sau handover D1.
---

# UAT Acceptance — Quản Lý Nghiệm Thu & Ký Duyệt Bàn Giao Khách Hàng

## Mục tiêu

Quản lý và thực hiện thủ tục **Nghiệm thu chấp nhận người dùng (User Acceptance Testing - UAT)** và ký kết **Biên bản nghiệm thu bàn giao (Acceptance Certificate)** với đại diện khách hàng. Đây là căn cứ pháp lý quyết định việc giải ngân, thanh lý hợp đồng hoặc chuyển sang giai đoạn bảo hành, bảo trì định kỳ.

Nguyên tắc nghiệm thu:
- **Tiêu chí định lượng rõ ràng:** Mọi hạng mục nghiệm thu phải căn cứ trên bản đặc tả yêu cầu (/a2-requirement-analysis) và kế hoạch kiểm thử chấp nhận UAT (/a8-test-plan).
- **Phân loại lỗi tồn đọng rõ ràng (Punch List):** Tuyệt đối không còn lỗi Severity 1 (Blocker/Critical) và Severity 2 (Major). Các lỗi nhỏ Severity 3/4 không ảnh hưởng luồng chính được ghi nhận vào Punch List cam kết khắc phục trong thời gian bảo hành.
- **Có chữ ký đại diện thẩm quyền:** Biên bản nghiệm thu phải có đầy đủ thông tin, chức danh và chữ ký của đại diện hai bên (Project Sponsor, PM, QA Lead).

---

## Bước -1 — Đọc Project Context (nếu có)

> **Giao thức chuẩn — chi tiết: `a1-project-init/references/context-protocol.md`** (KHÔNG chép lại vào skill):
> đọc bằng `load_context.py` + `cget()`; ghi bằng `update_context.py`; gate bằng `check_gate.py`.
> `NO_CONTEXT` → chạy chế độ hỏi/suy luận thủ công.

**Nếu có context** → tự động trích xuất:
- `project.name`, `client`, `go_live_target` (thông tin dự án).
- `team.client_stakeholders`, `team.project_manager` (đại diện ký biên bản).
- `deliverables` (danh mục sản phẩm bàn giao cần nghiệm thu).

---

## Bước 0 — Thu thập thông tin đầu vào

Đọc kết quả từ các bước trước:
1. `*_Statement_Of_Work.docx` (từ /b0-proposal-sow) & `*_Requirement_Specification.xlsx` (từ /a2-requirement-analysis) → Tiêu chí nghiệm thu đã cam kết trong hợp đồng.
2. `*_Test_Plan.xlsx` (từ /a8-test-plan) → UAT Checklist và kịch bản người dùng.
3. `*_Test_Execution.xlsx` (từ /c5-test-execution) → Kết quả chạy test UAT thực tế của khách hàng.
4. `*_Handover.docx` & `*_Runbook.md` (từ /d1-handover-doc) → Hồ sơ bàn giao kỹ thuật.

---

## Tiêu chí Chất lượng & Chống Sơ sài (Anti-Superficiality Checklist)

Bộ hồ sơ nghiệm thu bắt buộc gồm **2 file chính thức**:

| STT | File Deliverable | Định dạng | Tiêu chuẩn chất lượng tối thiểu |
|---|---|---|---|
| 1 | `[TênDựÁn]_UAT_Acceptance_Certificate.docx` | Word Document | Biên bản nghiệm thu chính thức gồm **6 mục chuẩn**: Căn cứ hợp đồng & phạm vi nghiệm thu, Danh mục sản phẩm đã bàn giao, Kết quả đánh giá UAT, Cam kết bảo hành & hỗ trợ kỹ thuật, Xác nhận giải ngân thanh toán, Khối chữ ký thẩm quyền 2 bên |
| 2 | `[TênDựÁn]_UAT_SignOff_Workbook.xlsx` | Excel Workbook | Đủ **4 sheets**: `Acceptance_Summary`, `UAT_Criteria_Verification`, `Punch_List_Minor_Defects`, `Warranty_Scope` |

---

## Cấu trúc file Excel (4 sheets)

### Sheet 1: Acceptance_Summary
- Cột A: STT
- Cột B: Hạng mục nghiệm thu tổng quát (Giao diện người dùng, Cơ sở dữ liệu, API, Bảo mật, Hiệu năng)
- Cột C: Tình trạng (Đạt / Đạt có điều kiện / Chưa đạt)
- Cột D: Đại diện nghiệm thu phía khách hàng
- Cột E: Ngày ký xác nhận

### Sheet 2: UAT_Criteria_Verification
- Cột A: Mã tiêu chí (`UAT-CRIT-01` ..)
- Cột B: Mô tả tiêu chí chấp nhận
- Cột C: Căn cứ tài liệu (Mục SOW / SRS tương ứng)
- Cột D: Bằng chứng kiểm thử (Screenshot / Log / Test case ID)
- Cột E: Đánh giá khách hàng (Accepted / Rejected)
- Cột F: Ghi chú phản hồi của khách hàng

### Sheet 3: Punch_List_Minor_Defects
- Cột A: Mã defect (`PUNCH-01` ..)
- Cột B: Mô tả lỗi tồn đọng mức độ thấp
- Cột C: Mức độ nghiêm trọng (Minor / Cosmetic)
- Cột D: Ảnh hưởng đến vận hành (Không ảnh hưởng luồng chính)
- Cột E: Kế hoạch khắc phục (Fix trong bản vá Sprint Warranty)
- Cột F: Hạn hoàn thành cam kết (SLA ngày hoàn thành)

### Sheet 4: Warranty_Scope
- Cột A: Thời gian bảo hành (Bắt đầu — Kết thúc)
- Cột B: Phạm vi bảo hành miễn phí (Sửa lỗi phát sinh so với đặc tả)
- Cột C: Trường hợp tính phí bổ sung (Yêu cầu thêm tính năng mới / thay đổi logic)
- Cột D: Kênh tiếp nhận sự cố khẩn cấp (Hotline / Email / Ticket portal)
- Cột E: Cam kết thời gian phản hồi theo mức độ (SLA SEV-1 đến SEV-3)

---

## 🔗 Workflow Integration

**Nguồn sự thật pipeline: `<skills_dir>/a1-project-init/references/pipeline.md`** — KHÔNG vẽ lại pipeline trong response; nếu nơi khác mô tả thứ tự lệch, pipeline.md thắng.

- **Bước hiện tại:** D2 — UAT Acceptance (Khách hàng nghiệm thu & ký duyệt bàn giao)
- **Input từ:** /d1-handover-doc (hồ sơ bàn giao) · /a8-test-plan (kịch bản UAT) · /c5-test-execution (kết quả test)
- **Output cho:** Biên bản nghiệm thu chính thức ký kết → /d3-user-guide-manual
- **Bước kế tiếp:** /d3-user-guide-manual (Sổ tay hướng dẫn người dùng cuối và quản trị viên)

**Kết thúc response:** theo quy ước chung trong `pipeline.md` (≤ 6 dòng ✅→▶; skill tạo/sửa file append `activity_log[]` bằng `update_context.py`).

---

## Self-Improvement Loop

Trước khi kết thúc tác vụ, hãy tự đánh giá lại quá trình thực hiện theo 3 câu hỏi:
1. Có bước nào thất bại, gặp lỗi hoặc phải dùng cách xử lý tạm (workaround) không?
2. Người dùng có phải đính chính, chỉnh sửa hoặc từ chối kết quả nào đáng chú ý không?
3. Có phát hiện thêm ngữ cảnh hay quy tắc mới nào giúp các lần chạy sau làm tốt hơn không?
