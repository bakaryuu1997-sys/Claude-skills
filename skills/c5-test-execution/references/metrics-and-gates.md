# Metrics & Quality Gate — định nghĩa thống nhất

Nguồn tính: `scripts/test_metrics.py` (cùng công thức với bảng dưới — nếu khác, script là đúng và tài liệu phải sửa).

| Metric | Công thức | Ghi chú |
|---|---|---|
| Execution rate | (pass + fail + blocked) / (tổng − N/A) | Không chạy hết = chưa đạt |
| Pass rate | pass / (pass + fail) | Blocked không vào mẫu số, nhưng phase có blocked thì không QUALIFIED |
| Defect density | số bug / số test case (hoặc / KLOC nếu có LOC từ c3) | Báo cáo theo phase, không so sánh giữa dự án khác nhau |
| Open Critical/High | bug có severity Critical/High và status ∉ {verified, closed, wontfix} | Gate: phải ≤ `open_critical_high_max` (mặc định 0) |
| UNVERIFIED_FIX | bug closed/verified thiếu regression_test_id, regression_impact_scope, required_regression_suites hoặc verified_commit | Chặn gate cho đến khi bổ sung |

## Ánh xạ mức độ
Thang chuẩn Critical/High/Medium/Low (`pipeline.md` §1). P1–P4 (backlog) và Sev1–Sev4 (UAT) quy về thang này theo bảng cùng file.

## QUALIFIED khi (phase UT/IT/ST)
1. Không có test notrun hoặc blocked.
2. Open Critical/High ≤ ngưỡng.
3. Không có UNVERIFIED_FIX.
4. Pass rate ≥ ngưỡng của phase (`ut_pass_rate` / `it_pass_rate` / `st_pass_rate`).
5. UT: coverage line ≥ `ut_coverage_line` và branch ≥ `ut_coverage_branch` (thiếu số liệu coverage = không đạt).

UAT: script báo số liệu; kết luận nghiệm thu do biên bản có chữ ký khách (/d2-uat-acceptance) quyết định.

## Cảnh báo phụ (không chặn gate)
- SLOW SUITE: suite/test > 3 s — ghi vào Dashboard, nhắc tối ưu mock I/O.
- COVERAGE REGRESSION: so với phase/sprint trước, nhánh giảm > 2 điểm — lấy baseline từ snapshot cũ (không tự suy đoán).
