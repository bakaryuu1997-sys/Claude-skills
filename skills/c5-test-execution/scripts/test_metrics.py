#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""test_metrics.py — tính metrics + cổng chất lượng (Quality Gate) cho một phase test (UT/IT/ST/UAT).

Input: snapshot JSON (nguồn sự thật, do người/CI ghi; xem references/snapshot-format.md):
  {
    "phase": "UT" | "IT" | "ST" | "UAT",
    "tests":   [ {"id": "AUTH-API-001", "module": "Auth", "viewpoint": "Security",
                  "result": "pass|fail|blocked|na|notrun", "bug_id": "BUG-003", "duration_ms": 120} ],
    "defects": [ {"id": "BUG-003", "severity": "Critical|High|Medium|Low", "status": "open|in progress|fixed|retest|verified|closed|wontfix",
                  "regression_test_id": "", "regression_impact_scope": "", "required_regression_suites": "",
                  "verified_commit": ""} ],
    "coverage": {"line": 91.2, "branch": 74.0}          # tùy chọn (UT)
  }

Context (tùy chọn): --context <ws>/project-context.json → đọc settings.quality_gates.
Mặc định ngưỡng khi thiếu context: xem pipeline.md "Hằng số chung" (UT pass 95 · IT pass 95 · ST pass 98 · coverage line 80 · branch 70 · 0 Critical/High mở).

Định nghĩa (thống nhất với SKILL.md):
  Total          = số test case trong phase
  Executed       = pass + fail + blocked                  (không tính na)
  Execution rate = Executed / (Total - na)
  Pass rate      = pass / (pass + fail)                   (blocked không vào mẫu số — được báo riêng)
  Các test notrun/blocked làm phase KHÔNG thể QUALIFIED.
  Defect "còn mở" = status không thuộc {verified, closed, wontfix}  (theo pipeline.md §1: Fixed chưa retest vẫn mở)
  Closed/verified thiếu một trong 4 trường regression ⇒ UNVERIFIED_FIX (chặn Quality Gate).
  Verdict: QUALIFIED chỉ khi: không notrun/blocked · open Critical/High ≤ open_critical_high_max · không UNVERIFIED_FIX
           · pass rate đạt ngưỡng phase (UT/IT/ST) · coverage (nếu có) đạt ngưỡng.
  UAT: không có ngưỡng pass rate mặc định — chỉ báo số liệu; đạt hay không do biên bản nghiệm thu quyết định.

Usage:
  python test_metrics.py snapshot.json [--context project-context.json] [--format md|json] [--repo <git repo>]
  --repo: với defect có verified_commit, chạy `git show --name-only --format=` để điền Impact Scope nếu trường đang trống.

Exit: 0 QUALIFIED (hoặc UAT đã báo số liệu) · 1 NOT QUALIFIED / RELEASE BLOCKED · 2 lỗi đầu vào.
Chỉ thư viện chuẩn; git gọi bằng danh sách đối số.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_GATES = {
    "ut_pass_rate": 95, "ut_coverage_line": 80, "ut_coverage_branch": 70,
    "it_pass_rate": 95, "st_pass_rate": 98, "open_critical_high_max": 0,
}
PHASE_PASS_KEY = {"UT": "ut_pass_rate", "IT": "it_pass_rate", "ST": "st_pass_rate"}
CLOSED_STATES = {"verified", "closed", "wontfix"}
REGRESSION_FIELDS = ("regression_test_id", "regression_impact_scope", "required_regression_suites", "verified_commit")
RESULTS = ("pass", "fail", "blocked", "na", "notrun")


