# Thực hành phát hành — tài liệu tham chiếu cho c8

Skill c8 dựng bộ hồ sơ phát hành. File này là các quy ước thực hành đi kèm; chi tiết theo từng dự án lấy từ `project-context.json` (`tech_stack`, `links`, `release`, `team`).

## 1. Phiên bản & changelog
- **SemVer** `MAJOR.MINOR.PATCH`: MAJOR = thay đổi không tương thích API/hợp đồng; MINOR = tính năng tương thích ngược; PATCH = sửa lỗi tương thích. Phiên bản đầu của hệ thống mới: `1.0.0` khi go-live, trước đó `0.x`.
- **Keep a Changelog**: mẫu `assets/CHANGELOG.template.md`. Mục Security không nêu chi tiết khai thác trước khi đã vá trên mọi môi trường.
- Tag Git: `v<MAJOR>.<MINOR>.<PATCH>` trên commit đã qua CI và đã có biên bản Go. Không đổi tag đã publish (tạo tag mới).
- Nhánh: trunk-based (`main` + nhánh ngắn) hoặc `release/x.y` nếu cần hotfix song song. Ghi rõ dự án dùng cái nào trong Release_Plan.
- Ghi vào context sau phát hành: `release.version`, `release.tag`, `release.date`, `release.rollback_hash` (commit để rollback về).

## 2. Quy trình phê duyệt phát hành (リリース判定)
- Go/No-Go: người quyết định được ghi trong `team[]` (`role` = Release Lead / PM / QA Lead / DB Admin, `side` = vendor hoặc client). Biên bản có ngày, danh sách điều kiện và chữ ký.
- Điều kiện Go tối thiểu: CI xanh; `check_gate.py` exit 0 (không còn Critical/High mở — exit 3 coi là chưa kiểm được, không được Go); c5 đạt QUALIFIED; c4 không có Critical/High chưa xử lý; c8 smoke staging đạt; rollback đã được diễn tập.
- Đối với hệ thống có khách nghiệm thu (D2): nghiệm thu UAT ký trước khi đưa lên production hoặc theo thỏa thuận trong SOW.
- Change calendar / CAB: thông báo cửa sổ bảo trì trước tối thiểu theo SLA đã thỏa thuận; tránh khung giờ kinh doanh cao điểm của khách (ghi rõ múi giờ).

## 3. Chiến lược triển khai
| Chiến lược | Khi dùng | Điều kiện |
|---|---|---|
| Rolling | Ứng dụng stateless, nhiều instance | Phiên bản cũ và mới phải tương thích tạm thời (expand trước) |
| Blue-green | Cần chuyển đổi tức thì và rollback nhanh | Đủ tài nguyên gấp đôi; DB phải tương thích cả hai phiên bản |
| Canary | Rủi ro cao, cần đo trước khi mở rộng | Có metric so sánh (lỗi 5xx, latency) và ngưỡng dừng tự động |
| Feature flag | Tách deploy khỏi release | Flag có chủ sở hữu, ngày gỡ, và bản test cả hai trạng thái |

Frontend tĩnh/CDN: purge cache theo phiên bản (hash tên file), kiểm tra service worker không giữ bản cũ.

## 4. Cơ sở dữ liệu
- **Expand → Migrate → Contract.** Pha **Contract** (xóa cột/bảng cũ) là **điểm không quay lại**: chỉ thực hiện sau khi phiên bản mới đã chạy ổn định qua một chu kỳ nghiệp vụ đủ dài (quyết định theo dự án, ghi rõ số ngày). Không gộp Contract vào cùng đợt deploy với Expand.
- DDL trên PostgreSQL: đặt `SET lock_timeout = '3s'` ở đầu migration (MySQL: tương đương `lock_wait_timeout`); index lớn dùng `CREATE INDEX CONCURRENTLY` ngoài transaction. Không áp dụng cú pháp PostgreSQL cho DB khác mà không kiểm tra.
- Backfill theo lô có điều kiện dừng và tiến độ; không khóa bảng lớn trong một câu lệnh.
- Rollback dữ liệu: **ưu tiên PITR** (point-in-time recovery) đến thời điểm trước deploy thay vì "restore snapshot" (snapshot cũ làm mất các ghi sau snapshot). Ghi thời điểm PITR cần thiết trong Rollback_Plan.
- Diễn tập: restore backup ra môi trường tạm và đo thời gian (RTO thực tế). Số đo ghi vào hồ sơ, không ước lượng.

## 5. Rollback
- Trigger tự động/thủ công được định nghĩa trước (ví dụ tỷ lệ 5xx, lỗi nghiệp vụ, migration thất bại) — ngưỡng lấy từ NFR dự án.
- Rollback ứng dụng: về `release.rollback_hash` bằng artefact cũ (không build lại). Rollback DB: chỉ hoàn tác được các pha Expand; pha Contract không hoàn tác được — vì vậy Contract phải có đợt riêng và tiêu chí riêng.
- Thời gian thực hiện rollback (RTO) và người có quyền quyết định ghi rõ trong Release_Plan.

## 6. Kiểm tra sau phát hành (post-release verification)
1. Smoke test production bằng `scripts/smoke_test_runner.py` (kiểm tài khoản/dữ liệu test có chủ đích, không thao tác ghi dữ liệu thật của khách).
2. Dashboard theo dõi: lỗi 5xx, latency p95, số đăng nhập thành công, lỗi nghiệp vụ, queue backlog — so sánh với mức trước deploy trong 30–60 phút đầu.
3. Log/alert: có người trực theo War Room trong thời gian cửa sổ phát hành.

## 6b. Hypercare
- Giai đoạn theo dõi sau go-live (thường 1–2 tuần, theo SOW): đội phát triển trực, SLA phản hồi theo mức Critical/High/Medium/Low (pipeline.md §1), họp hằng ngày ngắn.
- Kết thúc hypercare: biên bản ghi số incident, bug mở, bàn giao sang vận hành (D1).

## 7. Phát hành mobile
- App Store / Google Play có thời gian duyệt riêng; không hứa ngày go-live nếu chưa có ngày duyệt.
- Phiên bản build number tăng đơn điệu; ghi rõ bản nào hỗ trợ API nào (phải tương thích ngược với các bản chưa cập nhật).
- Chiến lược: staged rollout theo phần trăm người dùng; có kế hoạch cho bản cũ không tương thích (force-update) và ghi rõ trong thông báo khách.
- Không thể rollback bản đã phát hành trên store — rollback = phát hành bản vá mới hoặc tắt tính năng bằng server-side flag.

## 8. Truyền thông & hỗ trợ
- Thông báo người dùng: thời điểm bảo trì, ảnh hưởng, kênh (email, banner); mẫu nội dung theo `settings.languages.client_facing`.
- Sự cố: ghi incident với ID `INC-<NN>` (D1 Runbook), mức độ theo thang chuẩn, người nhận báo cáo, thời điểm bắt đầu/kết thúc.
- Post-mortem không đổ lỗi cá nhân: nguyên nhân gốc, hành động phòng ngừa (ACT-<NN>), owner, hạn.

## 9. Ghi nhận
Mỗi lần phát hành: cập nhật `release{}` trong context, `activity_log`, và đưa Release_Plan + Smoke_Test_Runbook sang D1 (/d1-handover-doc).
