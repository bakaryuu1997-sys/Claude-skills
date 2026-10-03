# -*- coding: utf-8 -*-
"""Kiểm tra project-context.json hợp lệ. Chạy độc lập hoặc import.
Không phụ thuộc thư viện ngoài (jsonschema là optional)."""
import json, sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REQUIRED_TOP = ["version", "project", "tech_stack", "team", "settings"]
PROJECT_TYPES = {"mobile_app", "web_app", "web_admin", "api_only", "fullstack"}

def validate_context(ctx: dict) -> list[str]:
    """Trả về danh sách lỗi (rỗng = hợp lệ)."""
    errs = []
    if not isinstance(ctx, dict):
        return ["context không phải object JSON"]
    for k in REQUIRED_TOP:
        if k not in ctx:
            errs.append(f"thiếu key bắt buộc: '{k}'")
    proj = ctx.get("project", {})
    if not proj.get("name"):
        errs.append("project.name trống")
    if proj.get("type") and proj["type"] not in PROJECT_TYPES:
        errs.append(f"project.type='{proj['type']}' không hợp lệ (cho phép: {sorted(PROJECT_TYPES)})")
    team = ctx.get("team", [])
    if not isinstance(team, list):
        errs.append("team phải là mảng")
    else:
        for i, m in enumerate(team):
            if not m.get("id") or not m.get("role"):
                errs.append(f"team[{i}] thiếu id hoặc role")
            a = m.get("allocation")
            if a is not None and not (0 <= a <= 1):
                errs.append(f"team[{i}].allocation={a} ngoài [0,1]")
    s = ctx.get("settings", {})
    wd = s.get("working_days_per_week")
    if wd is not None and not (1 <= wd <= 7):
        errs.append(f"settings.working_days_per_week={wd} ngoài [1,7]")
    # jsonschema nếu có (kiểm tra sâu hơn)
    try:
        import jsonschema  # optional
        schema = json.loads((Path(__file__).parent.parent / "assets" / "context-schema.json").read_text(encoding="utf-8"))
        for e in jsonschema.Draft7Validator(schema).iter_errors(ctx):
            errs.append(f"[schema] {'.'.join(map(str,e.path)) or '(root)'}: {e.message}")
    except ImportError:
        pass
    except Exception:
        pass
    return errs

if __name__ == "__main__":
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("project-context.json")
    if not p.exists():
        print(f"❌ không tìm thấy {p}"); sys.exit(1)
    try:
        ctx = json.loads(p.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        print(f"❌ JSON lỗi cú pháp: {e}"); sys.exit(1)
    errs = validate_context(ctx)
    if errs:
        print(f"❌ context KHÔNG hợp lệ ({len(errs)} lỗi):")
        for e in errs: print("   -", e)
        sys.exit(1)
    print(f"✅ context hợp lệ: {ctx['project']['name']}")
