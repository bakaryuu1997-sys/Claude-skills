#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fill_dev_estimate.py — điền block 開発 của sheet 見積明細書 trong template 見積書 (v2).

Giữ NGUYÊN logo/ảnh, định dạng, công thức và các block khác bằng cách sửa trực tiếp XML
(openpyxl lưu lại sẽ làm mất drawing). openpyxl chỉ dùng để ĐỌC / kiểm tra sau khi điền.

Usage:
  python fill_dev_estimate.py <tasks.json> <output.xlsx> --md-per-pm 22 [--unit md|mh]
        [--hours-per-md 7] [--template <path>] [--sheet 見積明細書]
        [--project-name "<tên hệ thống>"] [--date YYYY-MM-DD] [--client "<tên khách>"]
        [--vendor "<tên bên nhận thầu>"] [--vendor-address "<地址>"] [--vendor-phone "<電話>"]
        [--unit-price <円/人月 cho 開発・基本設計・手順書・結合テスト>]
        [--unit-price-mgmt <円/人月 cho BrSE・PM>]
        [--language ja|vi|en] [--sanitize-map <file.json>|default|none]
        [--allow-truncate] [--keep-empty-rows] [--allow-leak] [--strict]

Đơn vị (--unit):
  md (mặc định): cột 開発 nhập bằng 人日. Các block khác của template tính bằng 人時, nên:
                 - 人月 của 開発 = 小計 ÷ md_per_pm
                 - 人月 của các block 人時 = 小計 ÷ (md_per_pm × hours_per_md)
                 - công thức BrSE/PM (10% tổng) quy 開発 sang giờ (× hours_per_md) trước khi cộng.
  mh           : cột 開発 nhập bằng 人時; 人月 = 小計 ÷ (md_per_pm × hours_per_md) ở MỌI block.
  --md-per-pm PHẢI lấy từ settings.md_per_person_month (trùng /a6-estimate). Mặc định 22 nếu không truyền.

tasks.json: [{"category","function","detail","dev"}, ...] — "dev" theo đúng đơn vị đã chọn.

Mã thoát: 0 = OK; 2 = tham số/dữ liệu sai hoặc quá sức chứa (không ghi file);
          3 = --strict và còn giá trị mẫu của template (tên dự án/ngày/đơn giá/địa chỉ…);
          4 = còn rò rỉ tiếng Việt / tên vendor cũ / mã bước nội bộ trong file (trừ khi --allow-leak).
