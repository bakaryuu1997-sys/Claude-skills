# API VERSIONING & DEPRECATION — chính sách mẫu

> Áp dụng cho mọi API trong `api_spec.json` của a4. Mục tiêu: client của khách (app mobile, hệ thống đối tác) không bị gãy khi backend thay đổi. Chính sách này phải được ghi vào sheet `Versioning` của `*_API_Design.xlsx` và đưa vào hợp đồng (SOW điều khoản bảo trì API).

## 1. Quy tắc phiên bản

- Phiên bản nằm trong đường dẫn: `/api/v1/...`. Chỉ tăng major (`v2`) khi có **thay đổi phá vỡ** (breaking change).
- Thay đổi tương thích ngược (thêm trường tùy chọn, thêm endpoint, thêm mã lỗi có tài liệu) → KHÔNG tăng phiên bản, ghi vào `Changelog` của sheet API.
- Client phải bỏ qua trường lạ trong response (tolerant reader). Spec ghi rõ điều này.

## 2. Bảng phân loại thay đổi

| Loại | Ví dụ | Phá vỡ? | Cách xử lý |
|---|---|---|---|
| Thêm endpoint | `POST /v1/orders/{id}/cancel` | Không | Ghi Changelog |
| Thêm trường response (tùy chọn) | thêm `nickname` | Không | Ghi Changelog |
| Thêm trường request (tùy chọn, có mặc định) | `?include=items` | Không | Ghi Changelog |
| Thêm trường request bắt buộc | `currency` bắt buộc mới | **Có** | Tăng major hoặc giữ mặc định + deprecation |
| Đổi tên / xóa trường | `user_name` → `name` | **Có** | Tăng major |
| Đổi kiểu dữ liệu | `amount` string → number | **Có** | Tăng major |
| Đổi nghĩa mã lỗi / trạng thái | `409` dùng cho việc khác | **Có** | Tăng major |
| Đổi giới hạn (rate limit, kích thước) | 100 → 50 req/phút | **Có** (thực tế) | Thông báo trước ≥ 30 ngày |

## 3. Chính sách ngừng hỗ trợ (deprecation)

1. **Thông báo:** ghi `Deprecation` và `Sunset` (RFC 8594) vào header response, ví dụ `Sunset: Sat, 31 Dec 2027 23:59:59 GMT`.
2. **Thời hạn tối thiểu:** 6 tháng kể từ ngày thông báo cho API công khai; 3 tháng cho API nội bộ đã được xác nhận. Điều khoản thực tế lấy từ SOW — nếu SOW không ghi, ghi `[CẦN XÁC NHẬN]` và hỏi khách.
3. **Song song:** trong thời hạn, `v1` và `v2` chạy song song; có tài liệu di chuyển (migration guide) cho từng breaking change.
4. **Đo lường:** log số request còn gọi phiên bản cũ theo client; không tắt khi còn client đang dùng nếu chưa được xác nhận.
5. **Tắt:** trả `410 Gone` kèm link tài liệu di chuyển, không trả dữ liệu cũ.

## 4. Những thứ phải có trong spec mỗi endpoint

- Phiên bản đầu tiên xuất hiện (`since`) và trạng thái (`active | deprecated | sunset`).
- Idempotency: thao tác `POST` tạo tài nguyên có nhận header `Idempotency-Key` không; nếu có, ghi thời hạn lưu khóa.
- Phân trang: kiểu (cursor / offset), tham số, kích thước tối đa mặc định.
- Mã lỗi theo `pipeline.md` mục "Hợp đồng API dùng chung" (`{ "error": {...} }`, `ERR-<DOMAIN>-<NNN>`).

## 5. Checklist trước khi phát hành một phiên bản

- [ ] Changelog cập nhật, phân loại từng thay đổi theo bảng mục 2.
- [ ] Có thay đổi phá vỡ? → đã tăng major và có migration guide.
- [ ] Header `Deprecation`/`Sunset` đã đặt cho endpoint bị ngừng.
- [ ] Test contract (a8, c2) chạy cả phiên bản cũ và mới.
- [ ] Postman collection và OpenAPI tách theo phiên bản.
