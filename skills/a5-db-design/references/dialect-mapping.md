# DB Design — Bảng ánh xạ dialect SQL

> Nạp khi `tech_stack.database` KHÔNG phải PostgreSQL. Quy tắc thiết kế (naming, constraint, index) giữ nguyên; chỉ đổi cú pháp/kiểu theo bảng dưới. Dialect không có trong bảng → HỎI người dùng (AskUserQuestion), không đoán.

| Khái niệm | PostgreSQL (mặc định) | MySQL 8 / MariaDB 10.5+ | SQL Server 2019+ |
|---|---|---|---|
| PK tự tăng | `BIGSERIAL` hoặc `BIGINT GENERATED ALWAYS AS IDENTITY` | `BIGINT UNSIGNED AUTO_INCREMENT` | `BIGINT IDENTITY(1,1)` |
| PK UUID | `UUID DEFAULT gen_random_uuid()` | `CHAR(36)` hoặc `BINARY(16)` + `DEFAULT (UUID())` | `UNIQUEIDENTIFIER DEFAULT NEWID()` (hoặc `NEWSEQUENTIALID()`) |
| Chuỗi ngắn | `VARCHAR(n)` | `VARCHAR(n)` + `utf8mb4` | `NVARCHAR(n)` (cần tiếng Nhật/Việt) |
| Chuỗi dài | `TEXT` | `TEXT` / `LONGTEXT` | `NVARCHAR(MAX)` |
| Tiền | `NUMERIC(15,2)` | `DECIMAL(15,2)` | `DECIMAL(15,2)` |
| Ngày giờ có timezone | `TIMESTAMPTZ` | `DATETIME(3)` lưu UTC (không có tz) | `DATETIMEOFFSET(3)` |
| Boolean | `BOOLEAN DEFAULT false` | `TINYINT(1) DEFAULT 0` | `BIT DEFAULT 0` |
| JSON | `JSONB` (index GIN) | `JSON` (index qua generated column) | `NVARCHAR(MAX)` + `CHECK (ISJSON(col)=1)` |
| Mảng | `TEXT[]` hoặc bảng junction | bảng junction | bảng junction |
| Mặc định hiện tại | `DEFAULT NOW()` | `DEFAULT CURRENT_TIMESTAMP(3)` | `DEFAULT SYSDATETIMEOFFSET()` |
| `updated_at` tự cập nhật | trigger `set_updated_at()` | `ON UPDATE CURRENT_TIMESTAMP(3)` | trigger `AFTER UPDATE` |
| Partial index | `CREATE INDEX … WHERE …` | KHÔNG hỗ trợ → generated column + index, hoặc bỏ điều kiện | filtered index `CREATE INDEX … WHERE …` |
| CHECK enum | `CHECK (status IN (…))` | `CHECK (…)` (MySQL ≥ 8.0.16 mới thực thi) | `CHECK (…)` |
| Extension UUID | `CREATE EXTENSION pgcrypto` (PG < 13) | — | — |
| Transaction DDL | có (`BEGIN … COMMIT`) | KHÔNG (DDL auto-commit) → chạy từng bước, có file rollback | có |
| Comment bảng/cột | `COMMENT ON …` | `COMMENT '…'` trong DDL | `sp_addextendedproperty` |

Ghi vào sheet Assumptions: dialect đã chọn, phiên bản tối thiểu, điểm khác biệt đã áp dụng (đặc biệt: tz, partial index, transaction DDL).
