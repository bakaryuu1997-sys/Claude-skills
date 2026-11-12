#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cr_impact.py — tính tác động effort / timeline / chi phí của một Change Request (c7).

Usage:
    python cr_impact.py cr_input.json [--format md|json] [--lang auto|vi|ja|en] [--context project-context.json]

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

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "a1-project-init" / "scripts"))
from i18n import add_lang_args, pick, resolve_lang  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

MESSAGES = {
    "vi": {
        "note": "Delay là ước lượng tối thiểu theo capacity; lịch thật còn phụ thuộc vào quan hệ giữa các task và tải song song.",
        "h_item": "Hạng mục", "h_md": "MD", "level": "mức", "buffer": "Buffer", "total": "TOTAL CR",
        "delay": "Sprint delay (tối thiểu)", "delay_val": "{n} sprint ≈ {w} tuần",
        "vs_orig": "So với estimate gốc", "cost": "Chi phí phát sinh",
        "Major": "Major", "Medium": "Medium", "Minor": "Minor",
    },
    "ja": {
        "note": "遅延はキャパシティに基づく最小見積りです。実際のスケジュールはタスク間の依存関係と並行作業の負荷によって変わります。",
        "h_item": "項目", "h_md": "工数（人日）", "level": "影響度", "buffer": "バッファ", "total": "CR 合計",
        "delay": "スプリント遅延（最小）", "delay_val": "{n} スプリント ≈ {w} 週",
        "vs_orig": "当初見積比", "cost": "追加費用",
        "Major": "大", "Medium": "中", "Minor": "小",
    },
    "en": {
        "note": "The delay is a minimum estimate based on capacity; the real schedule also depends on task dependencies and parallel load.",
        "h_item": "Item", "h_md": "MD", "level": "impact", "buffer": "Buffer", "total": "TOTAL CR",
        "delay": "Sprint delay (minimum)", "delay_val": "{n} sprint(s) ≈ {w} week(s)",
        "vs_orig": "Versus original estimate", "cost": "Additional cost",
        "Major": "Major", "Medium": "Medium", "Minor": "Minor",
    },
}

KINDS = ("new", "rework", "regression")
TYPES = ("ADDITION", "MODIFICATION", "REMOVAL", "REPLACEMENT", "URGENT")


def compute(inp: dict, lang: str = "vi") -> dict:
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
        "note": pick(MESSAGES, lang)["note"], "lang": lang,
    }


def to_md(r: dict, lang: str = "vi") -> str:
    M = pick(MESSAGES, lang)
    s = r["subtotal"]
    L = [f"## {r['cr_id']} — {r['title']} ({r['cr_type']}, {M['level']} {M[r['impact_band']]})", "",
         f"| {M['h_item']} | {M['h_md']} |", "|---|---|",
         f"| NEW | {s['new']} |", f"| REWORK | {s['rework']} |", f"| REGRESSION | {s['regression']} |",
         f"| {M['buffer']} | {r['buffer_md']} |", f"| **{M['total']}** | **{r['total_cr_md']}** ({r['person_month']} PM) |",
         f"| {M['delay']} | " + M["delay_val"].format(n=r["sprint_delay_min"], w=r["timeline_delay_weeks_min"]) + " |"]
    if r["impact_pct_of_original"] is not None:
        L.append(f"| {M['vs_orig']} | +{r['impact_pct_of_original']}% ({r['original_total_md']} MD) |")
    if r["cost_impact"] is not None:
        L.append(f"| {M['cost']} | {r['cost_impact']:,.0f} {r['currency'] or ''} |")
    L += ["", r["note"]]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Tác động effort/timeline/chi phí của Change Request (c7)")
    ap.add_argument("input")
    ap.add_argument("--format", choices=("md", "json"), default="md")
    add_lang_args(ap, audience="client_facing")  # CR là tài liệu khách ký
    a = ap.parse_args(argv)
    lang = resolve_lang(a.lang, a.context, a.audience)
    try:
        inp = json.loads(Path(a.input).read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR không đọc được input: {e}", file=sys.stderr)
        return 2
    try:
        r = compute(inp, lang)
    except (ValueError, TypeError, KeyError) as e:
        print(f"ERROR {e}", file=sys.stderr)
        return 2
    print(json.dumps(r, ensure_ascii=False, indent=2) if a.format == "json" else to_md(r, lang))
    return 0


if __name__ == "__main__":
    sys.exit(main())
