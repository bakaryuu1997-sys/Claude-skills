# Ảnh chụp màn hình (screenshot) — quy tắc bắt buộc, che dữ liệu nhạy cảm

> Mọi bước thao tác trong User Manual / Admin Guide có ảnh minh hoạ, hoặc khung giữ chỗ có mã nếu chưa chụp được.
> Không dựng ảnh giả thay cho ảnh thật của hệ thống và không dùng ảnh của dự án khác.

## 1. Nguồn ảnh
- Chụp từ môi trường Staging/UAT đã nghiệm thu (hoặc production với tài khoản demo do khách duyệt), phiên bản trùng `release.version`. Không chụp từ mock/prototype và gọi là ảnh hệ thống (prototype chỉ dùng khi manual viết trước khi có bản chạy — ghi chú rõ ở chú thích).
- Dữ liệu chụp là dữ liệu mẫu/seed. KHÔNG chụp dữ liệu người dùng thật.
- Cách chụp: có Playwright/trình duyệt tự động thì dùng; không thì hướng dẫn người dùng chụp theo danh sách ở mục 5. Không có ảnh → để khung giữ chỗ.

## 2. Che dữ liệu nhạy cảm (kiểm TRƯỚC khi chèn ảnh vào tài liệu)
Che/thay bằng dữ liệu giả, không chỉ làm mờ nhẹ (làm mờ bằng blur đủ mạnh hoặc phủ hộp đặc màu):
- Họ tên, email, số điện thoại, địa chỉ, ID người dùng/khách hàng thật.
- Token, API key, session ID, cookie, URL có tham số bí mật, mã OTP, mã QR đăng nhập.
- Số tài khoản/thẻ, số tiền thật, dữ liệu giao dịch thật.
- Tên miền/IP/host nội bộ, tên server, đường dẫn hệ thống tập tin, tên công ty khác.
- Thanh địa chỉ trình duyệt, thanh bookmark, tab đang mở, thông báo hệ điều hành (cắt khỏi ảnh).
- Admin: bảng người dùng, audit log — chỉ dùng tài khoản mẫu.

## 3. Quy cách ảnh
- Mã ảnh = mã màn hình của tài liệu thiết kế cơ bản: `SCR-<NN>_<bước>.png` (vd `SCR-03_step2.png`); Admin dùng `ADM-<NN>_<bước>.png`.
- Rộng 1280 px (tối thiểu 1024 px), PNG, tỉ lệ thật, ngôn ngữ giao diện trùng ngôn ngữ tài liệu (nhiều ngôn ngữ → chụp từng bản).
- Chú thích bằng số trong vòng tròn (①②…) khớp số bước trong văn bản; một màu chú thích duy nhất, tương phản với nền.
- Có chú thích dưới ảnh (caption) và alt text mô tả hành động để đọc được bằng trình đọc màn hình.
- Ảnh nào quá nửa trang A4 thì cắt vùng liên quan; nhưng giữ một ảnh toàn màn hình cho mỗi màn hình mới.

## 4. Khung giữ chỗ khi chưa chụp được
```
[ẢNH CẦN CHỤP: SCR-03_step2 — Màn hình "<tên màn hình>", sau khi nhấn <nút>; dữ liệu mẫu: <mô tả>; che: <các vùng>]
```
Cuối response liệt kê toàn bộ khung giữ chỗ còn lại dưới dạng "Danh sách ảnh cần chụp" (mã ảnh, màn hình, bước, tài khoản/vai trò cần dùng).

## 5. Checklist cuối
- [ ] Mỗi màn hình trong Screen_List có ít nhất một ảnh hoặc khung giữ chỗ.
- [ ] Không còn email/tên/token/URL nội bộ thật trong ảnh (kiểm bằng cách phóng to 200%).
- [ ] Ảnh khớp phiên bản hệ thống nghiệm thu; nếu giao diện đổi sau đó, đánh dấu ảnh cần chụp lại.
- [ ] Số chú thích khớp số bước.
- [ ] Ngôn ngữ giao diện trong ảnh khớp ngôn ngữ tài liệu.
