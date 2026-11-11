# Bảng thuật ngữ tiêu đề Nhật — Detail Design (b3)

Dùng khi tài liệu b3 viết bằng tiếng Nhật (key `internal` hoặc `client_facing` = `ja` theo `i18n-policy.md`). Tên sheet GIỮ định danh tiếng Anh (c0/c1/c2 và `check_crud_coverage.py` tìm theo tên); chỉ ô tiêu đề (hàng 1) và header cột đổi sang tiếng Nhật.

| Sheet (định danh) | Tiêu đề hàng 1 (ja) |
|---|---|
| `Class_List` | クラス一覧 |
| `Method_List` | メソッド一覧 |
| `CRUD_Matrix` | CRUDマトリクス |
| `Validation_Spec` | バリデーション仕様 |
| `Error_Map` | エラーコード一覧 |
| `Traceability` | トレーサビリティ行列 |

| vi | ja |
|---|---|
| Mã Class / Method | クラスID / メソッドID |
| Tên Class | クラス名 |
| Tầng (Layer) | レイヤ |
| Trách nhiệm chính | 責務 |
| Phụ thuộc | 依存関係 |
| Tham số đầu vào / Kiểu trả về | 引数 / 戻り値 |
| Mô tả logic xử lý | 処理概要 |
| Exceptions ném ra | 例外 |
| Transaction / DB | トランザクション・DB |
| Mã FN / Mã SCR / Mã ITM | 機能ID / 画面ID / 項目ID |
| Endpoint API | APIエンドポイント |
| Tên field / Bắt buộc | 項目名 / 必須 |
| Kiểu dữ liệu / Giới hạn | データ型 / 桁数・範囲 |
| Định dạng / Regex | 形式(正規表現) |
| Quy tắc nghiệp vụ | 業務ルール |
| Mã lỗi | エラーコード |
| Điều kiện kích hoạt | 発生条件 |
| HTTP Status / Exception Class | HTTPステータス / 例外クラス |
| Thông điệp hiển thị | 表示メッセージ |
| Chiến lược xử lý | 対処方針 |
| Ghi chú Transaction | トランザクション備考 |
| Trạng thái `COVERED` | 網羅済 |

Mục docx: 1 表紙・改訂履歴 · 2 内部アーキテクチャ · 3 クラス・モジュール設計 · 4 シーケンス図 · 5 処理ロジック(擬似コード) · 6 DBアクセス設計・CRUD · 7 入力チェック仕様 · 8 メソッド一覧 · 9 例外処理・ログ設計 · 10 セキュリティ・性能・承認欄。
