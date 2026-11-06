#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_gate.py — THI HÀNH các gate của pipeline bằng code, không đếm tay (v3.17.0).
Gates:
  (1) >3 câu P1 chưa Answered trong *_QA_Tracker.xlsx → CHẶN /a6-estimate, /b1-project-kickoff
  (2) bug Critical/High còn mở trong known_issues[]     → CHẶN go-live
  (3) change_requests[] còn CR pending                  → cảnh báo (không chặn)
Usage: python check_gate.py <workspace_folder>
Exit code:
  0 = không gate nào chặn
  1 = có gate chặn (in lý do)
  3 = KHÔNG KIỂM ĐƯỢC gate P1 (thiếu file / thiếu openpyxl / không thấy header) — không coi là "đã qua"
Thang severity chuẩn: Critical / High / Medium / Low (xem pipeline.md → Quy ước dùng chung)."""
import json, sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

HEADER_SCAN_ROWS = 10  # file theo excel-style có title (dòng 1) + subheader (dòng 2) + header (dòng 3)
# Trạng thái ĐÃ XONG của câu hỏi Q&A (so khớp không phân biệt hoa thường, theo chuỗi con)
ANSWERED_MARKS = ("answered", "đã trả lời", "da tra loi", "closed", "resolved", "回答済", "✅")
# Trạng thái bug coi là CÒN MỞ (Fixed/Resolved chưa verify vẫn tính là mở — chỉ "verified/closed/wontfix" mới đóng)
BUG_OPEN_STATES = ("open", "in progress", "retest", "fixed", "unverified", "reopened", "new", "")
BUG_BLOCKING = ("critical", "high")


def _find_header(sheet):
    """Quét HEADER_SCAN_ROWS dòng đầu, trả (chỉ_số_dòng_header, ip, ist) hoặc None."""
    for n, row in enumerate(sheet.iter_rows(min_row=1, max_row=HEADER_SCAN_ROWS, values_only=True), start=1):
        cols = {str(c or "").strip().lower(): i for i, c in enumerate(row)}
        ip = next((i for k, i in cols.items() if "priority" in k or "ưu tiên" in k), None)
        ist = next((i for k, i in cols.items() if "trạng thái" in k or "status" in k), None)
        if ip is not None and ist is not None:
            return n, ip, ist
    return None


def count_open_p1(ws: Path):
    """Trả (số P1 mở | None, lỗi | None)."""
    files = sorted(set(list(ws.glob("*_QA_Tracker.xlsx")) + list(ws.glob("docs/**/*_QA_Tracker.xlsx"))))
    if not files:
        files = sorted(set(list(ws.glob("*_Requirement_Specification.xlsx")) + list(ws.glob("docs/**/*_Requirement_Specification.xlsx"))
                           + list(ws.glob("*_Requirement_*.xlsx")) + list(ws.glob("docs/**/*_Requirement_*.xlsx"))))
    files = [f for f in files if not f.name.startswith("~$")]
    if not files:
        return None, "không có *_QA_Tracker.xlsx hoặc *_Requirement_Specification.xlsx trong workspace"
    try:
        import openpyxl
    except ImportError:
        return None, "thiếu openpyxl (pip install openpyxl) — lưu ý: `python -I` không thấy openpyxl cài ở user-site, hãy chạy không có -I"
    n, found_header = 0, False
    for fp in files:
        try:
            wb = openpyxl.load_workbook(fp, read_only=True, data_only=True)
        except Exception as e:
            return None, f"{fp.name} không đọc được ({e})"
        for sheet in wb.worksheets:
            hdr = _find_header(sheet)
            if hdr is None:
                continue
            found_header = True
            hrow, ip, ist = hdr
            for r in sheet.iter_rows(min_row=hrow + 1, values_only=True):
                pri = str(r[ip] or "") if ip < len(r) else ""
                st = str(r[ist] or "").lower() if ist < len(r) else ""
                if "P1" in pri.upper() and not any(m in st for m in ANSWERED_MARKS):
                    n += 1
        wb.close()
    if not found_header:
        return None, f"không tìm thấy dòng header có cột Priority + Trạng thái/Status trong {HEADER_SCAN_ROWS} dòng đầu của {[f.name for f in files]}"
    return n, None


def main() -> int:
    ws = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    block, warn = [], []
    unverifiable = False

    p1, err = count_open_p1(ws)
    if err:
        warn.append(f"GATE P1: KHÔNG KIỂM ĐƯỢC — {err}")
        unverifiable = True
    elif p1 > 3:
        block.append(f"GATE P1: {p1} câu P1 chưa Answered (>3) — DỪNG /a6-estimate & /b1-project-kickoff (estimate sẽ sai >40%)")
    else:
        print(f"✅ GATE P1: {p1} câu P1 mở (≤ 3)")

    ctx_f = ws / "project-context.json"
    if ctx_f.exists():
        try:
            ctx = json.loads(ctx_f.read_text(encoding="utf-8-sig"))
            crit = [i for i in ctx.get("known_issues", []) if isinstance(i, dict)
                    and str(i.get("severity", "")).lower() in BUG_BLOCKING
                    and str(i.get("status", "open")).lower() in BUG_OPEN_STATES]
            if crit:
                block.append(f"GATE BUG: {len(crit)} bug Critical/High còn mở hoặc chưa verify — KHÔNG go-live")
            else:
                print("✅ GATE BUG: 0 bug Critical/High mở")
            pend = [c for c in ctx.get("change_requests", []) if isinstance(c, dict)
                    and str(c.get("status", "")).lower() in ("", "pending", "received", "in analysis", "negotiating")]
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
    if block:
        return 1
    return 3 if unverifiable else 0


if __name__ == "__main__":
    sys.exit(main())
