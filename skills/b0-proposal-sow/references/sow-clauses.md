# Khung điều khoản SOW & mục Proposal (b0)

> Đây là KHUNG ĐỂ SOẠN THẢO, không phải tư vấn pháp lý. Mọi giá trị trong `[CẦN ĐIỀN]` do người dùng/hai bên thỏa thuận; không bịa số ngày, tỷ lệ, mức trần. Bản sinh ra luôn ghi **"DRAFT — cần pháp chế/luật sư hai bên rà soát trước khi ký"**.
> Thuật ngữ Nhật chỉ dùng khi `client_facing = ja` (hoặc hợp đồng theo luật Nhật); các ngôn ngữ khác dịch tương đương.

## A. Proposal kỹ thuật — 11 mục (tối thiểu mục 1–10 + phụ lục)

| # | Mục | Nội dung / nguồn |
|---|---|---|
| 1 | Bối cảnh & mục tiêu | vấn đề của khách, mục tiêu kinh doanh (a2 Overview) |
| 2 | Hiểu biết yêu cầu & phạm vi tóm tắt | nhóm module theo Functional Scope; In/Out rút gọn (chi tiết ở SOW) |
| 3 | Kiến trúc giải pháp | sơ đồ tổng thể, công nghệ (`tech_stack`), tích hợp (`integrations`) |
| 4 | Luồng người dùng chính | Business Flows mức Must (a2) |
| 5 | Bảo mật & hiệu năng | NFR có nguồn từ a2; không đưa cam kết số khi a2 chưa có |
| 6 | Đội ngũ & cơ cấu | vai trò, số người, năng lực (`team`); đầu mối hai bên |
| 7 | Tiến độ tổng thể & mốc | số sprint, ngày bắt đầu/go-live, mốc (a9, `project.start_date`, `go_live_target`) |
| 8 | **Giá & điều kiện thanh toán** | tổng giá/đơn giá, tiền tệ, thuế, lịch thanh toán theo mốc (a6 + SOW). Chỉ đưa mức chi tiết khách đã thấy trong 見積; KHÔNG đưa buffer %, đơn giá nội bộ, biên lợi nhuận trừ khi hợp đồng là T&M cần đơn giá — hỏi người dùng |
| 9 | **Giả định, ràng buộc, rủi ro & phụ thuộc phía khách** | từ Risks & Assumptions (a2), Q&A còn mở (QA_Tracker), việc khách phải cung cấp |
| 10 | Cam kết chất lượng | quy trình review/test, tiêu chí chất lượng lấy từ `settings.quality_gates` |
| 11 | Phụ lục | thuật ngữ, tài liệu tham chiếu, bảng Scope/Milestone (trỏ SOW) |

## B. SOW — điều khoản (≥ 12 điều khoản; sinh đủ 16 dưới đây, bỏ điều khoản KHÔNG áp dụng kèm lý do)

