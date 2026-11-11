# Viewpoints kiểm thử — checklist trung tính (đọc khi sinh test case)

> Chọn viewpoint theo tính năng. Viewpoint không áp dụng → ghi `N/A — lý do` trong Notes. Số case là hệ quả của checklist, không điền cho đủ số. Ví dụ đầy đủ theo một app cụ thể: `example-notes-app.md` (chỉ minh họa).

## 1. Hiển thị & UI/UX
Áp dụng: mọi màn hình có giao diện.
- Trạng thái rỗng (empty state) có thông báo và hành động tiếp theo.
- Trạng thái đang tải (loading) khi mạng chậm; không nhấp nháy/lặp vô hạn ngoài trạng thái loading.
- Tràn chữ: tiêu đề/nhãn rất dài không làm vỡ layout.
- Responsive theo breakpoint đã thống nhất (`[CẦN ĐIỀN]`).
- Locale: ngày, giờ, tiền, số theo `settings.languages`.
- Nếu có chế độ sáng/tối: tương phản chữ/nền đạt ngưỡng đã chọn.

## 2. Nhập liệu & biên
Áp dụng: mọi input của người dùng.
- Phân vùng tương đương và giá trị biên (EP/BVA) cho từng trường có ràng buộc: dưới biên, tại biên, trên biên.
- Chuỗi: rỗng, khoảng trắng đầu/cuối, ký tự đặc biệt, Unicode nhiều byte (emoji, chữ có dấu).
- Số: 0, âm, số lẻ thập phân, tràn kiểu dữ liệu (theo `type` trong a5).
- File upload: rỗng, đúng giới hạn, vượt giới hạn (thông báo rõ), định dạng không cho phép.

## 3. Thao tác & luồng nghiệp vụ
Áp dụng: mọi feature có CRUD hoặc thay đổi trạng thái.
- CRUD đầy đủ (tạo, xem, sửa, xóa); xóa mềm và khôi phục nếu có `deleted_at`.
- Bấm nhiều lần liên tiếp (double submit) không tạo bản ghi trùng (kiểm idempotency).
- Rời trang khi có thay đổi chưa lưu → cảnh báo.
- Chuyển trạng thái hợp lệ và không hợp lệ (ví dụ đã hủy không được xác nhận lại).
- Lịch sử/rollback nếu nghiệp vụ yêu cầu.

## 4. Tìm kiếm, lọc & sắp xếp
Áp dụng: màn hình danh sách.
- Tìm theo từ khóa (có dấu / không dấu nếu tiếng Việt; full-width / half-width nếu tiếng Nhật).
- Lọc kết hợp nhiều tiêu chí (AND/OR theo spec).
- Sắp xếp từng cột, hai chiều.
- Không có kết quả → empty state.
- Phân trang: trang đầu, trang cuối, trang vượt quá, số bản ghi/trang.

## 5. Mạng & đồng thời
Áp dụng: khi có gọi API, realtime, offline, hoặc nhiều người sửa cùng bản ghi.
- Timeout và retry (số lần, khoảng cách theo spec).
- Lỗi máy chủ 5xx: thông báo thân thiện + hành động thử lại.
- Xung đột khi cập nhật đồng thời (409 / version check).
- Realtime (nếu có): cập nhật tab/thiết bị khác không cần tải lại; không lặp echo.
- Offline (nếu có): dữ liệu nháp không mất; đồng bộ lại khi có mạng.

## 6. Bảo mật & phân quyền
Áp dụng: mọi endpoint và màn hình có dữ liệu người dùng.
- Injection/XSS: payload trong trường nhập hiển thị lại → được escape.
- Liên kết ngoài do người dùng nhập: thuộc tính an toàn theo chuẩn của stack.
- IDOR: đổi ID tài nguyên sang của người khác → 403/404.
- Phân quyền theo role: mỗi role chỉ thấy/làm đúng phần được cấp.
- Hết hạn token: refresh tự động; nếu refresh lỗi → khóa phiên nhưng giữ dữ liệu nháp.
- Không lộ dữ liệu nhạy cảm trong response/log (mật khẩu, token, PII).
