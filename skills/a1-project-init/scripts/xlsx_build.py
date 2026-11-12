#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""xlsx_build.py — bộ dựng Excel DÙNG CHUNG cho mọi skill (áp dụng đúng references/excel-style.md).

Skill KHÔNG tự dựng style Excel. Skill viết một spec JSON (xem bên dưới) rồi gọi:
    python xlsx_build.py spec.json out.xlsx

Spec JSON:
{
  "title": "Tiêu đề workbook (metadata, không hiển thị)",
  "language": "ja" | "vi" | "en",              // dùng để chọn font (ja → Yu Gothic, còn lại Arial)
  "sheets": [
    {
      "name": "Test Plan",                       // ≤ 31 ký tự, không chứa : \\ / ? * [ ]
      "title": "Tiêu đề sheet (dòng 1, merge)",
      "subtitle": "Dòng phụ (dòng 2, tùy chọn)",
      "columns": [
        {"key": "id", "header": "Test ID", "width": 16, "wrap": false, "align": "left",
         "numfmt": "@", "validate": ["Y", "N", "Done"]}          // validate: danh sách thả xuống (tùy chọn)
      ],
      "rows": [
        {"id": "ORDER-API-001", "...": "..."},                  // dict theo key, HOẶC list theo thứ tự columns
        {"id": {"value": "P1", "fill": "FDE9E7", "font_color": "C00000", "bold": true}}   // ô có định dạng riêng
      ],
      "total_row": {"label": "Tổng", "sum": ["count"], "formulas": {"pct": "=IFERROR(B{r}/C{r},0)"}},
      "section_rows": {"5": "Nhóm: API"},                      // (tùy chọn) dòng tiêu đề nhóm, chỉ số dòng dữ liệu (0-based)
      "freeze": "auto",                                        // "auto" = ngay dưới header; hoặc ô cụ thể
      "autofilter": true,
      "landscape": true,
      "gridlines": false                                       // true khi skill yêu cầu hiện lưới (ví dụ X4)
    }
  ]
}

