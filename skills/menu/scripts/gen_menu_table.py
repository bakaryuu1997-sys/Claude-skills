#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_menu_table.py — bảng menu sinh từ manifest + frontmatter các skill ngoài manifest (v3.17).
Nhãn giai đoạn lấy từ pipeline.md, khoảng bước (A1 → A9, C0 → C8…) tính từ manifest — không hardcode.
Usage: python gen_menu_table.py [skills_dir]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import menu_common as mc  # noqa: E402

mc.setup_utf8()

skills_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
try:
    entries, manifest = mc.load_entries(skills_dir)
except FileNotFoundError as e:
    print(f"❌ {e}")
    sys.exit(1)

labels = mc.phase_labels(skills_dir, entries)
pipeline = [e for e in entries if not e["extra"]]
extras = [e for e in entries if e["extra"]]


def group_of(e):
    if e.get("phase") == "meta" or e.get("step", "-") == "-":
        return "-"
    return e["step"][0]


def row(e):
    outs = ", ".join(e.get("outputs", [])) or "—"
    step = e.get("step", "-")
    opt = " *(tùy chọn)*" if e.get("optional") else ""
    return f"| **{step}** | `/{e['name']}`{opt} | {e.get('summary', '')} | {outs} |"


HEAD = ["| Bước | Lệnh | Tóm tắt | Đầu ra chính |", "|---|---|---|---|"]
groups = {}
for e in sorted(pipeline, key=lambda x: mc.step_key(x.get("step", "-"))):
    groups.setdefault(group_of(e), []).append(e)

for g in sorted(k for k in groups if k != "-"):
    print(f"\n### {labels.get(g, 'GIAI ĐOẠN ' + g)}")
    print("\n".join(HEAD))
    for e in groups[g]:
        print(row(e))
if "-" in groups:
    names = ", ".join(e["name"] for e in groups["-"])
    print(f"\n### META — ĐIỀU HƯỚNG & KIỂM ĐỊNH ({names})")
    print("\n".join(HEAD))
    for e in groups["-"]:
        print(row(e))
if extras:
    print("\n### BỔ TRỢ — NGOÀI PIPELINE (dùng độc lập, không có bước)")
    print("| Lệnh | Tóm tắt | Đầu ra chính |")
    print("|---|---|---|")
    for e in extras:
        print(f"| `/{e['name']}` | {e.get('summary', '')} | {', '.join(e.get('outputs', [])) or '—'} |")

print(f"\nTổng: {len(entries)} skill ({len(pipeline)} trong pipeline + {len(extras)} bổ trợ ngoài manifest)")
