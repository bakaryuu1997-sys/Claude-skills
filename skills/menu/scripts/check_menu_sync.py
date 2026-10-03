# -*- coding: utf-8 -*-
"""Kiểm tra menu đồng bộ với các skill folder thực tế.
Chạy sau khi thêm/xóa skill để menu không bị lỗi thời.
Usage: python3 check_menu_sync.py [đường-dẫn-thư-mục-skills]"""
import re, sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

skills_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
import json
manifest_path = skills_dir / "a1-project-init" / "assets" / "skills-manifest.json"
if not manifest_path.exists():
    manifest_path = skills_dir / "project-init" / "assets" / "skills-manifest.json"
manifest_skills = set()
if manifest_path.exists():
    try:
        m = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest_skills = {e["name"] for e in m.get("skills", [])}
    except Exception as e:
        print(f"❌ Không parse được manifest: {e}")
        sys.exit(1)

folders = sorted(p.name for p in skills_dir.iterdir()
                 if p.is_dir() and (p / "SKILL.md").exists())

missing = [s for s in folders if s not in manifest_skills]
orphan = [s for s in sorted(manifest_skills) if s not in set(folders)]

print(f"📁 {len(folders)} skill folder | manifest có {len(manifest_skills)} skill")
if missing:
    print("❌ SKILL CÓ FOLDER NHƯNG THIẾU TRONG MANIFEST:")
    for s in missing: print("   -", s)
else:
    print("✅ Mọi skill folder đều có trong manifest")
if orphan:
    print("⚠️ SKILL TRONG MANIFEST NHƯNG THIẾU FOLDER:")
    for s in orphan: print("   -", s)
sys.exit(1 if missing else 0)
