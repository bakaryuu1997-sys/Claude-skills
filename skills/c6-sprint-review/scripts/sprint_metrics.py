#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""sprint_metrics.py — tính velocity, completion, Health Score, drag và cảnh báo cho một sprint (c6).

Usage:
    python sprint_metrics.py sprint_input.json [--format md|json]
    python sprint_metrics.py --help

Input JSON (xem references/sprint-input.md):
  {
    "sprint": 3, "sprint_weeks": 2,
    "capacity_md": 36,
    "tasks": [ {"id": "T-01", "title": "...", "planned_md": 8, "actual_md": 8,
                "status": "done|partial|not_started|moved", "reason": ""} ],
    "bugs": { "found": 5, "fixed": 4, "carry_over": 1, "p1_open": 0, "p2": 1, "p3p4": 4 },
    "demo": "ok|partial|no",
    "blockers_unresolved": 0,
    "prev_actions": { "total": 4, "done": 3 },          // action items của retro sprint trước
    "unresolved_debt_md": 2.0,                            // Enabler/tech debt chưa xong (MD)
    "remaining_md": 150,                                  // Remaining MD của toàn dự án sau sprint này
    "team_daily_burn_md": 3.0,                            // tùy chọn: MD/ngày của cả team (cho công thức delay)
    "history": [ {"sprint": 1, "planned_md": 36, "completed_md": 28, "health": 72} ]  // sprint trước
  }

Định nghĩa (thống nhất với SKILL.md):
  planned_md   = Σ planned_md của task (trừ status = moved)
  completed_md = Σ actual_md của task status = done   (partial KHÔNG tính vào velocity)
  completion%  = completed_md / planned_md
  Velocity trend: trung bình 3 sprint gần nhất (kể cả sprint này) của completed_md.
  Health Score (100): completion 40/30/20/10 theo ngưỡng 90/75/60 · P1 đang mở 0→20, 1→10, ≥2→0 ·
     demo ok 20 / partial 10 / no 0 · blocker mở 0→10 · action item trước đã xong 100%→10, ≥50%→5, <50%→0
     (không có action trước → 10). Nhãn: ≥80 Healthy · 60–79 At Risk · <60 Needs Attention.
  Drag coefficient = 1 − unresolved_debt_md / capacity_md
  Cảnh báo (ngưỡng thống nhất 1 bộ):
     completion < 75%  → OVER-COMMIT
     completion < 70% trong 2 sprint liên tiếp → escalate: chạy /a6-estimate lại hoặc review capacity /a9-project-timeline
     completion > 95% trong 2 sprint liên tiếp → UNDER-COMMIT (tăng scope)
     drag < 0.85 → DEBT DRAG
  Projection (nếu remaining_md > 0): sprints_needed = ceil(remaining_md / avg_completed_md_3)
  Delay (chỉ khi completion < 80% hoặc drag < 0.85 và có team_daily_burn_md):
     delay_days = (planned_md − completed_md) / team_daily_burn_md
  Final sprint: remaining_md == 0 → RELEASE_TRANSITION (chuyển sang /c8-release-deployment + /d1-handover-doc)

