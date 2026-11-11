# VÍ DỤ MINH HỌA (chỉ minh họa — KHÔNG đưa vào deliverable nếu requirement của dự án không có)

Ví dụ về cách "quy tắc theo dữ liệu" của b2 sinh ra các sơ đồ/mục cho một dự án giả định: ứng dụng ghi chú web PWA có dán ảnh từ clipboard và làm việc offline. Đây là phần trước kia bị đóng cứng thành deliverable bắt buộc; nay chỉ là tham khảo. Mọi tên (Note, Clipboard, IndexedDB…) là của dự án giả định.

## Điều kiện → sơ đồ/mục được sinh

| Dữ liệu từ a2/a3/a4 | Sơ đồ / mục b2 sinh ra |
|---|---|
| Functional Scope có "soạn & đồng bộ ghi chú" (Must) | Business Flow: sequence Editor → Live Preview → lưu nháp cục bộ → gọi API lưu → nhận sự kiện đồng bộ |
| Có "dán ảnh từ clipboard" | Flowchart: phím tắt dán → modal xem trước → tải lên → thông báo (+ MSG tương ứng, External_IF "Clipboard") |
| Có đăng nhập | Flowchart xác thực theo đúng cơ chế trong `tech_stack.auth` (giới hạn thử sai, cấp token, điều hướng) — KHÔNG ghi tên thuật toán nếu a2/a4 chưa chọn |
| NFR "làm việc offline" | Flowchart hàng đợi thao tác offline và đồng bộ khi có mạng; mục 10 docx "Yêu cầu vận hành" nêu cache/đồng bộ nền |
| NFR "dọn dữ liệu xóa mềm định kỳ" | Mục 10 docx: lịch dọn thùng rác; một dòng External_IF/batch nếu chạy job |
| Không có yêu cầu nào ở trên | KHÔNG vẽ các sơ đồ này |

## Cách đặt tên ví dụ (để thấy chuỗi ID)

`FEAT-NOTE-01` (soạn ghi chú) → `FN-01` → `SCR-02` (Trình soạn thảo, Prototype id `editor`) → `ITM-02-01` (ô nhập tiêu đề)…
