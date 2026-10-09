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

## Chiều cao dòng (Row Height) & Chống lỗi cắt chữ / đè dòng (Anti-Text-Clipping)
- **TUYỆT ĐỐI KHÔNG hardcode chiều cao cố định nhỏ** (như `height = 20` hay `22`) cho các dòng chứa cột mô tả dài có `wrap_text=True`. Việc này sẽ khóa cứng chiều cao ô, khiến dòng thứ 2, thứ 3 bị đè chèn và mất chữ (như lỗi 2 dòng đè 1).
- **Quy tắc tính chiều cao dòng động (Dynamic Row Height)**:
  - Nếu xét chiều cao thủ công: Tính theo số dòng quấn thực tế: `height = max(24, total_lines * 19 + 8)`.
    - 1 dòng: `height = 24–26`
    - 2 dòng: `height = 42–46`
    - 3 dòng: `height = 60–66`
    - 4 dòng trở lên: `height = total_lines * 19 + 8`
  - Hoặc để `row_dimensions[row].height = None` (để trống) để Excel tự động tính toán auto-fit dòng theo nội dung.
- Căn lề dọc: luôn đặt `vertical="center"` kèm padding để chữ thoáng và chuyên nghiệp.

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

## Tính Chuyên Nghiệp & Cấm Lộ Mã Nội Bộ (Professional Client-Facing Standards)
- **TUYỆT ĐỐI CẤM** viết các mã bước nội bộ của AI/pipeline như `A1`, `A2`, `A3`, `A4`, `A5`, `A6`, `B1`, `C1`, `D1`... vào nội dung tài liệu giao cho khách hàng hoặc thành viên team (cột Assumption, Task Detail, Notes, Scope, Header, Title...).
- Khách hàng và các thành viên khác sẽ không hiểu `A3` hay `A5` là gì!
- **BẮT BUỘC** viết rõ tên tài liệu / nghiệp vụ chính thức bằng ngôn ngữ dự án (Tiếng Nhật/Việt):
  - Thay `A3プロトタイプ準拠` bằng `画面プロトタイプ仕様書準拠` (UIプロトタイプ合意仕様)
  - Thay `A5設計書準拠` bằng `データベース物理設計書準拠` (DB物理設計仕様)
  - Thay `A4設計書準拠` bằng `API設計仕様書準拠`
  - Thay `A2要件仕様` bằng `要件定義書・業務フロー仕様`
  - Thay `D1ハンドオーバー` bằng `運用保守引継書・Runbook`
  - Thay `A9スケジュール` bằng `プロジェクト工程表(ガントチャート)`

## Kỷ Luật Ngôn Ngữ Đồng Nhất 100% (Zero Language Leak)
- **Đồng bộ tuyệt đối theo ngôn ngữ dự án**: Nếu dự án là tiếng Nhật (`client_facing = ja`), **100% các ô, các sheet, header, comment, điều khoản, mẫu template** phải bằng tiếng Nhật.
- **CẤM RÒ RỈ TIẾNG VIỆT/NGOẠI NGỮ KHÁC**: Khi sử dụng template có sẵn (như 見積書 trong /a7), BẮT BUỘC phải rà soát và dịch sạch toàn bộ các block đi kèm (`手順書作成`, `結合テスト`, `前提条件`, `成果物一覧`...), tuyệt đối không để sót tiếng Việt từ template mẫu gốc của công ty/dự án cũ.
- **CẤM RÒ RỈ THƯƠNG HIỆU BÊN THỨ BA (Rikkei, v.v.)**: Tuyệt đối không để tên công ty outsource cũ (`Rikkei`, `Rikkeisoft`, `リッケイ`, v.v.) hay thông tin tổ chức không liên quan xuất hiện trong file Excel (đặc biệt là sheet `表紙`, `見積書` phần bên nhận thầu/受注者). Phải lấy tên đối tác phát triển từ `project-context.json` hoặc để trung tính `システム開発受託チーム`.

## Thực thi
```bash
pip install "openpyxl==3.1.*" --break-system-packages -q && python <script.py>
```
