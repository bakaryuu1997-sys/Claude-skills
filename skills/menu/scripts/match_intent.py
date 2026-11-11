#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""match_intent.py — map mô tả task của người dùng → skill, từ intents trong manifest (v3.17).

Nguồn: skills-manifest.json (intents[]) + menu/assets/intent_aliases.json (cụm từ bổ sung)
+ skill ngoài manifest (menu/assets/extras.json hoặc frontmatter). Thêm skill mới chỉ cần khai intents.
Chấm điểm: cụm khớp nguyên văn > đủ token (mọi thứ tự) > token IDF (bỏ stopword) > bigram.

Usage: python match_intent.py <skills_dir> "<mô tả task>" [--json]
In top 3 skill khớp nhất. Không khớp gì → nói rõ, không đoán bừa.
Exit 0 = có kết quả, 1 = không khớp, 2 = sai cú pháp."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import menu_common as mc  # noqa: E402

mc.setup_utf8()


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--json"]
    as_json = "--json" in sys.argv
    if len(args) < 2:
        print(__doc__)
        return 2
    skills_dir, query = Path(args[0]), args[1]
    entries, _ = mc.load_entries(skills_dir)
    ranked = mc.rank(query, entries)
    if as_json:
        print(json.dumps([{"skill": e["name"], "step": e.get("step", "-"), "score": round(sc, 2), "intent": ph}
                          for sc, e, ph in ranked], ensure_ascii=False))
        return 0 if ranked else 1
    if not ranked:
        print(f"❓ Không skill nào khớp \"{query}\" — xem toàn bộ: /menu (không đoán bừa)")
        return 1
    print(f"🎯 Task: \"{query}\"")
    for sc, e, phrase in ranked:
        why = f"khớp intent \"{phrase}\"" if phrase else "khớp từ khóa"
        tag = "skill bổ trợ" if e.get("extra") else f"bước {e.get('step', '-')}"
        print(f"  {sc:5.1f}  /{e['name']}  ({tag}) — {why}")
    if len(ranked) > 1 and ranked[0][0] - ranked[1][0] < 2:
        print("  ↳ top 1 và top 2 sát điểm — nêu cả hai kèm điểm khác biệt khi trả lời.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