Exit: 0 OK · 2 input lỗi. Chỉ thư viện chuẩn.
"""
import argparse
import json
import math
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def completion_points(pct: float) -> int:
    if pct >= 90:
        return 40
    if pct >= 75:
        return 30
    if pct >= 60:
        return 20
    return 10


def compute(inp: dict) -> dict:
    tasks = [t for t in inp.get("tasks", []) if str(t.get("status", "")).lower() != "moved"]
    if not tasks:
        raise ValueError("tasks rỗng (cần ít nhất 1 task không ở trạng thái moved)")
    planned = sum(float(t.get("planned_md", 0) or 0) for t in tasks)
    if planned <= 0:
        raise ValueError("planned_md tổng bằng 0")
    completed = sum(float(t.get("actual_md", 0) or 0) for t in tasks if str(t.get("status")).lower() == "done")
    partial_md = sum(float(t.get("actual_md", 0) or 0) for t in tasks if str(t.get("status")).lower() == "partial")
    completion = round(100.0 * completed / planned, 1)

    history = list(inp.get("history", []))
    last3 = [float(h.get("completed_md", 0)) for h in history[-2:]] + [completed]
    avg3 = round(sum(last3) / len(last3), 2)

    bugs = inp.get("bugs", {}) or {}
    p1 = int(bugs.get("p1_open", 0) or 0)
    demo = str(inp.get("demo", "no")).lower()
    blockers = int(inp.get("blockers_unresolved", 0) or 0)
    pa = inp.get("prev_actions") or {}
    pa_total, pa_done = int(pa.get("total", 0) or 0), int(pa.get("done", 0) or 0)

    s_completion = completion_points(completion)
    s_p1 = 20 if p1 == 0 else (10 if p1 == 1 else 0)
    s_demo = {"ok": 20, "partial": 10}.get(demo, 0)
    s_block = 10 if blockers == 0 else 0
    if pa_total == 0:
        s_actions = 10
    else:
        rate = 100.0 * pa_done / pa_total
        s_actions = 10 if rate >= 100 else (5 if rate >= 50 else 0)
    health = s_completion + s_p1 + s_demo + s_block + s_actions
    label = "Healthy" if health >= 80 else ("At Risk" if health >= 60 else "Needs Attention")

    capacity = float(inp.get("capacity_md", 0) or 0)
    debt = float(inp.get("unresolved_debt_md", 0) or 0)
    drag = round(1 - debt / capacity, 3) if capacity > 0 else None

    warnings = []
    if completion < 75:
        warnings.append("OVER-COMMIT: completion < 75%")
    if completion > 95:
        warnings.append("UNDER-COMMIT: completion > 95% (cân nhắc tăng scope)")
    prev_c = [float(h.get("completion_pct", -1)) for h in history[-1:]] if history else []
    if completion < 70 and prev_c and prev_c[0] < 70:
        warnings.append("ESCALATE: completion < 70% 2 sprint liên tiếp → /a6-estimate hoặc review capacity /a9-project-timeline")
    if drag is not None and drag < 0.85:
        warnings.append(f"DEBT DRAG: drag {drag} < 0.85 — nợ kỹ thuật chiếm > 15% capacity")

    remaining = inp.get("remaining_md")
    projection = None
    if remaining is not None:
        remaining = float(remaining)
        if remaining <= 0:
            projection = {"status": "RELEASE_TRANSITION", "note": "scope cốt lõi đã xong — chuyển sang /c8-release-deployment và /d1-handover-doc"}
        elif avg3 > 0:
            n = math.ceil(remaining / avg3)
            projection = {"status": "PROJECTED", "sprints_needed": n,
                          "weeks_needed": n * int(inp.get("sprint_weeks", 2) or 2), "avg_completed_md_3": avg3}
        else:
            projection = {"status": "UNKNOWN", "note": "velocity trung bình = 0"}

    delay = None
    burn = inp.get("team_daily_burn_md")
    if burn and (completion < 80 or (drag is not None and drag < 0.85)):
        delay = round((planned - completed) / float(burn), 1)

    return {
        "sprint": inp.get("sprint"),
        "planned_md": round(planned, 2), "completed_md": round(completed, 2),
        "partial_md_not_counted": round(partial_md, 2), "completion_pct": completion,
        "velocity_avg_3": avg3, "health_score": health, "health_label": label,
        "health_breakdown": {"completion": s_completion, "p1": s_p1, "demo": s_demo, "blockers": s_block, "actions": s_actions},
        "bug_density_bug_per_md": round(int(bugs.get("found", 0) or 0) / planned, 3),
        "drag_coefficient": drag, "warnings": warnings, "projection": projection,
        "projected_delay_days": delay,
        "history_entry": {"sprint": inp.get("sprint"), "planned_md": round(planned, 2),
                          "completed_md": round(completed, 2), "completion_pct": completion, "health": health},
    }


def to_md(r: dict) -> str:
    L = [f"## Sprint {r['sprint']} — Health {r['health_score']}/100 ({r['health_label']})", "",
         "| Chỉ số | Giá trị |", "|---|---|",
         f"| Planned / Completed MD | {r['planned_md']} / {r['completed_md']} ({r['completion_pct']}%) |",
         f"| Partial (không tính velocity) | {r['partial_md_not_counted']} MD |",
         f"| Velocity TB 3 sprint | {r['velocity_avg_3']} MD |",
         f"| Bug density | {r['bug_density_bug_per_md']} bug/MD (tham khảo, chuẩn < 0.2) |",
         f"| Drag coefficient | {r['drag_coefficient']} |"]
    if r["projection"]:
        L.append(f"| Dự phóng | {json.dumps(r['projection'], ensure_ascii=False)} |")
    if r["projected_delay_days"] is not None:
        L.append(f"| Delay dự phóng | {r['projected_delay_days']} ngày |")
    b = r["health_breakdown"]
    L += ["", "Health breakdown: " + ", ".join(f"{k} {v}" for k, v in b.items())]
    if r["warnings"]:
        L += ["", "### Cảnh báo"] + [f"- {w}" for w in r["warnings"]]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Velocity, Health Score, drag và cảnh báo cho sprint (c6)")
    ap.add_argument("input")
    ap.add_argument("--format", choices=("md", "json"), default="md")
    a = ap.parse_args(argv)
    try:
        inp = json.loads(Path(a.input).read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR không đọc được input: {e}", file=sys.stderr)
        return 2
    try:
        r = compute(inp)
    except (ValueError, TypeError) as e:
        print(f"ERROR {e}", file=sys.stderr)
        return 2
    print(json.dumps(r, ensure_ascii=False, indent=2) if a.format == "json" else to_md(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