Quy tắc cứng (theo excel-style.md):
- Font Arial 9–10 (ja: Yu Gothic). Title navy #1F4E79 trắng đậm; subtitle #2E75B6 trắng; header navy trắng đậm căn giữa.
- Zebra #FFFFFF / #F2F2F2; viền thin #AAAAAA; freeze ngay dưới header; autofilter trên header.
- Chiều cao dòng động theo số dòng quấn thực tế (không hardcode 20/22 khi có wrap).
- Ô có giá trị bắt đầu bằng "=" là CÔNG THỨC (giữ nguyên, không tính trước).
- Không gridlines; in ngang, fit-to-width.
"""
import json
import math
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation
except ImportError:  # pragma: no cover
    sys.exit("❌ thiếu openpyxl: python -m pip install openpyxl (đừng chạy `python -I`)")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from i18n import common  # noqa: E402

NAVY, BLUE, ZEBRA, BORDER = "1F4E79", "2E75B6", "F2F2F2", "AAAAAA"
INVALID_SHEET = re.compile(r"[\\/?*\[\]:]")


def _font(language: str, size: float = 9, bold: bool = False, color: str = "000000") -> Font:
    name = "Yu Gothic" if language == "ja" else "Arial"
    return Font(name=name, size=size, bold=bold, color=color)


def _thin() -> Border:
    s = Side(style="thin", color=BORDER)
    return Border(left=s, right=s, top=s, bottom=s)


def _lines_needed(text: str, width: float) -> int:
    """Ước lượng số dòng quấn: ~1 ký tự ≈ 1 đơn vị width (ký tự CJK tính 2)."""
    if not text:
        return 1
    cap = max(1.0, width * 1.1)
    total = 0.0
    for ch in str(text):
        total += 2.0 if ord(ch) > 0x2E80 else 1.0
    return max(1, math.ceil(total / cap))


def _cell_value(raw):
    """Trả (value, style_overrides)."""
    if isinstance(raw, dict) and "value" in raw:
        return raw["value"], raw
    return raw, {}


def _build_sheet(wb: Workbook, spec: dict, language: str, idx: int):
    COMMON_L = common(language)
    name = str(spec["name"])
    if len(name) > 31 or INVALID_SHEET.search(name):
        raise ValueError(f"tên sheet không hợp lệ: {name!r} (≤31 ký tự, không chứa \\ / ? * [ ] :)")
    ws = wb.active if idx == 0 else wb.create_sheet()
    ws.title = name
    columns = spec.get("columns") or []
    if not columns:
        raise ValueError(f"sheet {name!r}: thiếu columns")
    ncol = len(columns)
    last = get_column_letter(ncol)
    for i, c in enumerate(columns, start=1):
        ws.column_dimensions[get_column_letter(i)].width = float(c.get("width", 14))

    # Dòng 1: tiêu đề (merge)
    r = 1
    ws.merge_cells(f"A{r}:{last}{r}")
    cell = ws[f"A{r}"]
    cell.value = spec.get("title", name)
    cell.font = _font(language, 12, True, "FFFFFF")
    cell.fill = PatternFill("solid", fgColor=NAVY)
    cell.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[r].height = 26

    # Dòng 2: subtitle (merge)
    r = 2
    ws.merge_cells(f"A{r}:{last}{r}")
    cell = ws[f"A{r}"]
    cell.value = spec.get("subtitle", "")
    cell.font = _font(language, 9, False, "FFFFFF")
    cell.fill = PatternFill("solid", fgColor=BLUE)
    cell.alignment = Alignment(horizontal="left", vertical="center", indent=1, wrap_text=True)
    ws.row_dimensions[r].height = 18

    # Dòng 3: header
    hdr_row = 3
    for i, c in enumerate(columns, start=1):
        cell = ws.cell(row=hdr_row, column=i, value=c.get("header", c.get("key", "")))
        cell.font = _font(language, 9, True, "FFFFFF")
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = _thin()
    max_hdr_lines = max(_lines_needed(c.get("header", ""), float(c.get("width", 14))) for c in columns)
    ws.row_dimensions[hdr_row].height = max(24, max_hdr_lines * 14 + 8)

    section_rows = {int(k): v for k, v in (spec.get("section_rows") or {}).items()}
    key_index = {c.get("key"): i for i, c in enumerate(columns, start=1)}
    r = hdr_row + 1
    data_index = 0
    for ridx, row in enumerate(spec.get("rows") or []):
        if ridx in section_rows:
            ws.merge_cells(f"A{r}:{last}{r}")
            sc = ws[f"A{r}"]
            sc.value = section_rows[ridx]
            sc.font = _font(language, 9, True, NAVY)
            sc.fill = PatternFill("solid", fgColor="DDEBF7")
            sc.alignment = Alignment(horizontal="left", vertical="center", indent=1)
            ws.row_dimensions[r].height = 20
            r += 1
        zebra_fill = PatternFill("solid", fgColor=ZEBRA if data_index % 2 else "FFFFFF")
        data_index += 1
        max_lines = 1
        for i, c in enumerate(columns, start=1):
            key = c.get("key")
            if isinstance(row, dict):
                raw = row.get(key, "")
            else:
                raw = row[i - 1] if i - 1 < len(row) else ""
            value, style = _cell_value(raw)
            cell = ws.cell(row=r, column=i, value=value)
            if c.get("numfmt"):
                cell.number_format = c["numfmt"]
            wrap = bool(c.get("wrap", False))
            cell.alignment = Alignment(horizontal=style.get("align", c.get("align", "left")),
                                       vertical="center", wrap_text=wrap)
            fill = style.get("fill")
            cell.fill = PatternFill("solid", fgColor=fill) if fill else zebra_fill
            cell.font = _font(language, 9, bool(style.get("bold", False)), style.get("font_color", "000000"))
            cell.border = _thin()
            if wrap and isinstance(value, str) and not value.startswith("="):
                max_lines = max(max_lines, _lines_needed(value, float(c.get("width", 14))))
        ws.row_dimensions[r].height = max(24, max_lines * 13 + 8)
        r += 1

    # Dòng tổng (tùy chọn)
    tot = spec.get("total_row")
    if tot:
        label_cell = ws.cell(row=r, column=1, value=tot.get("label", COMMON_L["total"]))
        label_cell.font = _font(language, 9, True, NAVY)
        for col_key in tot.get("sum", []):
            ci = key_index.get(col_key)
            if ci is None:
                raise ValueError(f"total_row.sum: không có cột {col_key!r}")
            L = get_column_letter(ci)
            cell = ws.cell(row=r, column=ci, value=f"=SUM({L}{hdr_row + 1}:{L}{r - 1})")
            cell.font = _font(language, 9, True, NAVY)
        for col_key, formula in (tot.get("formulas") or {}).items():
            ci = key_index.get(col_key)
            if ci is None:
                raise ValueError(f"total_row.formulas: không có cột {col_key!r}")
            cell = ws.cell(row=r, column=ci, value=formula.replace("{r}", str(r)))
            cell.font = _font(language, 9, True, NAVY)
        for i in range(1, ncol + 1):
            c_ = ws.cell(row=r, column=i)
            c_.fill = PatternFill("solid", fgColor="DDEBF7")
            c_.border = _thin()
        ws.row_dimensions[r].height = 20
        r += 1
    last_data_row = r - 1

    # Data validation (danh sách thả xuống)
    for i, c in enumerate(columns, start=1):
        if c.get("validate"):
            choices = [str(x) for x in c["validate"]]
            dv = DataValidation(type="list", formula1='"' + ",".join(choices).replace('"', "'") + '"', allow_blank=True)
            dv.error = COMMON_L["dv_msg"]
            dv.errorTitle = COMMON_L["dv_title"]
            ws.add_data_validation(dv)
            L = get_column_letter(i)
            dv.add(f"{L}{hdr_row + 1}:{L}{max(hdr_row + 1, last_data_row)}")

    # Freeze, filter, view, in
    freeze = spec.get("freeze", "auto")
    ws.freeze_panes = f"A{hdr_row + 1}" if freeze == "auto" else freeze
    if spec.get("autofilter", True) and last_data_row > hdr_row:
        ws.auto_filter.ref = f"A{hdr_row}:{last}{last_data_row}"
    ws.sheet_view.showGridLines = bool(spec.get("gridlines", False))  # X4 yêu cầu lưới: đặt "gridlines": true trong spec
    ws.page_setup.orientation = "landscape" if spec.get("landscape", True) else "portrait"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_title_rows = f"{hdr_row}:{hdr_row}"
    return ws


def build(spec: dict, out_path: Path) -> Path:
    language = spec.get("language", "vi")
    wb = Workbook()
    wb.properties.title = spec.get("title", "")
    sheets = spec.get("sheets") or []
    if not sheets:
        raise ValueError("spec.sheets rỗng")
    for i, s in enumerate(sheets):
        _build_sheet(wb, s, language, i)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out_path)
    return out_path


def main(argv) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    spec = json.loads(Path(argv[1]).read_text(encoding="utf-8-sig"))
    out = build(spec, Path(argv[2]))
    print(f"✅ đã dựng {out} ({len(spec.get('sheets', []))} sheet)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
