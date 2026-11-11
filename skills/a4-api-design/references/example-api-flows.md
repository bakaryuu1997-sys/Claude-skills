# Ví dụ minh họa — Flow API và mã lỗi (CHỈ MINH HỌA)

> Ví dụ dưới đây lấy từ một dự án đặt suất ăn nội bộ. KHÔNG chép tên, endpoint, mã lỗi hay số liệu này vào dự án khác. Khi làm dự án thật: lấy flow từ Functional Scope (`FEAT-…` của a2) và mã lỗi từ Error Map của b3 / code dự án.

## Flow mẫu (sheet Flow Diagram)

```
Flow: Đặt suất ăn                Actor: Mobile
─────────────────────────────────────────────────────
Bước 1 → POST /api/v1/auth/login               (lấy access token)
Bước 2 → GET  /api/v1/menu-items?date=…         (xem thực đơn ngày)
Bước 3 → POST /api/v1/orders                    (tạo đơn, trạng thái pending)
Bước 4 → POST /api/v1/orders/{orderId}/payments (thanh toán)
─────────────────────────────────────────────────────
Ngoại lệ: bước 4 thất bại → PATCH /api/v1/orders/{orderId}/status {"status":"cancelled"}
```

## Envelope lỗi mẫu

```json
{ "error": { "code": "ERR-ORDER-002", "message": "Suất ăn đã hết trong khung giờ này",
             "details": [ { "field": "slotId", "issue": "sold_out" } ], "requestId": "req_…" } }
```
