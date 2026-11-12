#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""lang_check.py — quét RÒ RỈ NGÔN NGỮ trong deliverable (xlsx, docx, pptx, md, html, txt, csv).

Mục đích: bảo đảm toàn bộ tài liệu đi theo ngôn ngữ đã chọn ở project-init (`settings.languages`), không lẫn tiếng khác
từ template cũ/ghi chú nháp (AGENTS.md: "Zero Language Leak").

Usage:
    python lang_check.py <file-hoặc-thư-mục> --expect ja|vi|en          # kiểm một đường dẫn theo ngôn ngữ chỉ định
    python lang_check.py --ws <workspace>                               # đọc settings.languages, kiểm đúng nhóm tài liệu
    (thêm --verbose để in từng ô/đoạn bị nghi; --max N giới hạn số dòng in)

Chế độ --ws: thư mục docs/ được chia theo người đọc (bảng trong i18n-policy.md):
    client_facing → B0 B1 B2 D1 D2 D3 (Runbook.md/handover đi theo client_facing)
    code          → C0 C1 C2 (chú thích/mô tả PR: `languages.code`)
    các thư mục nội bộ (A2 A4 A5 B3 A8 C3 C4 C5 C6 X*) → `languages.internal`
    Thư mục chứa cả bản khách lẫn bản nội bộ (C7, C8) được kiểm theo TÊN FILE: *_JA.* / *_VI.* / *_EN.* theo hậu tố; file không hậu tố bỏ qua.

Phát hiện (heuristic, thiên về ít báo nhầm):
    * expect ja → cờ nếu ô/đoạn có ≥ 2 ký tự đặc trưng tiếng Việt (ă â đ ê ô ơ ư và các chữ có dấu chồng).
    * expect en → cờ nếu có ≥ 2 ký tự tiếng Việt HOẶC ≥ 3 ký tự kana/kanji.
    * expect vi → cờ nếu có ≥ 3 ký tự kana (kanji đơn lẻ có thể là tên riêng nên không tính).
