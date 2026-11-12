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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i18n import pick, resolve_lang  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

HEADER_SCAN_ROWS = 10  # file theo excel-style có title (dòng 1) + subheader (dòng 2) + header (dòng 3)
# Trạng thái ĐÃ XONG của câu hỏi Q&A (so khớp không phân biệt hoa thường, theo chuỗi con)
# Tên cột/giá trị đa ngôn ngữ: Priority/優先度/ưu tiên · Status/ステータス/状態/trạng thái
PRIORITY_KEYS = ("priority", "優先度", "ưu tiên", "uu tien")
STATUS_KEYS = ("status", "ステータス", "状態", "trạng thái", "trang thai")
ANSWERED_MARKS = ("answered", "回答済", "đã trả lời", "da tra loi", "closed", "resolved", "✅")
# Trạng thái bug coi là CÒN MỞ (Fixed/Resolved chưa verify vẫn tính là mở — chỉ "verified/closed/wontfix" mới đóng)
BUG_OPEN_STATES = ("open", "in progress", "retest", "fixed", "unverified", "reopened", "new", "")
BUG_BLOCKING = ("critical", "high")


MESSAGES = {
    "vi": {
        "p1_unverifiable": "GATE P1: KHÔNG KIỂM ĐƯỢC — {err}",
        "p1_block": "GATE P1: {n} câu P1 chưa Answered (>3) — DỪNG /a6-estimate & /b1-project-kickoff (estimate sẽ sai >40%)",
        "p1_ok": "GATE P1: {n} câu P1 mở (≤ 3)",
        "bug_block": "GATE BUG: {n} bug Critical/High còn mở hoặc chưa verify — KHÔNG go-live",
        "bug_ok": "GATE BUG: 0 bug Critical/High mở",
        "cr": "CR: {n} change request chờ khách quyết định",
        "ctx_err": "project-context.json không đọc được ({e})",
        "no_ctx": "chưa có project-context.json (chạy /a1-project-init)",
        "e_nofile": "không có *_QA_Tracker.xlsx hoặc *_Requirement_Specification.xlsx trong workspace",
        "e_openpyxl": "thiếu openpyxl (pip install openpyxl) — lưu ý: `python -I` không thấy openpyxl cài ở user-site, hãy chạy không có -I",
        "e_read": "{f} không đọc được ({e})",
        "e_header": "không tìm thấy dòng header có cột Priority + Trạng thái/Status trong {n} dòng đầu của {files}",
    },
    "ja": {
        "p1_unverifiable": "GATE P1: 確認できません — {err}",
        "p1_block": "GATE P1: 未回答の P1 質問が {n} 件（3 件超）— 見積り・キックオフを停止（見積り誤差が 40% 超になる恐れ）",
        "p1_ok": "GATE P1: 未回答の P1 質問は {n} 件（3 件以内）",
        "bug_block": "GATE BUG: 未解決または未検証の Critical/High バグが {n} 件 — 本番リリース不可",
        "bug_ok": "GATE BUG: 未解決の Critical/High バグはありません",
        "cr": "CR: 顧客判断待ちの変更要求が {n} 件",
        "ctx_err": "project-context.json を読み込めません（{e}）",
        "no_ctx": "project-context.json がありません（プロジェクト初期化を実行してください）",
        "e_nofile": "ワークスペースに *_QA_Tracker.xlsx も *_Requirement_Specification.xlsx もありません",
        "e_openpyxl": "openpyxl がありません（pip install openpyxl）。注意: `python -I` ではユーザー領域の openpyxl が見えないため -I なしで実行してください",
        "e_read": "{f} を読み込めません（{e}）",
        "e_header": "{files} の先頭 {n} 行に Priority（優先度）と Status（ステータス）の列を持つ見出し行が見つかりません",
    },
    "en": {
        "p1_unverifiable": "GATE P1: CANNOT BE CHECKED — {err}",
        "p1_block": "GATE P1: {n} P1 questions unanswered (>3) — STOP estimate and kickoff (estimate would be off by >40%)",
        "p1_ok": "GATE P1: {n} P1 questions open (≤ 3)",
        "bug_block": "GATE BUG: {n} Critical/High bug(s) open or unverified — NO go-live",
        "bug_ok": "GATE BUG: no open Critical/High bugs",
        "cr": "CR: {n} change request(s) waiting for the customer's decision",
        "ctx_err": "project-context.json cannot be read ({e})",
        "no_ctx": "project-context.json is missing (run project init)",
        "e_nofile": "no *_QA_Tracker.xlsx or *_Requirement_Specification.xlsx in the workspace",
        "e_openpyxl": "openpyxl is missing (pip install openpyxl); note: `python -I` cannot see user-site packages, run without -I",
        "e_read": "{f} cannot be read ({e})",
        "e_header": "no header row with Priority + Status columns in the first {n} rows of {files}",
    },
}


