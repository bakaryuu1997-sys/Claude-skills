# EXCEL STYLE CHUNG — NGUỒN DUY NHẤT (v3.0.0)

> Mọi skill sinh file Excel (api-design, db-design, estimate, test-plan, test-execution, project-timeline, sprint-review, change-request, basic-design, detail-design, project-kickoff) dùng CHUNG bộ quy tắc này — không định nghĩa lại trong từng skill. Skill chỉ ghi thêm phần màu ĐẶC THÙ của nó (nếu có).

## Chuẩn chung
- Font: **Arial**, size 9–10. Title sheet: size 12–13.
- Title (row 1): nền navy `#1F4E79`, chữ trắng, bold, merged.
- Subheader (row 2): nền `#2E75B6`, chữ trắng, size 9.
- Header cột: nền navy `#1F4E79`, chữ trắng, bold, căn giữa.
- Dữ liệu: xen kẽ `#FFFFFF` / `#F2F2F2` (zebra).
- Border: thin toàn bộ, màu `#AAAAAA`.
- Freeze panes tại `A4` (hoặc ngay dưới header) ở mọi sheet có bảng dữ liệu.
- Wrap text: bật cho mọi cột mô tả/dài (Notes, Steps, Errors, Assumption…).

## Bảng màu trạng thái (dùng thống nhất)
| Ý nghĩa | Màu nền |
|---|---|
| OK / Pass / Done / Mới | `#E2EFDA` (xanh lá nhạt) |
| Cảnh báo / Partial / Deprecated | `#FFF2CC` (vàng nhạt) |
| Lỗi / Fail / Rework / Breaking | `#FFE0E0` (đỏ nhạt) |
| Blocked / Urgent | `#FCE4D6` (cam nhạt) |
| Trung tính / N/A / Not run | `#F2F2F2` (xám nhạt) |
| Info / FK / tham chiếu | `#DDEEFF` hoặc `#DBEAFE` (xanh dương nhạt) |

## Công thức — quy tắc BẮT BUỘC
1. Tổng luôn dùng công thức (`=SUM(...)`, `=SUMIF(...)`, `=COUNTIFS(...)`) — KHÔNG hardcode số tổng.
2. Tham chiếu cột bằng **CHỮ CÁI CỘT THẬT** (`$K:$K`) — không được viết tên cột kiểu `$Total:$Total` (không phải cú pháp Excel).
3. Tên sheet có dấu cách phải bọc nháy đơn: `'Detail Estimate'!$K:$K`.
4. Sau khi build file: **mở lại bằng openpyxl và kiểm** — số sheet đúng, số cột đúng như spec của skill, ô công thức bắt đầu bằng `=`. Sai → sửa rồi mới bàn giao.

## Thực thi
```bash
pip install "openpyxl==3.1.*" --break-system-packages -q && python <script.py>
```
