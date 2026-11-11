# Domain: Tài chính / Kế toán / Thị trường Nhật — quy tắc UI bổ sung

> **Nạp file này CHỈ KHI** dự án thuộc domain hóa đơn/hợp đồng/thanh toán/kế toán, hoặc `settings.languages.client_facing = ja` kèm nghiệp vụ thuế Nhật (インボイス制度, 電子帳簿保存法, 全銀). Dự án khác: bỏ qua toàn bộ file. Mọi tên thực thể (contracts, invoices…) chỉ minh họa — lấy tên thật từ B2 `Screen_List` / A4.

## 1. Validation đặc thù tại form (đồng bộ 1:1 với `Validation_Spec` của B3)
- Mã số doanh nghiệp (法人番号) 13 chữ số; mã số đăng ký hóa đơn (適格請求書発行事業者登録番号) dạng `T` + 13 số.
- Ngày hợp lệ theo lịch (tháng 28/29/30/31); định dạng hiển thị `YYYY/MM/DD` khi client là Nhật.
- Hiển thị rõ thuế suất 10% / 8% (軽減税率) theo từng dòng.

## 2. Tiền tệ & làm tròn
- Format theo locale: JPY `¥1,234,567`, VND `1.234.567 đ`, USD `$1,234.56`.
- Phép tính tạm tính trên UI (thuế hỗn hợp, phí chia theo ngày 按分) **phải dùng cùng công thức và quy tắc làm tròn với Backend** (đọc quy tắc từ B3/Detail Design — thường làm tròn xuống `Math.floor` theo từng hóa đơn). Ưu tiên gọi endpoint `simulate/preview` của Backend thay vì tính lại ở FE; nếu bắt buộc tính ở FE thì dùng chung test vector với Backend.

## 3. Wizard cho thao tác rủi ro cao
Ký hợp đồng thuê bao, phát hành hóa đơn hàng loạt, đối soát file ngân hàng (全銀 / Zengin): luồng 4 bước `Nhập liệu → Xem trước/Breakdown → Xác nhận (dialog) → Thực thi & Kết quả`, cảnh báo thoát trang khi nhập dở, nút chính disabled khi đang gửi, `x-idempotency-key` cho bước thực thi.

## 4. Luồng E2E nên có (nếu module tồn tại trong dự án)
Đăng ký hợp đồng, tính proration, xem trước hóa đơn điện tử, đối soát Zengin, chuyển light/dark, mở Command Palette. Lấy luồng thật từ `Screen_List` + Test Plan (A8) — không dựng luồng không có trong spec.

## 5. Giới hạn
Không chép số liệu mẫu (tên khách, số tiền) vào deliverable; thiếu dữ liệu → `[CẦN ĐIỀN]`.
