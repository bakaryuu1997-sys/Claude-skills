# Chuẩn Python (áp dụng khi `tech_stack.backend` là Python: FastAPI, Django, Flask…)

## 1. Kiểu dữ liệu
- Type hints đầy đủ cho hàm public (service, repository, router). Chạy `mypy` hoặc `pyright` ở mức đã thống nhất trong dự án (`pyproject.toml`); không có cấu hình thì ghi "chưa có type checker" vào báo cáo thay vì tự bật.
- Cấm `Any` ở ranh giới API. Dùng `pydantic` (FastAPI) hoặc `serializers`/`forms` (Django) để validate tại biên.

## 2. Database & transaction
- Ghi nhiều bảng hoặc ghi kèm log lịch sử → `with session.begin():` (SQLAlchemy) / `transaction.atomic()` (Django).
- Migration qua Alembic/Django migrations; không sửa schema tay trên môi trường chung.

## 3. Lỗi
- Lớp exception nghiệp vụ có `status_code`, `code` (`ERR-<DOMAIN>-<NNN>`), `message`.
- Cấm `except Exception: pass`. Bắt đúng loại; log hoặc `raise … from e`.
- Handler trung tâm trả đúng format `{ error: { code, message, details?, requestId? } }`.

## 4. Cấu hình & fail-fast
- Đọc biến môi trường qua một module cấu hình (pydantic `BaseSettings` hoặc tương đương).
- Production thiếu biến bắt buộc → lỗi khi khởi động. Không dùng giá trị mặc định cho secret.

## 5. Kiểm tra trước merge
- `ruff`/`flake8` (lint), `mypy`/`pyright` (type), `pytest --cov` (coverage theo `settings.quality_gates`).
- Dán output thật vào PR description.
