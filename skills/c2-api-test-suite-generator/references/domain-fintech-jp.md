# Domain: Tài chính / Ngân hàng Nhật — fixture & test bổ sung

> **Nạp file này CHỈ KHI** API có điện văn cố định (全銀 Zengin, EDI, SWIFT/MT940), batch xử lý lô tài chính, hoặc tính toán theo thời gian (aging, dunning, 按分). Dự án khác: bỏ qua.

## 1. Điện văn độ rộng cố định (Fixed-Width)
- Fixture/payload sinh bằng helper đệm theo byte (`padStart/padEnd`, `Buffer.alloc`) từ **bảng offset trong đặc tả ngân hàng đối tác** — ghi rõ offset **0-based hay 1-based** trong chú thích bảng. Không nối chuỗi tự do (lệch checksum/parse 0 đồng).
- Với Zengin 120-byte: header/data/trailer/end record; kiểm bằng parser của dự án rằng số tiền (đệm 0), mã ngân hàng, tên người nhận/người chuyển rơi đúng cột theo đặc tả; trailer = tổng số bản ghi + tổng số tiền. **Đối chiếu từng offset với tài liệu của ngân hàng** — không chép số offset từ ví dụ trong skill.
- Test round-trip: generator → parser → so khớp dữ liệu gốc; test lỗi: sai độ dài dòng, ký tự ngoài bộ cho phép, trailer lệch.

## 2. Mốc thời gian tương đối
Dữ liệu aging/dunning/hạn thanh toán: dùng helper `relativeDays(asOfDate, ±N)` thay ngày tĩnh để tránh time-drift khi chạy CI về sau.

## 3. Orchestrator / Batch endpoint
Mock ORM phải có cả nhóm đơn lẻ (`findUnique`, `findFirst`, `create`, `update`) và nhóm tập hợp (`findMany`, `count`, `createMany`, `updateMany`, `$transaction`) cho mọi entity liên đới, nếu không các processor lô sẽ lỗi "is not a function" ngoài ý muốn.
