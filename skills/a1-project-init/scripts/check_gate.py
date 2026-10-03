#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_gate.py — THI HÀNH các gate của pipeline bằng code, không đếm tay (v3.3.0).
Gates:
  (1) >3 câu P1 chưa Answered trong *_QA_Tracker.xlsx → CHẶN /a6-estimate, /b1-project-kickoff
  (2) bug Critical/High còn mở trong known_issues[]     → CHẶN go-live
  (3) change_requests[] còn CR pending                  → cảnh báo (không chặn)
Usage: python3 check_gate.py <workspace_folder>
Exit 0 = không gate nào chặn; 1 = có gate chặn (in lý do)."""
import json, sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def count_open_p1(ws: Path):
    """Trả (số P1 mở | None, lỗi | None)."""
    files = sorted(set(list(ws.glob("*_QA_Tracker.xlsx")) + list(ws.glob("docs/**/*_QA_Tracker.xlsx"))))
    if not files:
        files = sorted(set(list(ws.glob("*_Requirement_Specification.xlsx")) + list(ws.glob("docs/**/*_Requirement_Specification.xlsx")) + list(ws.glob("*_Requirement_*.xlsx")) + list(ws.glob("docs/**/*_Requirement_*.xlsx"))))
    if not files:
        return None, "không có *_QA_Tracker.xlsx hoặc *_Requirement_Specification.xlsx trong workspace"
    try:
        import openpyxl
    except ImportError:
        return None, "thiếu openpyxl (pip install openpyxl --break-system-packages)"
    n = 0
    for fp in files:
        try:
            wb = openpyxl.load_workbook(fp, read_only=True, data_only=True)
        except Exception as e:
            return None, f"{fp.name} không đọc được ({e})"
        for sheet in wb.worksheets:
            rows = sheet.iter_rows(values_only=True)
            header = next(rows, None)
            if not header:
                continue
            cols = {str(c or "").strip().lower(): i for i, c in enumerate(header)}
            ip = next((i for k, i in cols.items() if "priority" in k), None)
            ist = next((i for k, i in cols.items() if "trạng thái" in k or "status" in k), None)
            if ip is None or ist is None:
                continue
            for r in rows:
                pri = str(r[ip] or "") if ip < len(r) else ""
                st = str(r[ist] or "") if ist < len(r) else ""
                if "P1" in pri and "Answered" not in st and "✅" not in st:
                    n += 1
        wb.close()
    return n, None


def main() -> int:
    ws = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    block, warn = [], []

    p1, err = count_open_p1(ws)
    if err:
        warn.append(f"GATE P1: không kiểm được — {err}")
    elif p1 > 3:
        block.append(f"GATE P1: {p1} câu P1 chưa Answered (>3) — DỪNG /a6-estimate & /b1-project-kickoff (estimate sẽ sai >40%)")
    else:
        print(f"✅ GATE P1: {p1} câu P1 mở (≤ 3)")

    ctx_f = ws / "project-context.json"
    if ctx_f.exists():
        try:
            ctx = json.loads(ctx_f.read_text(encoding="utf-8"))
            open_states = ("open", "in progress", "retest", "")
            crit = [i for i in ctx.get("known_issues", [])
                    if str(i.get("severity", "")).lower() in ("critical", "high")
                    and str(i.get("status", "open")).lower() in open_states]
            if crit:
                block.append(f"GATE BUG: {len(crit)} bug Critical/High còn mở — KHÔNG go-live")
            else:
                print("✅ GATE BUG: 0 bug Critical/High mở")
            pend = [c for c in ctx.get("change_requests", [])
                    if str(c.get("status", "")).lower() in ("", "pending", "received", "in analysis", "negotiating")]
            if pend:
                warn.append(f"CR: {len(pend)} change request chờ khách quyết định")
        except Exception as e:
            warn.append(f"project-context.json không đọc được ({e})")
    else:
        warn.append("chưa có project-context.json (chạy /a1-project-init)")

    for w in warn:
        print("⚠️", w)
    for b in block:
        print("⛔", b)
    return 1 if block else 0


if __name__ == "__main__":
    sys.exit(main())
