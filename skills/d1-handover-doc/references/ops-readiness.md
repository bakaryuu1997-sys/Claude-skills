# Sẵn sàng vận hành (Operational Readiness) — nội dung bắt buộc của Handover

> Dùng khi soạn mục 6, 9, 10, 12 và Phụ lục A–C của `Handover.docx`, và sheet 5, 7 của `Handover_Workbook.xlsx`.
> Mọi con số (SLO, RPO, RTO, retention, thời gian phản hồi) PHẢI lấy từ SOW / hợp đồng vận hành / người dùng.
> Chưa có số → ghi `[CẦN ĐIỀN]` và nêu vào danh sách "việc còn thiếu trước khi ký bàn giao". Cấm tự đặt số cho khách.

## 1. SLO / SLI (mục 10 Monitoring & Alerting)

| Cột | Nội dung |
|---|---|
| Dịch vụ / hành trình người dùng | Tên theo tài liệu thiết kế (vd luồng đăng nhập, luồng giao dịch chính) |
| SLI (chỉ số đo) | Tỷ lệ request thành công; p95/p99 latency của endpoint chính; độ trễ job nền; tỷ lệ lỗi 5xx |
| Nguồn đo | Tên công cụ monitoring thật (APM/log/synthetic) + tên dashboard/query |
| SLO (mục tiêu) | `[CẦN ĐIỀN]` hoặc số trích từ SOW (kèm cửa sổ đo: 30 ngày/7 ngày) |
| Error budget | = 100% − SLO trong cửa sổ đo; ghi cách xử lý khi cạn (đóng băng release, ưu tiên sửa lỗi) |
| Alert gắn với SLO | Burn-rate alert (nhanh/chậm) → kênh nhận → mức severity |

Alert phân mức theo thang chuẩn Critical / High / Medium / Low (xem `pipeline.md`, mục Quy ước dùng chung; sự cố vận hành: P1→Critical, P2→High, P3→Medium). Mỗi alert phải có: điều kiện, kênh, người nhận, `INC-xx` liên quan.

## 2. RPO / RTO / Backup / Retention / Restore drill (mục 6)

| Hạng mục | Cần ghi |
|---|---|
| RPO (mất dữ liệu tối đa) | Theo hệ thống: DB chính, object storage, hàng đợi, cấu hình. `[CẦN ĐIỀN]` nếu chưa chốt |
| RTO (thời gian khôi phục tối đa) | Theo mức sự cố / theo hệ thống. Cột RTO của `INC-xx` phải nhất quán với bảng này |
| Phương thức backup | Snapshot tự động của nhà cung cấp / dump logic / PITR (WAL, binlog). Ghi lịch chạy và nơi lưu (khác vùng/tài khoản với bản chính nếu có) |
| Retention | Số ngày/bản giữ cho từng loại backup; cách xoá; yêu cầu pháp lý/hợp đồng về lưu trữ dữ liệu (nếu có) |
| Mã hoá & quyền truy cập backup | Khoá quản lý ở đâu; ai được restore |
| Restore drill | Quy trình thử khôi phục sang môi trường tách biệt, tần suất (tối thiểu trước go-live và định kỳ theo SOW), kết quả lần gần nhất: ngày, người thực hiện, thời gian thực tế so với RTO, dữ liệu mất so với RPO, vấn đề phát sinh |

Chưa từng restore thử = ghi rõ "CHƯA KIỂM CHỨNG" ở mục 6 và đưa vào Known Issues với mức Medium trở lên.

## 3. On-call & Escalation (mục 12, sheet 7)

- Lịch trực (rota): vai trò, người, kênh liên lạc chính/phụ, múi giờ, giờ phủ (24x7 hay giờ hành chính — theo hợp đồng), cách đổi ca.
- Ma trận escalation: L1 (tiếp nhận) → L2 (kỹ sư vận hành) → L3 (dev/tech lead) → quản lý/khách. Thời gian chờ trước khi lên cấp theo severity.
- Quy tắc tuyên bố sự cố (incident): ai được tuyên bố, kênh war room, vai trò Incident Commander / Comms / Scribe.
- Bên thứ ba (IdP, thanh toán, push, cloud): đầu mối, hợp đồng hỗ trợ, cách mở ticket, trang trạng thái.

## 4. DR / BCP (Phụ lục B)

- Kịch bản thảm hoạ cần phủ: mất vùng/AZ, mất DB chính, mất nhà cung cấp phụ thuộc, lộ thông tin xác thực, xoá nhầm dữ liệu.
- Với mỗi kịch bản: tác động, cách phát hiện, quyết định failover/restore (ai quyết định), bước khôi phục tham chiếu `INC-xx`, RTO/RPO mục tiêu, liên lạc với khách/người dùng.
- Chiến lược: backup-restore / pilot light / warm standby / active-active — ghi mức đang áp dụng thực tế, không ghi mức mong muốn.
- Kế hoạch duy trì hoạt động nghiệp vụ khi hệ thống ngừng (quy trình thủ công tạm thời) — hỏi khách; nếu khách chưa có → `[CẦN ĐIỀN]`.
- Lịch diễn tập DR và người chịu trách nhiệm.

## 5. Postmortem template (Phụ lục A)

Blameless, điền trong vòng 5 ngày làm việc sau sự cố Critical/High:

```
# Postmortem — INC-<NN> / <mã sự cố của hệ thống ticket> — <tiêu đề>
Ngày: <YYYY-MM-DD> | Severity: <Critical|High|Medium> | Incident Commander: <tên> | Người viết: <tên>
## Tóm tắt (3 câu: chuyện gì, ảnh hưởng ai, kéo dài bao lâu)
## Tác động (số người dùng/giao dịch bị ảnh hưởng — trích từ log/metric, ghi nguồn; vi phạm SLO? mất dữ liệu?)
## Timeline (UTC+<offset>): phát hiện → báo động → tuyên bố → giảm thiểu → khôi phục → đóng
## Nguyên nhân gốc (5 Whys) và yếu tố góp phần
## Điều làm tốt / điều chưa tốt / may mắn
## Hành động khắc phục (ACT-<NN>): mô tả | owner | hạn | ticket | loại (phòng ngừa/phát hiện/giảm thiểu)
## Bài học và cập nhật Runbook (INC-xx nào cần sửa)
```

## 6. Hypercare (Phụ lục C, sheet 1)

- Khoảng thời gian (theo SOW; `[CẦN ĐIỀN]` nếu chưa có) ngay sau go-live, đội dự án phối hợp trực với đội vận hành.
- Nội dung: giờ phủ, kênh, tần suất stand-up/tổng kết ngày, ngưỡng thoát hypercare (vd N ngày liên tục không sự cố Critical/High, SLO đạt trong cửa sổ đo, restore drill đã thực hiện), người ký thoát.
- Cutover checklist: đóng băng thay đổi, xác nhận backup trước cutover, smoke test sau deploy (tham chiếu `Smoke_Test_Runbook.md` của bước phát hành), xác nhận monitoring/alert đang hoạt động, thông báo người dùng.
- Chuyển giao tri thức 4 tuần (Overview_Signoff): tuần 1 kiến trúc và luồng nghiệp vụ; tuần 2 reverse shadowing (bên nhận thao tác, bên giao quan sát); tuần 3 forward shadowing; tuần 4 cổng bàn giao đầy đủ và diễn tập sự cố giả định. Điều chỉnh độ dài theo hợp đồng.
