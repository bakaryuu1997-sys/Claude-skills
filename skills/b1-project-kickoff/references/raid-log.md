# RAID LOG — mẫu chuẩn (Risks · Assumptions · Issues · Dependencies)

> Sheet `RAID_Log` trong `*_Kickoff_Workbook.xlsx`. Đây là sổ theo dõi rủi ro dự án do PM sở hữu; x3 đọc để cảnh báo mục quá hạn, c6 đọc để đưa vào retro. Mục rủi ro không có chủ sở hữu và hạn xử lý là chưa được quản lý.

## 1. Cột bắt buộc

| Cột | Ý nghĩa | Quy tắc |
|---|---|---|
| `RAID-ID` | Mã duy nhất | `R-NN` (Risk), `A-NN` (Assumption), `I-NN` (Issue), `D-NN` (Dependency) |
| `Loại` | R / A / I / D | Chọn một |
| `Mô tả` | Điều gì có thể xảy ra / đã xảy ra | Một câu, có chủ ngữ, không mơ hồ |
| `Tác động` | Ảnh hưởng nếu xảy ra | Critical / High / Medium / Low theo thang `pipeline.md` |
| `Xác suất` | Khả năng xảy ra (R) | High / Medium / Low |
| `Điểm rủi ro` | Tác động × xác suất | Công thức: `=MATCH(tác_động,{"Low","Medium","High","Critical"},0)*MATCH(xác_suất,{"Low","Medium","High"},0)` — tham chiếu thang chuẩn |
| `Chủ sở hữu` | Người xử lý | Lấy từ `team[]` (`id`), KHÔNG để trống |
| `Biện pháp đối phó` | Tránh / giảm / chuyển / chấp nhận | Phải ghi cụ thể: làm gì, bao giờ |
| `Hạn xử lý` | Ngày | YYYY-MM-DD |
| `Trạng thái` | Open · In progress · Closed · Accepted | Đóng khi có bằng chứng |
| `Liên kết` | ID sang FEAT, TM, CR, BUG, DEC | Truy vết hai chiều |
| `Ngày cập nhật` | Lần sửa gần nhất | YYYY-MM-DD |

## 2. Quy tắc phân loại

- **Risk (R):** chưa xảy ra. Có kế hoạch đối phó bắt buộc.
- **Assumption (A):** điều đang coi là đúng để lập kế hoạch (vd "khách cung cấp API key trước tuần 2"). Nếu sai → chuyển thành Issue hoặc Risk. Mỗi A phải có người xác nhận với khách.
- **Issue (I):** đã xảy ra, đang cản trở. Phải có hạn xử lý và người chịu trách nhiệm; nếu ảnh hưởng `known_issues` thì đồng bộ.
- **Dependency (D):** phụ thuộc bên ngoài (khách, bên thứ ba, team khác). Ghi mốc cần có và hậu quả nếu trễ.

## 3. Nhịp cập nhật

- Cập nhật mỗi tuần trước buổi họp dự án; x3 đọc để báo "R có điểm ≥ High chưa có chủ sở hữu hoặc đã quá hạn".
- Risk đóng khi biến cố không còn khả năng xảy ra (ghi lý do). Không xóa dòng.
- Mục `Accepted` cần người ký (tên, ngày) — tương tự chấp nhận rủi ro trong threat model.

## 4. Ví dụ dòng (chỉ minh họa — thay bằng dữ liệu thật)

| RAID-ID | Loại | Mô tả | Tác động | Xác suất | Chủ sở hữu | Đối phó | Hạn | Trạng thái |
|---|---|---|---|---|---|---|---|---|
| R-01 | R | Chậm xác nhận yêu cầu tích hợp bên thứ ba làm trễ sprint 3 | High | Medium | `team[].id` của PM | Giảm: gửi danh sách câu hỏi P1 trước kickoff; xin mốc trả lời bằng văn bản | 2026-12-01 | Open |

## 5. Chuyển đổi sang các nơi khác

- Issue Critical/High có liên quan tới chất lượng → ghi thêm `known_issues[]` (có `id` trùng `I-NN`).
- Dependency có ngày → đưa vào `Project_Timeline` của a9 (mốc phụ thuộc).
- Assumption ảnh hưởng hợp đồng → đưa vào mục giả định của Proposal/SOW (b0).
