# Khung 12 mục của `Handover.docx` (và phụ lục A–C)

> Khung CHUNG, không gắn với một dự án. Mọi `[…]` là chỗ phải điền bằng dữ liệu thật của dự án
> (context, tài liệu các bước trước, người dùng). Không có dữ liệu → `[CẦN ĐIỀN]`; cấm giữ giá trị mẫu.
> Tài liệu gửi khách KHÔNG chứa mã bước nội bộ (A1…D3), tên nhà thầu cũ, hay tên dự án khác.
> Tên ví dụ dưới đây chỉ minh hoạ định dạng.

## 1. Executive Summary (1 trang, cho người ra quyết định)
Hệ thống làm gì, phục vụ ai; số module/endpoint/màn hình (đếm từ tài liệu thiết kế); ngày go-live thực tế (`release.date`) và phiên bản (`release.version`); đội tiếp quản và ngày bắt đầu; tình trạng chất lượng (số liệu từ Test Report của giai đoạn kiểm thử, ghi nguồn); số Known Issues đang mở theo severity.

## 2. System Architecture Overview
Sơ đồ Mermaid vẽ từ `tech_stack` + `integrations` thật (chỉ vẽ thành phần có thực), nhãn theo ngôn ngữ của tài liệu. Mô tả 1–2 câu cho từng thành phần: vai trò, nơi chạy, chủ sở hữu.

## 3. Technology Stack
Bảng `Layer | Technology | Version | Purpose | License/Support`. Version lấy từ lockfile/Dockerfile/CI; không biết → `[CẦN ĐIỀN]`. Chỉ liệt kê tầng có trong dự án.

## 4. Environment Inventory
Bảng `Environment | Mục đích | URL | Branch/Tag | Cách deploy | Người có quyền`. URL từ `links.production_url` / `links.staging_url`. Biến môi trường: chỉ liệt kê TÊN + phân loại Secret/Plain + nơi lưu (vault/secret manager) + bắt buộc hay không. TUYỆT ĐỐI không ghi giá trị secret hoặc credential thật.

## 5. Deployment Guide
Tóm tắt quy trình deploy bình thường, tiêu chí health check, rollback — DẪN CHIẾU `Release_Plan`, `Deployment_Checklist`, `Smoke_Test_Runbook` của bước phát hành (tên file + phiên bản), không viết lại. Phần bổ sung: quyền cần có, nơi lưu artefact/image, cách xác định phiên bản đang chạy, `release.rollback_hash`. Biến thể theo hạ tầng: `hosting-variants.md`.

## 6. Database Overview
Số bảng, kích thước ước tính, công cụ migration, ERD (dẫn chiếu file ERD của bước thiết kế DB). Backup/Retention/RPO/RTO/Restore drill: `ops-readiness.md` §2. Quy trình restore (lệnh theo công cụ thật), người có quyền.

## 7. API Reference
Base URL, cơ chế xác thực, tài liệu đầy đủ (OpenAPI/Postman file trong thư mục tài liệu, Swagger URL nếu có). Bảng endpoint quan trọng lấy từ API Design (health, auth, 3–5 endpoint nghiệp vụ chính). Hợp đồng lỗi: định dạng `{error:{code,message,details,requestId}}` và mã `ERR-<DOMAIN>-<NNN>` theo Error Map của thiết kế chi tiết.

## 8. Key Business Flows (cho support)
Mỗi luồng chính lấy từ Business Flow của thiết kế cơ bản: các bước, endpoint/màn hình liên quan, điểm có thể lỗi, log/metric để truy vết (dùng `requestId`). Luồng thất bại quan trọng (thanh toán, tích hợp bên ngoài) và cách đối soát.

## 9. Runbook — xử lý sự cố (mỗi sự cố có ID `INC-<NN>`)
Bảng bắt buộc, ID ổn định (D3 sẽ liên kết tới ID này, đừng đánh số lại giữa các bản):

| INC-ID | Severity | Triệu chứng | Nguyên nhân thường gặp | Chẩn đoán | Khắc phục | Kiểm chứng | RTO mục tiêu | Escalate |
|---|---|---|---|---|---|---|---|---|
| INC-01 | Critical/High/Medium | … | … | lệnh/đường xem | bước copy-paste được | lệnh/kết quả mong đợi | từ bảng RTO | L2 → L3 |

Tối thiểu 6 sự cố, lấy từ: rủi ro trong thiết kế, Known Issues, Test Report, `Smoke_Test_Runbook` (API lỗi toàn bộ, đăng nhập/IdP lỗi, DB không kết nối, tích hợp bên thứ ba lỗi, hiệu năng suy giảm, job nền kẹt, hết dung lượng/quota, hết hạn chứng chỉ). Chỉ ghi sự cố áp dụng cho kiến trúc thật. Kèm mục "Kiểm tra sức khoẻ hệ thống" (xem `hosting-variants.md` §F).

## 10. Monitoring & Alerting
Bảng công cụ (tên thật, URL, dùng để làm gì, ai có quyền). SLO/SLI/error budget và danh sách alert (điều kiện, severity, kênh, `INC-xx`): `ops-readiness.md` §1.

## 11. Known Issues & Tech Debt
Known Issues: đọc `known_issues[]` trong context (id, severity, status, ticket) + khuyến nghị workaround. Nếu còn Critical/High chưa đóng (xem Gate ở SKILL.md) phải ghi nổi bật cùng quyết định chấp nhận rủi ro của khách. Tech Debt: bảng `# | Hạng mục | Priority | Effort ước tính | Lý do chưa làm` — lấy từ Code Review/Security Audit/Retro; không bịa.

## 12. Support Contacts & Escalation
Danh bạ từ `team[]` (`side=vendor` = đội dự án; `side=client` = đầu mối khách), cột `Role | Tên | Email | Điện thoại | Giờ phủ`. Lịch trực và escalation: `ops-readiness.md` §3. Bên thứ ba: đầu mối + cách mở ticket. Thời hạn và SLA bảo hành: CHÉP ĐÚNG từ SOW (Statement of Work, điều khoản bảo hành) và ghi "xem Warranty_Scope trong UAT_SignOff_Workbook"; không tự đặt số P1 24h/…; thiếu → `[CẦN ĐIỀN]`.

## Phụ lục
- **A. Postmortem template** — `ops-readiness.md` §5.
- **B. DR/BCP** — `ops-readiness.md` §4.
- **C. Hypercare & cutover** — `ops-readiness.md` §6.
- **D. Lịch sử thay đổi tài liệu** — bảng `Phiên bản | Ngày | Người sửa | Nội dung`.

## Trang ký
`Bên bàn giao ký ____ | Bên tiếp nhận ký ____` kèm họ tên, chức danh, ngày (ngày theo `i18n-policy.md`).

## Định dạng docx
Cover (tên dự án, phiên bản, ngày), Table of Contents tự động (dùng heading styles), 12 mục + phụ lục, trang ký. Font theo `settings.languages.client_facing` (bảng font trong `i18n-policy.md`; đặt `w:eastAsia` cho tiếng Nhật).

## Runbook.md (cheat sheet)
Chỉ gồm: mục 4 (Environment — tên biến, không có giá trị secret) + mục 9 (bảng INC và chi tiết từng sự cố) + mục 12 (Contacts/On-call). Mỗi sự cố là một heading `## INC-<NN> — <tiêu đề>` để liên kết được. Code block copy-paste được, đã thay hết placeholder hoặc để `[CẦN ĐIỀN]` hiển thị rõ.
