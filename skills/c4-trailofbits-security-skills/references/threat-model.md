# THREAT MODEL — mẫu chuẩn (STRIDE + OWASP ASVS)

> Dùng khi dự án có đăng nhập, dữ liệu cá nhân (個人情報), thanh toán, hoặc tích hợp bên thứ ba. Kết quả đi vào `Security_Audit_Report.md` (vector V-THREAT) và vào `NFR` của a2. Tên hệ thống, dữ liệu, bên liên quan LẤY TỪ `project-context.json` và tài liệu đã có — KHÔNG bịa.

## 1. Bước 1 — Vẽ phạm vi (DFD mức 1)

Liệt kê: tác nhân (người dùng, admin, hệ thống ngoài), tiến trình (API, worker, batch), kho dữ liệu (DB, file, cache), luồng dữ liệu (HTTP, queue, webhook). Vẽ bằng Mermaid `flowchart LR`, nhãn tiếng Nhật/Việt theo `settings.languages`. Ranh giới tin cậy (trust boundary): trình duyệt ↔ API, API ↔ DB, hệ thống ↔ bên thứ ba.

## 2. Bước 2 — STRIDE theo từng luồng cắt qua ranh giới

| Mối đe dọa | Câu hỏi kiểm | Kiểm soát thường dùng | ASVS (tham chiếu) |
|---|---|---|---|
| **S**poofing (giả mạo danh tính) | Có xác thực mạnh? Token có hết hạn, bị thu hồi được không? | MFA cho admin, token ngắn hạn + refresh, không tin header do client gửi | V2, V3 |
| **T**ampering (sửa dữ liệu) | Dữ liệu từ client có được kiểm tra toàn vẹn? | Validate phía server, ký webhook (HMAC), khóa lạc quan (version) | V5, V13 |
| **R**epudiation (chối bỏ) | Hành động quan trọng có nhật ký không sửa được? | Audit log append-only: ai, lúc nào, gì, từ đâu | V7 |
| **I**nformation disclosure (lộ thông tin) | PII có bị lộ trong log, lỗi, URL, cache? | Mã hóa at-rest/in-transit, mask PII, thông báo lỗi chung | V6, V8 |
| **D**enial of service (từ chối dịch vụ) | Endpoint nào tốn tài nguyên không giới hạn? | Rate limit theo người dùng/IP, giới hạn kích thước upload, timeout | V11 |
| **E**levation of privilege (leo quyền) | Kiểm tra quyền ở server cho MỌI endpoint hay chỉ ở UI? | RBAC/ABAC ở tầng service, kiểm tra sở hữu tài nguyên (IDOR) | V4 |

Mỗi dòng có: mã mối đe dọa `TM-<NN>`, luồng liên quan, mức rủi ro (xác suất × tác động, Critical/High/Medium/Low theo `pipeline.md`), kiểm soát đề xuất, trạng thái (có / thiếu / chấp nhận rủi ro có người ký).

## 3. Bước 3 — Ghi bằng chứng

- Mỗi "có" phải trỏ tới file:dòng hoặc cấu hình cụ thể. Không có bằng chứng → ghi "thiếu".
- Mỗi "thiếu" Critical/High → vào `known_issues[]` (id `TM-xx`, severity, status open). Gate `check_gate.py` sẽ chặn go-live.
- Mối đe dọa được chấp nhận → cần tên người ký và ngày, lưu trong `links.threat_model` (đường dẫn file).

## 4. Bước 4 — Liên kết

- NFR bảo mật của a2 (`NFR-SEC-xx`) phải có ít nhất một dòng cho mỗi TM Critical/High.
- Test case bảo mật của a8 (viewpoint Security) truy vết được về `TM-<NN>`.
- Sau khi đổi kiến trúc lớn → cập nhật threat model (x2 báo khi `links.architecture_file` cũ hơn).

## 5. Lưu ý

- Threat model là tài liệu sống, không phải báo cáo một lần. Ghi phiên bản và ngày.
- Không đưa tên khách, địa chỉ IP thật, token, hay cấu hình production vào file này.
