#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_intents.py — test hồi quy định tuyến của /menu.

Parse các bảng "Người dùng nói → Kỹ năng" trong AGENTS.md, đưa từng cụm từ qua match_intent
và báo tỉ lệ top-1 đúng. Cụm trỏ tới skill không có trong thư mục skills (vd impeccable, hallmark, ocr) bị bỏ qua.

Usage: python test_intents.py [skills_dir] [--agents <đường dẫn AGENTS.md>] [--min 95] [-v]
Exit 0 nếu tỉ lệ ≥ --min (mặc định 95), ngược lại 1."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import menu_common as mc  # noqa: E402

mc.setup_utf8()


def parse_args(argv):
    opts = {"agents": None, "min": 95.0, "verbose": False, "dir": None}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--agents":
            opts["agents"] = Path(argv[i + 1]); i += 2
        elif a == "--min":
            opts["min"] = float(argv[i + 1]); i += 2
        elif a in ("-v", "--verbose"):
            opts["verbose"] = True; i += 1
        else:
            opts["dir"] = Path(a); i += 1
    return opts


def parse_agents_table(text: str):
    """[(cụm, skill)] từ các dòng bảng: | *"a", "b"* | `/skill` ... |"""
    pairs = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or not cells[0].startswith("*\""):
            continue
        m = re.search(r"`/?([a-z][a-z0-9\-]*)", cells[1])
        if not m:
            continue
        for ph in re.findall(r"\"([^\"]+)\"", cells[0]):
            pairs.append((ph, m.group(1)))
    return pairs


def main() -> int:
    o = parse_args(sys.argv[1:])
    skills_dir = o["dir"] or Path(__file__).resolve().parents[2]
    agents = o["agents"] or skills_dir.parent / "AGENTS.md"
    if not agents.exists():
        print(f"❌ Không thấy AGENTS.md tại {agents} (dùng --agents)")
        return 2
    entries, _ = mc.load_entries(skills_dir)
    index = mc.build_index(entries)
    known = {e["name"] for e in entries}
    pairs = parse_agents_table(agents.read_text(encoding="utf-8"))
    total = ok = 0
    misses, skipped = [], []
    for ph, expected in pairs:
        if expected not in known:
            skipped.append((ph, expected))
            continue
        total += 1
        ranked = mc.rank(ph, entries, index, limit=1)
        got = ranked[0][1]["name"] if ranked else None
        if got == expected:
            ok += 1
        else:
            misses.append((ph, expected, got))
    rate = 100.0 * ok / total if total else 0.0
    print(f"Top-1 đúng: {ok}/{total} = {rate:.1f}%  (bỏ qua {len(skipped)} cụm trỏ skill ngoài bộ; ngưỡng {o['min']:.0f}%)")
    for ph, exp, got in misses:
        print(f"  MISS \"{ph}\" → mong đợi /{exp}, ra {('/' + got) if got else 'không khớp'}")
    if o["verbose"]:
        for ph, exp in skipped:
            print(f"  SKIP \"{ph}\" → {exp}")
    return 0 if rate >= o["min"] else 1


if __name__ == "__main__":
    sys.exit(main())
