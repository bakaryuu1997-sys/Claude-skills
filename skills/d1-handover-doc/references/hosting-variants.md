# Biến thể theo hạ tầng (mục 5 Deployment, mục 9 Runbook)

> Chọn biến thể theo `tech_stack.hosting` / `tech_stack.ci_cd` trong context và theo `Deployment_Checklist.xlsx`, `Smoke_Test_Runbook.md`, `Release_Plan_v[N].docx` của bước phát hành.
> KHÔNG viết lại quy trình deploy/rollback của bước phát hành — mục 5 chỉ tóm tắt và dẫn chiếu tới các file đó, rồi bổ sung phần đặc thù vận hành bên dưới.
> Lệnh dưới đây là khung tham khảo. Mọi tên service, namespace, region, tag… phải thay bằng giá trị thật hoặc `[CẦN ĐIỀN]`.
> Không tìm thấy hosting trong context → hỏi người dùng; không mặc định Docker/SSH/PostgreSQL.

## A. Máy chủ/VM chạy container (Docker, Compose)

| Việc | Khung lệnh |
|---|---|
| Trạng thái | `docker ps`, `docker compose ps` |
| Log | `docker logs <service> --tail 200` |
| Khởi động lại | `docker compose restart <service>` |
| Rollback về image cũ | Ghi tag/digest bản trước (lấy từ `release.rollback_hash`/Release Plan) rồi `docker compose up -d` với tag đó |
| Truy cập máy chủ | Qua bastion/SSM/VPN theo chính sách khách; không để đường dẫn khoá cá nhân trong tài liệu |

## B. Kubernetes

| Việc | Khung lệnh |
|---|---|
| Trạng thái | `kubectl -n <ns> get pods,deploy` |
| Log | `kubectl -n <ns> logs deploy/<name> --tail=200` |
| Rollback | `kubectl -n <ns> rollout undo deploy/<name>` (kèm `rollout status`) |
| Scale | `kubectl -n <ns> scale deploy/<name> --replicas=<n>` |
| Ghi thêm | Context/cluster nào, ai có quyền, cách xin quyền tạm thời (break-glass) |

## C. PaaS / Serverless (Vercel, Cloud Run, Lambda, App Service…)

| Việc | Cần ghi |
|---|---|
| Rollback | Cách promote lại deployment/revision/alias trước (đường đi trên console hoặc CLI của nhà cung cấp) |
| Log & metric | Nơi xem (tên dashboard), thời gian giữ log |
| Giới hạn | Timeout, concurrency, quota, cold start; cảnh báo khi gần ngưỡng |
| Cấu hình | Biến môi trường nằm ở đâu, ai sửa được, redeploy có bắt buộc không |

## D. Cơ sở dữ liệu (chọn theo `tech_stack.database`)

| Loại | Backup logic (ví dụ) | Ghi chú |
|---|---|---|
| PostgreSQL | `pg_dump` / `pg_restore`; mật khẩu qua `PGPASSWORD` hoặc `.pgpass` do vault cấp, không gõ trực tiếp | PITR nếu bật WAL archiving/managed |
| MySQL/MariaDB | `mysqldump` / `mysql`; tuỳ chọn single-transaction cho InnoDB | PITR bằng binlog |
| MongoDB | `mongodump` / `mongorestore` | Replica set/oplog cho point-in-time |
| Managed DB (RDS, Cloud SQL, Atlas…) | Snapshot tự động + PITR của nhà cung cấp | Ghi rõ retention, vùng lưu, cách restore sang instance mới |

Migration: tên công cụ thật (Prisma/Alembic/Flyway/Liquibase…), cách xem phiên bản hiện tại, quy tắc rollback migration (Expand/Contract: bước Contract không đảo ngược — nêu rõ trong runbook).

## E. Cache, hàng đợi, lưu trữ object

Chỉ ghi các thành phần thực sự có trong `tech_stack`. Mỗi thành phần: lệnh/đường kiểm tra sức khoẻ, hậu quả khi mất dữ liệu (cache có thể mất, hàng đợi thì không), cách xoá/làm nóng lại.

## F. Kiểm tra sức khoẻ tối thiểu (mục 9, mọi biến thể)

- Health endpoint của API (URL thật từ `links.production_url`).
- Kết nối DB và cache (lệnh theo công cụ thật).
- Log lỗi gần nhất (nơi xem + truy vấn mẫu).
- Trạng thái nhà cung cấp phụ thuộc (trang status).
