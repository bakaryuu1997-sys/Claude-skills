#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_postman.py — sinh Postman Collection v2.1 TỪ api_spec.json (v3.4.0).
Dẫn xuất thuần túy — KHÔNG bao giờ viết JSON collection bằng tay; sửa spec rồi chạy lại.

Usage: python3 gen_postman.py <api_spec.json> <output_collection.json>
Format api_spec.json: xem api-design/references/api-spec-format.md
Tự verify: parse lại output + đếm folder/request."""
import json, sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def _url(path, query=None):
    path = path.lstrip("/")
    u = {"raw": "{{baseUrl}}/" + path, "host": ["{{baseUrl}}"], "path": path.split("/")}
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


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    spec = json.loads(open(sys.argv[1], encoding="utf-8-sig").read())
    out = sys.argv[2]
    with open(out, "w", encoding="utf-8") as f:
        json.dump(build(spec), f, ensure_ascii=False, indent=2)
    chk = json.loads(open(out, encoding="utf-8").read())  # verify
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
