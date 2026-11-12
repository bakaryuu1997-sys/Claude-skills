#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""xlsx_verify.py — kiểm một file Excel do bộ skill sinh ra (chạy SAU xlsx_build.py hoặc sau khi skill ghi file).

Usage:
    python xlsx_verify.py <file.xlsx> [--client-facing] [--eval] [--allow-placeholder]

Kiểm (FAIL = chặn, WARN = cần xem):
  FAIL  sheet thiếu tiêu đề dòng 1 (merge) · header rỗng · freeze không nằm dưới header · tên sheet > 31 ký tự
  FAIL  công thức có lỗi (#REF!, #DIV/0!, #NAME?, #VALUE!, #N/A) — khi --eval (dùng thư viện `formulas`)
  FAIL  --client-facing: còn tên thương hiệu bên thứ ba (FPT, Rikkei, リッケイ, CMC) hoặc ký hiệu bước nội bộ (/a1-…, Bước A5…)
  WARN  còn placeholder chưa điền: [CẦN ĐIỀN], TODO, FIXME, xxx, {{ }}, lorem  (FAIL nếu --client-facing trừ khi --allow-placeholder)
  WARN  ô số được lưu dưới dạng chuỗi (ví dụ "1,000" hoặc "12.5") — dễ làm sai SUM
  INFO  số công thức, số sheet, số dòng dữ liệu

Exit 0 = không FAIL; 1 = có FAIL; 3 = không kiểm được (thiếu openpyxl/file)."""
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    from openpyxl import load_workbook
except ImportError:
    print("⚠️ thiếu openpyxl (python -m pip install openpyxl)")
    sys.exit(3)

THIRD_PARTY = re.compile(r"FPT|Rikkei|リッケイ|\bCMC\b|F-Pay", re.IGNORECASE)
STEP_CODE = re.compile(r"/[abcdx]\d-[a-z-]+|Bước\s+[ABCDX]\d\b|\bA\d設計書|\bD1\b.*運用")
# {{biến}} kiểu template (Postman/Handlebars) — KHÔNG bắt JSON lồng nhau như {"error": {"code": ...}}
PLACEHOLDER = re.compile(r"\[CẦN ĐIỀN\]|\[要記入\]|\[TO BE FILLED\]|TODO|FIXME|\bxxx\b|\{\{\s*\w+\s*\}\}|lorem", re.IGNORECASE)
# chỉ bắt số có dấu phân cách hàng nghìn hoặc số thập phân dạng chuỗi (ví dụ "1,000", "12.5"); mã số nguyên như 100001/400 là văn bản có chủ đích
NUM_AS_TEXT = re.compile(r"^\s*-?(\d{1,3}(,\d{3})+|\d+\.\d+)(\.\d+)?\s*$")
FORMULA_ERR = ("#REF!", "#DIV/0!", "#NAME?", "#VALUE!", "#N/A", "#NUM!", "#NULL!")


def check(path: Path, client_facing: bool, do_eval: bool, allow_placeholder: bool):
    fails, warns, infos = [], [], []
    wb = load_workbook(path)  # không data_only: đọc công thức
    n_formula = 0
    n_rows_total = 0
    for ws in wb.worksheets:
        where = f"[{ws.title}]"
        if len(ws.title) > 31:
            fails.append(f"{where} tên sheet > 31 ký tự")
        merged = {str(r) for r in ws.merged_cells.ranges}
        if not any(m.startswith("A1:") for m in merged) and ws.max_row >= 1:
            fails.append(f"{where} thiếu tiêu đề merge ở dòng 1")
        if ws.max_row < 3:
            warns.append(f"{where} ít hơn 3 dòng — chưa có bảng")
            continue
        headers = [ws.cell(row=3, column=c).value for c in range(1, ws.max_column + 1)]
        if not any(headers):
            fails.append(f"{where} dòng 3 (header) rỗng")
        elif any(h in (None, "") for h in headers[: max(i + 1 for i, h in enumerate(headers) if h not in (None, ""))]):
            warns.append(f"{where} header có ô trống giữa các cột")
        freeze = ws.freeze_panes
        if freeze not in (None, "A4", "A5", "B4"):
            warns.append(f"{where} freeze_panes = {freeze} (excel-style yêu cầu ngay dưới header, A4)")
        for row in ws.iter_rows(min_row=4):
            for cell in row:
                v = cell.value
                if v is None:
                    continue
                n_rows_total += 1 if cell.column == 1 else 0
                if isinstance(v, str) and v.startswith("="):
                    n_formula += 1
                    if any(e in v for e in FORMULA_ERR):
                        fails.append(f"{where} {cell.coordinate} công thức chứa lỗi: {v}")
                    continue
                s = str(v)
                if client_facing and THIRD_PARTY.search(s):
                    fails.append(f"{where} {cell.coordinate}: tên bên thứ ba còn sót: {s[:60]!r}")
                if client_facing and STEP_CODE.search(s):
                    fails.append(f"{where} {cell.coordinate}: mã bước nội bộ lộ ra: {s[:60]!r}")
                if PLACEHOLDER.search(s):
                    msg = f"{where} {cell.coordinate}: placeholder chưa điền: {s[:60]!r}"
                    (fails if (client_facing and not allow_placeholder) else warns).append(msg)
                if isinstance(v, str) and NUM_AS_TEXT.match(v) and not cell.number_format.startswith("@"):
                    warns.append(f"{where} {cell.coordinate}: số lưu dạng chuỗi {v!r}")
    infos.append(f"{len(wb.worksheets)} sheet · {n_formula} công thức · {n_rows_total} dòng dữ liệu (cột A)")

    if do_eval and n_formula:
        try:
            import formulas  # type: ignore
            xl = formulas.ExcelModel().loads(str(path)).finish()
            sol = xl.calculate()
            for k, v in sol.items():
                txt = str(getattr(v, "value", v))
                if any(e in txt for e in FORMULA_ERR):
                    fails.append(f"[eval] {k}: {txt[:80]}")
            infos.append("công thức đã được tính lại bằng thư viện `formulas`")
        except ImportError:
            warns.append("--eval cần `python -m pip install formulas`; bỏ qua tính lại công thức")
        except Exception as e:  # pragma: no cover
            warns.append(f"--eval không tính được: {e}")
    return fails, warns, infos


def main(argv) -> int:
    args = [a for a in argv[1:] if not a.startswith("--")]
    flags = {a for a in argv[1:] if a.startswith("--")}
    if not args:
        print(__doc__)
        return 2
    path = Path(args[0])
    if not path.exists():
        print(f"❌ không thấy file {path}")
        return 3
    try:
        fails, warns, infos = check(path, "--client-facing" in flags, "--eval" in flags, "--allow-placeholder" in flags)
    except Exception as e:
        print(f"❌ không mở được {path.name}: {e}")
        return 3
    for i in infos:
        print("INFO", i)
    for w in warns:
        print("⚠️ WARN", w)
    for f in fails:
        print("❌ FAIL", f)
    status = "ĐẠT" if not fails else "KHÔNG ĐẠT"
    print(f"\n{status}: {path.name} — {len(fails)} FAIL · {len(warns)} WARN")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
