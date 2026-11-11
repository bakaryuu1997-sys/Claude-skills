#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""docx_build.py — bộ dựng Word DÙNG CHUNG cho tài liệu thiết kế (áp dụng references/i18n-policy.md về font).

Usage:
    python docx_build.py spec.json out.docx

Spec JSON:
{
  "language": "ja" | "vi" | "en",
  "title": "基本設計書",                       // tiêu đề bìa + thuộc tính tài liệu
  "subtitle": "勤怠承認システム（サンプル）",
  "meta": [["版", "1.0"], ["作成日", "2026-11-12"], ["作成者", "[担当者]"], ["承認者", "[担当者]"]],
  "header_text": "勤怠承認システム（サンプル） 基本設計書",
  "footer_text": "Confidential — 社外秘",
  "blocks": [
    {"type": "h1", "text": "1. 目的・適用範囲"},
    {"type": "p", "text": "本書は……"},
    {"type": "bullets", "items": ["……", "……"]},
    {"type": "table", "caption": "表 1 画面一覧", "columns": ["画面ID", "画面名", "説明"], "widths": [2.5, 4, 9.5],
     "rows": [["SCR-01", "ログイン", "……"]]},
    {"type": "code", "text": "flowchart LR ...", "lang": "mermaid"},
    {"type": "pagebreak"}
  ]
}
- Font: ja → Yu Gothic (ascii/hAnsi/eastAsia/cs đều được đặt); vi/en → Arial. Không dựa font mặc định Calibri.
- Heading dùng style Heading 1/2/3 của Word (để tạo mục lục tự động trong Word).
- Bảng: hàng tiêu đề nền #1F4E79 chữ trắng đậm, lặp lại ở mỗi trang, viền #AAAAAA, cỡ chữ 9pt.
"""
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    from docx import Document
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_BREAK
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Cm, Pt, RGBColor
except ImportError:  # pragma: no cover
    sys.exit("❌ thiếu python-docx: python -m pip install python-docx (đừng chạy `python -I`)")

NAVY = "1F4E79"
BORDER = "AAAAAA"


def _set_font(run_or_style, name: str, size: float | None = None, bold: bool | None = None, color: str | None = None):
    font = run_or_style.font
    font.name = name
    el = run_or_style.element if hasattr(run_or_style, "element") else run_or_style._element
    rpr = el.get_or_add_rPr() if hasattr(el, "get_or_add_rPr") else el
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rfonts.set(qn(attr), name)
    if size:
        font.size = Pt(size)
    if bold is not None:
        font.bold = bold
    if color:
        font.color.rgb = RGBColor.from_string(color)


def _shade(cell, hex_color: str):
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcpr.append(shd)


def _borders(table):
    tbl = table._tbl
    tblpr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), BORDER)
        borders.append(el)
    tblpr.append(borders)


def _repeat_header(row):
    trpr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    trpr.append(el)


def _add_field(paragraph, instr: str):
    run = paragraph.add_run()
    b = OxmlElement("w:fldChar"); b.set(qn("w:fldCharType"), "begin")
    t = OxmlElement("w:instrText"); t.set(qn("xml:space"), "preserve"); t.text = instr
    e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), "end")
    run._r.append(b); run._r.append(t); run._r.append(e)


def build(spec: dict, out: Path) -> Path:
    lang = spec.get("language", "vi")
    font = "Yu Gothic" if lang == "ja" else "Arial"
    doc = Document()
    doc.core_properties.title = spec.get("title", "")
    doc.core_properties.subject = spec.get("subtitle", "")

    sec = doc.sections[0]
    sec.left_margin = sec.right_margin = Cm(2.0)
    sec.top_margin = sec.bottom_margin = Cm(2.0)
    hdr = sec.header.paragraphs[0]
    hdr.text = spec.get("header_text", spec.get("title", ""))
    for r in hdr.runs:
        _set_font(r, font, 8, color="7F7F7F")
    ftr = sec.footer.paragraphs[0]
    ftr.text = (spec.get("footer_text", "") + "    ").strip()
    for r in ftr.runs:
        _set_font(r, font, 8, color="7F7F7F")
    _add_field(ftr, "PAGE")

    normal = doc.styles["Normal"]
    _set_font(normal, font, 10)
    normal.paragraph_format.space_after = Pt(4)
    normal.paragraph_format.line_spacing = 1.25
    for name, size, color in (("Heading 1", 15, NAVY), ("Heading 2", 12, NAVY), ("Heading 3", 10.5, "000000")):
        st = doc.styles[name]
        _set_font(st, font, size, True, color)
        st.paragraph_format.space_before = Pt(12 if name == "Heading 1" else 8)
        st.paragraph_format.space_after = Pt(4)
        st.paragraph_format.keep_with_next = True

    # Bìa
    t = doc.add_paragraph()
    t.paragraph_format.space_before = Pt(90)
    r = t.add_run(spec.get("title", ""))
    _set_font(r, font, 26, True, NAVY)
    if spec.get("subtitle"):
        s = doc.add_paragraph()
        r = s.add_run(spec["subtitle"])
        _set_font(r, font, 14, False, "404040")
    if spec.get("meta"):
        doc.add_paragraph()
        mt = doc.add_table(rows=0, cols=2)
        mt.alignment = WD_TABLE_ALIGNMENT.LEFT
        _borders(mt)
        for k, v in spec["meta"]:
            row = mt.add_row().cells
            row[0].text, row[1].text = str(k), str(v)
            _shade(row[0], "DDEBF7")
            for c in row:
                for p in c.paragraphs:
                    for rr in p.runs:
                        _set_font(rr, font, 9)
        for row in mt.rows:
            row.cells[0].width = Cm(4)
            row.cells[1].width = Cm(12)
    doc.add_page_break()

    for blk in spec.get("blocks", []):
        typ = blk.get("type")
        if typ in ("h1", "h2", "h3"):
            doc.add_heading(blk["text"], level=int(typ[1]))
        elif typ == "p":
            p = doc.add_paragraph()
            r = p.add_run(blk["text"])
            _set_font(r, font, 10, bool(blk.get("bold")))
        elif typ == "bullets":
            for item in blk.get("items", []):
                p = doc.add_paragraph(style="List Bullet")
                r = p.add_run(item)
                _set_font(r, font, 10)
        elif typ == "numbered":
            for item in blk.get("items", []):
                p = doc.add_paragraph(style="List Number")
                r = p.add_run(item)
                _set_font(r, font, 10)
        elif typ == "code":
            p = doc.add_paragraph()
            r = p.add_run(blk["text"])
            _set_font(r, "Consolas" if lang != "ja" else "MS Gothic", 8.5)
            p.paragraph_format.left_indent = Cm(0.4)
            pPr = p._p.get_or_add_pPr()
            shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:fill"), "F2F2F2")
            pPr.append(shd)
        elif typ == "table":
            if blk.get("caption"):
                cp = doc.add_paragraph()
                cr = cp.add_run(blk["caption"])
                _set_font(cr, font, 9, True, NAVY)
                cp.paragraph_format.keep_with_next = True
            cols = blk["columns"]
            rows = blk.get("rows", [])
            tbl = doc.add_table(rows=1, cols=len(cols))
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            tbl.autofit = False
            _borders(tbl)
            head = tbl.rows[0]
            _repeat_header(head)
            for i, c in enumerate(cols):
                cell = head.cells[i]
                cell.text = ""
                r = cell.paragraphs[0].add_run(str(c))
                _set_font(r, font, 9, True, "FFFFFF")
                _shade(cell, NAVY)
            for row in rows:
                cells = tbl.add_row().cells
                for i, v in enumerate(row):
                    cells[i].text = ""
                    lines = str(v).split("\n")
                    for li, line in enumerate(lines):
                        para = cells[i].paragraphs[0] if li == 0 else cells[i].add_paragraph()
                        para.paragraph_format.space_after = Pt(0)
                        rr = para.add_run(line)
                        _set_font(rr, font, 9)
            widths = blk.get("widths")
            if widths:
                for row in tbl.rows:
                    for i, w in enumerate(widths):
                        row.cells[i].width = Cm(w)
            doc.add_paragraph()
        elif typ == "pagebreak":
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        else:
            raise ValueError(f"block type không hỗ trợ: {typ}")

    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out)
    return out


def main(argv) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    spec = json.loads(Path(argv[1]).read_text(encoding="utf-8-sig"))
    out = build(spec, Path(argv[2]))
    print(f"✅ đã dựng {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
