#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_deck.py — sinh deck PowerPoint 16:9 (theme sáng) từ file spec JSON. Engine duy nhất của /x7 (python-pptx).

Usage: python build_deck.py <spec.json> <output.pptx>

Spec (JSON):
{
  "title": "Tên deck", "subtitle": "Khách hàng · ngày",
  "slides": [
    {"type": "bullets", "title": "…", "points": ["…", "…"]},
    {"type": "metrics", "title": "…", "metrics": [
        {"value": "12", "label": "API đã triển khai", "source": "Demo_API_Design_v1.xlsx › Overview"}]},
    {"type": "image", "title": "…", "image": "<đường dẫn ảnh chụp màn hình>", "caption": "…", "source": "…"}
  ]
}

Quy tắc cứng (pipeline.md "Quy ước dùng chung" §5):
- Mỗi "metrics" phải có `source` (file/context thật). Thiếu nguồn → script TỪ CHỐI, không điền số mẫu.
- Không có tên thương hiệu/ngoặc vuông kiểu "[UI/UX]" — script không tự thêm.
- Ảnh chụp màn hình: đặt nguyên, không khung màu dày.
Thiếu python-pptx → báo lỗi rõ (pip install python-pptx)."""
import json
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

try:
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.util import Emu, Inches, Pt
except ImportError:
    print("❌ Thiếu thư viện python-pptx. Cài: python -m pip install python-pptx")
    sys.exit(2)

PRIMARY = RGBColor(0x1F, 0x4E, 0x79)
SECONDARY = RGBColor(0x2E, 0x75, 0xB6)
TEXT = RGBColor(0x1F, 0x29, 0x37)
MUTED = RGBColor(0x6B, 0x72, 0x80)
BG = RGBColor(0xFF, 0xFF, 0xFF)
FONT = "Segoe UI"


def add_text(slide, left, top, width, height, text, size, bold=False, color=TEXT, align=None):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.name = FONT
    p.font.color.rgb = color
    if align is not None:
        p.alignment = align
    return box


def title_bar(slide, text):
    add_text(slide, Inches(0.6), Inches(0.35), Inches(12.1), Inches(0.9), text, 28, bold=True, color=PRIMARY)
    line = slide.shapes.add_shape(1, Inches(0.6), Inches(1.2), Inches(12.1), Emu(22000))
    line.fill.solid()
    line.fill.fore_color.rgb = SECONDARY
    line.line.fill.background()


def footer(slide, source):
    if source:
        add_text(slide, Inches(0.6), Inches(6.95), Inches(12.1), Inches(0.4), CL["source"] + ": " + source, 10, color=MUTED)


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "a1-project-init" / "scripts"))
from i18n import common, placeholder  # noqa: E402
CL, PH = common("vi"), placeholder("vi")


def build(spec: dict, out: Path):
    global CL, PH
    _lang = spec.get("language", "vi")
    CL, PH = common(_lang), placeholder(_lang)
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    blank = prs.slide_layouts[6]

    s = prs.slides.add_slide(blank)
    add_text(s, Inches(0.8), Inches(2.6), Inches(11.7), Inches(1.4), spec.get("title", "Presentation"), 40, bold=True, color=PRIMARY)
    add_text(s, Inches(0.8), Inches(4.1), Inches(11.7), Inches(0.8), spec.get("subtitle", ""), 18, color=MUTED)

    for i, sd in enumerate(spec.get("slides", []), 1):
        kind = sd.get("type", "bullets")
        s = prs.slides.add_slide(blank)
        title_bar(s, sd.get("title", f"Slide {i}"))
        if kind == "bullets":
            pts = sd.get("points", [])
            body = s.shapes.add_textbox(Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.0))
            tf = body.text_frame
            tf.word_wrap = True
            for j, pt in enumerate(pts):
                p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
                p.text = str(pt)
                p.font.size = Pt(18)
                p.font.name = FONT
                p.font.color.rgb = TEXT
                p.space_after = Pt(10)
            footer(s, sd.get("source", ""))
        elif kind == "metrics":
            ms = sd.get("metrics", [])
            missing = [m.get("label", "?") for m in ms if not str(m.get("source", "")).strip()]
            if missing:
                print(f"❌ Slide {i} '{sd.get('title')}': số liệu không có nguồn ({', '.join(missing)}) — từ chối, không điền số mẫu.")
                sys.exit(3)
            n = max(len(ms), 1)
            col_w = 11.7 / n
            for k, m in enumerate(ms):
                x = Inches(0.8 + k * col_w)
                add_text(s, x, Inches(2.2), Inches(col_w - 0.2), Inches(1.2), str(m.get("value", "")), 44, bold=True, color=PRIMARY)
                add_text(s, x, Inches(3.5), Inches(col_w - 0.2), Inches(1.0), str(m.get("label", "")), 16, color=TEXT)
                add_text(s, x, Inches(4.5), Inches(col_w - 0.2), Inches(0.9), CL["source"] + ": " + str(m.get("source", "")), 11, color=MUTED)
        elif kind == "image":
            img = Path(sd.get("image", ""))
            if img.exists():
                s.shapes.add_picture(str(img), Inches(0.8), Inches(1.6), width=Inches(8.4))
            else:
                add_text(s, Inches(0.8), Inches(3.0), Inches(8.4), Inches(1.0), f"{PH[:-1]}: {CL['image']} {img.name}]", 16, color=MUTED)
            if sd.get("caption"):
                add_text(s, Inches(9.5), Inches(1.8), Inches(3.4), Inches(3.0), sd["caption"], 16, color=TEXT)
            footer(s, sd.get("source", ""))
        else:
            print(f"❌ Slide {i}: type '{kind}' không hỗ trợ (bullets | metrics | image)")
            sys.exit(4)

    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out))
    return len(prs.slides)


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    spec = json.loads(Path(argv[0]).read_text(encoding="utf-8"))
    n = build(spec, Path(argv[1]))
    print(json.dumps({"file": str(Path(argv[1]).resolve()), "slides": n}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
