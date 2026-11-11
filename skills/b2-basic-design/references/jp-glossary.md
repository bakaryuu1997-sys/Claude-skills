# Bảng thuật ngữ tiêu đề Nhật — Basic Design (b2)

Dùng khi `settings.languages.client_facing = ja`: tiêu đề hàng 1 của sheet, header cột và tên mục docx phải theo cột "ja" (không để sót tiếng Việt — `i18n-policy.md` quy tắc 6).
**Tên sheet trong workbook GIỮ NGUYÊN định danh tiếng Anh** (`Screen_List`…) vì `/x2-project-architecture`, `/b3-detail-design` và các skill sau tìm sheet theo tên; chỉ ô tiêu đề (hàng 1) ghi tên Nhật.

## Sheet và tiêu đề (hàng 1)

| Sheet (định danh) | Tiêu đề hàng 1 (ja) |
|---|---|
| `Screen_List` | 画面一覧 |
| `Function_List` | 機能一覧 |
| `Screen_Items` | 画面項目定義書 |
| `Message_List` | メッセージ一覧 |
| `External_IF` | 外部インターフェース一覧 |
| `Traceability` | トレーサビリティマトリクス |

## Header cột

| vi (spec trong SKILL.md) | ja |
|---|---|
| Mã chức năng (FN) | 機能ID |
| Mã MH (SCR) | 画面ID |
| Prototype id | プロトタイプID |
| Tên màn hình | 画面名 |
| Tên chức năng | 機能名 |
| Module | モジュール |
| FEAT ref / Mã yêu cầu | 要件ID |
| Vai trò truy cập / Vai trò sử dụng | 利用ロール(アクセス権限) |
| Kiểu giao diện / Loại điều khiển | 画面種別 / コントロール種別 |
| Mô tả chức năng chính | 機能概要 |
| Độ ưu tiên | 優先度 |
| Trạng thái | ステータス |
| Mã Item (ITM) | 項目ID |
| Tên Item | 項目名 |
| Kiểu dữ liệu | データ型 |
| Độ dài tối đa | 桁数(最大長) |
| Bắt buộc | 必須 |
| Quy tắc ràng buộc (validation UI) | 入力規則 |
| Giá trị mặc định | 初期値 |
| Điều kiện hiển thị / kích hoạt | 表示条件・活性制御 |
| Endpoint API / nguồn dữ liệu | 連携API・データソース |
| Sự kiện kích hoạt | イベント |
| Ghi chú nghiệp vụ | 備考 |
| Mã Message | メッセージID |
| Phân loại / Mức nghiêm trọng | 種別 / 重要度 |
| Điều kiện kích hoạt | 表示条件 |
| Kiểu hiển thị (Toast/Modal/Inline) | 表示方法 |
| Nội dung | メッセージ内容 |
| Mã IF / Tên giao diện | IF-ID / IF名 |
| Hướng (Inbound/Outbound) | 方向 |
| Giao thức / Định dạng / Tần suất | 方式 / データ形式 / 連携頻度 |
| Bảo mật & xác thực | セキュリティ・認証 |
| Xử lý lỗi / Fallback | エラー時の処理 |
| API Endpoint ánh xạ | APIエンドポイント |
| Bảng DB | DBテーブル |
| Mã Test | テストID |

Giá trị ô: `✅/⬜` → `○/－` khi ja; ngày `YYYY/MM/DD`; trạng thái `COVERED` → `網羅済`.

## Mục docx (Basic_Design)

| # | ja |
|---|---|
| 1 | 表紙・改訂履歴 |
| 2 | システム概要 |
| 3 | 機能構成(機能一覧) |
| 4 | 画面一覧 |
| 5 | 画面遷移 |
| 6 | 画面仕様 |
| 7 | 業務フロー |
| 8 | 外部インターフェース |
| 9 | メッセージ一覧 |
| 10 | 運用・帳票・バッチ要件(該当時) |
| 11 | UI/UX標準・承認欄 |

Xưng hô: 御中 sau tên công ty khách ở trang bìa; tên người ký có 様 / chức danh.
