# CI/CD PIPELINE SPEC — mẫu chuẩn

> Đặc tả pipeline tích hợp và triển khai, ghi tại `docs/C8_release-deployment/CICD_Spec.md`. Mục tiêu theo DORA: đo được tần suất triển khai, thời gian từ commit đến production, tỷ lệ thất bại khi thay đổi, thời gian khôi phục. Mọi ngưỡng lấy từ `settings.quality_gates` của context; KHÔNG tự đặt số.

## 1. Các giai đoạn (stage) và cổng (gate)

| Giai đoạn | Chạy khi | Việc phải làm | Cổng (chặn nếu không đạt) |
|---|---|---|---|
| **Lint & format** | mọi commit/PR | lint, format, type-check | 0 lỗi |
| **Unit test** | mọi commit/PR | chạy UT, đo coverage | pass ≥ `ut_pass_rate`; coverage dòng ≥ `ut_coverage_line` |
| **Build** | mọi commit/PR | build artifact có version | build thành công; artifact có tag commit |
| **Security scan** | mọi PR | SAST, quét secret, SCA (`npm audit`/`pip-audit`) | 0 `open_critical_high_max` |
| **Integration test** | merge vào nhánh chính | IT với DB thật (container) | pass ≥ `it_pass_rate` |
| **Deploy staging** | merge vào nhánh chính | triển khai tự động, migration thử | smoke test pass |
| **Smoke/E2E staging** | sau deploy staging | `smoke_test_runner.py` + E2E | pass ≥ `st_pass_rate` |
| **Phê duyệt production** | thủ công | Go/No-Go (xem `release-practices.md`) | có người ký trong `Release_Plan` |
| **Deploy production** | sau phê duyệt | canary hoặc blue-green, không big-bang | health check qua mốc canary |
| **Theo dõi sau deploy** | 60 phút đầu + hypercare | dashboard lỗi, latency, tỷ lệ 5xx | không vượt ngưỡng SLO |

## 2. Nguyên tắc bắt buộc

- **Build một lần, triển khai nhiều lần:** artifact staging và production là cùng một file, khác cấu hình.
- **Cấu hình theo môi trường tách khỏi mã** (12-factor): biến môi trường, không hardcode URL/khóa.
- **Bí mật không đi vào repo:** dùng secret store của nền tảng (GitHub Secrets, Vault, SSM…). Quét secret ở stage Security scan.
- **Migration DB tách khỏi deploy code** theo Expand → Migrate → Contract (chi tiết `release-practices.md`). Pha Contract không đảo ngược được — phải có người phê duyệt riêng.
- **Rollback đã thử:** mỗi lần phát hành phải có bước rollback được kiểm trên staging, không chỉ viết trên giấy.
- **Không deploy thứ sáu chiều và trước kỳ nghỉ** trừ khi có phê duyệt ngoại lệ (áp dụng lịch nghỉ lễ Nhật/Việt nếu dự án ở đó).

## 3. Khóa context liên quan

- `tech_stack.ci_cd` — nền tảng CI đang dùng.
- `links.git_repo`, `links.staging_url`, `links.production_url` — điểm truy cập.
- `release{}` — ghi sau mỗi lần phát hành (version, tag, date, rollback_hash).
- `known_issues[]` — `check_gate.py` chặn production nếu còn Critical/High mở.

## 4. Đo lường (DORA) — ghi vào `Smoke_Test_Runbook.md` hoặc báo cáo sprint

- Deployment Frequency: số lần deploy production trong kỳ.
- Lead Time for Changes: từ commit đầu tiên của PR đến production.
- Change Failure Rate: % lần deploy phải rollback hoặc hotfix.
- Time to Restore: thời gian từ phát hiện sự cố đến khôi phục.

Không có số liệu thật → ghi `[CHƯA ĐO]`, không ước lượng.

## 5. Checklist khi viết pipeline mới

- [ ] Mỗi stage có cổng và người sở hữu.
- [ ] Không có bước nào phụ thuộc máy cá nhân.
- [ ] Có log và artifact giữ đủ lâu để điều tra (ghi số ngày).
- [ ] Có đường thoát khẩn cấp (break-glass) có ghi nhật ký và người phê duyệt.
