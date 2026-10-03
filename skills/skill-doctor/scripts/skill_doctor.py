#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""skill_doctor.py — linter cho bộ skill (v3.3.0). Usage: python3 skill_doctor.py <skills_dir>
Exit 0 = sạch (có thể có WARN), 1 = có FAIL.

PHẠM VI LINT: chỉ các skill có trong skills-manifest.json. Folder skill hệ thống/plugin ngoài
(docx, pdf, pptx, xlsx, theme-factory, schedule…) được BỎ QUA — không phải lỗi của bộ.
Ngoại lệ: folder ngoài manifest mà SKILL.md trỏ pipeline.md của bộ → FAIL D08 (skill mới quên đăng ký)."""
import json, re, sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
issues = []  # (level, skill, rule, msg)


def add(level, skill, rule, msg):
    issues.append((level, skill, rule, msg))


all_folders = {p.name: p for p in sorted(ROOT.iterdir())
               if p.is_dir() and (p / "SKILL.md").exists() and not p.name.startswith("_")}

# ---- manifest (D08)
manifest_path = ROOT / "project-init" / "assets" / "skills-manifest.json"
manifest = {}
if manifest_path.exists():
    try:
        m = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest = {e["name"]: e for e in m.get("skills", [])}
    except Exception as e:
        add("FAIL", "project-init", "D08", f"manifest không parse được: {e}")
else:
    add("FAIL", "project-init", "D08", "thiếu assets/skills-manifest.json")

# ---- Phân loại: skill của bộ (lint) / skill ngoài (skip) / skill bộ quên đăng ký (FAIL)
skills, skipped = {}, []
for name, p in all_folders.items():
    if name in manifest:
        skills[name] = p
    else:
        txt = (p / "SKILL.md").read_text(encoding="utf-8", errors="ignore")
        if "project-init/references/pipeline.md" in txt or "## 🔗 Workflow Integration" in txt:
            add("FAIL", name, "D08", "SKILL.md trỏ pipeline của bộ nhưng THIẾU trong manifest (quên đăng ký?)")
        else:
            skipped.append(name)  # skill hệ thống / plugin ngoài — không lint

for name in manifest:
    if name not in all_folders:
        add("FAIL", name, "D08", "có trong manifest nhưng KHÔNG có folder")
    elif not manifest[name].get("intents"):
        add("WARN", name, "D12", "manifest thiếu intents[] — decision tree của /menu sẽ không thấy skill này")

for name, p in skills.items():
    t = (p / "SKILL.md").read_text(encoding="utf-8")
    lines = t.splitlines()

    # D01 frontmatter
    fm = re.match(r"\A---\n(.*?)\n---\n", t, re.S)
    if not fm:
        add("FAIL", name, "D01", "không có frontmatter")
        continue
    fmt = fm.group(1)
    mname = re.search(r"^name:\s*(\S+)", fmt, re.M)
    mver = re.search(r"^version:\s*\"?([\d.]+)\"?", fmt, re.M)
    if not mname or mname.group(1) != name:
        add("FAIL", name, "D01", f"frontmatter name={mname.group(1) if mname else None!r} != folder")
    if not mver:
        add("FAIL", name, "D01", "thiếu version")
    elif manifest.get(name) and manifest[name].get("version") != mver.group(1):
        add("FAIL", name, "D08", f"version {mver.group(1)} != manifest {manifest[name].get('version')}")
    dm = re.search(r"description:\s*>-?\n((?:[ \t]+.*\n?)+)", fmt)
    desc = " ".join(l.strip() for l in dm.group(1).splitlines()) if dm else ""
    if not desc:
        add("FAIL", name, "D01", "thiếu description")
    # D02
    if len(desc) > 700:
        add("WARN", name, "D02", f"description {len(desc)} ký tự (> 700 — nên rút gọn)")
    # D03
    if len(lines) > 500:
        add("WARN", name, "D03", f"{len(lines)} dòng (> 500 — nên tách references/)")
    # D04 — block copy-paste cũ
    if "Trước khi làm gì khác, kiểm tra" in t:
        add("FAIL", name, "D04", "còn block context copy-paste cũ")
    if "Chạy script chung — KHÔNG copy code đọc context" in t:
        add("FAIL", name, "D04", "còn block Bước -1 dài (đã thay bằng pointer context-protocol.md từ v3.3)")
    # D05
    n_wf = t.count("## 🔗 Workflow Integration")
    if name != "menu":
        if n_wf != 1:
            add("FAIL", name, "D05", f"số section Workflow = {n_wf} (phải 1)")
        elif "pipeline.md" not in t.split("## 🔗 Workflow Integration")[1]:
            add("FAIL", name, "D05", "tail không trỏ pipeline.md")
    # D06 — vẽ lại pipeline dài
    if name not in ("menu",):
        chains = len(re.findall(r"→ \[", t))
        if chains > 3:
            add("WARN", name, "D06", f"nghi vẽ lại pipeline ({chains} chuỗi '→ [')")
    # D07 — công thức Excel sai: $Word:$Word với Word ≥ 4 chữ cái (không phải cột)
    for mm in re.finditer(r"\$([A-Za-z]{4,}):\$([A-Za-z]{4,})", t):
        ln = t[:mm.start()].count("\n") + 1
        ctx_line = lines[ln - 1] if ln <= len(lines) else ""
        if "TUYỆT ĐỐI" in ctx_line or "không phải cú pháp" in ctx_line:
            continue
        add("FAIL", name, "D07", f"dòng {ln}: công thức nghi sai cú pháp `${mm.group(1)}:${mm.group(2)}`")
    # D09 — ASCII box dài
    box = sum(1 for l in lines if l.count("━") > 10)
    if box > 15:
        add("WARN", name, "D09", f"{box} dòng ━ (ASCII box dài — tốn token, nên bỏ)")
    # D10 — ví dụ FPT phải có cảnh báo
    if re.search(r"FPT|F-Pay|fpt-canteen", t) and "VÍ DỤ MINH HỌA" not in t:
        add("FAIL", name, "D10", "có ví dụ FPT/F-Pay nhưng thiếu cảnh báo VÍ DỤ MINH HỌA")
    # D11 — header "(N sheets)" phải khớp số "### Sheet" liệt kê bên dưới
    for hm in re.finditer(r"^##[^\n]*Cấu trúc file Excel \((\d+) sheets?\)", t, re.M):
        declared = int(hm.group(1))
        tail = t[hm.end():]
        nxt = re.search(r"^## [^#]", tail, re.M)
        seg = tail[:nxt.start()] if nxt else tail
        actual = len(re.findall(r"^### Sheet\b", seg, re.M))
        if actual and actual != declared:
            ln = t[:hm.start()].count("\n") + 1
            add("FAIL", name, "D11", f"dòng {ln}: header khai {declared} sheets nhưng liệt kê {actual} mục '### Sheet'")

# ---- report
fails = [i for i in issues if i[0] == "FAIL"]
warns = [i for i in issues if i[0] == "WARN"]
print(f"🩺 SKILL DOCTOR — lint {len(skills)} skill (bỏ qua {len(skipped)} skill ngoài bộ) | {len(fails)} FAIL | {len(warns)} WARN\n")
for level, skill, rule, msg in sorted(issues):
    icon = "❌" if level == "FAIL" else "⚠️"
    print(f"{icon} [{rule}] {skill}: {msg}")
if not issues:
    print("✅ Sạch tuyệt đối — mọi rule PASS")
elif not fails:
    print("\n✅ Không có FAIL (chỉ WARN — cân nhắc từng cái)")
sys.exit(1 if fails else 0)
