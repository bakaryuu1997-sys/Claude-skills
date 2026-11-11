# Bố cục bản ghi Zengin (全銀協規定形式, 120 byte) — để sinh fixture và kiểm parser

> Chỉ nạp khi dự án xử lý điện văn 全銀 (振込データ). Đây là **mẫu tham chiếu có ghi rõ mức độ xác minh**. Trước khi dùng cho production, đối chiếu với đặc tả của NGÂN HÀNG ĐỐI TÁC (媒体仕様書) — bản đó là nguồn sự thật, không phải file này.

## 1. Quy ước đánh số

- **Bảng dưới đây đánh số 1-based** (byte đầu tiên = 1), đúng như hầu hết tài liệu ngân hàng.
- Khi viết code (JavaScript `slice`, Python `[a:b]`), phải đổi sang 0-based: `start0 = start - 1`, `end0 = end` (end inclusive ở bảng).
- Mọi offset trong test phải ghi kèm chú thích "1-based" hoặc "0-based" — không để trống.

## 2. Bản ghi dữ liệu (Data Record), 120 byte

| Trường | Độ dài | Vị trí 1-based | Kiểu | Mức xác minh |
|---|---|---|---|---|
| データ区分 (loại bản ghi = 2) | 1 | 1 | N | Theo quy ước chung của 全銀 |
| 被仕向銀行番号 (mã ngân hàng nhận, 4 số) | 4 | 2–5 | N | **Độ dài đã đối chiếu** (tài liệu ngân hàng công khai) |
| 被仕向銀行名 (tên ngân hàng nhận) | 15 | 6–20 | C | Suy ra từ thứ tự trường — **chưa đối chiếu độ dài** |
| 被仕向支店番号 (mã chi nhánh) | 3 | 21–23 | N | Suy ra — chưa đối chiếu |
| 被仕向支店名 (tên chi nhánh) | 15 | 24–38 | C | Suy ra — chưa đối chiếu |
| 手形交換所番号 | 4 | 39–42 | N | Suy ra; thường toàn số 0 |
| 預金種目 (loại tiền gửi: 1 普通, 2 当座, 4 貯蓄, 9 その他) | 1 | 43 | N | **Độ dài và mã giá trị đã đối chiếu** |
| 口座番号 (số tài khoản, căn phải, đệm 0) | 7 | 44–50 | N | **Độ dài và cách đệm đã đối chiếu** |
| 受取人名 (tên người nhận, kana nửa chiều) | 30 | 51–80 | C | **Độ dài đã đối chiếu**; vị trí 51–80 khớp các tài liệu đã thấy |
| 振込金額 (số tiền, căn phải, đệm 0) | 10 | 81–90 | N | **Độ dài và cách đệm đã đối chiếu** |
| 新規コード (mã mới) | 1 | 91 | N | Suy ra — chưa đối chiếu |
| 顧客コード1 (mã khách hàng của người gửi) | 10 | 92–101 | C | Suy ra — chưa đối chiếu |
| 振込指定番号 / 予備 | 19 | 102–120 | — | Phần còn lại — **không tự điền**, lấy đặc tả ngân hàng |

Quy tắc: nếu đặc tả ngân hàng khác bảng này ở bất kỳ trường nào, **đặc tả ngân hàng thắng**.

## 3. Đệm và căn lề

- Số (N): căn phải, đệm **0** bên trái. Ví dụ tiền 12,500 yên → `0000012500`.
- Chữ (C): căn trái, đệm **khoảng trắng** bên phải, chữ kana nửa chiều (半角). Ký tự ngoài bộ ký tự cho phép bị từ chối bởi ngân hàng — test phải có ca ký tự không hợp lệ.
- Số tài khoản: căn phải, đệm 0 (không có dấu gạch).

## 4. Bản ghi khác

- Header (区分 1), Trailer (区分 8: số bản ghi 6 số, tổng tiền 12 số), End (区分 9). Mỗi bản ghi đúng 120 byte. Thêm CR LF nếu đặc tả yêu cầu.

## 5. Cách sinh và kiểm

- Viết helper `padNum(value, len)` và `padText(value, len)` dùng `String.padStart/padEnd` theo **byte**, không theo ký tự (kana nửa chiều 1 byte, chữ Nhật 2 byte khi mã hóa Shift-JIS/UTF-8 — kiểm đúng bảng mã của ngân hàng).
- Test round-trip: sinh → parse bằng parser của dự án → các trường khớp, tổng độ dài = 120.
- Test biên: tên đúng 30 byte, số tiền 9,999,999,999 (10 số), tài khoản 7 số, mã ngân hàng bắt đầu bằng số 0.

## 6. Mức độ tin cậy của tài liệu này

- Độ dài và cách đệm: đã đối chiếu với tài liệu công khai của ngân hàng (xem nguồn bên dưới).
- Vị trí các trường còn lại: suy ra từ thứ tự chuẩn, **chưa đối chiếu từng byte**. Phải xác minh trước khi go-live.

Nguồn tham khảo đã dùng: tài liệu "振込先ファイル・フォーマット（全銀協規定形式）" của các ngân hàng công khai (ví dụ Kiraboshi Bank, MUFG) — kiểm tra lại phiên bản hiện hành trước khi dùng.
