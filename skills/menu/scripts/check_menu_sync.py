#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_menu_sync.py — kiểm menu đồng bộ với skill folder thực tế (v3.17).
Kiểm: (1) mọi skill trong manifest có folder, (2) skill ngoài manifest có description trong frontmatter
và không phải skill lifecycle quên đăng ký, (3) menu/assets/*.json không trỏ skill không tồn tại,
(4) mỗi skill có ≥1 intent để /menu định tuyến được.
Usage: python check_menu_sync.py [skills_dir]   Exit 1 nếu có lỗi."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import menu_common as mc  # noqa: E402

mc.setup_utf8()

skills_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
try:
    entries, manifest = mc.load_entries(skills_dir)
except Exception as e:  # noqa: BLE001
    print(f"❌ Không đọc được manifest: {e}")
    sys.exit(1)

folders = sorted(p.name for p in skills_dir.iterdir()
                 if p.is_dir() and (p / "SKILL.md").exists() and not p.name.startswith(("_", ".")))
in_manifest = {e["name"] for e in entries if not e["extra"]}
extras = [e for e in entries if e["extra"]]
errors, warns = [], []

orphan = sorted(in_manifest - set(folders))
for s in orphan:
    errors.append(f"manifest có '{s}' nhưng thiếu folder")
for e in extras:
    txt = (skills_dir / e["name"] / "SKILL.md").read_text(encoding="utf-8", errors="ignore")
    if "pipeline.md" in txt or "## 🔗 Workflow Integration" in txt:
        errors.append(f"'{e['name']}' trỏ pipeline.md nhưng THIẾU trong manifest (quên đăng ký?)")
    if not e.get("has_description"):
        errors.append(f"skill ngoài manifest '{e['name']}' thiếu description trong frontmatter")
    if not e.get("intents"):
        warns.append(f"skill ngoài manifest '{e['name']}' chưa có intents (menu/assets/extras.json) — /menu khó định tuyến")
for e in entries:
    if not e["extra"] and not e.get("intents"):
        warns.append(f"'{e['name']}' không có intents[]")
for fname in ("intent_aliases.json", "extras.json"):
    data = mc._json_or_empty(skills_dir / "menu" / "assets" / fname)
    for k in data:
        if k not in folders:
            errors.append(f"menu/assets/{fname}: '{k}' không phải folder skill")

print(f"📁 {len(folders)} skill folder | manifest {len(in_manifest)} + bổ trợ ngoài manifest {len(extras)}"
      + (f" ({', '.join(e['name'] for e in extras)})" if extras else ""))
print("✅ Mọi skill trong manifest đều có folder" if not orphan else "❌ Có skill trong manifest thiếu folder")
for m in errors:
    print("❌", m)
for m in warns:
    print("⚠️", m)
if not errors:
    print("✅ Menu đồng bộ")
sys.exit(1 if errors else 0)
