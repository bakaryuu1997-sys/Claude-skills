# VÍ DỤ MINH HỌA (chỉ minh họa — KHÔNG đưa vào deliverable nếu dự án không có yêu cầu/công nghệ tương ứng)

Trước đây b3 đóng cứng các hàm/sơ đồ dưới đây như deliverable bắt buộc (xuất phát từ một dự án ứng dụng ghi chú Node/Prisma giả định). Nay chúng chỉ là ví dụ về cách "tiêu chí chọn hàm phức tạp" sinh ra nội dung. Tên công nghệ là của dự án giả định; dự án thật lấy từ `tech_stack`.

## Tiêu chí chọn hàm cần pseudo-code → ví dụ

| Tiêu chí (dựa trên Business Flow b2 + API a4) | Ví dụ hàm giả định | Sơ đồ đi kèm |
|---|---|---|
| Xác thực/phân quyền có xoay vòng token | `AuthService.login/refresh` | Sequence: Client → Controller → Service → Repository → Token store |
| Ghi nhiều bảng trong 1 transaction | `NoteService.create` (ghi note + tag + revision) | Sequence CRUD + ranh giới transaction |
| Upload/streaming file | `AttachmentService.saveStream` | Sequence: Controller → Service → Storage |
| Đồng bộ ngoại tuyến / phát lại thao tác | `SyncService.replay(queue)` | Sequence reconnect |
| Cạnh tranh đồng thời (hai người sửa) | `NoteService.update` với cột `version` | Logic flowchart: so sánh version → ghi / trả 409 `ERR-CONFLICT-001` |

Dự án không có upload / offline / sửa đồng thời ⇒ không có các hàm này; chọn hàm phức tạp thật của dự án (tính tiền, phê duyệt nhiều bước, import CSV…).

## Ví dụ ghi chú về công nghệ

Class diagram theo tầng thật của `tech_stack.backend` (vd NestJS: Controller → Service → Repository → ORM; Express: route → handler → service → model). Logging/ORM/realtime chỉ xuất hiện nếu có trong `tech_stack` hoặc quy chuẩn `ENGINEERING_STANDARDS.md` (x5).
