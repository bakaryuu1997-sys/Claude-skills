#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""compute_status.py — nguồn DUY NHẤT cho logic quét tài liệu + staleness + gate (v3.17.0).
/x3-project-status và /x2-project-architecture CÙNG dùng script này — không skill nào tự cài lại việc quét.

Usage: python3 compute_status.py <workspace_folder> [<skills_dir>]
Output: JSON {generated_at, documents[], gates{}, progress{}}
  documents[].status: present | stale | missing   (stale kèm stale_because[])"""
import json, subprocess, sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Hợp đồng phụ thuộc input→output — rút từ pipeline.md (đổi pipeline → sửa Ở ĐÂY, một chỗ)
DEPS = {
    "a5-db-design": ["a4-api-design"],
    "a6-estimate": ["a4-api-design", "a5-db-design", "a3-prototype-ui", "a2-requirement-analysis"],
    "a7-estimate-template-fill": ["a6-estimate"],
    "a8-test-plan": ["a4-api-design", "a5-db-design", "a2-requirement-analysis"],
    "a9-project-timeline": ["a6-estimate", "a8-test-plan"],
    "b0-proposal-sow": ["a2-requirement-analysis", "a4-api-design", "a5-db-design", "a6-estimate", "a9-project-timeline"],
    "b1-project-kickoff": ["b0-proposal-sow", "a2-requirement-analysis", "a6-estimate", "a9-project-timeline"],
    "b2-basic-design": ["a2-requirement-analysis", "a3-prototype-ui", "a4-api-design", "a5-db-design", "a8-test-plan"],
    "b3-detail-design": ["b2-basic-design", "a4-api-design", "a5-db-design"],
    "c1-dev-implement": ["b3-detail-design", "a4-api-design", "a5-db-design"],
    "c2-api-test-suite-generator": ["a4-api-design", "b3-detail-design"],
    "c3-code-review": ["c1-dev-implement", "a4-api-design", "a5-db-design"],
    "c4-trailofbits-security-skills": ["c1-dev-implement", "a4-api-design"],
    "c5-test-execution": ["a8-test-plan", "c1-dev-implement"],
    "c6-sprint-review": ["a9-project-timeline", "c5-test-execution"],
    "c7-change-request": ["a6-estimate", "a9-project-timeline"],
    "c8-release-deployment": ["c1-dev-implement", "c3-code-review", "c4-trailofbits-security-skills", "c5-test-execution"],
    "d1-handover-doc": ["c8-release-deployment", "c4-trailofbits-security-skills", "c5-test-execution", "a4-api-design", "a5-db-design"],
    "d2-uat-acceptance": ["d1-handover-doc", "a8-test-plan", "c5-test-execution"],
    "d3-user-guide-manual": ["b2-basic-design", "a3-prototype-ui", "d2-uat-acceptance"],
    "x2-project-architecture": ["a4-api-design", "a5-db-design", "b3-detail-design"],
}


def _step_key(step) -> tuple:
    """Sắp xếp A1<A2<…<B0<…<C0<…<X7; bước lạ xuống cuối."""
    import re
    m = re.match(r"^([A-Za-z]+)(\d+)", str(step or ""))
    return (m.group(1).upper(), int(m.group(2))) if m else ("~", 0)


def main() -> int:
    ws = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    skills_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parents[2]
    manifest_p = skills_dir / "a1-project-init" / "assets" / "skills-manifest.json"
    if not manifest_p.exists():
        manifest_p = skills_dir / "project-init" / "assets" / "skills-manifest.json"
    manifest = []
    if manifest_p.exists():
        try:
            manifest = json.loads(manifest_p.read_text(encoding="utf-8")).get("skills", [])
        except Exception as e:
            print(json.dumps({"error": f"manifest không đọc được: {e}"}))
            return 1

    ctx = {}
    ctx_f = ws / "project-context.json"
    if ctx_f.exists():
        try:
            ctx = json.loads(ctx_f.read_text(encoding="utf-8"))
        except Exception:
            ctx = {"_error": "project-context.json không parse được"}

    docs, newest_out = [], {}
    for sk in manifest:
        outs = []
        for pat in sk.get("outputs", []):
            g = pat.replace("[N]", "*").replace("[Phase]", "*").replace("[date]", "*")
            stem, _, ext = g.rpartition(".")
            if g.startswith("*_") and not stem.endswith("*") and ext in ("docx", "xlsx", "pptx", "html", "md"):
                g = stem + "*." + ext  # nhận cả bản _v2, _v3 khi re-run
            if "<" in g:  # pattern mô tả (vd <template-filled>) không phải glob
                continue
            if g.endswith("/"):  # thư mục output (vd frontend/): có tồn tại và không rỗng là đủ
                d = ws / g.rstrip("/")
                if d.is_dir() and any(d.iterdir()):
                    outs.append({"file": d.name + "/", "path": g, "mtime": datetime.fromtimestamp(d.stat().st_mtime).isoformat(timespec="seconds"), "_ts": d.stat().st_mtime})
                continue
            found = [f for f in sorted(set(list(ws.glob(g)) + list(ws.glob(f"docs/**/{g}")))) if not f.name.startswith("~$")]
            for f in found:
                outs.append({"file": f.name,
                             "path": str(f.relative_to(ws)).replace("\\", "/"),
                             "mtime": datetime.fromtimestamp(f.stat().st_mtime).isoformat(timespec="seconds"),
                             "_ts": f.stat().st_mtime})
        if outs:
            newest_out[sk["name"]] = max(o["_ts"] for o in outs)
        if not sk.get("outputs"):  # skill đọc-only (menu, x3, x6): không có tài liệu để quét
            docs.append({"skill": sk["name"], "step": sk.get("step"), "files": [], "status": "n/a"})
            continue
        status = "present" if outs else ("optional" if sk.get("optional") else "missing")
        docs.append({"skill": sk["name"], "step": sk.get("step"), "files": outs, "status": status})

    docs.sort(key=lambda d: _step_key(d.get("step")))
    for d in docs:  # staleness: input mới hơn output → stale
        if d["status"] != "present":
            continue
        newer = [i for i in DEPS.get(d["skill"], [])
                 if newest_out.get(i) and newest_out[i] > newest_out[d["skill"]]]
        if newer:
            d["status"] = "stale"
            d["stale_because"] = newer
    for d in docs:
        for o in d["files"]:
            o.pop("_ts", None)

    gates = {"raw": "", "blocked": False, "unverifiable": False}
    try:
        r = subprocess.run([sys.executable, str(Path(__file__).parent / "check_gate.py"), str(ws)],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
        gates = {"raw": (r.stdout + r.stderr).strip(), "blocked": r.returncode == 1, "unverifiable": r.returncode == 3}
    except Exception as e:
        gates = {"raw": f"check_gate lỗi: {e}", "blocked": False}

    proj = ctx.get("project") if isinstance(ctx.get("project"), dict) else {}
    est = ctx.get("estimates") if isinstance(ctx.get("estimates"), dict) else {}
    progress = {"current_sprint": proj.get("current_sprint"),
                "total_sprints": est.get("total_sprints"),
                "go_live_target": proj.get("go_live_target"),
                "activity_log_entries": len(ctx.get("activity_log") or [])}

    print(json.dumps({"generated_at": datetime.now().isoformat(timespec="seconds"),
                      "workspace": str(ws), "documents": docs,
                      "gates": gates, "progress": progress},
                     ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
