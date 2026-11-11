# -*- coding: utf-8 -*-
"""menu_common.py — hàm dùng chung cho gen_menu_table.py, check_menu_sync.py, match_intent.py, test_intents.py.

Nguồn dữ liệu của menu (KHÔNG hardcode tên skill/nhãn giai đoạn):
  1. skills-manifest.json  → 33 skill trong pipeline (step, phase, summary, outputs, intents)
  2. folder skill NGOÀI manifest (vd ui-ux-pro-max, product-teardown) → "skill bổ trợ":
       - metadata lấy từ frontmatter (name/description) của SKILL.md
       - intents/summary bổ sung (nếu có) lấy từ menu/assets/extras.json
  3. menu/assets/intent_aliases.json → cụm từ tiếng Việt bổ sung cho BẤT KỲ skill nào (manifest không sửa được ở đây)
  4. nhãn giai đoạn: đọc từ dòng "GIAI ĐOẠN X — …" trong pipeline.md; khoảng bước (A1 → A9) tính từ manifest.
"""
import json
import math
import re
import sys
import unicodedata
from pathlib import Path


def setup_utf8():
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            s.reconfigure(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------- văn bản
def strip_accents(s: str) -> str:
    """Bỏ dấu tiếng Việt (đ→d); giữ nguyên chữ Nhật/Hán (không tách dakuten)."""
    out = []
    for c in unicodedata.normalize("NFD", s.lower().replace("đ", "d")):
        if unicodedata.category(c) == "Mn" and out and ord(out[-1]) < 0x250:
            continue
        out.append(c)
    return unicodedata.normalize("NFC", "".join(out))


STOP = set("""
toi minh ban em anh chi muon can cho cua nay do la va de mot cac nhung co khong thi duoc xin hay giup
voi tu den o trong ra vao len xuong nhe nha oi a the to and or of for me my please want need
lam ve ma se dang da roi nao sao gi the nao nhu
""".split())


def tokens(s: str):
    return re.findall(r"[a-z0-9぀-ヿ一-鿿]+", strip_accents(s))


def content_tokens(s: str):
    return [t for t in tokens(s) if t not in STOP]


# ---------------------------------------------------------------- frontmatter
def read_frontmatter(skill_md: Path) -> dict:
    """Đọc name/version/description; hỗ trợ >-, >, |, "…" một dòng, '…', plain."""
    try:
        t = skill_md.read_text(encoding="utf-8")
    except OSError:
        return {}
    t = t.lstrip("﻿").replace("\r\n", "\n")
    m = re.match(r"\A---\n(.*?)\n---\n", t, re.S)
    if not m:
        return {}
    fm, out = m.group(1), {}
    for key in ("name", "version"):
        k = re.search(rf"^{key}:\s*[\"']?([^\"'\n]+?)[\"']?\s*$", fm, re.M)
        if k:
            out[key] = k.group(1).strip()
    d = re.search(r"^description:[ \t]*(.*)$", fm, re.M)
    if d:
        first = d.group(1).strip()
        if first in (">", ">-", ">+", "|", "|-", "|+", ""):
            body = []
            for line in fm[d.end():].split("\n")[1:]:
                if line.strip() == "" or line.startswith((" ", "\t")):
                    body.append(line.strip())
                else:
                    break
            out["description"] = " ".join(x for x in body if x)
        elif first[0] in "\"'" and first[-1] == first[0] and len(first) > 1:
            out["description"] = first[1:-1]
        else:
            out["description"] = first
    return out


# ---------------------------------------------------------------- manifest + extras
def find_manifest(skills_dir: Path):
    for rel in ("a1-project-init/assets/skills-manifest.json", "project-init/assets/skills-manifest.json"):
        p = skills_dir / rel
        if p.exists():
            return p
    return None


def load_manifest(skills_dir: Path) -> dict:
    p = find_manifest(skills_dir)
    if not p:
        raise FileNotFoundError(f"Không tìm thấy skills-manifest.json trong {skills_dir}")
    return json.loads(p.read_text(encoding="utf-8"))


def _json_or_empty(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    except (OSError, ValueError):
        return {}


def short(text: str, n: int = 140) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    first = re.split(r"(?<=[.!?])\s", text, maxsplit=1)[0]
    first = first if len(first) <= n else first[: n - 1].rstrip() + "…"
    return first


def load_entries(skills_dir: Path):
    """Trả (entries, manifest). entry: name, step, phase, summary, outputs, intents, extra(bool), version."""
    manifest = load_manifest(skills_dir)
    aliases = _json_or_empty(skills_dir / "menu" / "assets" / "intent_aliases.json")
    extras_cfg = _json_or_empty(skills_dir / "menu" / "assets" / "extras.json")
    entries, known = [], set()
    for e in manifest.get("skills", []):
        d = dict(e)
        d["extra"] = False
        d["intents"] = list(e.get("intents", [])) + list(aliases.get(e["name"], []))
        entries.append(d)
        known.add(e["name"])
    for p in sorted(skills_dir.iterdir()):
        if not p.is_dir() or p.name in known or p.name.startswith(("_", ".")) or not (p / "SKILL.md").exists():
            continue
        fm = read_frontmatter(p / "SKILL.md")
        cfg = extras_cfg.get(p.name, {})
        entries.append({
            "name": p.name, "step": "-", "phase": "extra", "extra": True,
            "version": fm.get("version", ""),
            "summary": cfg.get("summary") or short(fm.get("description", "")),
            "outputs": cfg.get("outputs", []),
            "intents": list(cfg.get("intents", [])) + list(aliases.get(p.name, [])),
            "has_description": bool(fm.get("description")),
        })
    return entries, manifest


# ---------------------------------------------------------------- nhãn giai đoạn
def step_key(step: str):
    if not step or step == "-":
        return (99, 99, "")
    m = re.match(r"([A-Za-z]+)(\d*)", step)
    return (ord(m.group(1)[0].upper()), int(m.group(2) or 0), step)


def phase_labels(skills_dir: Path, entries):
    """{chữ cái giai đoạn: 'GIAI ĐOẠN A — … (A1 → A9)'} — tiêu đề từ pipeline.md, khoảng bước từ manifest."""
    titles = {}
    pl = skills_dir / "a1-project-init" / "references" / "pipeline.md"
    if pl.exists():
        for line in pl.read_text(encoding="utf-8").splitlines():
            m = re.match(r"GIAI ĐOẠN ([A-Z]) — (.+)$", line.strip())
            if m:
                title = re.sub(r"\s*\(.*$", "", m.group(2)).strip()
                titles[m.group(1)] = title
    ranges = {}
    for e in entries:
        s = e.get("step", "-")
        if e.get("extra") or s == "-" or e.get("phase") == "meta":
            continue
        ranges.setdefault(s[0], []).append(s)
    out = {}
    for letter, steps in ranges.items():
        steps = sorted(steps, key=step_key)
        out[letter] = f"GIAI ĐOẠN {letter} — {titles.get(letter, letter)} ({steps[0]} → {steps[-1]})"
    return out


# ---------------------------------------------------------------- chấm điểm intent
def build_index(entries):
    """IDF trên tập token intents của từng skill."""
    docs = {e["name"]: set(t for ph in e.get("intents", []) for t in content_tokens(ph)) for e in entries}
    n = max(len(docs), 1)
    df = {}
    for toks in docs.values():
        for t in toks:
            df[t] = df.get(t, 0) + 1
    idf = {t: math.log(1 + n / c) for t, c in df.items()}
    return {"docs": docs, "idf": idf, "n": n}


def score(query: str, entry: dict, index: dict):
    """(điểm, cụm intent tốt nhất | None). Cụm khớp nguyên văn > đủ token (mọi thứ tự) > token IDF > bigram."""
    qn = " ".join(tokens(query))
    qtok = content_tokens(query)
    qset = set(qtok)
    qbi = set(zip(qtok, qtok[1:]))
    idf = index["idf"]
    best_ph, best = None, 0.0
    ibi = set()
    for ph in entry.get("intents", []):
        pn = " ".join(tokens(ph))
        ptok = content_tokens(ph)
        ibi |= set(zip(ptok, ptok[1:]))
        s = 0.0
        if pn and f" {pn} " in f" {qn} ":
            s = 4.0 + len(pn.split()) + (4.0 if pn == qn else 0.0)
        elif len(ptok) >= 2 and set(ptok) <= qset:
            s = 3.0 + len(ptok)
        if s > best:
            best, best_ph = s, ph
    toks = index["docs"].get(entry["name"], set())
    tok_score = 0.6 * sum(idf.get(t, 0.0) for t in qset & toks)
    bi_score = 1.5 * len(qbi & ibi)
    sum_toks = set(content_tokens(entry.get("summary", "")))
    sum_score = 0.2 * sum(idf.get(t, 0.0) for t in qset & sum_toks if t not in toks)
    return best + tok_score + bi_score + sum_score, best_ph


MIN_SCORE = 2.5


def rank(query: str, entries, index=None, limit=3):
    index = index or build_index(entries)
    res = []
    for e in entries:
        sc, ph = score(query, e, index)
        if sc >= MIN_SCORE:
            res.append((sc, e, ph))
    res.sort(key=lambda x: (-x[0], x[1]["name"]))
    return res[:limit] if limit else res
