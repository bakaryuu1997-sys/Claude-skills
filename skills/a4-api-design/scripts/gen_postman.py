#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_postman.py — sinh Postman Collection v2.1 TỪ api_spec.json (v3.4.0).
Dẫn xuất thuần túy — KHÔNG bao giờ viết JSON collection bằng tay; sửa spec rồi chạy lại.

Usage: python gen_postman.py <api_spec.json> <output_collection.json>
Format api_spec.json: xem a4-api-design/references/api-spec-format.md
Tự verify: parse lại output + đếm folder/request."""
import json
import re
import sys
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def _pm_path(path):
    # Postman dùng ':param' cho path variable; '{param}' (chuẩn OpenAPI) sẽ bị gửi nguyên văn.
    return re.sub(r"\{(\w+)\}", r":\1", path.lstrip("/"))


def _url(path, query=None):
    p = _pm_path(path)
    u = {"raw": "{{baseUrl}}/" + p, "host": ["{{baseUrl}}"], "path": p.split("/")}
    path_vars = re.findall(r"\{(\w+)\}", path)
    if path_vars:
        # giá trị thật do người dùng điền trong Postman; không bịa id mẫu
        u["variable"] = [{"key": v, "value": "", "description": PH} for v in path_vars]
    if query:
        u["query"] = [{"key": q["name"], "value": str(q.get("example", ""))} for q in query]
        u["raw"] += "?" + "&".join(f'{q["name"]}={q.get("example", "")}' for q in query)
    return u


def build(spec: dict) -> dict:
    name = spec.get("project", "API")
    auth = spec.get("auth") or {}
    coll = {
        "info": {"name": f"{name} API",
                 "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"},
        "variable": [{"key": "baseUrl", "value": spec.get("base_url", "http://localhost:3000/api/v1")},
                     {"key": "accessToken", "value": ""}],
        "item": [],
    }
    login_path = auth.get("login_path")
    if login_path:
        tf = auth.get("token_field", "accessToken")
        body = auth.get("login_body_example", {"email": "test@example.com", "password": "test123"})
        coll["item"].append({
            "name": "⚙️ Setup & Auth",
            "item": [{
                "name": "POST Login (get token)",
                "event": [{"listen": "test", "script": {"exec": [
                    "const res = pm.response.json();",
                    f"if (res.{tf}) {{",
                    f"  pm.collectionVariables.set('accessToken', res.{tf});",
                    "  pm.collectionVariables.set('refreshToken', res.refreshToken || '');",
                    "  console.log('✅ Token saved');",
                    "} else {",
                    "  console.error('❌ No token in response:', JSON.stringify(res));",
                    "}"]}}],
                "request": {
                    "method": "POST",
                    "header": [{"key": "Content-Type", "value": "application/json"}],
                    "url": _url(login_path),
                    "body": {"mode": "raw",
                             "raw": json.dumps(body, ensure_ascii=False, indent=2),
                             "options": {"raw": {"language": "json"}}}},
            }]})
    for mod in spec.get("modules", []):
        folder = {"name": mod["name"], "item": []}
        for ep in mod.get("endpoints", []):
            headers = [{"key": "Content-Type", "value": "application/json"}]
            if ep.get("auth_required"):
                headers.append({"key": "Authorization", "value": "Bearer {{accessToken}}"})
            req = {"method": ep["method"].upper(), "header": headers,
                   "url": _url(ep["path"], ep.get("query"))}
            if ep.get("body_example") is not None and ep["method"].upper() in ("POST", "PUT", "PATCH", "DELETE"):
                req["body"] = {"mode": "raw",
                               "raw": json.dumps(ep["body_example"], ensure_ascii=False, indent=2),
                               "options": {"raw": {"language": "json"}}}
            folder["item"].append({"name": f"{ep['method'].upper()} {ep.get('summary', ep['path'])}",
                                   "request": req})
        coll["item"].append(folder)
    return coll


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
    out = sys.argv[2]
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(build(spec), f, ensure_ascii=False, indent=2)
    chk = json.loads(Path(out).read_text(encoding="utf-8"))  # verify
    n_req = sum(len(f.get("item", [])) for f in chk["item"])
    n_ep = sum(len(m.get("endpoints", [])) for m in spec.get("modules", []))
    expected = n_ep + (1 if (spec.get("auth") or {}).get("login_path") else 0)
    if n_req != expected:
        print(f"❌ verify FAIL: {n_req} request != {expected} kỳ vọng")
        return 1
    print(f"✅ {out}: {len(chk['item'])} folder, {n_req} request (verified)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
