# Project Timeline — Công thức capacity, sprint, mốc và ICS

> File tham chiếu của /a9-project-timeline. Số liệu do `scripts/timeline_calc.py` tính; doc này giải thích công thức để người review kiểm lại. KHÔNG tính tay trong chat.

## 1. Capacity

```
cap(người)  = md_per_sprint × allocation × (sprint_duration_weeks / 2)
cap(team)   = Σ cap(người)                       (mọi role)
```

- `md_per_sprint` = công suất ở allocation 100% **đã trừ** họp/review/blocker (mặc định BE/FE/Mobile 8 · QA 7 · PM 5 · DevOps 6; `team[].md_per_sprint` ghi đè).
- `allocation` (0 < x ≤ 1): người làm part-time nhân hệ số. Ví dụ PM 0.5 → 5 × 0.5 = 2.5 MD/sprint.
- Ví dụ (context mẫu): BE-1 8 + BE-2 8 + MOB-1 8 + QA-1 7 + PM-1 (0.5) 2.5 = **33.5 MD/sprint**.

## 2. Số sprint

```
base_sprints   = ceil(total_md / cap(team))
buffer_sprints = 2 nếu base > 10 ; 1 nếu base > 6 ; ngược lại 0
total_sprints  = base + buffer
```

- `total_md` = `estimates.total_md` của /a6-estimate. Tổng này ĐÃ gồm PM và Buffer/Risk của a6 → a9 KHÔNG cộng thêm `buffer_percent` lần nữa.
- `buffer_sprints` là dự phòng **lịch** (không phải effort), chỉ có một lớp buffer trong bộ skill.
- Ví dụ: 329 ÷ 33.5 = 9.8 → base 10 → buffer 1 → **11 sprint**.

## 3. Mốc M1–M6

| Mốc | Ngày |
|---|---|
| M1 Kickoff | ngày bắt đầu (`project.start_date`) |
| M2 API Freeze | cuối sprint `round(N × 5/11)` |
| M3 Feature Complete | cuối sprint `round(N × 8/11)` |
| M4 Code Freeze | cuối sprint `round(N × 9/11)` |
| M5 UAT Start | cuối sprint `round(N × 10/11)` |
| M6 Go-Live (kế hoạch) | cuối sprint N |

- "Cuối sprint k" = `start + k × sprint_duration_weeks × 7 ngày`.
- Tỷ lệ 5/11…10/11 lấy từ dự án mẫu 11 sprint; khi N đổi, mốc tự co giãn theo tỷ lệ (không dùng số sprint cố định).
- Ví dụ (N = 11, start 2026-07-01, sprint 2 tuần): M2 2026-09-09 · M3 2026-10-21 · M4 2026-11-04 · M5 2026-11-18 · M6 2026-12-02.

## 4. Kiểm go-live

- `end` = cuối sprint N. Nếu `end > project.go_live_target` → cảnh báo số tuần trễ.
- Ví dụ: go-live 2026-10-15 nhưng `end` 2026-12-02 → trễ 7 tuần.
- Phương án (chọn một, ghi vào Change Log): giảm scope (đưa hạng mục vào Out of Scope của /a6-estimate), tăng người ở role nút thắt (role có "Sprint cần" cao nhất ở Role Breakdown), hoặc đàm phán lại mốc go-live.

## 5. Phân bổ effort theo phase (tham khảo, không áp cứng)

Tỷ lệ mặc định cho fullstack (backend + mobile/web): Design & Setup 12% · Backend Core 35% · Frontend/Mobile 25% · Integration 8% · Testing 12% · Bug Fix & Release 8%. Theo `project.type`: `api_only` bỏ Frontend/Mobile và chia lại cho Backend + Testing; `web_admin` thay Mobile bằng Frontend. Tổng phải bằng 100%.

## 6. Phân công song song

- Tách theo **module**, không tách theo layer: mỗi dev sở hữu trọn một module.
- Task có phụ thuộc (A phải xong trước B) → cùng một người, không tách.
- Mỗi người một dòng riêng trong Gantt (không gộp theo role).
- Communication overhead: thêm 5–10% effort khi team > 3 người (ghi vào Assumptions, không cộng ngầm).

## 7. File .ics (RFC 5545)

Sinh bằng script, không viết tay:

```bash
python <skills_dir>/a9-project-timeline/scripts/timeline_calc.py "<workspace_folder>" \
  --ics "<workspace_folder>/docs/A9_project-timeline/<TênDựÁn>_Milestones_v1.ics" \
  --json "<workspace_folder>/docs/A9_project-timeline/timeline_v1.json"
```

Script đảm bảo:
- CRLF là ký tự xuống dòng; gấp dòng ở 75 octet UTF-8 (không cắt giữa ký tự).
- Mỗi VEVENT có `UID` duy nhất (`uuid5` từ tên dự án + mã mốc, hậu tố `@claude-skill`), `DTSTAMP` (UTC), `DTSTART;VALUE=DATE`, `DTEND;VALUE=DATE` (ngày + 1), `SUMMARY`, `DESCRIPTION`, `CATEGORIES`.
- Escape `\ ; ,` trong text; mã UTF-8 cho tiếng Nhật/Việt.
- Parse lại trước khi ghi: đúng `BEGIN/END VCALENDAR`, số VEVENT = số mốc (6), UID không trùng. Lỗi → exit 1, KHÔNG ghi file.
- Kiểm thêm bằng `icalendar` nếu đã cài (`python -m pip install icalendar`).

Import: Google Calendar → Settings → Import; Outlook → File → Open & Export → Import iCalendar; Apple Calendar → File → Import.

Ví dụ một VEVENT (sinh từ ví dụ ở mục 3, đã gấp dòng):

```
BEGIN:VEVENT
UID:370f62ce-be67-504c-b902-98180fe7564b@claude-skill
DTSTAMP:20261111T123552Z
DTSTART;VALUE=DATE:20260701
DTEND;VALUE=DATE:20260702
SUMMARY:<Tên dự án> M1 — Kickoff
DESCRIPTION:Mốc M1 (sprint 0) — Kickoff
CATEGORIES:MILESTONE
END:VEVENT
```
