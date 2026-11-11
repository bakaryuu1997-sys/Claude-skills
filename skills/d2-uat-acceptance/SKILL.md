---
name: d2-uat-acceptance
version: "3.17.0"
description: >-
  Nghiệm thu chính thức (検収) với khách hàng: quy trình nghiệm thu (thời hạn kiểm tra, từ chối/tái nghiệm thu,
  từng phần, mặc nhiên nếu SOW cho phép), truy vết SOW-UAT, Acceptance Certificate/検収書, Punch List, phạm vi
  bảo hành (nguồn SOW); chặn ký khi còn bug Critical/High (check_gate.py). Trigger: "nghiệm thu", "uat acceptance",
  "biên bản nghiệm thu", "検収", "sign-off", "acceptance criteria", "bàn giao thanh toán". Bước D2 — sau D1.
---

# UAT Acceptance — Quản Lý Nghiệm Thu & Ký Duyệt Bàn Giao Khách Hàng

> ⚠️ **Mọi giá trị cụ thể trong skill và `references/` (số ngày, tên mốc, tên người ký) là KHUNG MINH HỌA** — khi làm dự án thực phải lấy từ SOW, context và tài liệu của dự án đó; thiếu thì `[CẦN ĐIỀN]`, không tự đặt.

## Mục tiêu

Quản lý **nghiệm thu chấp nhận (UAT) và nghiệm thu chính thức (検収)**, lập **Biên bản nghiệm thu (Acceptance Certificate / 検収書)** với đại diện có thẩm quyền của khách — căn cứ để mở mốc thanh toán, thanh lý hợp đồng hoặc chuyển sang bảo hành. Thứ tự theo pipeline: C5 chạy UAT → C8 phát hành → D1 bàn giao hồ sơ → **D2 nghiệm thu chính thức** → D3 tài liệu người dùng.

Nguyên tắc:
- **Tiêu chí định lượng, có căn cứ**: mọi hạng mục nghiệm thu truy về SOW (mốc `M1..MN`, `In_Scope`), yêu cầu (`FEAT-…` của Requirement Specification) và Test ID của Test Plan (`<MODULE>-<TYPE>-<NNN>`); không dùng ID tự chế.
- **Cổng chất lượng bằng code**: còn bug Critical/High mở ⇒ KHÔNG ký "Đạt" (xem Bước 1). Thang severity chuẩn Critical/High/Medium/Low (`pipeline.md`; UAT Sev1→Critical, Sev2→High, Sev3→Medium, Sev4→Low). Punch List chỉ chứa Medium/Low không ảnh hưởng luồng chính.
- **Quy trình nghiệm thu rõ ràng**: thời hạn kiểm tra, từ chối/tái nghiệm thu, nghiệm thu từng phần, nghiệm thu mặc nhiên (chỉ khi SOW cho phép) — `references/acceptance-process.md`.
- **Chữ ký thẩm quyền**: đại diện hai bên có họ tên, chức danh, ngày.
- **Một nguồn cho bảo hành/SLA**: SOW. D2 chép đúng vào `Warranty_Scope`; D1 và D3 chỉ dẫn chiếu.
- **Ngôn ngữ & thương hiệu**: ngôn ngữ/font theo `settings.languages.client_facing` (`i18n-policy.md`; `ja` ⇒ 100% tiếng Nhật, dùng 検収書). Không lộ mã bước nội bộ (`A1`…`D3`) hay tên nhà thầu cũ trong tài liệu gửi khách.

Thư mục xuất: `<workspace_folder>/docs/D2_uat-acceptance/`. Tên có `_v1` ngay từ bản đầu; Certificate đã ký không bị ghi đè — mỗi lần nộp/tái nghiệm thu sinh `_v2`, `_v3`.

---

## Bước -1 — Đọc Project Context (nếu có)

> **Giao thức chuẩn: `a1-project-init/references/context-protocol.md`** (KHÔNG chép lại): đọc bằng `load_context.py` + `cget()`; ghi bằng `update_context.py`; gate bằng `check_gate.py`. `NO_CONTEXT` → chạy chế độ hỏi/suy luận thủ công.

Có context → tự trích: `project.name`, `project.client`, `project.go_live_target`, `release{}` (version, date); người ký phía khách = các phần tử `team[]` có `side=client` (`name`, `role`, `email`), phía đội dự án = `team[]` có `side=vendor` (PM, QA lead); `known_issues[]`; `settings.quality_gates`; `settings.languages`. Danh mục sản phẩm cần nghiệm thu KHÔNG có khóa riêng trong context — lấy từ SOW (`In_Scope`, `Milestone_Deliverables`). Thiếu người ký phía khách → hỏi người dùng, không bịa.

