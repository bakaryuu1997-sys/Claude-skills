# Mẫu đặc tả MỘT màn hình (mục 6 của Basic_Design.docx) — 8 mục

Lặp lại đúng cấu trúc này cho TỪNG màn hình trong `Screen_List` (không gộp "các màn hình tương tự"). Tiêu đề mục theo ngôn ngữ tài liệu (ja: `jp-glossary.md`). Ô chưa có dữ liệu → `[CẦN ĐIỀN]` và hỏi lại; không bịa.

**Tiêu đề màn hình**: `SCR-NN — <Tên màn hình>` (+ `Prototype id: <slug>` khớp `data-screen`/`id="screen-<slug>"` của prototype A3).

| # | Mục | Nội dung bắt buộc | Nguồn dữ liệu |
|---|---|---|---|
| 1 | Mục đích & đối tượng | 1–2 câu; vai trò sử dụng; FN và FEAT liên quan | Function_List, Functional Scope (a2) |
| 2 | Tiền / hậu điều kiện | Trạng thái đăng nhập, quyền, dữ liệu cần có trước; trạng thái hệ thống sau khi thao tác xong | Business Flows (a2), API Design |
| 3 | Bố cục | Vùng: header / nội dung / thao tác / modal. Kèm hình chụp prototype (nếu có) và đánh số vùng | Prototype A3 |
| 4 | Bảng item I/O | Trích từ `Screen_Items` của chính màn hình này: ITM, tên, control, kiểu, độ dài, bắt buộc, validation, giá trị mặc định | Screen_Items |
| 5 | Ràng buộc UI & quy tắc nhập | Validation theo item; quan hệ giữa các item (bật/tắt, phụ thuộc) | Screen_Items, NFR |
| 6 | Sự kiện & hành động | Bảng: sự kiện → xử lý phía màn hình → API gọi (METHOD URL từ `*_API_Design.xlsx`) → chuyển tới SCR nào | API Design, Screen Transition |
| 7 | Thông báo | Mã MSG hiển thị theo từng điều kiện lỗi/thành công (khớp `Message_List`) | Message_List |
| 8 | Phi chức năng của màn hình | Chỉ số có NGUỒN (NFR a2 hoặc cam kết SOW); không có nguồn → bỏ mục | a2 NFR, SOW |

## Quy tắc phủ (thay cho các ngưỡng số cứng)

- Mỗi SCR có ≥ 1 FN; mỗi FN `Must` có ≥ 1 SCR (hoặc ghi rõ "không có màn hình — batch/API-only").
- Mỗi input/hiển thị trong prototype của màn hình đó có ≥ 1 dòng `Screen_Items`; mỗi nút có một dòng với "Sự kiện".
- Mỗi item bắt buộc/có validation ⇒ có ít nhất 1 `MSG-ERR` tương ứng ở `Message_List`.
- Mỗi lỗi trong cột "Errors" của API (a4) mà người dùng nhìn thấy ⇒ có MSG.
- Mỗi API mà màn hình gọi tồn tại trong `*_API_Design.xlsx`; thiếu/lệch ⇒ xem "Quy trình lệch API" trong SKILL.md, không tự thêm endpoint.