def pct(n, d):
    return round(100.0 * n / d, 2) if d else None


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def git_impact_scope(repo: Path, commit: str):
    try:
        out = subprocess.run(["git", "-C", str(repo), "show", "--name-only", "--format=", commit],
                             capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None
    if out.returncode != 0:
        return None
    files = [l.strip().replace("\\", "/") for l in out.stdout.splitlines() if l.strip()]
    return ", ".join(files) if files else None


def compute(snap: dict, gates: dict, repo: Path | None):
    phase = str(snap.get("phase", "")).upper()
    tests = snap.get("tests") or []
    defects = snap.get("defects") or []
    if phase not in ("UT", "IT", "ST", "UAT"):
        raise ValueError("phase phải là UT | IT | ST | UAT")
    counts = {r: 0 for r in RESULTS}
    bad = []
    for t in tests:
        r = str(t.get("result", "notrun")).lower()
        if r not in counts:
            bad.append(t.get("id", "?"))
            r = "notrun"
        counts[r] += 1
    if bad:
        raise ValueError(f"result không hợp lệ ở: {', '.join(map(str, bad[:10]))}")

    total = len(tests)
    executed = counts["pass"] + counts["fail"] + counts["blocked"]
    applicable = total - counts["na"]
    pass_rate = pct(counts["pass"], counts["pass"] + counts["fail"])

    # Viewpoint breakdown
    vp = {}
    for t in tests:
        v = t.get("viewpoint") or "(chưa gán)"
        d = vp.setdefault(v, {"total": 0, "pass": 0, "fail": 0})
        d["total"] += 1
        if str(t.get("result")).lower() == "pass":
            d["pass"] += 1
        if str(t.get("result")).lower() == "fail":
            d["fail"] += 1

    # Defects
    open_ch, unverified, open_list, filled = 0, [], [], []
    for d in defects:
        status = str(d.get("status", "open")).lower()
        sev = str(d.get("severity", "")).capitalize()
        if status not in CLOSED_STATES:
            if sev in ("Critical", "High"):
                open_ch += 1
            open_list.append(d.get("id"))
        if status in ("closed", "verified"):
            if not d.get("impact_scope_source") and repo and d.get("verified_commit") and not d.get("regression_impact_scope"):
                scope = git_impact_scope(repo, d["verified_commit"])
                if scope:
                    d["regression_impact_scope"] = scope
                    d["impact_scope_source"] = "git"
                    filled.append(d.get("id"))
            missing = [f for f in REGRESSION_FIELDS if not str(d.get(f, "")).strip()]
            if missing:
                unverified.append({"id": d.get("id"), "missing": missing})

    # Gates
    blockers = []
    if counts["notrun"]:
        blockers.append(f"{counts['notrun']} test chưa chạy (notrun)")
    if counts["blocked"]:
        blockers.append(f"{counts['blocked']} test bị blocked")
    max_open = int(gates.get("open_critical_high_max", 0))
    if open_ch > max_open:
        blockers.append(f"{open_ch} bug Critical/High còn mở (ngưỡng {max_open})")
    if unverified:
        blockers.append(f"{len(unverified)} bug Closed/Verified thiếu bằng chứng hồi quy (UNVERIFIED_FIX)")
    cov = snap.get("coverage") or {}
    key = PHASE_PASS_KEY.get(phase)
    if key:
        need = float(gates.get(key, DEFAULT_GATES[key]))
        if pass_rate is None or pass_rate < need:
            blockers.append(f"pass rate {pass_rate}% < {need}%")
    if phase == "UT":
        for m, gk in (("line", "ut_coverage_line"), ("branch", "ut_coverage_branch")):
            if cov.get(m) is None:
                blockers.append(f"thiếu coverage {m}")
            elif float(cov[m]) < float(gates.get(gk, DEFAULT_GATES[gk])):
                blockers.append(f"coverage {m} {cov[m]}% < {gates.get(gk, DEFAULT_GATES[gk])}%")

    if phase == "UAT":
        verdict = "UAT: số liệu đã tổng hợp — kết luận nghiệm thu do biên bản ký của khách quyết định"
        code = 0 if not blockers else 1
        if blockers:
            verdict = "UAT: CHƯA ĐỦ điều kiện giao nghiệm thu — " + "; ".join(blockers)
    else:
        code = 0 if not blockers else 1
        verdict = "QUALIFIED" if not blockers else "NOT QUALIFIED / RELEASE BLOCKED"

    return {
        "phase": phase, "total": total, "counts": counts,
        "execution_rate": pct(executed, applicable), "pass_rate": pass_rate,
        "viewpoints": vp, "defects_total": len(defects), "open_critical_high": open_ch,
        "open_defects": open_list, "unverified_fix": unverified,
        "coverage": {"line": cov.get("line"), "branch": cov.get("branch")},
        "blockers": blockers, "verdict": verdict, "impact_scope_filled_from_git": filled,
        "top_slowest": sorted(
            [(t.get("id"), t.get("duration_ms")) for t in tests if isinstance(t.get("duration_ms"), (int, float))],
            key=lambda x: -x[1])[:5],
        "slow_suites_over_3s": [i for i, ms in [(t.get("id"), t.get("duration_ms")) for t in tests]
                                if isinstance(ms, (int, float)) and ms > 3000],
    }, code


def to_md(r: dict) -> str:
    L = [f"## Phase {r['phase']} — {r['verdict']}", "",
         "| Chỉ số | Giá trị |", "|---|---|",
         f"| Tổng test case | {r['total']} |",
         f"| Pass / Fail / Blocked / N/A / Notrun | {r['counts']['pass']} / {r['counts']['fail']} / {r['counts']['blocked']} / {r['counts']['na']} / {r['counts']['notrun']} |",
         f"| Execution rate | {r['execution_rate']}% |",
         f"| Pass rate | {r['pass_rate']}% |",
         f"| Defect Critical/High còn mở | {r['open_critical_high']} |",
         f"| Coverage line / branch | {r['coverage']['line']}% / {r['coverage']['branch']}% |", "",
         "### Viewpoint", "| Viewpoint | Total | Pass | Fail |", "|---|---|---|---|"]
    for v, d in r["viewpoints"].items():
        L.append(f"| {v} | {d['total']} | {d['pass']} | {d['fail']} |")
    if r["blockers"]:
        L += ["", "### Lý do chặn"] + [f"- {b}" for b in r["blockers"]]
    if r["unverified_fix"]:
        L += ["", "### UNVERIFIED_FIX"] + [f"- {u['id']}: thiếu {', '.join(u['missing'])}" for u in r["unverified_fix"]]
    if r["slow_suites_over_3s"]:
        L += ["", "### WARN: SLOW SUITE (> 3 s)"] + [f"- {s}" for s in r["slow_suites_over_3s"]]
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Metrics + Quality Gate cho một phase test (c5)")
    ap.add_argument("snapshot")
    ap.add_argument("--context", help="project-context.json để đọc settings.quality_gates")
    ap.add_argument("--format", choices=("md", "json"), default="md")
    ap.add_argument("--repo", help="git repo để điền Impact Scope từ verified_commit")
    a = ap.parse_args(argv)

    try:
        snap = load(Path(a.snapshot))
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR không đọc được snapshot: {e}", file=sys.stderr)
        return 2
    gates = dict(DEFAULT_GATES)
    if a.context:
        try:
            ctx = load(Path(a.context))
            gates.update({k: v for k, v in ((ctx.get("settings") or {}).get("quality_gates") or {}).items() if v is not None})
        except (OSError, json.JSONDecodeError) as e:
            print(f"WARN không đọc được context, dùng ngưỡng mặc định: {e}", file=sys.stderr)
    try:
        result, code = compute(snap, gates, Path(a.repo) if a.repo else None)
    except ValueError as e:
        print(f"ERROR {e}", file=sys.stderr)
        return 2

    if a.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(to_md(result))
    return code


if __name__ == "__main__":
    sys.exit(main())
