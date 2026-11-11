# Ví dụ minh họa — test plan cho một ứng dụng ghi chú (CHỈ MINH HỌA)

> Ví dụ về ĐỘ CHI TIẾT mong đợi (case nguyên tử, cách đặt ID, cách tách điều kiện). KHÔNG chép tên module, ID, số liệu hay ngưỡng này cho dự án khác.

## Tách một trường thành case nguyên tử

| Test ID | Feature | Điều kiện | Expected |
|---|---|---|---|
| NOTE-VAL-001 | Tiêu đề ghi chú | Tiêu đề rỗng | Lấy dòng đầu nội dung làm tiêu đề |
| NOTE-VAL-002 | Tiêu đề ghi chú | Đúng 255 ký tự | Lưu thành công |
| NOTE-VAL-003 | Tiêu đề ghi chú | 256 ký tự | Hiển thị lỗi "Tiêu đề không quá 255 ký tự"; không lưu |

Sai: gộp "Kiểm tra tiêu đề: rỗng, sai format, vượt 255 ký tự" vào một dòng.

## Một dòng UAT

| # | Requirement Ref | User story | Tiêu chí chấp nhận | Người kiểm | Trạng thái |
|---|---|---|---|---|---|
| 1 | FEAT-AUTH-01 | Người dùng đăng nhập bằng tài khoản công ty | Đăng nhập thành công bằng tài khoản thuộc tổ chức; tài khoản ngoài tổ chức bị từ chối | Business owner | ⬜ |

## Một kịch bản performance (số liệu PHẢI lấy từ NFR — đây chỉ là cấu trúc)

| Test ID | Kịch bản | Số user | Thời lượng | Ngưỡng p95 | Tiêu chí pass |
|---|---|---|---|---|---|
| PERF-001 | Giờ cao điểm: đặt đồng thời | [CẦN ĐIỀN từ NFR] | [CẦN ĐIỀN] | [CẦN ĐIỀN] | Tỷ lệ lỗi dưới ngưỡng NFR |
