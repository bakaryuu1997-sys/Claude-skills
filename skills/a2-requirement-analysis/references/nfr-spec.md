# NFR SPEC — đặc tả yêu cầu phi chức năng (mẫu chuẩn)

> Sheet `NFR` trong `*_Requirement_Specification.xlsx`. Căn cứ phân loại: ISO/IEC 25010 (tính năng, hiệu năng, khả dụng, bảo mật, khả năng bảo trì, khả năng di chuyển, khả năng sử dụng, tương thích…). Mỗi NFR phải ĐO ĐƯỢC và có cách kiểm; NFR không đo được ("nhanh", "an toàn") bị đánh dấu `[CẦN LÀM RÕ]` và đưa vào Q&A với khách.

## 1. Cột bắt buộc

| Cột | Quy tắc |
|---|---|
| `NFR-ID` | `NFR-<LOẠI>-<NN>`, LOẠI ∈ PERF, AVAIL, SEC, MAINT, COMPAT, USAB, PRIV, OPS |
| `Loại (ISO 25010)` | Một trong 8 đặc tính |
| `Yêu cầu` | Câu khẳng định có số đo: "p95 ≤ 500 ms cho `GET /v1/orders` ở 200 req/s" |
| `Chỉ số` | Tên đại lượng: latency p95, RPO, RTO, tỷ lệ 5xx, thời gian khôi phục… |
| `Mục tiêu` | Con số cụ thể + đơn vị |
| `Cách kiểm` | Công cụ/phương pháp: k6 (a8 đã có kế hoạch k6), đo staging, audit log, pen test |
| `Mức ưu tiên` | Must / Should / Could (MoSCoW) |
| `Nguồn` | Từ hợp đồng, từ khách phát biểu (ghi ngày), hay đề xuất của đội (cần khách duyệt) |
| `Liên kết` | FEAT-…, TM-…, TC-… |
| `Trạng thái` | Đề xuất / Đã chốt với khách / Đã kiểm |

## 2. Mục tối thiểu phải có cho một hệ thống nghiệp vụ

- **Hiệu năng:** thời gian phản hồi p95 cho 5 luồng nghiệp vụ chính; số người dùng đồng thời; thông lượng.
- **Khả dụng:** SLA (vd 99.5% tháng), giờ bảo trì, RPO, RTO (lấy từ hợp đồng nếu có).
- **Bảo mật:** xác thực (MFA cho quản trị), phân quyền theo vai trò, mã hóa at-rest và in-transit, nhật ký kiểm toán không sửa được, kiểm tra SAST/SCA trước release (liên kết c4).
- **Dữ liệu cá nhân (個人情報):** phạm vi PII, thời hạn lưu, quyền xóa/xuất dữ liệu, vị trí lưu trữ. Nếu có, liên kết threat model.
- **Bảo trì:** độ phủ test tối thiểu (lấy từ `quality_gates`), thời gian triển khai, tài liệu vận hành (d1).
- **Tương thích & trình duyệt/thiết bị:** danh sách cụ thể, phiên bản tối thiểu; WCAG cấp độ (vd AA) nếu khách yêu cầu.
- **Ngôn ngữ & múi giờ:** ngôn ngữ UI theo `settings.languages.client_facing`; múi giờ hiển thị; định dạng ngày/số.
- **Vận hành:** giám sát (log, metric, alert), cảnh báo ai nhận, backup và kiểm khôi phục (restore drill).

## 3. Quy tắc viết

- Không dùng: "nhanh", "tiện lợi", "an toàn", "ổn định", "dễ dùng" — thay bằng chỉ số.
- Một NFR một đo lường. Nếu có hai đo lường → tách hai dòng.
- Khách chưa cho số → đề xuất giá trị mặc định kèm nguồn "đề xuất của đội", đánh dấu cần khách duyệt. KHÔNG ghi như thể khách đã chốt.
- Số liệu phải trích từ tài liệu hoặc câu trả lời của khách; không bịa số để cho đẹp.

## 4. Kiểm tra trước khi chuyển sang thiết kế (B2)

- [ ] Mỗi NFR Must có cách kiểm cụ thể.
- [ ] Mọi NFR bảo mật Critical/High có ít nhất một TM tương ứng.
- [ ] Không còn NFR nào chỉ có tính từ.
- [ ] Mục "Đề xuất của đội" đã có chữ ký duyệt của khách hoặc đánh dấu chờ.