Exit: 0 sạch · 1 có rò rỉ · 2 đầu vào sai. Cần openpyxl/python-docx/python-pptx nếu có file tương ứng (thiếu → bỏ qua loại đó và báo).
"""
import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

VI_CHARS = set("ăâđêôơưĂÂĐÊÔƠƯ" "ạảãấầẩẫậắằẳẵặẹẻẽếềểễệịỉĩọỏõốồổỗộớờởỡợụủũứừửữựỵỷỹ"
                "ẠẢÃẤẦẨẪẬẮẰẲẴẶẸẺẼẾỀỂỄỆỊỈĨỌỎÕỐỒỔỖỘỚỜỞỠỢỤỦŨỨỪỬỮỰỴỶỸ")
KANA = re.compile(r"[぀-ヿ]")
KANJI = re.compile(r"[一-鿿]")
SKIP_DIRS = {"node_modules", ".git", ".context-history", "__pycache__"}
TEXT_EXT = {".md", ".txt", ".html", ".htm", ".csv"}

CLIENT_DIRS = ("B0_", "B1_", "B2_", "D1_", "D2_", "D3_")
CODE_DIRS = ("C0_", "C1_", "C2_")
MIXED_DIRS = ("C7_", "C8_")
SUFFIX_LANG = {"_JA": "ja", "_VI": "vi", "_EN": "en"}


def texts_of(path: Path, notes: list):
    """Sinh (vị trí, văn bản) của từng ô/đoạn."""
    ext = path.suffix.lower()
    try:
        if ext == ".xlsx":
            from openpyxl import load_workbook
            wb = load_workbook(path, read_only=False, data_only=False)
            for ws in wb.worksheets:
                yield f"{ws.title}!sheetname", ws.title
                for row in ws.iter_rows():
                    for c in row:
                        if isinstance(c.value, str) and not c.value.startswith("="):
                            yield f"{ws.title}!{c.coordinate}", c.value
        elif ext == ".docx":
            from docx import Document
            d = Document(str(path))
            for i, p in enumerate(d.paragraphs):
                if p.text.strip():
                    yield f"p{i + 1}", p.text
            for ti, t in enumerate(d.tables):
                for ri, r in enumerate(t.rows):
                    for ci, c in enumerate(r.cells):
                        if c.text.strip():
                            yield f"table{ti + 1}[{ri + 1},{ci + 1}]", c.text
            for si, sec in enumerate(d.sections):
                for part, name in ((sec.header, "header"), (sec.footer, "footer")):
                    for p in part.paragraphs:
                        if p.text.strip():
                            yield f"sec{si + 1}.{name}", p.text
        elif ext == ".pptx":
            from pptx import Presentation
            for si, sl in enumerate(Presentation(str(path)).slides, 1):
                for sh in sl.shapes:
                    if sh.has_text_frame and sh.text_frame.text.strip():
                        yield f"slide{si}", sh.text_frame.text
                    if getattr(sh, "has_table", False) and sh.has_table:
                        for r in sh.table.rows:
                            for c in r.cells:
                                if c.text.strip():
                                    yield f"slide{si}.table", c.text
                if sl.has_notes_slide and sl.notes_slide.notes_text_frame.text.strip():
                    yield f"slide{si}.notes", sl.notes_slide.notes_text_frame.text
        elif ext in TEXT_EXT:
            for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if line.strip():
                    yield f"L{i}", line
    except ImportError as e:
        notes.append(f"bỏ qua {path.name}: thiếu thư viện ({e.name})")
    except Exception as e:  # file hỏng không được làm sập cả lần quét
        notes.append(f"không đọc được {path.name}: {e}")


def leaks(text: str, expect: str):
    vi = sum(1 for ch in text if ch in VI_CHARS)
    kana = len(KANA.findall(text))
    kanji = len(KANJI.findall(text))
    out = []
    if expect == "ja" and vi >= 2:
        out.append("tiếng Việt")
    if expect == "en":
        if vi >= 2:
            out.append("tiếng Việt")
        if kana + kanji >= 3:
            out.append("tiếng Nhật")
    if expect == "vi" and kana >= 3:
        out.append("tiếng Nhật")
    return out


def scan_file(path: Path, expect: str, notes: list):
    found = []
    for where, text in texts_of(path, notes):
        kinds = leaks(text, expect)
        if kinds:
            found.append((where, "+".join(kinds), text.strip().replace("\n", " ")[:90]))
    return found


def iter_files(root: Path):
    if root.is_file():
        yield root
        return
    for p in sorted(root.rglob("*")):
        if p.is_file() and not any(part in SKIP_DIRS for part in p.parts) and p.suffix.lower() in TEXT_EXT | {".xlsx", ".docx", ".pptx"} \
                and not p.name.startswith("~$"):
            yield p


def plan_for_ws(ws: Path):
    """Trả [(file, expect)] theo bảng nhóm tài liệu; kèm cảnh báo thiếu cấu hình."""
    ctxp = ws / "project-context.json"
    try:
        langs = (json.loads(ctxp.read_text(encoding="utf-8-sig")).get("settings") or {}).get("languages") or {}
    except (OSError, json.JSONDecodeError):
        langs = {}
    if langs.get("internal") not in ("vi", "ja", "en") and langs.get("client_facing") in ("vi", "ja", "en"):
        langs = dict(langs, internal=langs["client_facing"])  # cùng quy tắc với i18n.resolve_lang
    missing = [k for k in ("client_facing", "internal", "code") if langs.get(k) not in ("vi", "ja", "en")]
    items = []
    docs = ws / "docs"
    for d in sorted(p for p in docs.iterdir() if p.is_dir()) if docs.exists() else []:
        name = d.name
        if name.startswith(MIXED_DIRS):
            for f in iter_files(d):
                stem = f.stem.upper()
                for suf, lang in SUFFIX_LANG.items():
                    if stem.endswith(suf):
                        items.append((f, lang))
            continue
        key = "client_facing" if name.startswith(CLIENT_DIRS) else ("code" if name.startswith(CODE_DIRS) else "internal")
        expect = langs.get(key)
        if expect in ("vi", "ja", "en"):
            items += [(f, expect) for f in iter_files(d)]
    return items, missing


def main(argv=None):
    ap = argparse.ArgumentParser(description="Quét rò rỉ ngôn ngữ trong deliverable")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--expect", choices=("ja", "vi", "en"))
    ap.add_argument("--ws", help="workspace có project-context.json và docs/")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--max", type=int, default=30)
    a = ap.parse_args(argv)

    notes, plan = [], []
    if a.ws:
        plan, missing = plan_for_ws(Path(a.ws))
        if missing:
            print(f"CẢNH BÁO settings.languages thiếu/không hợp lệ: {', '.join(missing)} — nhóm tương ứng KHÔNG được kiểm "
                  "(chạy lại project-init hoặc update_context.py set settings.languages.<khóa> <ja|vi|en>)")
    elif a.path and a.expect:
        root = Path(a.path)
        if not root.exists():
            print(f"ERROR không thấy {root}", file=sys.stderr)
            return 2
        plan = [(f, a.expect) for f in iter_files(root)]
    else:
        ap.error("cần --ws <workspace> hoặc <path> --expect <ja|vi|en>")

    total, bad_files, shown = 0, 0, 0
    for f, expect in plan:
        found = scan_file(f, expect, notes)
        total += 1
        if found:
            bad_files += 1
            print(f"❌ {f} (kỳ vọng {expect}): {len(found)} chỗ lẫn ngôn ngữ")
            for where, kind, snip in found:
                if (a.verbose or shown < a.max):
                    print(f"     {where} [{kind}] {snip}")
                    shown += 1
    for n in notes:
        print("ℹ️ ", n)
    print(f"\nlang_check: {total} file đã quét | {bad_files} file có rò rỉ ngôn ngữ")
    return 1 if bad_files else 0


if __name__ == "__main__":
    sys.exit(main())
