#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""match_intent.py — map mô tả task của người dùng → skill, TỪ manifest intents (v3.5.0).
Decision tree của /menu sinh từ đây — thêm skill mới chỉ cần khai intents trong manifest.

Usage: python3 match_intent.py <skills_dir> "<mô tả task>"
In top 3 skill khớp nhất (điểm, step, lý do). Không khớp gì → nói rõ, không đoán bừa."""
import json, sys, unicodedata
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def strip_accents(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


def score(query: str, entry: dict) -> tuple:
    qn = strip_accents(query)
    hits, best_phrase = 0.0, None
    for ph in entry.get("intents", []):
        if strip_accents(ph) in qn:
            hits += 3
            best_phrase = best_phrase or ph
    q_tokens = set(qn.split())
    for src, w in ((entry.get("intents", []), 1.0), ([entry.get("summary", "")], 0.5)):
        toks = set()
        for ph in src:
            toks |= set(strip_accents(ph).split())
        hits += w * len(q_tokens & toks)
    return hits, best_phrase


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    skills_dir, query = Path(sys.argv[1]), sys.argv[2]
    mf = json.loads((skills_dir / "project-init/assets/skills-manifest.json").read_text(encoding="utf-8"))
    ranked = []
    for e in mf.get("skills", []):
        sc, phrase = score(query, e)
        if sc >= 2.0:  # ngưỡng tối thiểu — chặn khớp rác do trùng 1 token vô nghĩa
            ranked.append((sc, e, phrase))
    ranked.sort(key=lambda x: -x[0])
    if not ranked:
        print(f"❓ Không skill nào khớp \"{query}\" — xem toàn bộ: /menu (không đoán bừa)")
        return 1
    print(f"🎯 Task: \"{query}\"")
    for sc, e, phrase in ranked[:3]:
        why = f"khớp intent \"{phrase}\"" if phrase else "khớp từ khóa mô tả"
        print(f"  {sc:5.1f}  /{e['name']}  (bước {e.get('step','-')}) — {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
