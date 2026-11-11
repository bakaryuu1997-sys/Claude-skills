#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""skill_self_update.py — áp dụng + push một cải tiến NHỎ cho đúng 1 skill (không tương tác).

Quy trình đầy đủ và rào an toàn: skills/a1-project-init/references/self-improvement.md
Agent SỬA file trong skills/<skill>/ của repo nguồn TRƯỚC, rồi gọi script này để kiểm tra + bump + commit + push:

    python scripts/skill_self_update.py --skill c3-code-review --task-id 20261106-1432 \
        --summary "Thêm checklist kiểm token FE" [--type changed|added|fixed] [--dry-run] [--no-push]

Repo nguồn lấy từ biến môi trường SKILLS_REPO (mặc định C:\\Users\\asus\\Claude\\Projects\\claude-skill).

Mã thoát: 0 xong · 2 từ chối (không đổi gì) · 3 skill_doctor FAIL (đã hoàn tác thay đổi) ·
          4 rebase thất bại (commit giữ ở local) · 5 push thất bại (commit giữ ở local)
KHÔNG BAO GIỜ: git add -A · force-push · sửa quá 1 skill · xóa quy tắc sẵn có · đưa dữ liệu nhạy cảm vào skill."""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_REPO = str(Path(__file__).resolve().parents[1])  # thư mục gốc repo, không hardcode đường dẫn cá nhân
REPO_MARK = "claude-skills"            # origin URL phải chứa chuỗi này (không phân biệt hoa thường)
BRANCH = "main"
MAX_ADDED_LINES = 40                   # tổng dòng thêm cho 1 lần tự sửa
MAX_REMOVED_LINES = 5                  # chỉ cho phép làm rõ, không xóa quy tắc
MAX_NEW_FILES = 2                      # chỉ trong references/ của chính skill
PLUGIN_VERSION_FILES = [".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", "marketplace.json", "plugin.json"]
MANIFEST_REL = "skills/a1-project-init/assets/skills-manifest.json"
DOCTOR_REL = "skills/x6-skill-doctor/scripts/skill_doctor.py"

ALLOWED_EMAIL_DOMAINS = ("example.com", "example.org", "example.jp", "example.vn", "localhost")
SENSITIVE = [
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+\.)+[A-Za-z]{2,}")),
    ("API key/token", re.compile(r"(sk-[A-Za-z0-9_-]{16,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{30,})")),
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("đường dẫn cá nhân Windows", re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+|[A-Za-z]:\\(?:マイドライブ|My Drive)", re.IGNORECASE)),
    ("đường dẫn cá nhân Unix", re.compile(r"(?<![\w.-])(/Users/[^/\s]+|/home/[^/\s]+)")),
    ("mật khẩu/secret gán cứng", re.compile(r"(?i)\b(password|passwd|secret|api[_-]?key|token)\b\s*[:=]\s*['\"][^'\"\s]{6,}['\"]")),
]


class Refuse(Exception):
    def __init__(self, msg: str, code: int = 2):
        super().__init__(msg)
        self.code = code


def run(repo: Path, *args: str, check: bool = True, input_text: str | None = None) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-c", "core.quotepath=false", *args], cwd=repo, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", input=input_text)
    if check and r.returncode != 0:
        raise Refuse(f"git {' '.join(args)} thất bại: {(r.stderr or r.stdout).strip()}", 2)
    return r


def bump_patch(v: str) -> str:
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", v)
    if not m:
        raise Refuse(f"version '{v}' không phải X.Y.Z")
    return f"{m.group(1)}.{m.group(2)}.{int(m.group(3)) + 1}"


def preflight(repo: Path, skill: str, task_id: str) -> Path:
    if not repo.is_dir() or not (repo / ".git").exists():
        raise Refuse(f"SKILLS_REPO không phải repo git: {repo}")
    url = run(repo, "remote", "get-url", "origin").stdout.strip()
    if REPO_MARK not in url.lower():
        raise Refuse(f"origin ({url}) không phải repo Claude-skills — từ chối chạy")
    branch = run(repo, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if branch != BRANCH:
        raise Refuse(f"đang ở nhánh '{branch}', chỉ chạy trên '{BRANCH}'")
    git_dir = Path(run(repo, "rev-parse", "--absolute-git-dir").stdout.strip())
    for marker in ("MERGE_HEAD", "rebase-merge", "rebase-apply", "CHERRY_PICK_HEAD"):
        if (git_dir / marker).exists():
            raise Refuse(f"repo đang giữa thao tác git ({marker}) — xử lý xong rồi chạy lại")
    if not re.fullmatch(r"[A-Za-z0-9._-]{4,64}", task_id):
        raise Refuse("--task-id phải 4–64 ký tự [A-Za-z0-9._-] (duy nhất cho mỗi tác vụ của người dùng)")
    used = git_dir / "skill_self_update_tasks.txt"
    if used.exists() and task_id in used.read_text(encoding="utf-8").split():
        raise Refuse(f"tác vụ '{task_id}' đã dùng quyền tự sửa 1 lần — tối đa 1 lần/tác vụ")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", skill) or not (repo / "skills" / skill / "SKILL.md").exists():
        raise Refuse(f"không có skills/{skill}/SKILL.md")
    return used


def changed_paths(repo: Path) -> list[str]:
    out = run(repo, "status", "--porcelain=v1", "-z").stdout
    parts = out.split("\0")
    paths, i = [], 0
    while i < len(parts):
        e = parts[i]
        if len(e) < 4:
            i += 1
            continue
        x, y, path = e[0], e[1], e[3:]
        paths.append(path.replace("\\", "/"))
        if x in "RC" or y in "RC":  # rename/copy: mục kế tiếp là đường dẫn gốc
            i += 1
        i += 1
    return paths


def collect_added_lines(repo: Path, skill: str) -> tuple[list[str], int, int, list[str]]:
    """Trả (dòng thêm, tổng thêm, tổng xóa, file mới)."""
    base = f"skills/{skill}"
    added, add_n, del_n = [], 0, 0
    num = run(repo, "diff", "HEAD", "--numstat", "--", base).stdout
    for line in num.splitlines():
        a, d, name = (line.split("\t") + ["", "", ""])[:3]
        if a == "-" or d == "-":
            raise Refuse(f"file nhị phân bị đổi: {name}")
        add_n += int(a)
        del_n += int(d)
    patch = run(repo, "diff", "HEAD", "-U0", "--", base).stdout
    added += [l[1:] for l in patch.splitlines() if l.startswith("+") and not l.startswith("+++")]
    new_files = [p for p in run(repo, "ls-files", "--others", "--exclude-standard", "--", base).stdout.splitlines() if p]
    for nf in new_files:
        txt = (repo / nf).read_text(encoding="utf-8", errors="replace")
        lines = txt.splitlines()
        add_n += len(lines)
        added += lines
    return added, add_n, del_n, new_files


def scan_sensitive(lines: list[str]) -> list[str]:
    hits = []
    for ln in lines:
        for label, rx in SENSITIVE:
            for m in rx.finditer(ln):
                if label == "email" and m.group(0).lower().split("@")[-1] in ALLOWED_EMAIL_DOMAINS:
                    continue
                hits.append(f"{label}: {m.group(0)[:60]}")
    return hits


def read_frontmatter_version(skill_md: Path) -> tuple[str | None, str]:
    txt = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n(.*?)\r?\n---", txt, re.S)
    if not m:
        return None, txt
    v = re.search(r"^version:\s*[\"']?(\d+\.\d+\.\d+)[\"']?\s*$", m.group(1), re.M)
    return (v.group(1) if v else None), txt


def run_doctor(repo: Path) -> tuple[int, str]:
    r = subprocess.run([sys.executable, "-I", "-B", str(repo / DOCTOR_REL), str(repo / "skills")], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=300)
    return r.returncode, (r.stdout + r.stderr).strip()


def revert_skill(repo: Path, skill: str, reason: str) -> str:
    base = f"skills/{skill}"
    patch = run(repo, "diff", "HEAD", "--", base, check=False).stdout
    saved = Path(tempfile.gettempdir()) / f"skill_self_update_rejected_{skill}_{datetime.now():%Y%m%d-%H%M%S}.patch"
    saved.write_text(patch, encoding="utf-8")
    run(repo, "restore", "--source=HEAD", "--staged", "--worktree", "--", base, check=False)
    run(repo, "clean", "-fdq", "--", base, check=False)
    return f"đã hoàn tác thay đổi của {base} ({reason}); bản vá bị từ chối lưu tại {saved}"


def edit_versions(repo: Path, skill: str, old_skill_v: str | None, new_skill_v: str | None, old_plugin: str, new_plugin: str) -> list[str]:
    touched: list[str] = []
    if old_skill_v and new_skill_v:
        sm = repo / "skills" / skill / "SKILL.md"
        raw = sm.read_bytes().decode("utf-8")
        new = re.sub(r"(?m)^(version:\s*[\"']?)" + re.escape(old_skill_v) + r"([\"']?\s*)$", r"\g<1>" + new_skill_v + r"\g<2>", raw, count=1)
        if new == raw:
            raise Refuse("không bump được version trong frontmatter SKILL.md")
        sm.write_bytes(new.encode("utf-8"))
    mp = repo / MANIFEST_REL
    if mp.exists():
        m = json.loads(mp.read_text(encoding="utf-8"))
        m["manifest_version"] = new_plugin
        m["updated_at"] = datetime.now().strftime("%Y-%m-%d")
        for e in m.get("skills", []):
            if e.get("name") == skill and new_skill_v:
                e["version"] = new_skill_v
        mp.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
        touched.append(MANIFEST_REL)
    for rel in PLUGIN_VERSION_FILES:
        fp = repo / rel
        if not fp.exists():
            continue
        raw = fp.read_bytes().decode("utf-8")
        new, n = re.subn(r'("version"\s*:\s*")' + re.escape(old_plugin) + '"', r"\g<1>" + new_plugin + '"', raw)
        if n == 0:
            raise Refuse(f"{rel} không chứa version {old_plugin} — các file version đang lệch nhau, sửa tay trước")
        fp.write_bytes(new.encode("utf-8"))
        touched.append(rel)
    return touched


def update_changelog(repo: Path, skill: str, new_plugin: str, kind: str, summary: str) -> str:
    rel = "skills/CHANGELOG.md" if (repo / "skills" / "CHANGELOG.md").exists() else "CHANGELOG.md"
    fp = repo / rel
    section = {"added": "Added", "changed": "Changed", "fixed": "Fixed"}[kind]
    entry = f"## [{new_plugin}] - {datetime.now():%Y-%m-%d}\n### {section}\n- **{skill}**: {summary} (self-update)\n\n"
    if fp.exists():
        raw = fp.read_bytes().decode("utf-8")
        crlf = "\r\n" in raw
        txt = raw.replace("\r\n", "\n")
        m = re.search(r"(?m)^## ", txt)
        txt = (txt[:m.start()] + entry + txt[m.start():]) if m else (txt.rstrip("\n") + "\n\n" + entry)
        if crlf:
            txt = txt.replace("\n", "\r\n")
        fp.write_bytes(txt.encode("utf-8"))
    else:
        header = ("# Changelog\n\nTất cả thay đổi đáng chú ý của bộ skill được ghi ở đây.\n"
                  "Định dạng theo [Keep a Changelog](https://keepachangelog.com/) và [Semantic Versioning](https://semver.org/).\n\n")
        fp.write_text(header + entry, encoding="utf-8", newline="\n")
    return rel


def main() -> int:
    ap = argparse.ArgumentParser(description="Tự sửa + push cải tiến nhỏ cho đúng 1 skill (có rào an toàn).")
    ap.add_argument("--skill", required=True, help="tên thư mục skill, vd c3-code-review")
    ap.add_argument("--task-id", required=True, help="mã duy nhất của tác vụ người dùng hiện tại (tối đa 1 lần tự sửa/tác vụ)")
    ap.add_argument("--summary", required=True, help="một câu mô tả thay đổi (≤120 ký tự)")
    ap.add_argument("--type", choices=("added", "changed", "fixed"), default="changed")
    ap.add_argument("--dry-run", action="store_true", help="chỉ kiểm tra, không đổi gì")
    ap.add_argument("--no-push", action="store_true", help="commit local, không pull/push")
    a = ap.parse_args()
    summary = " ".join(a.summary.split())
    if not summary or len(summary) > 120:
        print("❌ --summary phải 1–120 ký tự")
        return 2

    repo = Path(os.environ.get("SKILLS_REPO", DEFAULT_REPO))
    try:
        used_file = preflight(repo, a.skill, a.task_id)

        base = f"skills/{a.skill}/"
        changed = changed_paths(repo)
        if not changed:
            raise Refuse("không có thay đổi nào trong working tree — hãy sửa skill trước rồi chạy lại")
        outside = [p for p in changed if not p.startswith(base)]
        if outside:
            raise Refuse("working tree có thay đổi ngoài skill này (chỉ được sửa 1 skill, không đụng file khác): " + ", ".join(outside[:8]))

        added, add_n, del_n, new_files = collect_added_lines(repo, a.skill)
        deleted_files = run(repo, "ls-files", "--deleted", "--", base[:-1]).stdout.split()
        if deleted_files:
            raise Refuse("không được xóa file: " + ", ".join(deleted_files[:5]))
        if add_n > MAX_ADDED_LINES:
            raise Refuse(f"thêm {add_n} dòng > giới hạn {MAX_ADDED_LINES} — chia nhỏ hoặc xin người dùng duyệt thủ công")
        if del_n > MAX_REMOVED_LINES:
            raise Refuse(f"xóa {del_n} dòng > giới hạn {MAX_REMOVED_LINES} — tự sửa chỉ được thêm hoặc làm rõ, không xóa quy tắc")
        bad_new = [f for f in new_files if not re.match(rf"^skills/{re.escape(a.skill)}/references/[^/]+\.md$", f)]
        if len(new_files) > MAX_NEW_FILES or bad_new:
            raise Refuse(f"file mới chỉ được là references/*.md (tối đa {MAX_NEW_FILES}): {bad_new or new_files}")
        if any(re.match(r"^version:", l) for l in added):
            raise Refuse("không tự sửa dòng 'version:' — script tự bump")

        hits = scan_sensitive(added)
        if hits:
            msg = revert_skill(repo, a.skill, "phát hiện dữ liệu nhạy cảm") if not a.dry_run else "(dry-run: chưa hoàn tác)"
            raise Refuse("TỪ CHỐI — diff chứa mẫu nhạy cảm: " + "; ".join(hits[:5]) + f". {msg}")

        rc, out = run_doctor(repo)
        if rc != 0:
            msg = revert_skill(repo, a.skill, "skill_doctor FAIL") if not a.dry_run else "(dry-run: chưa hoàn tác)"
            print(out[-1500:])
            raise Refuse(f"skill_doctor báo FAIL — {msg}", 3)

        plugin_json = repo / ".claude-plugin" / "plugin.json"
        old_plugin = json.loads(plugin_json.read_text(encoding="utf-8"))["version"]
        new_plugin = bump_patch(old_plugin)
        old_skill_v, _ = read_frontmatter_version(repo / "skills" / a.skill / "SKILL.md")
        new_skill_v = bump_patch(old_skill_v) if old_skill_v else None

        print(f"Kiểm tra OK: +{add_n}/-{del_n} dòng, {len(new_files)} file mới, doctor sạch.")
        print(f"Kế hoạch: skill {a.skill} {old_skill_v or '(không có version)'} → {new_skill_v or '-'}; plugin {old_plugin} → {new_plugin}")
        if a.dry_run:
            print("(dry-run) không thay đổi gì thêm.")
            return 0

        touched = edit_versions(repo, a.skill, old_skill_v, new_skill_v, old_plugin, new_plugin)
        changelog_rel = update_changelog(repo, a.skill, new_plugin, a.type, summary)
        rc, out = run_doctor(repo)
        if rc != 0:
            print(out[-1500:])
            run(repo, "restore", "--source=HEAD", "--staged", "--worktree", "--", *touched, changelog_rel, f"skills/{a.skill}", check=False)
            run(repo, "clean", "-fdq", "--", f"skills/{a.skill}", check=False)
            raise Refuse("skill_doctor FAIL sau khi bump version — đã hoàn tác toàn bộ", 3)

        paths = [f"skills/{a.skill}", *touched, changelog_rel]
        run(repo, "add", "--", *paths)
        ctype = {"added": "feat", "changed": "docs", "fixed": "fix"}[a.type]
        msg = (f"{ctype}(skills): {a.skill} — {summary}\n\n"
               f"Self-update v{new_plugin} (task {a.task_id}); diff +{add_n}/-{del_n}.\n"
               f"Hoàn tác: git revert <hash>\n")
        co = os.environ.get("SKILL_SELF_UPDATE_COAUTHOR", "").strip()
        if co:
            msg += f"\nCo-Authored-By: {co}\n"
        run(repo, "commit", "-m", msg)
        commit = run(repo, "rev-parse", "--short", "HEAD").stdout.strip()
        with open(used_file, "a", encoding="utf-8") as fh:
            fh.write(a.task_id + "\n")

        report = (f"\n📦 Skill: {a.skill} ({old_skill_v or '-'} → {new_skill_v or '-'}), plugin {new_plugin}\n"
                  f"📝 Đổi: {summary}\n🔖 Commit: {commit}\n↩️  Hoàn tác: git revert {commit}\n")
        if a.no_push:
            print(report + "ℹ️  --no-push: commit chỉ ở local.")
            return 0
        pull = run(repo, "pull", "--rebase", "origin", BRANCH, check=False)
        if pull.returncode != 0:
            run(repo, "rebase", "--abort", check=False)
            print(report + f"⚠️ git pull --rebase thất bại — commit GIỮ Ở LOCAL, chưa push.\n   Lý do: {(pull.stderr or pull.stdout).strip()[:400]}")
            return 4
        commit = run(repo, "rev-parse", "--short", "HEAD").stdout.strip()
        push = run(repo, "push", "origin", BRANCH, check=False)
        if push.returncode != 0:
            print(report + f"⚠️ git push thất bại — commit GIỮ Ở LOCAL (không force-push).\n   Lý do: {(push.stderr or push.stdout).strip()[:400]}")
            return 5
        print(f"\n📦 Skill: {a.skill} ({old_skill_v or '-'} → {new_skill_v or '-'}), plugin {new_plugin}\n"
              f"📝 Đổi: {summary}\n🔖 Commit (đã push): {commit}\n↩️  Hoàn tác: git revert {commit}\n"
              f"✅ Đã push origin/{BRANCH}.")
        return 0
    except Refuse as e:
        print(f"⛔ {e}")
        return e.code


if __name__ == "__main__":
    sys.exit(main())
