# Đặc tả `Handover_Workbook.xlsx` (7 sheet) — tác nghiệp tra cứu nhanh

> Định dạng Excel theo `a1-project-init/references/excel-style.md` (nguồn duy nhất về màu, font, freeze pane, auto-filter, công thức thay cho số cứng).
> Ngôn ngữ và font theo `i18n-policy.md`. Công cụ: openpyxl (kiểm `ImportError`, báo cách cài `pip install openpyxl`).
> Dữ liệu từ context và tài liệu thật; không thấy → `[CẦN ĐIỀN]`. Giá trị biến môi trường: KHÔNG ghi giá trị thật.

| # | Tên sheet | Nội dung bắt buộc |
|---|---|---|
| 1 | `Overview_Signoff` | KPI (số module, endpoint, màn hình — dùng công thức COUNTA/COUNTIF trỏ sheet liên quan); tóm tắt bàn giao; điều kiện chấp nhận bàn giao (checklist có cột Trạng thái/Người xác nhận/Ngày); bảng ký 2 bên; lộ trình chuyển giao tri thức và hypercare (`ops-readiness.md` §6) |
| 2 | `Tech_Stack_Envs` | Các tầng công nghệ (version, vai trò, license); môi trường Prod/Staging/Dev; **ma trận biến môi trường**: Tên biến, Secret/Plain, Nơi lưu (vault/secret manager, tên path/ARN — không phải giá trị), Giá trị mẫu trung tính (không lộ credential), Bắt buộc?, Người cấp, Đã đối soát (Y/N) |
| 3 | `Database_Schema` | Mọi bảng: cột, kiểu, PK/FK/UK, Nullable, Default, index, cascade rule — nhập từ file DB Design, không tự bịa. Kèm khối Backup/Retention/RPO/RTO (`ops-readiness.md` §2) |
| 4 | `API_Catalog` | Method, path, chức năng, auth/permission, rate limit, DTO request/response, mã lỗi `ERR-<DOMAIN>-<NNN>` — từ API Design / Error Map |
| 5 | `Runbook_Matrix` | Cột: **INC-ID**, Severity (Critical/High/Medium), Triệu chứng, Nguyên nhân, Chẩn đoán, Khắc phục (copy-paste được), Kiểm chứng, RTO mục tiêu, Escalate, Liên quan alert. ≥ 6 dòng, ID trùng với `Runbook.md`. Khối thứ hai: **Backup & Restore drill log** (ngày, người, kết quả, thời gian thực tế, RPO/RTO đạt/không) |
| 6 | `Known_Issues_Debt` | Known issues từ `known_issues[]` (BUG-ID, severity, status, workaround, ticket), Tech debt (priority, effort, lý do), backlog phase sau. Tô màu theo severity |
| 7 | `Contacts_SLA` | Danh bạ vendor/client (`team[]`), lịch on-call, ma trận escalation, SLA theo severity (Critical/High/Medium/Low) và SLO/SLI (`ops-readiness.md` §1, §3). Thời hạn + SLA bảo hành: chép từ SOW, một dòng dẫn chiếu `Warranty_Scope` — không đặt số riêng |

## Chuẩn trình bày bổ sung (ngoài excel-style.md)
- Hiển thị gridlines, freeze pane dưới hàng tiêu đề, auto-filter cho mọi bảng dữ liệu.
- Status badge dùng bảng màu trong `excel-style.md` (không tự định nghĩa lại màu).
- Mỗi sheet có hàng nhãn nguồn: tên file + phiên bản + ngày lấy dữ liệu, để truy vết.
- Sheet 5 và `Runbook.md` là hai bản của cùng một dữ liệu: sinh từ cùng một nguồn trong code (một danh sách INC), không gõ hai lần.
