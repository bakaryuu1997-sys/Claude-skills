#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""compute_status.py — nguồn DUY NHẤT cho logic quét tài liệu + staleness + gate (v3.3.0).
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
    "b1-project-kickoff": ["a2-requirement-analysis", "a6-estimate", "a9-project-timeline"],
    "b2-basic-design": ["a2-requirement-analysis", "a3-prototype-ui", "a4-api-design"],
    "b3-detail-design": ["b2-basic-design", "a4-api-design", "a5-db-design"],
    "db-design": ["api-design"],
    "estimate": ["api-design", "db-design", "prototype-ui", "requirement-analysis"],
    "estimate-template-fill": ["estimate"],
    "test-plan": ["api-design", "db-design", "requirement-analysis"],
    "project-timeline": ["estimate", "test-plan"],
    "project-kickoff": ["requirement-analysis", "estimate", "project-timeline"],
    "basic-design": ["requirement-analysis", "prototype-ui", "api-design"],
    "detail-design": ["basic-design", "api-design", "db-design"],
}


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
            found = [f for f in sorted(set(list(ws.glob(g)) + list(ws.glob(f"docs/**/{g}")))) if not f.name.startswith("~$")]
            for f in found:
                outs.append({"file": f.name,
                             "path": str(f.relative_to(ws)).replace("\\", "/"),
                             "mtime": datetime.fromtimestamp(f.stat().st_mtime).isoformat(timespec="seconds"),
                             "_ts": f.stat().st_mtime})
        if outs:
            newest_out[sk["name"]] = max(o["_ts"] for o in outs)
        docs.append({"skill": sk["name"], "step": sk.get("step"),
                     "files": outs, "status": "present" if outs else "missing"})

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

    gates = {"raw": "", "blocked": False}
    try:
        r = subprocess.run([sys.executable, str(Path(__file__).parent / "check_gate.py"), str(ws)],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
        gates = {"raw": (r.stdout + r.stderr).strip(), "blocked": r.returncode != 0}
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
