#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""skill_doctor.py — linter cho bộ skill (v3.17). Usage: python skill_doctor.py <skills_dir>
Exit 0 = sạch (có thể có WARN), 1 = có FAIL.

PHẠM VI LINT:
  - Skill TRONG skills-manifest.json: lint đầy đủ (D01–D17).
  - Folder NGOÀI manifest: nếu SKILL.md trỏ pipeline.md của bộ → FAIL D08 (quên đăng ký);
    còn lại lint TỐI THIỂU: name khớp folder (D01), description ≤ 700 (D02), không block copy-paste (D04),
    tham chiếu chết (D14). Script của chúng vẫn qua D15.
  - Folder hệ thống/plugin ngoài không có SKILL.md → bỏ qua."""
import json
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
REPO = ROOT.parent
issues = []  # (level, skill, rule, msg)

# Danh sách rule — NGUỒN để D16 đối chiếu "N rule" trong tài liệu. Thêm rule mới ở ĐÂY.
RULES = {
    "D01": "Frontmatter hợp lệ (name khớp folder, version, description)", "D02": "description ≤ 700 ký tự",
    "D03": "SKILL.md ≤ 500 dòng", "D04": "Không còn block context copy-paste cũ",
    "D05": "Đúng 1 section Workflow Integration có trỏ pipeline.md", "D06": "Không vẽ lại pipeline dài",
    "D07": "Không anti-pattern công thức Excel", "D08": "Manifest ↔ folder đồng bộ, version khớp",
    "D09": "Không ASCII box dài", "D10": "Ví dụ FPT/F-Pay phải có cảnh báo VÍ DỤ MINH HỌA",
    "D11": "Header (N sheets) khớp số '### Sheet'", "D12": "Manifest có intents[]",
    "D13": "Self-Improvement: đúng 1 mục, ≤ 8 dòng, trỏ self-improvement.md",
    "D14": "Tham chiếu chết (đường dẫn file trong backtick phải tồn tại)",
    "D15": "Script Windows-safe (compile OK; in non-ASCII phải reconfigure UTF-8)",
    "D16": "Số liệu khớp nguồn (số rule x6, N skill)", "D17": "Version đồng bộ manifest = plugin.json = marketplace.json",
}


def add(level, skill, rule, msg):
    issues.append((level, skill, rule, msg))


def read_text(p: Path) -> str:
    t = p.read_text(encoding="utf-8", errors="replace")
    return t[1:] if t.startswith("﻿") else t


def parse_frontmatter(t: str):
    """(dict name/version/description | None). Hỗ trợ description dạng >, >-, |, "…", '…', plain."""
    m = re.match(r"\A---\n(.*?)\n---\n", t, re.S)
    if not m:
        return None
    fm, out = m.group(1), {}
    n = re.search(r"^name:\s*[\"']?([^\s\"']+)", fm, re.M)
    v = re.search(r"^version:\s*[\"']?([\d.]+)", fm, re.M)
    out["name"], out["version"] = (n.group(1) if n else None), (v.group(1) if v else None)
    d = re.search(r"^description:[ \t]*(.*)$", fm, re.M)
    desc = ""
    if d:
        first = d.group(1).strip()
        if first in ("", ">", ">-", ">+", "|", "|-", "|+"):
            body = []
            for line in fm[d.end():].split("\n")[1:]:
                if line.strip() == "" or line.startswith((" ", "\t")):
                    body.append(line.strip())
                else:
                    break
            desc = " ".join(x for x in body if x)
        elif len(first) > 1 and first[0] in "\"'" and first[-1] == first[0]:
            desc = first[1:-1]
        else:
            desc = first
    out["description"] = desc
    return out


def workflow_section(t: str):
    """Nội dung từ heading Workflow Integration tới heading '## ' kế tiếp (hoặc hết file)."""
    key = "## 🔗 Workflow Integration"
    i = t.find(key)
    if i < 0:
        return None
    rest = t[i + len(key):]
    nxt = re.search(r"^## (?!#)", rest, re.M)
    return rest[: nxt.start()] if nxt else rest


all_folders = {p.name: p for p in sorted(ROOT.iterdir())
               if p.is_dir() and (p / "SKILL.md").exists() and not p.name.startswith(("_", "."))}

# ---- manifest (D08)
manifest_path = ROOT / "a1-project-init" / "assets" / "skills-manifest.json"
if not manifest_path.exists():
    manifest_path = ROOT / "project-init" / "assets" / "skills-manifest.json"
manifest, manifest_doc = {}, {}
if manifest_path.exists():
    try:
        manifest_doc = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest = {e["name"]: e for e in manifest_doc.get("skills", [])}
    except Exception as e:  # noqa: BLE001
        add("FAIL", "a1-project-init", "D08", f"manifest không parse được: {e}")
else:
    add("FAIL", "a1-project-init", "D08", "thiếu assets/skills-manifest.json")

# ---- Phân loại: skill của bộ (lint đầy đủ) / ngoài manifest (lint tối thiểu) / quên đăng ký (FAIL)
skills, minimal = {}, {}
for name, p in all_folders.items():
    if name in manifest:
        skills[name] = p
    else:
        txt = read_text(p / "SKILL.md")
        if "pipeline.md" in txt or "## 🔗 Workflow Integration" in txt:
            add("FAIL", name, "D08", "SKILL.md trỏ pipeline của bộ nhưng THIẾU trong manifest (quên đăng ký?)")
        else:
            minimal[name] = p

for name in manifest:
    if name not in all_folders:
        add("FAIL", name, "D08", "có trong manifest nhưng KHÔNG có folder")
    elif not manifest[name].get("intents"):
        add("WARN", name, "D12", "manifest thiếu intents[] — decision tree của /menu sẽ không thấy skill này")

COPYPASTE = [("Trước khi làm gì khác, kiểm tra", "còn block context copy-paste cũ"),
             ("Chạy script chung — KHÔNG copy code đọc context",
              "còn block Bước -1 dài (đã thay bằng pointer context-protocol.md từ v3.3)")]

# ---- lint tối thiểu cho skill ngoài manifest
for name, p in minimal.items():
    t = read_text(p / "SKILL.md").replace("\r\n", "\n")
    fm = parse_frontmatter(t)
    if not fm:
        add("FAIL", name, "D01", "không có frontmatter")
        continue
    if fm["name"] != name:
        add("FAIL", name, "D01", f"frontmatter name={fm['name']!r} != folder")
    if not fm["description"]:
        add("FAIL", name, "D01", "thiếu description")
    elif len(fm["description"]) > 700:
        add("WARN", name, "D02", f"description {len(fm['description'])} ký tự (> 700 — nên rút gọn)")
    for needle, msg in COPYPASTE:
        if needle in t:
            add("FAIL", name, "D04", msg)

# ---- lint đầy đủ skill trong manifest
for name, p in skills.items():
    t = read_text(p / "SKILL.md").replace("\r\n", "\n")
    lines = t.splitlines()
    fm = parse_frontmatter(t)
    if not fm:
        add("FAIL", name, "D01", "không có frontmatter")
        continue
    # D01
    if fm["name"] != name:
        add("FAIL", name, "D01", f"frontmatter name={fm['name']!r} != folder")
    if not fm["version"]:
        add("FAIL", name, "D01", "thiếu version")
    elif manifest.get(name) and manifest[name].get("version") != fm["version"]:
        add("FAIL", name, "D08", f"version {fm['version']} != manifest {manifest[name].get('version')}")
    desc = fm["description"]
    if not desc:
        add("FAIL", name, "D01", "thiếu description")
    # D02
    if len(desc) > 700:
        add("WARN", name, "D02", f"description {len(desc)} ký tự (> 700 — nên rút gọn)")
    # D03
    if len(lines) > 500:
        add("WARN", name, "D03", f"{len(lines)} dòng (> 500 — nên tách references/)")
    # D04
    for needle, msg in COPYPASTE:
        if needle in t:
            add("FAIL", name, "D04", msg)
    # D05 — CHỈ xét trong section Workflow (không tính chữ pipeline.md ở nơi khác)
    n_wf = t.count("## 🔗 Workflow Integration")
    if name != "menu":
        if n_wf != 1:
            add("FAIL", name, "D05", f"số section Workflow = {n_wf} (phải 1)")
        elif "pipeline.md" not in (workflow_section(t) or ""):
            add("FAIL", name, "D05", "section Workflow không trỏ pipeline.md")
    # D06
    if name != "menu":
        chains = len(re.findall(r"→ \[", t))
        if chains > 3:
            add("WARN", name, "D06", f"nghi vẽ lại pipeline ({chains} chuỗi '→ [')")
    # D07 — công thức Excel sai: $Word:$Word với Word ≥ 4 ký tự chữ/gạch dưới (không phải cột)
    for mm in re.finditer(r"\$([A-Za-z_]{4,}):\$([A-Za-z_]{4,})", t):
        ln = t[:mm.start()].count("\n") + 1
        ctx_line = lines[ln - 1] if ln <= len(lines) else ""
        if "TUYỆT ĐỐI" in ctx_line or "không phải cú pháp" in ctx_line:
            continue
        add("FAIL", name, "D07", f"dòng {ln}: công thức nghi sai cú pháp `${mm.group(1)}:${mm.group(2)}`")
    # D09
    box = sum(1 for l in lines if l.count("━") > 10)
    if box > 15:
        add("WARN", name, "D09", f"{box} dòng ━ (ASCII box dài — tốn token, nên bỏ)")
    # D10
    if re.search(r"FPT|F-Pay|fpt-canteen", t) and "VÍ DỤ MINH HỌA" not in t:
        add("FAIL", name, "D10", "có ví dụ FPT/F-Pay nhưng thiếu cảnh báo VÍ DỤ MINH HỌA")
    # D11
    for hm in re.finditer(r"^##[^\n]*Cấu trúc file Excel \((\d+) sheets?\)", t, re.M):
        declared = int(hm.group(1))
        tail = t[hm.end():]
        nxt = re.search(r"^## [^#]", tail, re.M)
        seg = tail[:nxt.start()] if nxt else tail
        actual = len(re.findall(r"^### Sheet\b", seg, re.M))
        if actual and actual != declared:
            ln = t[:hm.start()].count("\n") + 1
            add("FAIL", name, "D11", f"dòng {ln}: header khai {declared} sheets nhưng liệt kê {actual} mục '### Sheet'")

    # D13 — mục Self-Improvement: đúng 1 lần, ngắn, trỏ về nguồn duy nhất
    si = list(re.finditer(r"^## Self-Improvement Loop\s*$", t, re.M))
    if len(si) != 1:
        add("FAIL", name, "D13", f"phải có đúng 1 mục '## Self-Improvement Loop' (đang {len(si)})")
    else:
        tail = t[si[0].end():]
        nx = re.search(r"^## ", tail, re.M)
        body = (tail[:nx.start()] if nx else tail).strip().splitlines()
        if len(body) > 8:
            add("FAIL", name, "D13", f"mục Self-Improvement dài {len(body)} dòng (tối đa 8) — trỏ về references, không chép lại quy trình")
        if "self-improvement.md" not in "\n".join(body):
            add("FAIL", name, "D13", "mục Self-Improvement không trỏ tới a1-project-init/references/self-improvement.md")

# ======================================================================= D14 — tham chiếu chết
EXTS = r"(?:py|md|json|yaml|yml|js|mjs|ts|sh|ps1|csv|html|xlsx|docx|pptx)"
TOKEN_RE = re.compile(r"(?<![\w/.\\<>-])((?:[\w<>.${}\[\]*-]+/)*[\w<>.${}\[\]*-]+\." + EXTS + r")(?![\w])", re.I)
EXAMPLE_HINT = re.compile(r"(ví dụ|vd[: .]|e\.g\.|example|minh họa|vi du)", re.I)
WORKSPACE_PREFIX = ("docs/", "tests/", "test/", "src/", "frontend/", "backend/", "design-system/", "app/", "public/",
                    "dist/", "build/", "node_modules/", "prisma/", "migrations/", ".github/", "scripts/auto")
all_names = {p.name for p in ROOT.rglob("*") if p.is_file() and "__pycache__" not in p.parts}


def resolve_ref(tok: str, skill_dir: Path, doc_dir: Path):
    """True nếu tồn tại, False nếu chết, None nếu không kiểm (ví dụ/template/ngoài bộ skill)."""
    s = tok.replace("\\", "/").strip("`'\"()")
    if s.startswith(("http", "~", "/", "file:")) or "://" in s:
        return None
    s = s.replace("${CLAUDE_PLUGIN_ROOT}/skills/", "<skills_dir>/")
    if s.startswith("<workspace_folder>") or "{" in s or "*" in s or "[" in s or "$" in s:
        return None
    s = s.replace("<skills_dir>/", "").replace("<skill_dir>/", "@skill/")
    if "<" in s or ">" in s or s.startswith(WORKSPACE_PREFIX):
        return None
    if s.startswith("@skill/"):
        return (skill_dir / s[7:]).exists()
    if s.startswith("./"):
        s = s[2:]
    if "/" not in s:  # tên trần: chỉ kiểm script .py (tài liệu/json trần thường là ví dụ ở workspace)
        if s.lower().endswith(".py"):
            return s in all_names
        return None
    first = s.split("/", 1)[0]
    if first in all_folders or first == "evals":
        return (ROOT / s).exists()
    if first in ("references", "scripts", "assets"):
        return (skill_dir / s).exists() or (doc_dir / s).exists() or (REPO / s).exists()
    return None


def d14_scan(skill, skill_dir):
    docs = [skill_dir / "SKILL.md"]
    if (skill_dir / "references").exists():
        docs += sorted((skill_dir / "references").glob("*.md"))
    for doc in docs:
        text = read_text(doc).replace("\r\n", "\n")
        for ln, line in enumerate(text.splitlines(), 1):
            if EXAMPLE_HINT.search(line):
                continue
            for span in re.findall(r"`([^`\n]+)`", line) + ([line] if line.startswith(("python ", "bash ", "node ", "    python ")) else []):
                for m in TOKEN_RE.finditer(span):
                    ok = resolve_ref(m.group(1), skill_dir, doc.parent)
                    if ok is False:
                        level = "FAIL" if "/" in m.group(1).replace("\\", "/") else "WARN"  # tên .py trần: có thể là ví dụ
                        add(level, skill, "D14", f"{doc.relative_to(ROOT).as_posix()}:{ln}: tham chiếu chết `{m.group(1)}`")


for name, p in {**skills, **minimal}.items():
    d14_scan(name, p)

# ======================================================================= D15 — script Windows-safe
def has_non_ascii_literal(src: str) -> bool:
    """True nếu có chuỗi literal non-ASCII (bỏ qua docstring và comment)."""
    import ast
    tree = ast.parse(src)
    doc_ids = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(getattr(first, "value", None), ast.Constant):
                doc_ids.add(id(first.value))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in doc_ids:
            if any(ord(c) > 127 for c in node.value):
                return True
    return False


for name, p in {**skills, **minimal}.items():
    sdir = p / "scripts"
    if not sdir.exists():
        continue
    for py in sorted(sdir.rglob("*.py")):
        if "__pycache__" in py.parts or "tests" in py.relative_to(sdir).parts:
            continue
        rel = py.relative_to(ROOT).as_posix()
        try:
            src = py.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            add("FAIL", name, "D15", f"{rel}: không phải UTF-8 ({e})")
            continue
        try:
            compile(src, str(py), "exec")
        except SyntaxError as e:
            add("FAIL", name, "D15", f"{rel}:{e.lineno}: SyntaxError {e.msg}")
            continue
        has_print = re.search(r"(?<![\w.])print\(", src) is not None or "sys.stdout.write" in src
        non_ascii = has_non_ascii_literal(src)
        if has_print and non_ascii and not re.search(r"reconfigure\(|setup_utf8\(|PYTHONUTF8|PYTHONIOENCODING", src):
            add("FAIL", name, "D15", f"{rel}: in ký tự non-ASCII nhưng thiếu sys.stdout.reconfigure(encoding='utf-8') "
                                     "(crash trên console cp932/cp1252)")
        if re.search(r"[\"']/tmp/", src):
            add("WARN", name, "D15", f"{rel}: dùng đường dẫn /tmp (không có trên Windows) — dùng tempfile")

# ======================================================================= D16 — số liệu khớp nguồn
_x6_md = read_text(ROOT / "x6-skill-doctor" / "SKILL.md") if (ROOT / "x6-skill-doctor" / "SKILL.md").exists() else ""
# D13 (Self-Improvement) có thể được thêm riêng ở giai đoạn sau: tính nếu đã được liệt kê trong SKILL.md của x6
n_rules = len(set(RULES) | ({"D13"} if re.search(r"^\|\s*D13", _x6_md, re.M) else set()))
n_folders = len(all_folders)
n_manifest = len(manifest)
rule_docs = []
if "x6-skill-doctor" in manifest:
    rule_docs.append(("manifest summary x6", str(manifest["x6-skill-doctor"].get("summary", ""))))
for rel in ("x6-skill-doctor/SKILL.md",):
    if (ROOT / rel).exists():
        rule_docs.append((rel, read_text(ROOT / rel)))
for rel in ("README.md", "AGENTS.md", "rules/AGENTS.md"):
    if (REPO / rel).exists():
        rule_docs.append((rel, read_text(REPO / rel)))
for label, text in rule_docs:
    for ln, line in enumerate(text.splitlines(), 1):
        if not re.search(r"x6|skill[- ]doctor|linter|lint\b", line, re.I):
            continue
        for m in re.finditer(r"(\d+)\s*(?:rule|quy tắc|quy chuẩn chống)", line, re.I):
            if int(m.group(1)) != n_rules and int(m.group(1)) > 3:
                add("FAIL", "x6-skill-doctor", "D16", f"{label}:{ln}: ghi {m.group(1)} rule nhưng linter có {n_rules}")
count_docs = [(rel, REPO / rel) for rel in ("README.md", "AGENTS.md", "rules/AGENTS.md")] + \
             [("skills/menu/SKILL.md", ROOT / "menu" / "SKILL.md")]
for label, path in count_docs:
    if not path.exists():
        continue
    for ln, line in enumerate(read_text(path).splitlines(), 1):
        if re.search(r"bỏ qua|không lint|skip", line, re.I):
            continue
        for m in re.finditer(r"(?:bộ|tổng(?: cộng)?:?|gồm|total|toàn bộ|lint)\s*(\d+)\s*(?:skills?|kỹ năng)\b", line, re.I):
            n = int(m.group(1))
            if n not in (n_folders, n_manifest) and n > 10:
                add("WARN", "menu", "D16", f"{label}:{ln}: ghi {n} skill nhưng thư mục có {n_folders} "
                                           f"(manifest {n_manifest})")

# ======================================================================= D17 — version đồng bộ
mv = manifest_doc.get("manifest_version")
if mv:
    for rel in ("plugin.json", "marketplace.json", ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"):
        fp = REPO / rel
        if not fp.exists():
            continue
        try:
            doc = json.loads(fp.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            add("FAIL", "a1-project-init", "D17", f"{rel} không parse được: {e}")
            continue
        found = []

        def walk(o, path=""):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k == "version" and isinstance(v, str):
                        found.append((f"{path}.version".lstrip("."), v))
                    else:
                        walk(v, f"{path}.{k}")
            elif isinstance(o, list):
                for i, v in enumerate(o):
                    walk(v, f"{path}[{i}]")

        walk(doc)
        for where, v in found:
            if v != mv:
                add("FAIL", "a1-project-init", "D17", f"{rel}:{where}={v} != manifest_version {mv}")
else:
    add("FAIL", "a1-project-init", "D17", "manifest thiếu manifest_version")

# ---- report
fails = [i for i in issues if i[0] == "FAIL"]
warns = [i for i in issues if i[0] == "WARN"]
print(f"🩺 SKILL DOCTOR — lint đầy đủ {len(skills)} skill + lint tối thiểu {len(minimal)} skill ngoài manifest | "
      f"{len(fails)} FAIL | {len(warns)} WARN\n")
for level, skill, rule, msg in sorted(issues):
    icon = "❌" if level == "FAIL" else "⚠️"
    print(f"{icon} [{rule}] {skill}: {msg}")
if not issues:
    print("✅ Sạch tuyệt đối — mọi rule PASS")
elif not fails:
    print("\n✅ Không có FAIL (chỉ WARN — cân nhắc từng cái)")
sys.exit(1 if fails else 0)
