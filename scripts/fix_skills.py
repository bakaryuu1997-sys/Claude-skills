#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_skills.py
Script tự động chuẩn hóa toàn diện bộ skill (dev-lifecycle-skills v3.8.0):
1. Sửa toàn bộ nhãn "Bước" trong frontmatter description của 20 skill.
2. Sửa lỗi tên & tham chiếu chéo (a6-estimate man-day, api-design, v.v.).
3. Chuẩn hóa đường dẫn output docs/C0_... thành docs/C1_....
4. Cập nhật README.md (14 cột, docs path, superpowers note, UTF-8 sạch).
5. Thêm claude-mem vào plugin.json và đồng bộ tất cả version lên 3.8.0.
"""

import json
import re
from pathlib import Path

REPO_ROOT = Path(r"C:\Users\asus\Claude\Projects\claude-skill")
SKILLS_DIR = REPO_ROOT / "skills"
PLUGIN_JSON = REPO_ROOT / "plugin.json"
MARKETPLACE_JSON = REPO_ROOT / "marketplace.json"
README_MD = REPO_ROOT / "README.md"
MANIFEST_JSON = SKILLS_DIR / "a1-project-init" / "assets" / "skills-manifest.json"

TARGET_VERSION = "3.8.0"

CORE_SKILLS = [
    "a1-project-init", "a2-requirement-analysis", "a3-prototype-ui",
    "a4-api-design", "a5-db-design", "a6-estimate", "a7-estimate-template-fill",
    "a8-test-plan", "a9-project-timeline",
    "b0-proposal-sow", "b1-project-kickoff", "b2-basic-design", "b3-detail-design",
    "c1-dev-implement", "c2-api-test-suite-generator", "c3-code-review",
    "c4-trailofbits-security-skills", "c5-test-execution", "c6-sprint-review",
    "c7-change-request", "c8-release-deployment",
    "d1-handover-doc", "d2-uat-acceptance", "d3-user-guide-manual",
    "x1-acquire-codebase-knowledge", "x2-project-architecture", "x3-project-status",
    "x4-meeting-minutes", "x5-coding-standards", "x6-skill-doctor", "x7-presentation-deck",
    "menu"
]

print("="*70)
print(f"BAT DAU CHUAN HOA TOAN DIEN BO SKILL LEN v{TARGET_VERSION}")
print("="*70)

# -------------------------------------------------------------
# 1 & 2. Sửa nhãn "Bước", lỗi tham chiếu chéo & nâng version trong SKILL.md
# -------------------------------------------------------------
STEP_REPLACEMENTS = {
    "a1-project-init": [
        (r"Bước A0 — CHẠY ĐẦU TIÊN", r"Bước A1 — CHẠY ĐẦU TIÊN"),
    ],
    "a2-requirement-analysis": [
        (r"Bước A1\.", r"Bước A2."),
    ],
    "a3-prototype-ui": [
        (r"Bước A2 —", r"Bước A3 —"),
    ],
    "a4-api-design": [
        (r"Bước A3 pipeline", r"Bước A4 pipeline"),
    ],
    "a5-db-design": [
        (r"Bước A3 \(song song /a4-api-design\)", r"Bước A5 (song song /a4-api-design)"),
    ],
    "a6-estimate": [
        (r"báo giá/WBS/a6-estimate man-day", r"báo giá/WBS/estimate man-day"),
        (r"Bước A4\.", r"Bước A6."),
    ],
    "a7-estimate-template-fill": [
        (r"Bước A4b\.", r"Bước A7."),
    ],
    "a8-test-plan": [
        (r"Bước A5\.", r"Bước A8."),
    ],
    "a9-project-timeline": [
        (r"Bước A6\.", r"Bước A9."),
    ],
    "b3-detail-design": [
        (r"CẦN api-design \+ db-design trước", r"CẦN a4-api-design + a5-db-design trước"),
    ],
    "c1-dev-implement": [
        (r"Bước C0 —", r"Bước C1 —"),
        (r"detail-design \+ api-design \+ db-design", r"b3-detail-design + a4-api-design + a5-db-design"),
        (r"docs/C0_dev-implement", r"docs/C1_dev-implement"),
    ],
    "c2-api-test-suite-generator": [
        (r"Bước C0b —", r"Bước C2 —"),
        (r"docs/C0_dev-implement", r"docs/C1_dev-implement"),
    ],
    "c3-code-review": [
        (r"đối chiếu spec api-design/a5-db-design", r"đối chiếu spec a4-api-design/a5-db-design"),
        (r"Bước C1 — mỗi PR\.", r"Bước C3 — mỗi PR."),
    ],
    "c4-trailofbits-security-skills": [
        (r"Bước C1b —", r"Bước C4 —"),
        (r"docs/C1_security-audit", r"docs/C4_security-audit"),
    ],
    "c5-test-execution": [
        (r"Bước C2\.", r"Bước C5."),
        (r"docs/C2_test-execution", r"docs/C5_test-execution"),
    ],
    "c6-sprint-review": [
        (r"Bước C3 — cuối mỗi sprint\.", r"Bước C6 — cuối mỗi sprint."),
        (r"docs/C3_sprint-review", r"docs/C6_sprint-review"),
    ],
    "c7-change-request": [
        (r"Bước C4 — bất kỳ lúc nào", r"Bước C7 — bất kỳ lúc nào"),
    ],
    "x1-acquire-codebase-knowledge": [
        (r"Bước X0\.", r"Bước X1."),
        (r"docs/X0_codebase-knowledge", r"docs/X1_codebase-knowledge"),
    ],
    "x2-project-architecture": [
        (r"Bước X1 — chạy bất kỳ lúc nào sau A3", r"Bước X2 — chạy bất kỳ lúc nào sau A4/A5"),
    ],
    "x3-project-status": [
        (r"Bước X2 — chạy bất kỳ lúc nào\.", r"Bước X3 — chạy bất kỳ lúc nào."),
        (r"A0→D1", r"A1→D3"),
    ],
    "x6-skill-doctor": [
        (r"Bước X3\.", r"Bước X6."),
    ],
}

# Quét sửa từng SKILL.md
for skill_name in CORE_SKILLS:
    skill_file = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_file.exists():
        continue
    content = skill_file.read_text(encoding="utf-8")

    # Nâng version lên 3.8.0 trong frontmatter
    content = re.sub(r'version:\s*"[^"]+"', f'version: "{TARGET_VERSION}"', content)
    content = re.sub(r"version:\s*'[^']+'", f'version: "{TARGET_VERSION}"', content)

    # Áp dụng các thay đổi đặc thù
    if skill_name in STEP_REPLACEMENTS:
        for pattern, replacement in STEP_REPLACEMENTS[skill_name]:
            content = re.sub(pattern, replacement, content)

    skill_file.write_text(content, encoding="utf-8")
    print(f"  [OK] Da cap nhat {skill_name}/SKILL.md -> v{TARGET_VERSION}")

# -------------------------------------------------------------
# 3. Chuẩn hóa đường dẫn output docs/ trong các file liên quan
# -------------------------------------------------------------
DOCS_PATH_MAP = [
    (r"docs/C0_dev-implement", r"docs/C1_dev-implement"),
    (r"docs/C1_security-audit", r"docs/C4_security-audit"),
    (r"docs/C2_test-execution", r"docs/C5_test-execution"),
    (r"docs/C3_sprint-review", r"docs/C6_sprint-review"),
    (r"docs/X0_codebase-knowledge", r"docs/X1_codebase-knowledge"),
]

# -------------------------------------------------------------
# 4. Cập nhật README.md
# -------------------------------------------------------------
if README_MD.exists():
    readme_content = README_MD.read_text(encoding="utf-8")

    # Sửa 17 cột thành 14 cột cho a8-test-plan
    readme_content = re.sub(r"\(17 cột, bao phủ 6 viewpoints\)", r"(14 cột, bao phủ 6 viewpoints)", readme_content)
    readme_content = re.sub(r"17 cột", r"14 cột", readme_content)

    # Sửa các đường dẫn output trong bảng Phase C và Phase X
    for old_p, new_p in DOCS_PATH_MAP:
        readme_content = re.sub(old_p, new_p, readme_content)

    # Chú thích Superpowers
    if "Kỹ Năng Đặc Nhiệm & Lập Trình Tự Trị (Superpowers Skills)" in readme_content:
        superpower_note = (
            "\n> 💡 **Ghi chú về Superpowers:** 12 kỹ năng đặc nhiệm dưới đây (brainstorming, writing-plans, TDD...) "
            "được tích hợp và kế thừa từ plugin `superpowers` đi kèm của hệ thống.\n"
        )
        if "được tích hợp và kế thừa từ plugin `superpowers`" not in readme_content:
            readme_content = re.sub(
                r"(## ⚡ KỸ NĂNG ĐẶC NHIỆM & LẬP TRÌNH TỰ TRỊ \(SUPERPOWERS SKILLS\)\n\n)",
                r"\1" + superpower_note + "\n",
                readme_content
            )

    README_MD.write_text(readme_content, encoding="utf-8")
    print("  [OK] Da cap nhat README.md (14 cot, output paths, chu thich superpowers)")

# -------------------------------------------------------------
# 5. Cập nhật plugin.json, marketplace.json & skills-manifest.json
# -------------------------------------------------------------
if PLUGIN_JSON.exists():
    plugin_data = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    plugin_data["version"] = TARGET_VERSION
    if "mcpServers" not in plugin_data:
        plugin_data["mcpServers"] = {}
    
    # Bổ sung claude-mem vào mcpServers
    plugin_data["mcpServers"]["claude-mem"] = {
        "command": "node",
        "args": [
            "C:/Users/asus/Claude/Projects/claude-skill/claude-mem/plugin/scripts/mcp-server.cjs"
        ]
    }
    PLUGIN_JSON.write_text(json.dumps(plugin_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  [OK] Da cap nhat plugin.json (version {TARGET_VERSION}, them claude-mem MCP)")

if MARKETPLACE_JSON.exists():
    mkt_data = json.loads(MARKETPLACE_JSON.read_text(encoding="utf-8"))
    mkt_data["version"] = TARGET_VERSION
    if "plugins" in mkt_data:
        for p in mkt_data["plugins"]:
            p["version"] = TARGET_VERSION
    MARKETPLACE_JSON.write_text(json.dumps(mkt_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  [OK] Da cap nhat marketplace.json -> v{TARGET_VERSION}")

if MANIFEST_JSON.exists():
    manifest_data = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    manifest_data["manifest_version"] = TARGET_VERSION
    for sk in manifest_data.get("skills", []):
        sk["version"] = TARGET_VERSION
        # Chuan hoa output paths trong manifest neu co
        if "outputs" in sk:
            new_outs = []
            for out in sk["outputs"]:
                cur = out
                for old_p, new_p in DOCS_PATH_MAP:
                    cur = cur.replace(old_p, new_p)
                new_outs.append(cur)
            sk["outputs"] = new_outs
    MANIFEST_JSON.write_text(json.dumps(manifest_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  [OK] Da cap nhat skills-manifest.json -> v{TARGET_VERSION}")

print("="*70)
print("DA HOAN TAT FIX_SKILLS.PY!")
print("="*70)
