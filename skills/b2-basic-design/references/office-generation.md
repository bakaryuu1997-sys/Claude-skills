# Sinh file Office (docx / pptx / xlsx) + nhúng sơ đồ — dùng chung cho b0, b1, b2, b3

> Nguồn chung cho 4 skill nhóm B. Quy tắc màu/font/công thức Excel nằm ở `a1-project-init/references/excel-style.md`
> và `i18n-policy.md` — file này chỉ thêm kỹ thuật cài đặt. Đoạn code dưới đây đã chạy thử với python-docx 1.x,
> python-pptx 1.x, openpyxl 3.1 (Windows, Python 3.12).

## 0. Điều kiện chạy

```python
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # console Windows mặc định cp932/cp1252
try:
    import docx, openpyxl            # python-docx, openpyxl
    import pptx                      # python-pptx (chỉ b1 cần)
except ImportError as e:
    raise SystemExit(f"Thiếu thư viện: {e.name}. Chạy: python -m pip install python-docx python-pptx openpyxl")
```

- Chạy bằng `python` (KHÔNG `python -I` khi cần thư viện cài ở user-site: `-I` bỏ user-site).
- Ghi/đọc file văn bản luôn `encoding="utf-8"`, dùng `pathlib.Path`; tên file tiếng Việt/Nhật hợp lệ trên Windows nhưng tránh ký tự `\ / : * ? " < > |` và `[` `]` trong tên dự án.
- Thư mục xuất: `docs/<MÃ BƯỚC>_<tên-skill>/` (tạo bằng `Path.mkdir(parents=True, exist_ok=True)`).

## 1. Font theo ngôn ngữ (bắt buộc đặt rõ — `i18n-policy.md`)

`FONT = {"ja": "Yu Gothic", "vi": "Arial", "en": "Arial"}[settings.languages.client_facing]` (b3 dùng key `internal`).

```python
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def _set_rfonts(rpr, name):
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.insert(0, rf)
    for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
        rf.set(qn(a), name)

def apply_docx_font(doc, name):                  # gọi 1 lần sau Document()
    for st in doc.styles:
        if st.type == 1:                         # paragraph styles (Normal, Heading 1…)
            st.font.name = name
            _set_rfonts(st.element.get_or_add_rPr(), name)

def set_run_font(run, name):                     # cho run tạo thêm có font riêng (code block: "Consolas")
    run.font.name = name
    _set_rfonts(run._element.get_or_add_rPr(), name)
```

```python
# pptx: bắt buộc đặt latin + ea + cs cho MỌI run (python-pptx chỉ đặt latin)
from pptx.oxml.ns import qn as pqn
def set_pptx_font(run, name):
    run.font.name = name
    rpr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        el = rpr.find(pqn(tag))
        if el is None:
            el = rpr.makeelement(pqn(tag), {}); rpr.append(el)
        el.set("typeface", name)
# Lưu ý: RGBColor của pptx (pptx.dml.color) KHÁC của docx (docx.shared) — import đúng thư viện.
```

```python
# openpyxl
from openpyxl.styles import Font
cell.font = Font(name=FONT, size=10, bold=False)
```

Sau khi sinh: mở file, kiểm có chữ Nhật/dấu Việt hiển thị đúng; không để ô nào còn font Calibri/Arial lẫn trong file `ja`.

## 2. Excel — checklist tối thiểu (chi tiết: `excel-style.md`)

- Màu: dùng palette excel-style (title/header `#1F4E79`, sub `#2E75B6`, zebra `#F2F2F2`, border `#AAAAAA`); freeze panes dưới header; wrap text cột dài; KHÔNG đặt chiều cao dòng cố định nhỏ.
- Mọi số tổng/tỷ lệ phủ là CÔNG THỨC, ví dụ (hàng dữ liệu 2..N, N lấy từ code):

```python
ws[f"F{n+2}"] = f"=SUM(F2:F{n+1})"                                   # tổng % thanh toán
ws[f"G{n+2}"] = f'=IF(ROUND(F{n+2},4)=1,"OK","Tổng khác 100%")'
ws["I2"] = f'=COUNTIF(H2:H{n+1},"COVERED")/COUNTA(A2:A{n+1})'        # tỷ lệ phủ
ws["I2"].number_format = "0%"
```

- Tên sheet là định danh cố định bằng tiếng Anh (các skill sau và `x2` tìm theo tên: `Screen_List`, `Validation_Spec`, `Milestone_Deliverables`…); tiêu đề hàng 1 và header cột theo ngôn ngữ tài liệu (xem `jp-glossary.md` ở b2/b3).
- Sau khi lưu: `openpyxl.load_workbook(path)` kiểm số sheet, số cột, ô công thức bắt đầu bằng `=`; sai → sửa rồi mới bàn giao.

## 3. docx / pptx — cấu hình nhanh

```python
from docx import Document
from docx.shared import Inches, Pt
doc = Document()
apply_docx_font(doc, FONT)
for s in doc.sections:
    s.left_margin = s.right_margin = s.top_margin = s.bottom_margin = Inches(1)
# Ô bảng: nền màu header
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
cell._tc.get_or_add_tcPr().append(parse_xml(r'<w:shd {} w:fill="1F4E79"/>'.format(nsdecls("w"))))
doc.save(path)
```

```python
from pptx import Presentation
from pptx.util import Inches
prs = Presentation(); prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)   # 16:9
blank = prs.slide_layouts[6]
```

## 4. Nhúng sơ đồ Mermaid vào docx (khách ký docx nên sơ đồ phải nằm TRONG docx)

1. Kiểm công cụ: `mmdc --version` (hoặc `npx -y @mermaid-js/mermaid-cli --version`). Có → bước 2. Không có → bước 5.
2. Tách khối ```` ```mermaid ```` từ `*_Diagrams.md` thành file `.mmd`:

```python
import re
from pathlib import Path
def split_mermaid(md_path, out_dir):
    text = Path(md_path).read_text(encoding="utf-8")
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    blocks = re.findall(r"```mermaid\s*\n(.*?)```", text, flags=re.S)
    for i, b in enumerate(blocks, 1):
        (out / f"diagram_{i:02d}.mmd").write_text(b, encoding="utf-8")
    return len(blocks)
```

3. Render từng file (font phải có glyph Nhật/Việt — đặt qua file cấu hình):
   `config.json` = `{"theme":"default","themeVariables":{"fontFamily":"Yu Gothic, Meiryo, Arial"}}`
   `mmdc -i diagram_01.mmd -o diagram_01.png -c config.json -b white -s 2`
4. Nhúng: `doc.add_picture(str(png), width=Inches(6.0))` + caption "Hình N: …". Lỗi render một sơ đồ (cú pháp) → sửa theo `mermaid-rules.md`, KHÔNG nhúng ảnh lỗi.
5. Không có mmdc: giữ `*_Diagrams.md` làm bản sơ đồ gốc; trong docx thay hình bằng BẢNG tương đương (ví dụ Screen Transition → bảng "SCR nguồn / sự kiện / điều kiện / SCR đích"; Sequence → bảng các bước) và ghi rõ trong response "hình chưa nhúng vì thiếu mmdc". Không dán mã Mermaid thô vào tài liệu gửi khách.