## Bước 0 — Thu thập đầu vào

1. `*_Statement_Of_Work*.docx` + `*_SOW_Scope_Matrix*.xlsx` (B0): mốc `M1..MN`, tiêu chí nghiệm thu, % thanh toán, thời hạn kiểm tra, điều khoản bảo hành/nghiệm thu mặc nhiên/契約不適合.
2. `*_Requirement_Specification*.xlsx` (A2): `FEAT-…` để truy vết hai chiều.
3. `*_Test_Plan*.xlsx` (A8): UAT Checklist + Test ID.
4. `*_Test_Execution*.xlsx` và `*_Test_Report_*.docx` (C5): kết quả UAT thực tế, defect.
5. `*_Handover*.docx`, `*_Runbook*.md` (D1) và phát hành (`release{}`): hồ sơ bàn giao.

## Bước 1 — Gate trước khi lập Certificate

```bash
python <skills_dir>/a1-project-init/scripts/check_gate.py "<workspace_folder>"
```

- **exit 0**: được lập Certificate "Đạt" / "Đạt có điều kiện".
- **exit 1**: còn Critical/High mở. Không lập "Đạt". Lập báo cáo "Chưa đạt" liệt kê `BUG-…` chặn. Chỉ khi khách chấp nhận bằng văn bản từng bug (ghi trong `Acceptance_Log` và mục 3 Certificate) mới được "Đạt có điều kiện".
- **exit 3**: không kiểm được gate — báo người dùng, KHÔNG coi là đã qua.

Đối chiếu thêm với `settings.quality_gates` và exit criteria của báo cáo test UAT.

---

## Bộ hồ sơ nghiệm thu (2 file chính thức)

| STT | File | Tiêu chuẩn tối thiểu |
|---|---|---|
| 1 | `[TênDựÁn]_UAT_Acceptance_Certificate_v1.docx` | **6 mục**: (1) Căn cứ hợp đồng & phạm vi (số SOW, mốc `M<n>`); (2) Danh mục sản phẩm đã bàn giao; (3) Kết quả đánh giá UAT (số liệu từ báo cáo test, kết quả gate, bug mở được khách chấp nhận); (4) Cam kết bảo hành & hỗ trợ (chép từ SOW / `Warranty_Scope`); (5) Xác nhận mốc thanh toán (% từ SOW, không tự đặt); (6) Khối chữ ký 2 bên (họ tên, chức danh, ngày) |
| 2 | `[TênDựÁn]_UAT_SignOff_Workbook_v1.xlsx` | **5 sheet** bên dưới. Punch List là một sheet trong workbook, không phải file riêng |

Excel theo `a1-project-init/references/excel-style.md`; tổng/tỷ lệ bằng công thức, không số cứng. Thư viện: openpyxl (kiểm `ImportError`).

## Cấu trúc file Excel (5 sheets)

### Sheet 1: Acceptance_Summary
Cột: STT · Hạng mục (theo SOW `In_Scope`: giao diện, API, CSDL, bảo mật, hiệu năng…) · Mốc `M<n>` · Tình trạng (`Đạt` / `Đạt có điều kiện` / `Nghiệm thu từng phần` / `Chưa đạt`) · Đại diện khách (từ `team[]` `side=client`) · Ngày ký · % thanh toán của mốc (từ SOW). Dòng tổng: % thanh toán tích lũy của các mốc `Đạt` bằng `SUMIFS`.

### Sheet 2: UAT_Criteria_Verification
Cột: Mã `UAT-CRIT-NN` · Mô tả tiêu chí · Mốc `M<n>` · `FEAT-…` (A2) · Test ID (A8) · Bằng chứng (Test ID/kết quả C5, file ảnh/log) · Đánh giá khách (`Accepted` / `Rejected` / `Partial`) · Ghi chú phản hồi · Ngày phản hồi.
**Cổng phạm vi hợp đồng**: mọi dòng `In_Scope` của SOW có ít nhất một `UAT-CRIT`; ô kiểm tra bằng `COUNTIF`/`COUNTIFS` (phủ 100% hay còn thiếu bao nhiêu) — thiếu ⇒ tô đỏ, không ký.

