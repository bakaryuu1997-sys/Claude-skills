#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""coverage_summary.py — gom số liệu thực chứng cho Review_Summary / Files_Reviewed của c3.

Đọc:
  * coverage/coverage-summary.json  (Jest/Istanbul reporter `json-summary`)   --coverage
  * kết quả Jest `--json`            (số test pass/fail)                      --tests
  * git diff --numstat <base>...HEAD (LOC thêm/xóa theo file)                 --base

Usage:
    python coverage_summary.py [--coverage coverage/coverage-summary.json] [--tests tests/results/x.json]
                               [--base origin/main] [--repo .] [--format json|md]

Không có input nào → vẫn chạy, trường tương ứng là null và có cảnh báo trong "warnings".
Exit code: 0 luôn khi chạy xong (đây là script thu thập số liệu, không phải gate); 2 khi tham số sai.
Chỉ dùng thư viện chuẩn; gọi git bằng danh sách đối số (không shell).
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "a1-project-init" / "scripts"))
from i18n import add_lang_args, pick, resolve_lang  # noqa: E402

MESSAGES = {
    "vi": {"nofile": "không thấy file: {p}", "unread": "không đọc được {p}: {e}", "fmt": "{p}: định dạng không nhận diện (cần Jest --json hoặc pytest-json-report)",
           "nogit": "không chạy được git: {e}", "giterr": "git diff lỗi: {e}", "h_metric": "Chỉ số", "h_value": "Giá trị", "cov": "Coverage",
           "test": "Test", "pass": "pass", "fail": "fail", "skip": "skip/todo", "loc": "LOC", "lines": "dòng", "files": "file", "warn": "Cảnh báo"},
    "ja": {"nofile": "ファイルが見つかりません: {p}", "unread": "{p} を読み込めません: {e}", "fmt": "{p}: 形式を認識できません（Jest --json または pytest-json-report が必要）",
           "nogit": "git を実行できません: {e}", "giterr": "git diff に失敗: {e}", "h_metric": "指標", "h_value": "値", "cov": "カバレッジ",
           "test": "テスト", "pass": "合格", "fail": "失敗", "skip": "スキップ/todo", "loc": "変更行数", "lines": "行", "files": "ファイル", "warn": "警告"},
    "en": {"nofile": "file not found: {p}", "unread": "cannot read {p}: {e}", "fmt": "{p}: unrecognised format (need Jest --json or pytest-json-report)",
           "nogit": "cannot run git: {e}", "giterr": "git diff failed: {e}", "h_metric": "Metric", "h_value": "Value", "cov": "Coverage",
           "test": "Test", "pass": "pass", "fail": "fail", "skip": "skipped/todo", "loc": "LOC", "lines": "lines", "files": "files", "warn": "Warning"},
}
LANG_M = pick(MESSAGES, "vi")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def load_json(path: Path, warnings: list):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        warnings.append(LANG_M["nofile"].format(p=path))
    except (OSError, json.JSONDecodeError) as e:
        warnings.append(LANG_M["unread"].format(p=path, e=e))
    return None


def norm(p: str, repo: Path) -> str:
    """Đưa đường dẫn về dạng tương đối repo, dấu '/'."""
    q = Path(p)
    try:
        q = q.resolve().relative_to(repo.resolve())
    except (ValueError, OSError):
        pass
    return str(q).replace("\\", "/")


def coverage_part(path: Path, repo: Path, warnings: list):
    data = load_json(path, warnings)
    if not isinstance(data, dict) or "total" not in data:
        return None
    def pct(block, key):
        v = block.get(key, {}).get("pct")
        return v if isinstance(v, (int, float)) else None
    total = data["total"]
    files = {}
    for k, v in data.items():
        if k == "total" or not isinstance(v, dict):
            continue
        files[norm(k, repo)] = {m: pct(v, m) for m in ("lines", "statements", "functions", "branches")}
    return {
        "total": {m: pct(total, m) for m in ("lines", "statements", "functions", "branches")},
        "files": files,
    }


