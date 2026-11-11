# Đặc tả workbook `<Project>_PR<id>_Code_Review_Report.xlsx` (5 sheet)

> **Trung thực về công cụ:** không có script dựng workbook trong skill. Agent tự viết một script Python (openpyxl) theo đặc tả này và `a1-project-init/references/excel-style.md` (font Arial, header navy `#1F4E79`, zebra, freeze `A4`, màu trạng thái, công thức thay số cứng). Script có thể là file tạm — không commit vào repo trừ khi người dùng yêu cầu. Sau khi dựng: mở lại bằng openpyxl kiểm số sheet = 5 và các ô tổng bắt đầu bằng `=` (quy tắc 4 của excel-style).
> Số liệu coverage/LOC lấy từ `python <skills_dir>/c3-code-review/scripts/coverage_summary.py` (xem SKILL) — không gõ tay.

Tên file: `docs/C3_code-review/<Project>_PR<id>_Code_Review_Report.xlsx` (`<id>` = số PR/commit/tên nhánh, không ghi đè lần trước).

| Sheet | Nội dung |
|---|---|
| `Review_Summary` | Thông tin phiên review (PR, tác giả, reviewer, stack, ngày) · KPI: tổng file, tổng LOC thay đổi, số finding theo severity (công thức `COUNTIF` từ `Findings_Defects`) · **Test Evidence** (số test pass/tổng, coverage line/branch — từ `coverage_summary.py`; ghi `[CẦN ĐIỀN]` nếu chưa có) · Verdict (APPROVE / APPROVE WITH COMMENTS / REQUEST CHANGES) · điều kiện merge |
| `Review_Checklist` | 25 dòng R01–R25 (xem SKILL): ID · Nhóm · Tiêu chí · Mức rủi ro · File liên quan · Kết quả (`PASS` / `FIXED` / `REC` = khuyến nghị / `FAIL` / `N/A`) · Ghi chú kỹ thuật |
| `Files_Reviewed` | Đường dẫn · Layer · Ngôn ngữ · LOC (+/−) · Rủi ro (Cao/TB/Thấp) · Hàm/lớp trọng tâm · Trạng thái |
| `Findings_Defects` | ID (`F-<PR>-<NN>`) · Severity (Critical/High/Medium/Low) · Category · File:dòng · Problem · Why · Code hiện tại · Code đề xuất · Tiêu chí R-ID · Trạng thái (Open/Fixed/Verified/Wontfix) · BUG-ID (nếu đưa vào `known_issues[]`) |
| `Key_Praises` | Tối đa 5 điểm tốt **có thật** trong PR: mô tả · file:dòng · vì sao tốt (không dùng danh sách khen cố định) |

Màu severity (excel-style): Critical `#FFE0E0` · High `#FCE4D6` · Medium `#FFF2CC` · Low `#DDEEFF` · Pass/Praise `#E2EFDA`.