### Sheet 3: Punch_List_Minor_Defects
Cột: Mã `PUNCH-NN` · Mô tả · Severity (`Medium` / `Low` — Critical/High không được xuất hiện) · Ảnh hưởng vận hành · Kế hoạch khắc phục · Fix owner · Hạn (ngày) · Tham chiếu `BUG-<NNN>` (nếu có) · Trạng thái.
**Xuất backlog bảo hành**: `python <skills_dir>/d2-uat-acceptance/scripts/punch_list_to_backlog.py <workbook.xlsx> --project "<tên>" [--append-context "<workspace_folder>"]` sinh `punch_list_warranty_backlog.json` (schema `references/backlog-schema.json`) và, khi có `--append-context`, nạp từng mục vào `known_issues[]` qua `update_context.py`. Script từ chối (exit 1) nếu thấy Critical/High hoặc trùng mã.

### Sheet 4: Warranty_Scope
Nguồn duy nhất: SOW. Cột: Thời hạn bảo hành (bắt đầu = ngày ký Certificate; kéo dài theo SOW) · Phạm vi miễn phí (lỗi so với đặc tả đã nghiệm thu) · Trường hợp tính phí (tính năng mới/đổi logic ⇒ quy trình Change Request) · Kênh tiếp nhận sự cố (hotline/email/ticket portal, giờ phủ) · Thời gian phản hồi và khắc phục theo severity Critical/High/Medium/Low · Điều khoản trách nhiệm đối với sản phẩm không phù hợp hợp đồng (契約不適合責任) và thời hạn thông báo — chép từ SOW/hợp đồng, nếu chưa có ghi `[CẦN ĐIỀN]` để pháp chế xác nhận.

### Sheet 5: Acceptance_Log
Cột: Lần nộp (#) · Mốc · Ngày nộp · Hạn kiểm tra (`WORKDAY(ngày nộp, số ngày theo SOW)`) · Ngày phản hồi · Kết quả (`Accepted` / `Conditional` / `Rejected` / `Không phản hồi`) · Người phản hồi · Căn cứ (mã tiêu chí bị trượt, điều khoản mặc nhiên nếu có) · Ghi chú. Quy trình chi tiết: `references/acceptance-process.md`.

---

## Quy trình thực hiện

1. Đọc context + đầu vào; hỏi phần còn thiếu (người ký phía khách, số ngày kiểm tra nếu SOW không nêu).
2. Chạy gate (Bước 1).
3. Dựng `UAT_Criteria_Verification` từ SOW × A2 × A8 × C5; tính cổng phạm vi.
4. Lập Punch List (Medium/Low), chạy `punch_list_to_backlog.py`.
5. Lập `Warranty_Scope`, `Acceptance_Summary`, `Acceptance_Log`; sinh Certificate (6 mục).
6. Quét ngôn ngữ/mã bước/tên nhà thầu cũ/`[CẦN ĐIỀN]` còn sót; lưu `docs/D2_uat-acceptance/`.
7. Ghi context: `append activity_log`; khi Certificate đã ký, `patch`/`set` ngày nghiệm thu nếu người dùng yêu cầu.

---

## 🔗 Workflow Integration

**Nguồn sự thật pipeline: `<skills_dir>/a1-project-init/references/pipeline.md`** — KHÔNG vẽ lại pipeline trong response; nếu nơi khác mô tả thứ tự lệch, pipeline.md thắng.

- **Bước hiện tại:** D2 — UAT Acceptance (nghiệm thu chính thức & ký Certificate)
- **Input từ:** D1 (hồ sơ bàn giao) · A8 (UAT Checklist) · C5 (kết quả test, `known_issues[]`) · B0 (SOW, mốc, bảo hành)
- **Output cho:** Certificate + SignOff Workbook (khách ký) → mở mốc thanh toán/bảo hành; Punch List + `Warranty_Scope` → /d3-user-guide-manual (giới hạn đã biết, kênh hỗ trợ)
- **Bước kế tiếp:** /d3-user-guide-manual (Sổ tay người dùng cuối và quản trị viên)

**Kết thúc response:** theo quy ước chung trong `pipeline.md` (≤ 6 dòng ✅→▶; skill tạo/sửa file append `activity_log[]` bằng `update_context.py`).

---

## Self-Improvement Loop
Cuối tác vụ tự trả lời 3 câu: có lỗi/workaround không? người dùng có đính chính không? có quy tắc mới giúp lần sau không? Không có gì → im lặng.
Có phát hiện HỆ THỐNG → in `💡 Đề xuất cải thiện` (≤ 3 dòng) rồi áp dụng theo quy trình duy nhất: `a1-project-init/references/self-improvement.md`.
Áp dụng: 1 skill/tác vụ, ≤ 40 dòng thêm, không xóa quy tắc, chạy `scripts/skill_self_update.py`; báo skill · thay đổi · commit · `git revert <hash>`.
