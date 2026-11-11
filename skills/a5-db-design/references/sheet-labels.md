# DB Design — Nhãn sheet / cột theo ngôn ngữ

> Ngôn ngữ file chọn theo `i18n-policy.md`: DB Design là tài liệu `internal` (đổi sang `client_facing` nếu khách yêu cầu bàn giao tài liệu này). Chọn MỘT cột ngôn ngữ cho TOÀN BỘ tên sheet + header + nhãn; không trộn Nhật/Việt/Anh trong cùng file. Thiếu `settings.languages` → hỏi 1 lần theo `i18n-policy.md`.
> Font: `ja` → Yu Gothic; `vi`/`en` → Arial (xem bảng font trong `i18n-policy.md`).

## Tên sheet

| Sheet | vi | en | ja |
|---|---|---|---|
| 1 | Tổng quan & ERD | Overview & ERD | 概要・ERD一覧 |
| 2 | Mô hình dữ liệu | Data Model | データモデル |
| 3 | Quan hệ & Khóa ngoại | Relations & Foreign Keys | リレーション・外部キー |
| 4 | Thiết kế Index | Index Design | インデックス設計 |
| 5 | Health Check | Health Check | ヘルスチェック |
| 6 | Giả định & Ghi chú migration | Assumptions & Migration Notes | 前提・移行メモ |

## Header 6 cột của card bảng (Sheet 2)

| Cột | vi | en | ja |
|---|---|---|---|
| 1 | Tên cột (vật lý) | Column (physical) | カラム名 |
| 2 | Tên logic | Logical name | 論理名 |
| 3 | Kiểu dữ liệu | Data type | 型 |
| 4 | NULL / Bắt buộc | NULL / Required | NULL / 必須 |
| 5 | Ràng buộc & mặc định | Constraints & default | 制約・デフォルト |
| 6 | Mô tả & quy tắc nghiệp vụ | Description & rules | 説明・業務ルール |

## Header Sheet 3 / 4

- Sheet 3: `No | Bảng nguồn | Cột FK | Bảng đích | Cột đích (PK) | Quan hệ | ON DELETE | ON UPDATE | Ý nghĩa` — dịch tương ứng sang ngôn ngữ đã chọn (ja: `No | 参照元テーブル | FKカラム | 参照先テーブル | 参照先カラム | 関係 | ON DELETE | ON UPDATE | 業務上の意味`).
- Sheet 4: `No | Bảng | Tên index | Cột | Loại (B-Tree/GIN/Partial/Unique) | Điều kiện lọc | Mục đích / endpoint` — dịch tương ứng (ja: `No | テーブル | インデックス名 | 対象カラム | 種別 | 絞込条件 | 目的・対象API`).

Tên bảng/cột vật lý, kiểu dữ liệu và từ khóa SQL luôn giữ nguyên (snake_case, tiếng Anh).
