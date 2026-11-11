#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cr_impact.py — tính tác động effort / timeline / chi phí của một Change Request (c7).

Usage:
    python cr_impact.py cr_input.json [--format md|json]

Input JSON (xem references/cr-input.md):
  {
    "cr_id": "CR-001", "title": "...", "cr_type": "ADDITION|MODIFICATION|REMOVAL|REPLACEMENT|URGENT",
    "items": [ {"module": "Orders", "task": "...", "kind": "new|rework|regression",
                "dev": 2, "ut": 0.5, "bd": 0, "dd": 0.5, "it": 0} ],
    "settings": { "md_per_person_month": 22, "buffer_percent": 15, "sprint_duration_weeks": 2 },   // BẮT BUỘC lấy từ context
    "capacity_md": 36,                         // estimates.team_capacity_per_sprint
    "original_total_md": 286,                  // estimates.total_md (tùy chọn, để tính %)
    "rate_per_pm": 1500000, "currency": "JPY"  // tùy chọn (đơn giá nhân-tháng từ hợp đồng)
  }

Công thức (thống nhất với SKILL.md):
  row_total   = dev + ut + bd + dd + it
  New / Rework / Regression = Σ row_total theo kind
  Buffer      = buffer_percent% × (New + Rework)           (không tính buffer trên regression)
  Total CR MD = New + Rework + Regression + Buffer
  Person-Month = Total CR MD ÷ settings.md_per_person_month
  Sprint delay = ceil(Total CR MD ÷ capacity_md)            (chỉ là ước lượng tối thiểu, có tính tải song song)
  Timeline delay (tuần) = sprint delay × sprint_duration_weeks
  Cost impact = Person-Month × rate_per_pm (nếu có)
  Mức độ: Major > 20 MD · Medium 5–20 MD · Minor < 5 MD
Exit: 0 OK · 2 thiếu/sai đầu vào (ví dụ thiếu md_per_person_month — KHÔNG tự đặt số 22).
Chỉ thư viện chuẩn.
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

KINDS = ("new", "rework", "regression")
TYPES = ("ADDITION", "MODIFICATION", "REMOVAL", "REPLACEMENT", "URGENT")


def compute(inp: dict) -> dict:
    s = inp.get("settings") or {}
    if not s.get("md_per_person_month"):
        raise ValueError("thiếu settings.md_per_person_month (lấy từ project-context.json; không tự đặt số)")
    if s.get("buffer_percent") is None:
        raise ValueError("thiếu settings.buffer_percent (lấy từ project-context.json)")
    if not inp.get("capacity_md"):
        raise ValueError("thiếu capacity_md (estimates.team_capacity_per_sprint)")
    if str(inp.get("cr_type", "")).upper() not in TYPES:
        raise ValueError(f"cr_type phải là một trong {', '.join(TYPES)}")

    sums = {k: 0.0 for k in KINDS}
    rows = []
    for it in inp.get("items", []):
        kind = str(it.get("kind", "")).lower()
        if kind not in KINDS:
            raise ValueError(f"kind không hợp lệ ở '{it.get('task', '?')}': {kind}")
        tot = sum(float(it.get(c, 0) or 0) for c in ("dev", "ut", "bd", "dd", "it"))
        sums[kind] += tot
        rows.append({**it, "row_total": round(tot, 2)})
    if not rows:
        raise ValueError("items rỗng")

    buffer_md = round(float(s["buffer_percent"]) / 100.0 * (sums["new"] + sums["rework"]), 2)
    total = round(sums["new"] + sums["rework"] + sums["regression"] + buffer_md, 2)
    pm = round(total / float(s["md_per_person_month"]), 3)
    cap = float(inp["capacity_md"])
    sprints = math.ceil(total / cap) if cap > 0 else None
    weeks = sprints * int(s.get("sprint_duration_weeks", 2)) if sprints is not None else None
    original = inp.get("original_total_md")
    pct = round(100.0 * total / float(original), 1) if original else None
    cost = round(pm * float(inp["rate_per_pm"]), 0) if inp.get("rate_per_pm") else None
    band = "Major" if total > 20 else ("Medium" if total >= 5 else "Minor")

    return {
        "cr_id": inp.get("cr_id", "CR-???"), "title": inp.get("title", ""), "cr_type": str(inp["cr_type"]).upper(),
        "subtotal": {k: round(v, 2) for k, v in sums.items()}, "buffer_md": buffer_md,
        "total_cr_md": total, "person_month": pm, "impact_band": band,
        "sprint_delay_min": sprints, "timeline_delay_weeks_min": weeks,
        "original_total_md": original, "impact_pct_of_original": pct,
        "cost_impact": cost, "currency": inp.get("currency"), "rows": rows,
        "note": "Delay là ước lượng tối thiểu theo capacity; lịch thật còn phụ thuộc vào quan hệ giữa các task và tải song song.",
    }


def to_md(r: dict) -> str:
    s = r["subtotal"]
    L = [f"## {r['cr_id']} — {r['title']} ({r['cr_type']}, mức {r['impact_band']})", "",
         "| Hạng mục | MD |", "|---|---|",
         f"| NEW | {s['new']} |", f"| REWORK | {s['rework']} |", f"| REGRESSION | {s['regression']} |",
         f"| Buffer | {r['buffer_md']} |", f"| **TOTAL CR** | **{r['total_cr_md']}** ({r['person_month']} PM) |",
         f"| Sprint delay (tối thiểu) | {r['sprint_delay_min']} sprint ≈ {r['timeline_delay_weeks_min']} tuần |"]
    if r["impact_pct_of_original"] is not None:
        L.append(f"| So với estimate gốc | +{r['impact_pct_of_original']}% ({r['original_total_md']} MD) |")
    if r["cost_impact"] is not None:
        L.append(f"| Chi phí phát sinh | {r['cost_impact']:,.0f} {r['currency'] or ''} |")
    L += ["", r["note"]]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Tác động effort/timeline/chi phí của Change Request (c7)")
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
    except (ValueError, TypeError, KeyError) as e:
        print(f"ERROR {e}", file=sys.stderr)
        return 2
    print(json.dumps(r, ensure_ascii=False, indent=2) if a.format == "json" else to_md(r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