def tests_part(path: Path, warnings: list):
    data = load_json(path, warnings)
    if not isinstance(data, dict):
        return None
    if "numTotalTests" in data:  # Jest --json
        return {
            "total": data.get("numTotalTests"),
            "passed": data.get("numPassedTests"),
            "failed": data.get("numFailedTests"),
            # it.todo / it.skip nằm trong numTotalTests nhưng không chạy → tách riêng, không để "pass/total" gây hiểu nhầm.
            "skipped": (data.get("numPendingTests") or 0) + (data.get("numTodoTests") or 0),
            "suites": data.get("numTotalTestSuites"),
        }
    summ = data.get("summary")   # pytest-json-report
    if isinstance(summ, dict):
        return {"total": summ.get("total"), "passed": summ.get("passed"), "failed": summ.get("failed"),
                "skipped": summ.get("skipped", 0), "suites": None}
    warnings.append(LANG_M["fmt"].format(p=path))
    return None


def diff_part(base: str, repo: Path, warnings: list):
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "diff", "--numstat", f"{base}...HEAD"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
    except (OSError, subprocess.SubprocessError) as e:
        warnings.append(LANG_M["nogit"].format(e=e))
        return None
    if out.returncode != 0:
        warnings.append(LANG_M["giterr"].format(e=out.stderr.strip()[:200]))
        return None
    files = []
    for line in out.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        add, dele, name = parts
        files.append({
            "path": name.replace("\\", "/"),
            "added": int(add) if add.isdigit() else None,   # file nhị phân: '-'
            "deleted": int(dele) if dele.isdigit() else None,
        })
    return {
        "files": files,
        "total_added": sum(f["added"] or 0 for f in files),
        "total_deleted": sum(f["deleted"] or 0 for f in files),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description="Gom coverage + test + git diff cho báo cáo code review (c3)")
    ap.add_argument("--coverage", default="coverage/coverage-summary.json")
    ap.add_argument("--tests", help="file kết quả test (Jest --json / pytest-json-report)")
    ap.add_argument("--base", help="nhánh/commit gốc để diff, vd origin/main")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--format", choices=("json", "md"), default="json")
    add_lang_args(ap, audience="internal")  # bảng bằng chứng vào báo cáo code review (nội bộ)
    a = ap.parse_args(argv)
    global LANG_M
    LANG_M = pick(MESSAGES, resolve_lang(a.lang, a.context, a.audience))

    repo = Path(a.repo)
    warnings = []
    cov = coverage_part(repo / a.coverage if not Path(a.coverage).is_absolute() else Path(a.coverage), repo, warnings)
    tst = tests_part(Path(a.tests), warnings) if a.tests else None
    dif = diff_part(a.base, repo, warnings) if a.base else None

    # ghép coverage vào từng file đã đổi
    if cov and dif:
        for f in dif["files"]:
            f["coverage"] = cov["files"].get(f["path"])

    result = {"coverage": cov["total"] if cov else None, "tests": tst, "diff": dif, "warnings": warnings}
    if a.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    lines = [f"| {LANG_M['h_metric']} | {LANG_M['h_value']} |", "|---|---|"]
    if cov:
        for m, v in cov["total"].items():
            lines.append(f"| {LANG_M['cov']} {m} | {v if v is not None else 'n/a'}% |")
    if tst:
        skipped = f", {tst['skipped']} {LANG_M['skip']}" if tst.get("skipped") else ""
        lines.append(f"| {LANG_M['test']} | {tst['passed']}/{tst['total']} {LANG_M['pass']}, {tst['failed']} {LANG_M['fail']}{skipped} |")
    if dif:
        lines.append(f"| {LANG_M['loc']} | +{dif['total_added']} / -{dif['total_deleted']} ({len(dif['files'])} {LANG_M['files']}) |")
    for w in warnings:
        lines.append(f"| {LANG_M['warn']} | {w} |")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
