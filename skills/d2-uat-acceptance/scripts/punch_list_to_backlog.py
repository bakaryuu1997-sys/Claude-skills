#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""punch_list_to_backlog.py — đọc sheet Punch_List_Minor_Defects của *_UAT_SignOff_Workbook*.xlsx và sinh
punch_list_warranty_backlog.json (schema: references/backlog-schema.json). Tùy chọn nạp vào known_issues[] của context.

Cột sheet (theo SKILL.md): A Mã (PUNCH-NN) · B Mô tả · C Severity (Medium/Low) · D Ảnh hưởng ·
E Kế hoạch khắc phục · F Fix owner · G Hạn (ngày) · H BUG ref (tùy chọn) · I Trạng thái (tùy chọn, mặc định open).

Usage:
    python punch_list_to_backlog.py <workbook.xlsx> [--out <file.json>] [--project <tên>] [--append-context <workspace_folder>]
Exit: 0 OK · 1 lỗi dữ liệu (vd có Critical/High trong Punch List, severity lạ, trùng mã) · 2 lỗi dùng/thiếu thư viện/không đọc được file.
Không ghi gì ngoài --out (mặc định: cùng thư mục workbook) và, khi có --append-context, qua update_context.py."""
import json
import re
import subprocess
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SHEET = "Punch_List_Minor_Defects"
SEV_MAP = {
    "medium": "Medium", "trung bình": "Medium", "trung binh": "Medium", "中": "Medium", "major": "Medium",
    "low": "Low", "minor": "Low", "cosmetic": "Low", "thấp": "Low", "thap": "Low", "低": "Low",
}
BLOCKING = {"critical", "high", "blocker", "cao", "nghiêm trọng", "高", "致命的"}
ID_RE = re.compile(r"^PUNCH-\d+$", re.I)


def _cell(row, i):
    return row[i] if i < len(row) and row[i] is not None else ""


def _date(v):
    if isinstance(v, (datetime, date)):
        return v.strftime("%Y-%m-%d")
    s = str(v).strip()
    return s.replace("/", "-") if re.match(r"^\d{4}/\d{1,2}/\d{1,2}$", s) else s


def parse(path: Path):
    try:
        import openpyxl
    except ImportError:
        print("❌ Thiếu openpyxl — cài: pip install openpyxl (lưu ý: 'python -I' không thấy gói cài ở user-site)")
        sys.exit(2)
    try:
        wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    except Exception as e:  # file không tồn tại / hỏng / đang mở
        print(f"❌ Không đọc được {path}: {e}")
        sys.exit(2)
    if SHEET not in wb.sheetnames:
        print(f"❌ Không có sheet '{SHEET}' trong {path.name} (có: {', '.join(wb.sheetnames)})")
        sys.exit(2)
    items, errors, seen = [], [], set()
    for n, row in enumerate(wb[SHEET].iter_rows(values_only=True), start=1):
        pid = str(_cell(row, 0)).strip()
        if not ID_RE.match(pid):
            continue
        pid = pid.upper()
        raw_sev = str(_cell(row, 2)).strip()
        key = raw_sev.lower()
        if pid in seen:
            errors.append(f"dòng {n}: trùng mã {pid}")
        seen.add(pid)
        if key in BLOCKING:
            errors.append(f"dòng {n}: {pid} có severity '{raw_sev}' — Critical/High KHÔNG được nằm trong Punch List (chặn nghiệm thu)")
            continue
        sev = SEV_MAP.get(key)
        if not sev:
            errors.append(f"dòng {n}: {pid} severity '{raw_sev}' không thuộc Medium/Low (Minor/Cosmetic được quy về Low)")
            continue
        item = {
            "id": pid,
            "title": str(_cell(row, 1)).strip(),
            "severity": sev,
            "status": (str(_cell(row, 8)).strip().lower() or "open"),
            "impact": str(_cell(row, 3)).strip(),
            "plan": str(_cell(row, 4)).strip(),
            "owner": str(_cell(row, 5)).strip(),
            "due": _date(_cell(row, 6)) if _cell(row, 6) != "" else "",
            "found_in": "UAT",
            "date": date.today().isoformat(),
        }
        ref = str(_cell(row, 7)).strip()
        if ref:
            item["ref_bug"] = ref
        if not item["title"]:
            errors.append(f"dòng {n}: {pid} thiếu mô tả")
        items.append(item)
    wb.close()
    return items, errors


def append_context(ws: Path, items):
    upd = Path(__file__).resolve().parents[2] / "a1-project-init" / "scripts" / "update_context.py"
    ctx_f = ws / "project-context.json"
    if not upd.exists() or not ctx_f.exists():
        print(f"❌ Không thấy update_context.py hoặc {ctx_f}")
        return 2
    existing = {str(i.get("id")) for i in json.loads(ctx_f.read_text(encoding="utf-8-sig")).get("known_issues", [])}
    added = 0
    for it in items:
        if it["id"] in existing:
            print(f"  = bỏ qua {it['id']} (đã có trong known_issues[])")
            continue
        payload = {k: it[k] for k in ("id", "title", "severity", "status", "found_in", "date")}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as tf:
            json.dump(payload, tf, ensure_ascii=False)
            tmp = Path(tf.name)
        try:
            r = subprocess.run([sys.executable, "-B", str(upd), str(ws), "append", "known_issues", "--file", str(tmp)],
                               capture_output=True, text=True, encoding="utf-8", errors="replace")
        finally:
            tmp.unlink(missing_ok=True)
        if r.returncode != 0:
            print(f"❌ append {it['id']} thất bại: {(r.stdout + r.stderr).strip()}")
            return 1
        added += 1
    print(f"✅ Đã nạp {added} mục vào known_issues[] ({len(items) - added} bỏ qua)")
    return 0


def main() -> int:
    argv = sys.argv[1:]
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    wbp = Path(argv[0])
    opts = {"--out": None, "--project": "", "--append-context": None}
    i = 1
    while i < len(argv):
        if argv[i] in opts and i + 1 < len(argv):
            opts[argv[i]] = argv[i + 1]
            i += 2
        else:
            print(f"❌ Tham số không hợp lệ: {argv[i]}")
            return 2
    items, errors = parse(wbp)
    for e in errors:
        print("❌", e)
    if errors:
        return 1
    out = Path(opts["--out"]) if opts["--out"] else wbp.with_name("punch_list_warranty_backlog.json")
    doc = {"generated_at": datetime.now().isoformat(timespec="seconds"), "source_workbook": wbp.name,
           "project": opts["--project"], "items": items}
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ {len(items)} mục Punch List → {out}")
    if opts["--append-context"]:
        return append_context(Path(opts["--append-context"]), items)
    return 0


if __name__ == "__main__":
    sys.exit(main())