| # | Điều khoản | Phải có |
|---|---|---|
| 1 | Mục đích, định nghĩa, tài liệu hợp đồng | thuật ngữ; thứ tự ưu tiên giữa hợp đồng khung, SOW, phụ lục |
| 2 | **Hình thức hợp đồng & thời hạn** | chọn MỘT (hỏi người dùng): **請負 (khoán — cam kết hoàn thành sản phẩm, có 検収 và 契約不適合責任)** / **準委任 (ủy thác theo thời gian/công — cam kết thực hiện nghiệp vụ, không cam kết kết quả, báo cáo định kỳ)** / T&M. Hình thức quyết định điều khoản 6, 7, 10 |
| 3 | Phạm vi bàn giao | tham chiếu `SOW_Scope_Matrix.xlsx` sheet `In_Scope` (FEAT ref) |
| 4 | Ngoài phạm vi, giả định & ràng buộc | sheet `Out_Of_Scope`; giả định từ a2 |
| 5 | Mốc, deliverable & tiêu chí nghiệm thu | sheet `Milestone_Deliverables`: mã mốc, ngày, sản phẩm, Acceptance Criteria đo được |
| 6 | **Quy trình nghiệm thu (検収)** | thời hạn khách kiểm tra `[CẦN ĐIỀN]` ngày làm việc; cách thông báo lỗi; sửa và kiểm lại; điều kiện coi là đã nghiệm thu khi khách không phản hồi (nếu hai bên thỏa thuận); liên hệ UAT |
| 7 | **Giá & thanh toán** | tổng giá, tiền tệ, thuế (消費税/VAT), % thanh toán theo mốc (tổng = 100%), hạn thanh toán (締め日/支払サイト), chi phí phát sinh ngoài giá, lãi/phạt chậm trả `[CẦN ĐIỀN]` |
| 8 | Trách nhiệm hai bên & phụ thuộc | việc khách phải cung cấp (tài khoản, môi trường, dữ liệu, người quyết định), thời hạn phản hồi; hệ quả trễ = dời lịch tương ứng |
| 9 | **Quản lý thay đổi (Change Control)** | quy trình: đề xuất thay đổi → đánh giá tác động (công số, lịch, chi phí) → khách phê duyệt bằng văn bản → cập nhật SOW/kế hoạch; đơn giá cho thay đổi; không làm việc ngoài phạm vi khi chưa được duyệt |
| 10 | **Bảo hành / 契約不適合責任 & hỗ trợ (SLA)** | thời hạn `[CẦN ĐIỀN]` tháng từ nghiệm thu; phạm vi (lỗi so với spec đã ký), loại trừ (khách tự sửa, thay đổi môi trường), thời gian phản hồi/khắc phục theo mức Critical/High/Medium/Low (giá trị do hai bên chốt), hỗ trợ sau bảo hành = hợp đồng riêng |
| 11 | Sở hữu trí tuệ | quyền sở hữu deliverable và thời điểm chuyển giao (sau thanh toán đủ); thành phần có sẵn/mã nguồn mở và giấy phép |
| 12 | **Bảo mật thông tin (秘密保持/NDA) & dữ liệu cá nhân (個人情報)** | phạm vi thông tin mật, thời hạn, trả/hủy dữ liệu khi kết thúc; xử lý dữ liệu cá nhân theo luật áp dụng của hợp đồng; thời hạn báo sự cố rò rỉ `[CẦN ĐIỀN]` giờ |
| 13 | **Tái ủy thác (再委託)** | cấm hoặc cho phép khi có chấp thuận bằng văn bản; trách nhiệm của bên nhận thầu chính |
| 14 | **Chấm dứt hợp đồng & giới hạn trách nhiệm** | điều kiện chấm dứt, thanh toán phần đã làm, mức trần bồi thường `[CẦN ĐIỀN]`, loại trừ thiệt hại gián tiếp, bất khả kháng |
| 15 | Luật áp dụng & giải quyết tranh chấp | luật, nơi xét xử/trọng tài `[CẦN ĐIỀN]` |
| 16 | Hiệu lực, ngôn ngữ ưu tiên, chữ ký | hai khối chữ ký đại diện hợp pháp |

Quy tắc áp dụng:
- Điều khoản 2 chưa chọn ⇒ DỪNG hỏi; không mặc định.
- Điều khoản số ngày/tỷ lệ/mức trần chưa có ⇒ `[CẦN ĐIỀN]` và liệt kê ở cuối response.
- Điều khoản 7: tổng % mốc phải = 100% (công thức ở sheet `Milestone_Deliverables`).
- Nội dung tài liệu gửi khách không chứa mã bước, slash command hay nhãn nội bộ; mô tả quy trình bằng lời ("theo quy trình Quản lý thay đổi tại Điều 9").

## C. Mapping Excel `SOW_Scope_Matrix.xlsx`

Chi tiết cột ở SKILL.md. Điều khoản 3/4/5/7 của SOW chỉ trích dẫn sheet tương ứng; không chép số liệu hai nơi (một nguồn: Excel).
