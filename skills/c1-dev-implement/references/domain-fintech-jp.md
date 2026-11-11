# Domain: Tài chính / Kế toán / Thị trường Nhật — quy tắc code bổ sung

> **Nạp file này CHỈ KHI** dự án có module hóa đơn, chứng từ, thanh toán, đối soát, tính thuế, hoặc yêu cầu pháp lý Nhật (インボイス制度, 電子帳簿保存法, 全銀). Dự án khác: bỏ qua. Ngưỡng/thời hạn cụ thể lấy từ SOW/Detail Design của dự án — các con số dưới đây là mặc định tham khảo, ghi `[CẦN XÁC NHẬN VỚI KHÁCH]` nếu spec không nêu.

## 1. Pure Calculation Engine
- Logic tiền/thuế/chiết khấu/phân bổ ngày 按分/aging/đánh giá tín dụng nằm trong `*.engine.ts` riêng: hàm thuần, **zero dependency** vào framework/ORM/HTTP, tất định, nhận mốc thời gian qua tham số (`asOfDate?: string | Date`).
- Test bảng chân trị (table-driven) phủ 100% nhánh: tháng 28/29 (nhuận)/30/31 ngày; ngày đầu/giữa/cuối tháng; mẫu số 0; mảng rỗng.
- Quy tắc làm tròn (floor/round/ceil, theo dòng hay theo hóa đơn) lấy từ Detail Design; FE dùng cùng test vector.

## 2. Chứng từ có giá trị pháp lý (hóa đơn, biên lai)
- Tính hash SHA-256 (hoặc SHA-512) của file nhị phân ngay trong memory/stream trước khi upload; lưu hex trong DB; test round-trip (tải về, hash lại, so khớp). Cấm MD5/SHA-1.
- Dấu thời gian: đính timestamp từ nhà cung cấp được công nhận (ví dụ time-stamp JIPDEC) theo yêu cầu của khách; lưu trong metadata.
- Lưu trữ bất biến: chính sách Object Lock (chế độ Compliance) với thời hạn theo luật/khách yêu cầu (thường 7–10 năm — xác nhận với khách).
- Sau khi hóa đơn ở trạng thái đã phát hành/đã thanh toán: guard chặn sửa các trường tài chính (subtotal, tax_amount, dòng chi tiết); có test tiêu cực assert 400/409.
- Presigned URL tải chứng từ: TTL ngắn (mặc định tham khảo ≤ 900 giây), `ResponseContentDisposition: attachment`; có test assert TTL.

## 3. Giao thức điện văn cố định (全銀 120-byte, EDI, SWIFT/MT940)
Sinh/parse bằng helper đệm theo byte và bảng offset **ghi rõ 0-based hay 1-based** lấy từ đặc tả ngân hàng đối tác; không dùng nối chuỗi tự do. Round-trip test generator→parser, kiểm checksum/trailer.

## 4. Realtime (WebSocket) — chỉ khi spec yêu cầu
JWT ở handshake, heartbeat ping/pong (mặc định 30s) dọn socket zombie, registry kết nối, broadcast có cờ `excludeSender` chống echo.