"""
import argparse
import datetime
import html
import json
import math
import os
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import openpyxl
except ImportError:
    print("LỖI: thiếu openpyxl — chạy `python -m pip install openpyxl` (không dùng `python -I` vì -I ẩn user-site).")
    sys.exit(2)

HERE = Path(__file__).resolve().parent
# Template 見積書 KHÔNG đóng gói trong repo (chứa tên/đơn giá của dự án cũ).
# Truyền --template <file.xlsx> của dự án; bản mặc định chỉ dùng khi bạn tự giữ file cục bộ.
DEFAULT_TEMPLATE = HERE.parent / "assets" / "MPL-H12 App_IOS_見積書_template.xlsx"
DEFAULT_MAP = HERE.parent / "assets" / "sanitize-map-mpl-template.json"
NEUTRAL_VENDOR = "システム開発受託チーム"
TEMPLATE_FIXED_DIVISOR = "140"  # divisor 人月 cứng trong template gốc (20 MD × 7 giờ)

# Giá trị mẫu của template (dự án cũ) — nếu sau khi điền còn nguyên là chưa thay
PLACEHOLDERS = {
    "表紙!B14": "法人向け契約・請求・入金管理システム",
    "表紙!B4": "〒100-0001 東京都千代田区千代田1-1",
    "表紙!B5": "03-1234-5678",
    "見積書!B3": "〒100-0001 東京都千代田区千代田1-1",
    "見積書!B4": "03-1234-5678",
}
PLACEHOLDER_NUMS = {"表紙!D16": 46184, "表紙!C21": 46184,
                    "見積書!E15": 380000, "見積書!E16": 380000, "見積書!E17": 380000,
                    "見積書!E18": 380000, "見積書!E19": 400000, "見積書!E20": 400000}

VN_RE = re.compile(r"[ăâêôơưđĂÂÊÔƠƯĐàáảãạèéẻẽẹìíỉĩịòóỏõọùúủũụỳýỷỹỵấầẩẫậắằẳẵặếềểễệốồổỗộớờởỡợứừửữự]")
STEP_RE = re.compile(r"(?<![A-Za-z0-9])[ABCDX][0-9](?=[぀-ヿ一-鿿])")
EN_PHRASE_RE = re.compile(r"[A-Za-z][A-Za-z0-9 \-/&().,']{3,}")


# ───────────────────────── tham số ─────────────────────────
def parse_args(argv):
    p = argparse.ArgumentParser(description="Điền block 開発 của 見積明細書 (xem docstring đầu file).")
    p.add_argument("tasks")
    p.add_argument("out")
    p.add_argument("--unit", choices=["md", "mh"], default="md")
    p.add_argument("--md-per-pm", type=float, default=22.0)
    p.add_argument("--hours-per-md", type=float, default=7.0)
    p.add_argument("--template", default=None, help="file 見積書 (bắt buộc nếu không có bản mặc định cục bộ)")
    p.add_argument("--sheet", default="見積明細書")
    p.add_argument("--project-name")
    p.add_argument("--date", help="YYYY-MM-DD hoặc YYYY/MM/DD (ngày lập 表紙)")
    p.add_argument("--client", help="tên khách — ghi 'X 御中' vào 見積書!B6 nếu ô tồn tại")
    p.add_argument("--vendor")
    p.add_argument("--vendor-address")
    p.add_argument("--vendor-phone")
    p.add_argument("--unit-price", type=float)
    p.add_argument("--unit-price-mgmt", type=float)
    p.add_argument("--language", choices=["ja", "vi", "en"], default="ja")
    p.add_argument("--sanitize-map", default=None, help="file JSON | default | none")
    p.add_argument("--allow-truncate", action="store_true")
    p.add_argument("--keep-empty-rows", action="store_true")
    p.add_argument("--allow-leak", action="store_true")
    p.add_argument("--strict", action="store_true")
    a = p.parse_args(argv)
    if a.template is None:
        if not DEFAULT_TEMPLATE.exists():
            p.error("thiếu template 見積書: truyền --template <file.xlsx> (file mặc định không có trong repo)")
        a.template = str(DEFAULT_TEMPLATE)
    if a.md_per_pm <= 0 or a.hours_per_md <= 0:
        p.error("--md-per-pm và --hours-per-md phải > 0")
    return a


def fnum(x):
    return str(int(x)) if float(x) == int(x) else repr(float(x))


def ceil01(v):
    return math.ceil(round(v / 0.1, 9)) * 0.1


# ───────────────────────── đọc template ─────────────────────────
def locate_block(xlsx_path, sheet_name):
    wb = openpyxl.load_workbook(xlsx_path, data_only=False)
    if sheet_name not in wb.sheetnames:
        raise RuntimeError("Không thấy sheet %s trong template (có: %s)" % (sheet_name, wb.sheetnames))
    ws = wb[sheet_name]
    header_row = None
    for r in range(1, ws.max_row + 1):
        if ws.cell(row=r, column=1).value == "開発":
            for rr in range(r + 1, r + 4):
                if ws.cell(row=rr, column=2).value == "カテゴリ":
                    header_row = rr
                    break
            break
    if not header_row:
        raise RuntimeError("Không tìm thấy block 開発 / header カテゴリ — KHÔNG đoán bừa")
    data_start = header_row + 1
    subtotal_row = None
    for r in range(data_start, ws.max_row + 1):
        if ws.cell(row=r, column=2).value == "小計":
            subtotal_row = r
            break
    if not subtotal_row:
        raise RuntimeError("Không tìm thấy dòng 小計 của block 開発")
    return header_row, data_start, subtotal_row


def sheet_xml_path(tmpdir, sheet_name):
    wbxml = (Path(tmpdir) / "xl" / "workbook.xml").read_text(encoding="utf-8")
    m = re.search(r'<sheet name="%s"[^>]*r:id="(rId\d+)"' % re.escape(sheet_name), wbxml)
    if not m:
        raise RuntimeError("Không thấy sheet %s trong workbook.xml" % sheet_name)
    rels = (Path(tmpdir) / "xl" / "_rels" / "workbook.xml.rels").read_text(encoding="utf-8")
    m2 = re.search(r'<Relationship Id="%s"[^>]*Target="([^"]+)"' % m.group(1), rels)
    return Path(tmpdir) / "xl" / m2.group(1)


def col_styles(xml, row):
    m = re.search(r'<row r="%d"[^>]*>(.*?)</row>' % row, xml, re.S)
    styles = {}
    if not m:
        return styles
    for cm in re.finditer(r'<c r="([A-H])%d"([^>]*?)(?:/>|>)' % row, m.group(1)):
        sm = re.search(r' s="(\d+)"', cm.group(2))
        styles[cm.group(1)] = sm.group(1) if sm else "0"
    return styles


def esc(s):
    return html.escape(str(s), quote=False)


# ───────────────────────── sửa cell ─────────────────────────
def _col_idx(ref):
    letters = re.match(r"[A-Z]+", ref).group(0)
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch) - 64
    return n


def set_cell(xml, ref, kind, value, default_style=None):
    """kind: 'text' | 'num'. Giữ style s="" của cell cũ. Trả (xml_mới, đã_ghi)."""
    row_no = int(re.search(r"\d+", ref).group(0))
    pat = re.compile(r'<c r="%s"([^>]*?)(?:/>|>.*?</c>)' % ref, re.S)
    m = pat.search(xml)
    style = None
    if m:
        sm = re.search(r' s="(\d+)"', m.group(1))
        style = sm.group(1) if sm else None
    style = style or default_style or "0"
    if kind == "text":
        new = ('<c r="%s" s="%s" t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>'
               % (ref, style, esc(value)))
    else:
        new = '<c r="%s" s="%s"><v>%s</v></c>' % (ref, style, fnum(value))
    if m:
        return xml[:m.start()] + new + xml[m.end():], True
    rm = re.search(r'(<row r="%d"[^>]*?)(/>|>(.*?)</row>)' % row_no, xml, re.S)
    if not rm:
        return xml, False
    if rm.group(2) == "/>":
        return xml[:rm.start()] + rm.group(1) + ">" + new + "</row>" + xml[rm.end():], True
    inner = rm.group(3)
    pos = len(inner)
    for cm in re.finditer(r'<c r="([A-Z]+)\d+"', inner):
        if _col_idx(cm.group(1)) > _col_idx(ref):
            pos = cm.start()
            break
    inner2 = inner[:pos] + new + inner[pos:]
    return xml[:rm.start()] + rm.group(1) + ">" + inner2 + "</row>" + xml[rm.end():], True


def replace_inner(xml, rn, inner):
    return re.sub(r'(<row r="%d"[^>]*>).*?(</row>)' % rn,
                  lambda m: m.group(1) + inner + m.group(2), xml, count=1, flags=re.S)


def hide_rows(xml, rows):
    for r in rows:
        def _h(m):
            tag = m.group(0)
            if tag.endswith("/>"):
                return tag
            if re.search(r' hidden="[^"]*"', tag):
                return re.sub(r' hidden="[^"]*"', ' hidden="1"', tag)
            return tag[:-1] + ' hidden="1">'
        xml = re.sub(r'<row r="%d"[^>]*?>' % r, _h, xml, count=1)
    return xml


def to_serial(date_text):
    d = datetime.datetime.strptime(date_text.replace("/", "-"), "%Y-%m-%d").date()
    return (d - datetime.date(1899, 12, 30)).days


# ───────────────────────── làm sạch template ─────────────────────────
def load_map(a):
    spec = a.sanitize_map
    if spec is None:
        spec = "default" if Path(a.template).resolve() == DEFAULT_TEMPLATE.resolve() else "none"
    if spec == "none":
        return {}
    path = DEFAULT_MAP if spec == "default" else Path(spec)
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as e:
        print("LỖI: không đọc được sanitize-map %s (%s)" % (path, e))
        sys.exit(2)


def sanitize_xml(tmpdir, smap, a):
    """Replace chuỗi theo map (dự án mẫu cũ → trung tính). Chỉ áp dụng nếu có map."""
    if not smap:
        return 0
    vendor = esc(a.vendor or NEUTRAL_VENDOR)
    changed = 0
    for fp in Path(tmpdir).rglob("*.xml"):
        text = fp.read_text(encoding="utf-8")
        orig = text
        if a.language == "ja":
            for vn, ja in smap.get("vn_to_ja", []):
                text = text.replace(esc(vn), esc(ja))
            for old, new in smap.get("exact_cells", []):
                text = text.replace(">%s<" % esc(old), ">%s<" % esc(new))
        for pat in smap.get("brand_patterns", []):
            text = text.replace(esc(pat), vendor)
        for old, new in smap.get("internal_steps", []):
            text = text.replace(esc(old), esc(new))
        if text != orig:
            fp.write_text(text, encoding="utf-8", newline="")
            changed += 1
    return changed


# ───────────────────────── kiểm sau khi điền ─────────────────────────
def scan_output(out_path, smap, a, dev_rows):
    """Trả (leaks[], warns[]). leaks => exit 4."""
    leaks, warns = [], []
    vendor_pat = [p.lower() for p in smap.get("vendor_patterns", [])] + ["rikkei", "リッケイ"]
    wb = openpyxl.load_workbook(out_path, data_only=False)
    for ws in wb.worksheets:
        hidden = ws.sheet_state != "visible"
        if hidden:
            warns.append("sheet ẩn '%s' còn trong file (%d dòng) — mở file kiểm tra/xóa trước khi gửi khách"
                         % (ws.title, ws.max_row))
        for row in ws.iter_rows():
            for c in row:
                v = c.value
                if not isinstance(v, str) or v.startswith("="):
                    continue
                where = "%s!%s%s" % (ws.title, c.coordinate, " (sheet ẩn)" if hidden else "")
                low = v.lower()
                if a.language == "ja" and VN_RE.search(v):
                    leaks.append("%s tiếng Việt: %r" % (where, v[:50]))
                if any(p in low for p in vendor_pat):
                    leaks.append("%s tên vendor cũ: %r" % (where, v[:50]))
                if STEP_RE.search(v):
                    leaks.append("%s mã bước nội bộ: %r" % (where, v[:50]))
                if (a.language == "ja" and not hidden and EN_PHRASE_RE.fullmatch(v.strip())
                        and not (ws.title == a.sheet and c.row in dev_rows and c.column in (2, 3, 4))):
                    warns.append("%s toàn tiếng Anh: %r" % (where, v[:40]))
    for key, val in PLACEHOLDERS.items():
        sh, ref = key.split("!")
        if sh in wb.sheetnames and wb[sh][ref].value == val:
            warns.append("PLACEHOLDER %s vẫn là giá trị mẫu của template: %r" % (key, val))
    for key, val in PLACEHOLDER_NUMS.items():
        sh, ref = key.split("!")
        if sh in wb.sheetnames:
            cv = wb[sh][ref].value
            if isinstance(cv, datetime.datetime):
                cv = to_serial(cv.strftime("%Y-%m-%d"))
            if cv == val:
                warns.append("PLACEHOLDER %s vẫn là giá trị mẫu của template: %r" % (key, val))
    return leaks, warns


# ───────────────────────── main ─────────────────────────
def main():
    a = parse_args(sys.argv[1:])
    try:
        tasks = json.loads(Path(a.tasks).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as e:
        print("LỖI: không đọc được tasks.json (%s)" % e)
        return 2
    if not isinstance(tasks, list) or not tasks:
        print("LỖI: tasks.json phải là mảng không rỗng")
        return 2
    for i, t in enumerate(tasks, 1):
        try:
            float(t.get("dev", 0))
        except (TypeError, ValueError, AttributeError):
            print("LỖI: task #%d có 'dev' không phải số" % i)
            return 2
        if not t.get("function") and not t.get("category"):
            print("LỖI: task #%d thiếu category/function" % i)
            return 2
    tpl = Path(a.template)
    if not tpl.exists():
        print("LỖI: không thấy template: %s" % tpl)
        return 2
    try:
        header_row, data_start, subtotal_row = locate_block(str(tpl), a.sheet)
    except RuntimeError as e:
        print("LỖI:", e)
        return 2
    capacity = subtotal_row - data_start
    n = len(tasks)
    if n > capacity:
        if not a.allow_truncate:
            print("LỖI: %d task > sức chứa %d dòng của block 開発 — báo giá sẽ thiếu hạng mục. "
                  "Mở rộng template (chèn dòng) hoặc gộp task; chỉ dùng --allow-truncate khi chủ ý cắt." % (n, capacity))
            return 2
        print("CẢNH BÁO: cắt còn %d task đầu (--allow-truncate)." % capacity)
        tasks, n = tasks[:capacity], capacity
    last = data_start + n - 1
    smap = load_map(a)
    hpd = fnum(a.hours_per_md)
    hour_div = fnum(a.md_per_pm * a.hours_per_md)

    tmp = tempfile.mkdtemp(prefix="fill_dev_")
    try:
        with zipfile.ZipFile(tpl) as z:
            z.extractall(tmp)
        sanitize_xml(tmp, smap, a)

        sxml_path = sheet_xml_path(tmp, a.sheet)
        xml = sxml_path.read_text(encoding="utf-8")
        st = col_styles(xml, data_start)
        sub_st = col_styles(xml, subtotal_row)
        mb = re.search(r'<c r="B%d".*?(?:</c>|/>)' % subtotal_row, xml, re.S)
        b_subtotal_cell = mb.group(0)

        def s(col): return st.get(col, "0")
        def ss(col): return sub_st.get(col, "0")
        def num(ref, sty, v): return '<c r="%s" s="%s"><v>%s</v></c>' % (ref, sty, v)
        def istr(ref, sty, t): return ('<c r="%s" s="%s" t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>'
                                       % (ref, sty, esc(t)))
        def empt(ref, sty): return '<c r="%s" s="%s"/>' % (ref, sty)
        def fml(ref, sty, f): return '<c r="%s" s="%s"><f>%s</f></c>' % (ref, sty, f)

        for i, t in enumerate(tasks):
            r = data_start + i
            cells = (num("A%d" % r, s("A"), i + 1)
                     + istr("B%d" % r, s("B"), t.get("category", ""))
                     + istr("C%d" % r, s("C"), t.get("function", ""))
                     + istr("D%d" % r, s("D"), t.get("detail", ""))
                     + num("E%d" % r, s("E"), fnum(round(float(t.get("dev", 0)), 1)))
                     + fml("F%d" % r, s("F"), "CEILING((E%d)*0.4, 0.1)" % r)
                     + fml("G%d" % r, s("G"), "CEILING((E%d)*0.1, 0.1)" % r)
                     + fml("H%d" % r, s("H"), "SUM(E%d:G%d)" % (r, r)))
            xml = replace_inner(xml, r, cells)

        for r in range(last + 1, subtotal_row):
            xml = replace_inner(xml, r, "".join(empt("%s%d" % (c, r), s(c)) for c in "ABCDEFGH"))
        if not a.keep_empty_rows and last + 1 < subtotal_row:
            xml = hide_rows(xml, range(last + 1, subtotal_row))

        sub = (empt("A%d" % subtotal_row, ss("A")) + b_subtotal_cell
               + empt("C%d" % subtotal_row, ss("C")) + empt("D%d" % subtotal_row, ss("D"))
               + fml("E%d" % subtotal_row, ss("E"), "SUM(E%d:E%d)" % (data_start, last))
               + fml("F%d" % subtotal_row, ss("F"), "SUM(F%d:F%d)" % (data_start, last))
               + fml("G%d" % subtotal_row, ss("G"), "SUM(G%d:G%d)" % (data_start, last))
               + fml("H%d" % subtotal_row, ss("H"), "SUM(H%d:H%d)" % (data_start, last)))
        xml = replace_inner(xml, subtotal_row, sub)

        # ── Đơn vị: tiêu đề cột H + divisor 人月 + quy đổi BrSE/PM ──
        hstyle = col_styles(xml, header_row).get("H", "0")
        unit_title = "小計 (人日)" if a.unit == "md" else "小計 (人時)"
        new_h = ('<c r="H%d" s="%s" t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>'
                 % (header_row, hstyle, unit_title))
        xml = re.sub(r'<c r="H%d"[^>]*?(?:/>|>.*?</c>)' % header_row, lambda m: new_h, xml, count=1, flags=re.S)

        # mọi 人月 = H<row>/140 trong template → divisor đúng đơn vị
        def _div(m):
            row = int(m.group(1))
            if row == subtotal_row and a.unit == "md":
                return "H%d/%s" % (row, fnum(a.md_per_pm))
            return "H%d/%s" % (row, hour_div)
        xml, n_div = re.subn(r"H(\d+)/%s(?![0-9])" % TEMPLATE_FIXED_DIVISOR, _div, xml)
        if n_div == 0:
            print("CẢNH BÁO: không thấy công thức 人月 '/%s' trong template — kiểm tra divisor thủ công." % TEMPLATE_FIXED_DIVISOR)
        # BrSE / PM = 10% tổng các block (đều ở 人時): quy block 開発 sang giờ khi nhập bằng MD
        if a.unit == "md":
            xml, n_mix = re.subn(r"\(H%d\+" % subtotal_row, "(H%d*%s+" % (subtotal_row, hpd), xml)
            if n_mix == 0:
                print("CẢNH BÁO: không thấy công thức BrSE/PM dạng (H%d+…) — kiểm tra đơn vị hỗn hợp thủ công." % subtotal_row)

        # ── Ô ghi đè theo map (vd. đánh lại số thứ tự) ──
        for sheet_name, cells in (smap.get("cell_overrides") or {}).items():
            try:
                p = sheet_xml_path(tmp, sheet_name)
            except RuntimeError:
                continue
            sx = xml if p == sxml_path else p.read_text(encoding="utf-8")
            for ref, val in cells.items():
                sx, _ = set_cell(sx, ref, "num" if isinstance(val, (int, float)) else "text", val)
            if p == sxml_path:
                xml = sx
            else:
                p.write_text(sx, encoding="utf-8", newline="")

        sxml_path.write_text(xml, encoding="utf-8", newline="")

        # ── 表紙 / 見積書: tên dự án, ngày, vendor, đơn giá ──
        edits = {}  # sheet -> [(ref, kind, value)]
        def want(sheet, ref, kind, val):
            if val is not None:
                edits.setdefault(sheet, []).append((ref, kind, val))
        want("表紙", "B14", "text", a.project_name)
        if a.date:
            try:
                ser = to_serial(a.date)
            except ValueError:
                print("LỖI: --date phải là YYYY-MM-DD hoặc YYYY/MM/DD")
                return 2
            want("表紙", "D16", "num", ser)
            want("表紙", "C21", "num", ser)
        if a.vendor:
            want("表紙", "B3", "text", a.vendor)
            want("見積書", "B2", "text", a.vendor)
        if a.vendor_address:
            want("表紙", "B4", "text", a.vendor_address)
            want("見積書", "B3", "text", a.vendor_address)
        if a.vendor_phone:
            want("表紙", "B5", "text", a.vendor_phone)
            want("見積書", "B4", "text", a.vendor_phone)
        if a.client:
            want("見積書", "B6", "text", "%s 御中" % a.client)
        for ref in ("E15", "E16", "E17", "E18"):
            want("見積書", ref, "num", a.unit_price)
        for ref in ("E19", "E20"):
            want("見積書", ref, "num", a.unit_price_mgmt)
        for sheet_name, items in edits.items():
            try:
                p = sheet_xml_path(tmp, sheet_name)
            except RuntimeError:
                print("CẢNH BÁO: template không có sheet %s — bỏ qua %d ô" % (sheet_name, len(items)))
                continue
            sx = p.read_text(encoding="utf-8")
            for ref, kind, val in items:
                sx, ok = set_cell(sx, ref, kind, val, default_style="3")
                if not ok:
                    print("CẢNH BÁO: không ghi được %s!%s (ô/dòng không tồn tại trong template)" % (sheet_name, ref))
            p.write_text(sx, encoding="utf-8", newline="")

        # ── Buộc Excel tính lại + bỏ giá trị cache của dự án cũ ──
        wbp = Path(tmp) / "xl" / "workbook.xml"
        wbx = wbp.read_text(encoding="utf-8")
        if "fullCalcOnLoad" not in wbx:
            if re.search(r"<calcPr", wbx):
                wbx = re.sub(r"<calcPr", '<calcPr fullCalcOnLoad="1"', wbx, count=1)
            else:
                wbx = wbx.replace("</workbook>", '<calcPr fullCalcOnLoad="1"/></workbook>')
        wbp.write_text(wbx, encoding="utf-8", newline="")
        cc = Path(tmp) / "xl" / "calcChain.xml"
        if cc.exists():
            cc.unlink()  # calcChain cũ không còn khớp công thức → Excel báo hỏng file
            for fp in (Path(tmp) / "[Content_Types].xml", Path(tmp) / "xl" / "_rels" / "workbook.xml.rels"):
                t = fp.read_text(encoding="utf-8")
                t = re.sub(r"<(?:Override|Relationship)[^>]*calcChain[^>]*/>", "", t)
                fp.write_text(t, encoding="utf-8", newline="")
        for fp in (Path(tmp) / "xl" / "worksheets").glob("sheet*.xml"):
            t = fp.read_text(encoding="utf-8")
            t2 = re.sub(r"(<f(?:\s[^>/]*)?(?:/>|>.*?</f>))<v>.*?</v>", r"\1", t, flags=re.S)
            if t2 != t:
                fp.write_text(t2, encoding="utf-8", newline="")

        out = Path(a.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists():
            out.unlink()
        files = sorted((str(p.relative_to(tmp)).replace("\\", "/"), p)
                       for p in Path(tmp).rglob("*") if p.is_file())
        files.sort(key=lambda x: (x[0] != "[Content_Types].xml", x[0]))
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for arc, p in files:
                z.write(p, arc)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ── Tổng hợp số liệu (tính lại bằng Python, khớp công thức CEILING của Excel) ──
    devs = [round(float(t.get("dev", 0)), 1) for t in tasks]
    tot_e = round(sum(devs), 1)
    tot_f = round(sum(ceil01(d * 0.4) for d in devs), 1)
    tot_g = round(sum(ceil01(d * 0.1) for d in devs), 1)
    tot_h = round(tot_e + tot_f + tot_g, 1)
    if a.unit == "md":
        pm = round(tot_h / a.md_per_pm, 2)
        unit_lbl = "人日 (MD)"
    else:
        pm = round(tot_h / (a.md_per_pm * a.hours_per_md), 2)
        unit_lbl = "人時 (MH)"
    print("OK: điền %d task (dòng %d-%d), 小計 dòng %d. đơn vị=%s, md_per_pm=%s, hours_per_md=%s."
          % (n, data_start, last, subtotal_row, a.unit.upper(), fnum(a.md_per_pm), hpd))
    print("    開発=%s %s | UT=%s | Review=%s | 小計=%s %s | ~%s 人月 (chỉ khối 開発)" % (
        tot_e, unit_lbl, tot_f, tot_g, tot_h, unit_lbl, pm))
    print("    Giá trị trong file sẽ được Excel tính lại khi mở (fullCalcOnLoad); file chưa lưu cache số.")

    leaks, warns = scan_output(a.out, smap, a, set(range(data_start, last + 1)))
    for w in warns:
        print("CẢNH BÁO:", w)
    for l in leaks:
        print("RÒ RỈ:", l)
    if leaks and not a.allow_leak:
        print("→ %d chỗ rò rỉ (tiếng Việt/vendor cũ/mã bước). Sửa tasks.json hoặc template rồi chạy lại; "
              "--allow-leak chỉ để bỏ qua có chủ ý." % len(leaks))
        return 4
    if a.strict and any(w.startswith("PLACEHOLDER") for w in warns):
        print("→ --strict: còn giá trị mẫu của template (truyền --project-name/--date/--vendor/--unit-price…).")
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
