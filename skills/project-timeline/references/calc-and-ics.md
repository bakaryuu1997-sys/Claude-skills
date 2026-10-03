# Project Timeline — Thuật toán tính sprint/capacity & template ICS

> File tham chiếu của skill /project-timeline — SKILL.md trỏ tới đây (progressive disclosure). ĐỌC TOÀN BỘ file này khi thực thi skill.

## Quy tắc tính timeline tự động (hỗ trợ parallel team)

```python
# ── Bước 1: Cấu hình team ──────────────────────────────────────────
team = [
    {"id": "BE-1", "role": "Backend Dev",  "name": "Nguyễn A", "allocation": 1.0, "md_per_sprint": 8},
    {"id": "BE-2", "role": "Backend Dev",  "name": "Trần B",   "allocation": 1.0, "md_per_sprint": 8},
    {"id": "MOB-1","role": "Mobile Dev",   "name": "Lê C",     "allocation": 1.0, "md_per_sprint": 8},
    {"id": "QA-1", "role": "QA",           "name": "Phạm D",   "allocation": 1.0, "md_per_sprint": 7},
    {"id": "PM-1", "role": "PM",           "name": "TBD",      "allocation": 0.5, "md_per_sprint": 5},
]

# ── Bước 2: Tính capacity ──────────────────────────────────────────
capacity_by_role = {}
for m in team:
    capacity_by_role.setdefault(m["role"], 0)
    capacity_by_role[m["role"]] += m["md_per_sprint"]
# → {"Backend Dev": 16, "Mobile Dev": 8, "QA": 7, "PM": 5}

total_team_capacity = sum(capacity_by_role.values())  # 36 MD/sprint

# ── Bước 3: Tính số sprint ─────────────────────────────────────────
total_md = 329  # từ estimate Grand Total
base_sprints = ceil(total_md / total_team_capacity)

buffer_sprints = 0
if base_sprints > 10: buffer_sprints = 2
elif base_sprints > 6: buffer_sprints = 1

total_sprints = base_sprints + buffer_sprints
# 329 ÷ 36 = 9.1 → 10 base + 1 buffer = 11 sprints

# ── Bước 4: Phân bổ effort theo phase ──────────────────────────────
phases = {
    "Design & Setup":    {"effort": 0.12 * total_md, "roles": ["Backend Dev", "PM"]},
    "Backend Core":      {"effort": 0.35 * total_md, "roles": ["Backend Dev"]},
    "Frontend/Mobile":   {"effort": 0.25 * total_md, "roles": ["Mobile Dev"]},
    "Integration":       {"effort": 0.08 * total_md, "roles": ["Backend Dev", "Mobile Dev"]},
    "Testing":           {"effort": 0.12 * total_md, "roles": ["QA"]},
    "Bug Fix & Release": {"effort": 0.08 * total_md, "roles": ["Backend Dev", "Mobile Dev", "QA"]},
}

# ── Bước 5: Split task song song trong cùng role ────────────────────
# Khi Backend Dev effort = 48 MD và có 2 BE Dev (16 MD/sprint):
# → 48 ÷ 16 = 3 sprints thay vì 6 sprints nếu chỉ có 1 BE Dev
# Chia module: BE-1 nhận module A+B, BE-2 nhận module C+D
# Không chia task lẻ trong cùng module cho 2 người

# ── Bước 6: Assign member cụ thể cho từng sprint block ─────────────
# Gantt rows = mỗi member 1 row (không gộp theo role)
sprint_assignments = {
    "Sprint 1": {
        "BE-1": ["Infra setup", "Auth module (BE)"],
        "BE-2": ["DB schema design", "Category API"],
        "MOB-1": ["App project setup", "Navigation"],
        "QA-1": ["Test plan writing"],   # QA bắt đầu ngay từ Sprint 1 để viết test plan
        "PM-1": ["Kickoff", "Sprint planning"],
    },
    # ...
}

# ── Bước 7: Milestone dates ─────────────────────────────────────────
sprint_duration_weeks = 2
milestones = {
    "M1 Kickoff":         start_date + timedelta(weeks=0),
    "M2 API Freeze":      start_date + timedelta(weeks=sprint_duration_weeks * 5),
    "M3 Feature Complete":start_date + timedelta(weeks=sprint_duration_weeks * 8),
    "M4 Code Freeze":     start_date + timedelta(weeks=sprint_duration_weeks * 9),
    "M5 UAT Start":       start_date + timedelta(weeks=sprint_duration_weeks * 10),
    "M6 Go-Live":         start_date + timedelta(weeks=sprint_duration_weeks * 11),
}
```

> ⚠️ Tỷ lệ phase ở trên là MẶC ĐỊNH cho dự án fullstack (backend + mobile/web). Đọc `project.type` từ context để chọn bộ tỷ lệ: `api_only` → bỏ Frontend/Mobile, phân bổ lại cho Backend + Testing; `web_admin` → thay Mobile bằng Frontend. KHÔNG áp cứng một bộ tỷ lệ cho mọi dự án.

**Lưu ý quan trọng khi dùng parallel team:**
- Đừng chia effort bằng cách nhân capacity đơn giản — cần check module dependencies trước
- Task có dependency (A phải xong trước B) → assign cùng 1 người, không split
- Task độc lập với nhau (module Auth vs module Menu) → mới split cho 2 người song song
- Communication overhead: thêm 5–10% effort khi team > 3 dev

---


## Output 2: Milestones ICS Calendar (`[TênDựÁn]_Milestones.ics`)

File `.ics` chuẩn iCalendar — import vào Google Calendar, Outlook, Apple Calendar bằng 1 click:

```
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//AI Project Timeline Skill//EN
CALSCALE:GREGORIAN

BEGIN:VEVENT
DTSTART;VALUE=DATE:20260701
DTEND;VALUE=DATE:20260702
SUMMARY:[TênDựÁn] M1 — Project Kickoff
DESCRIPTION:Requirement sign-off\, team onboard\, Sprint 1 begins
CATEGORIES:MILESTONE
END:VEVENT

BEGIN:VEVENT
DTSTART;VALUE=DATE:20260830
DTEND;VALUE=DATE:20260831
SUMMARY:[TênDựÁn] M3 — Feature Complete
DESCRIPTION:All features dev done\, QA testing begins
CATEGORIES:MILESTONE
END:VEVENT

BEGIN:VEVENT
DTSTART;VALUE=DATE:20261001
DTEND;VALUE=DATE:20261002
SUMMARY:[TênDựÁn] M6 — GO-LIVE 🚀
DESCRIPTION:Production deployment\, smoke test pass
CATEGORIES:MILESTONE
END:VEVENT

END:VCALENDAR
```

Cách dùng:
- **Google Calendar**: Settings → Import → chọn file .ics
- **Outlook**: File → Open & Export → Import → Import iCalendar
- **Apple Calendar**: File → Import → chọn .ics

