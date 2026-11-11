# Quy trình nghiệm thu chính thức (検収) — nạp khi lập Certificate và sheet `Acceptance_Log`

> Mọi con số (số ngày kiểm tra, thời hạn phản hồi, điều khoản nghiệm thu mặc nhiên, tỷ lệ thanh toán) PHẢI lấy từ SOW / hợp đồng
> (`Statement_Of_Work`, sheet `Milestone_Deliverables` của `SOW_Scope_Matrix`). Hợp đồng không quy định → `[CẦN ĐIỀN]` và hỏi người dùng;
> không tự đặt. Skill này không thay thế tư vấn pháp lý: điều khoản về trách nhiệm đối với sản phẩm không phù hợp hợp đồng (契約不適合責任),
> bảo hành và nghiệm thu mặc nhiên cần pháp chế/khách xác nhận.

## 1. Vòng đời một lần nghiệm thu (theo mốc `M1..MN` của SOW)

```
Nộp nghiệm thu (bàn giao D1 + báo cáo test) → Kiểm tra (検収期間) → Kết quả:
  Đạt .................. ký Certificate (6 mục) / 検収書, mốc thanh toán được mở
  Đạt có điều kiện ..... ký kèm Punch List (chỉ Medium/Low) + hạn đóng + điều kiện đóng
  Từ chối .............. khách nêu tiêu chí `UAT-CRIT-NN` bị trượt + bằng chứng → sửa → tái nghiệm thu
  Không phản hồi ....... xem mục 4 (nghiệm thu mặc nhiên)
```

Mỗi vòng ghi một dòng trong sheet `Acceptance_Log`: lần nộp (#), mốc, ngày nộp, hạn kiểm tra (= ngày nộp + số ngày làm việc theo SOW, dùng công thức `WORKDAY`), ngày phản hồi, kết quả, người phản hồi, ghi chú.

## 2. Kiểm tra (検収期間)

- Hạn kiểm tra = số ngày theo SOW kể từ ngày bên khách nhận đủ bàn giao (hồ sơ D1, bản phát hành, báo cáo test, UAT Checklist).
- Gói nộp tối thiểu: danh sách hạng mục + `UAT-CRIT` tương ứng, báo cáo test với số liệu thật (nguồn: `Test_Report` của giai đoạn UAT), `known_issues[]` đang mở, Punch List dự kiến, hướng dẫn truy cập môi trường nghiệm thu.
- Khách thực hiện UAT theo UAT Checklist (từ Test Plan) và ghi kết quả Accepted / Rejected / Partial kèm bằng chứng.

## 3. Từ chối và tái nghiệm thu

- Từ chối phải nêu: mã tiêu chí `UAT-CRIT-NN`, hiện tượng, bằng chứng (ảnh/log/Test ID), mức severity theo thang chuẩn (Critical/High/Medium/Low).
- Bên làm tạo defect (`BUG-<NNN>`) vào `known_issues[]` (`update_context.py append known_issues`), sửa, retest; defect chỉ đóng khi `verified`/`closed`.
- Tái nghiệm thu: lần nộp mới (#2, #3…) chỉ kiểm lại tiêu chí bị từ chối + regression liên quan; ghi vào `Acceptance_Log`. Thời hạn kiểm tra của vòng mới theo SOW (nếu SOW không nói → hỏi).
- Mỗi lần nộp lại sinh Certificate/Workbook bản mới (`_v2`…); không sửa đè bản đã ký.

## 4. Nghiệm thu mặc nhiên (deemed acceptance) — chỉ khi SOW cho phép

- Điều kiện thường gặp: hết hạn kiểm tra, khách không phản hồi, bên làm đã gửi nhắc bằng văn bản theo đầu mối trong hợp đồng.
- Quy trình: (1) kiểm tra SOW có điều khoản; không có → KHÔNG áp dụng, leo thang qua PM/Sponsor; (2) gửi thông báo nhắc có ghi hạn; (3) lưu bằng chứng gửi/nhận vào `Acceptance_Log`; (4) lập biên bản ghi rõ căn cứ điều khoản + ngày; (5) vẫn đợi người có thẩm quyền của mình xác nhận trước khi tính mốc thanh toán.
- Skill chỉ soạn hồ sơ; việc coi là đã nghiệm thu do người có thẩm quyền hai bên quyết định.

## 5. Nghiệm thu từng phần (theo mốc)

- Mỗi mốc `M<n>` nghiệm thu độc lập, tình trạng `Nghiệm thu từng phần` ở `Acceptance_Summary`; % thanh toán tích lũy = tổng % của các mốc đã Đạt (công thức `SUMIFS`, lấy % từ SOW).
- Hạng mục chưa nghiệm thu nằm ở mốc sau hoặc ở Punch List (chỉ khi Medium/Low). Hạng mục Critical/High chưa đạt thì mốc KHÔNG thể là Đạt.

## 6. Cổng ký

Trước khi ký Certificate: chạy `check_gate.py` (xem SKILL.md). Còn Critical/High mở ⇒ chỉ được lập tình trạng "Chưa đạt" hoặc "Đạt có điều kiện" nếu Critical/High đó đã được khách chấp nhận bằng văn bản (ghi vào `Acceptance_Log` và mục 3 của Certificate); mặc định là không ký "Đạt".

## 7. Biến thể tiếng Nhật (`client_facing = ja`)

- Tiêu đề 検収書 (納品物検収書), 検収完了日, 御中, ngày `YYYY/MM/DD`, thuật ngữ 検収期間, 契約不適合, 保証期間, 検収条件. Font Yu Gothic (`w:eastAsia`).
- Không để tiếng Việt, mã bước nội bộ hay tên nhà thầu cũ trong bất kỳ ô nào.
