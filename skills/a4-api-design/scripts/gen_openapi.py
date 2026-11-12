#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_openapi.py — sinh OpenAPI 3.0.3 YAML TỪ api_spec.json (v3.4.0).
Dẫn xuất thuần túy — KHÔNG bao giờ viết YAML bằng tay; sửa spec rồi chạy lại.

Usage: python gen_openapi.py <api_spec.json> <output_openapi.yaml>
Thiếu pyyaml → fallback ghi JSON (JSON là YAML hợp lệ) + cảnh báo.
Tự verify: parse lại output + đếm path."""
import json, re, sys
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def infer_schema(v):
    if isinstance(v, bool):
        return {"type": "boolean", "example": v}
    if isinstance(v, int):
        return {"type": "integer", "example": v}
    if isinstance(v, float):
        return {"type": "number", "example": v}
    if isinstance(v, str):
        return {"type": "string", "example": v}
    if isinstance(v, list):
        return {"type": "array", "items": infer_schema(v[0]) if v else {}}
    if isinstance(v, dict):
        return {"type": "object", "properties": {k: infer_schema(x) for k, x in v.items()}}
    return {}


def build(spec: dict) -> dict:
    doc = {
        "openapi": "3.0.3",
        "info": {"title": f"{spec.get('project', 'API')} API",
                 "version": spec.get("version", "1.0.0"),
                 "description": "Sinh tự động từ api_spec.json (gen_openapi.py) — sửa spec, không sửa file này"},
        "servers": spec.get("servers") or [{"url": spec.get("base_url", "http://localhost:3000/api/v1"),
                                            "description": "Default"}],
        "security": [{"BearerAuth": []}],
        "components": {
            "securitySchemes": {"BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}},
            "schemas": {"Error": {"type": "object", "properties": {"error": {"type": "object", "properties": {
                "code": {"type": "string", "example": "USER_NOT_FOUND"},
                "message": {"type": "string", "example": "User with id 123 not found"}}}}}}},
        "paths": {},
    }
    for mod in spec.get("modules", []):
        for ep in mod.get("endpoints", []):
            path, method = ep["path"], ep["method"].lower()
            op = {"tags": [mod["name"]], "summary": ep.get("summary", ""), "responses": {}}
            if not ep.get("auth_required"):
                op["security"] = []
            params = [{"name": m, "in": "path", "required": True, "schema": {"type": "string"}}
                      for m in re.findall(r"\{(\w+)\}", path)]
            for q in ep.get("query") or []:
                params.append({"name": q["name"], "in": "query", "required": bool(q.get("required")),
                               "schema": {"type": q.get("type", "string")}})
            if params:
                op["parameters"] = params
            if ep.get("body_example") is not None and method in ("post", "put", "patch", "delete"):
                op["requestBody"] = {"required": True, "content": {"application/json": {
                    "schema": ep.get("body_schema") or infer_schema(ep["body_example"])}}}
            ok = str(ep.get("success_status", 200))
            resp = {"description": CL["ok_resp"]}
            if ep.get("response_example") is not None:
                resp["content"] = {"application/json": {"schema": infer_schema(ep["response_example"])}}
            op["responses"][ok] = resp
            for e in ep.get("errors") or []:
                op["responses"].setdefault(str(e.get("status", 400)), {
                    "description": e.get("message", e.get("code", CL["err_resp"])),
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}})
            slot = doc["paths"].setdefault(path, {})
            if method in slot:
                raise ValueError(f"trùng khóa {ep['method']} {path} (module {mod['name']}) — mỗi method+path chỉ khai báo một lần")
            slot[method] = op
    return doc


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "a1-project-init" / "scripts"))
from i18n import common, lang_from_argv, placeholder  # noqa: E402

CL, PH = common("vi"), placeholder("vi")


def main() -> int:
    global CL, PH
    _lang, _args = lang_from_argv(sys.argv[1:])
    sys.argv = [sys.argv[0]] + _args
    CL, PH = common(_lang), placeholder(_lang)
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    try:
        spec = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        print(f"❌ không thấy file spec: {sys.argv[1]}")
        return 2
    except (OSError, ValueError) as e:
        print(f"❌ api_spec.json không đọc được: {e}")
        return 2
    try:
        doc = build(spec)
    except (ValueError, KeyError) as e:
        print(f"❌ api_spec.json sai cấu trúc: {e}")
        return 1
    out = sys.argv[2]
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    try:
        import yaml
        with open(out, "w", encoding="utf-8") as f:
            yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False)
        parsed = yaml.safe_load(open(out, encoding="utf-8"))  # verify
        mode = "YAML"
    except ImportError:
        with open(out, "w", encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False, indent=2)
        parsed = json.loads(open(out, encoding="utf-8").read())
        mode = "JSON-as-YAML (thiếu pyyaml — `python -m pip install pyyaml` để có YAML thuần)"
    if len(parsed.get("paths", {})) != len(doc["paths"]):
        print("❌ verify FAIL: paths không khớp sau khi parse lại")
        return 1
    print(f"✅ {out}: {len(doc['paths'])} path ({mode}, verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