def _find_header(sheet):
    """Quét HEADER_SCAN_ROWS dòng đầu, trả (chỉ_số_dòng_header, ip, ist) hoặc None."""
    for n, row in enumerate(sheet.iter_rows(min_row=1, max_row=HEADER_SCAN_ROWS, values_only=True), start=1):
        cols = {str(c or "").strip().lower(): i for i, c in enumerate(row)}
        ip = next((i for k, i in cols.items() if any(x in k for x in PRIORITY_KEYS)), None)
        ist = next((i for k, i in cols.items() if any(x in k for x in STATUS_KEYS)), None)
        if ip is not None and ist is not None:
            return n, ip, ist
    return None


def count_open_p1(ws: Path, M=None):
    M = M or pick(MESSAGES, "vi")
    """Trả (số P1 mở | None, lỗi | None)."""
    files = sorted(set(list(ws.glob("*_QA_Tracker.xlsx")) + list(ws.glob("docs/**/*_QA_Tracker.xlsx"))))
    if not files:
        files = sorted(set(list(ws.glob("*_Requirement_Specification.xlsx")) + list(ws.glob("docs/**/*_Requirement_Specification.xlsx"))
                           + list(ws.glob("*_Requirement_*.xlsx")) + list(ws.glob("docs/**/*_Requirement_*.xlsx"))))
    files = [f for f in files if not f.name.startswith("~$")]
    if not files:
        return None, M["e_nofile"]
    try:
        import openpyxl
    except ImportError:
        return None, M["e_openpyxl"]
    n, found_header = 0, False
    for fp in files:
        try:
            wb = openpyxl.load_workbook(fp, read_only=True, data_only=True)
        except Exception as e:
            return None, M["e_read"].format(f=fp.name, e=e)
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
        return None, M["e_header"].format(n=HEADER_SCAN_ROWS, files=[f.name for f in files])
    return n, None


def main() -> int:
    ws = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    block, warn = [], []
    unverifiable = False
    M = pick(MESSAGES, resolve_lang("auto", ws / "project-context.json", "internal"))

    p1, err = count_open_p1(ws, M)
    if err:
        warn.append(M["p1_unverifiable"].format(err=err))
        unverifiable = True
    elif p1 > 3:
        block.append(M["p1_block"].format(n=p1))
    else:
        print("✅ " + M["p1_ok"].format(n=p1))

    ctx_f = ws / "project-context.json"
    if ctx_f.exists():
        try:
            ctx = json.loads(ctx_f.read_text(encoding="utf-8-sig"))
            crit = [i for i in ctx.get("known_issues", []) if isinstance(i, dict)
                    and str(i.get("severity", "")).lower() in BUG_BLOCKING
                    and str(i.get("status", "open")).lower() in BUG_OPEN_STATES]
            if crit:
                block.append(M["bug_block"].format(n=len(crit)))
            else:
                print("✅ " + M["bug_ok"])
            pend = [c for c in ctx.get("change_requests", []) if isinstance(c, dict)
                    and str(c.get("status", "")).lower() in ("", "pending", "received", "in analysis", "negotiating")]
            if pend:
                warn.append(M["cr"].format(n=len(pend)))
        except Exception as e:
            warn.append(M["ctx_err"].format(e=e))
    else:
        warn.append(M["no_ctx"])

    for w in warn:
        print("⚠️", w)
    for b in block:
        print("⛔", b)
    if block:
        return 1
    return 3 if unverifiable else 0


if __name__ == "__main__":
    sys.exit(main())
