#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""smoke_test_runner.py — smoke test sau deploy, chạy chéo nền tảng (Windows/macOS/Linux), chỉ thư viện chuẩn.

Usage:
    python smoke_test_runner.py smoke.json [--format md|json] [--timeout 10] [--lang auto|vi|ja|en] [--context project-context.json]

Input JSON (xem assets/smoke.example.json):
  {
    "base_url": "https://staging-api.example.com",            // hoặc để trống và đặt url tuyệt đối từng check
    "checks": [
      { "id": "SMK-01", "name": "Health", "method": "GET", "path": "/health",
        "expect_status": 200, "max_latency_ms": 500,
        "expect_json_path": {"status": "ok"},                  // tùy chọn: data["status"] == "ok"
        "expect_body_contains": "ok",                          // tùy chọn
        "headers": {"Authorization": "Bearer ${SMOKE_TOKEN}"}, // đọc từ biến môi trường, KHÔNG ghi token vào file
        "body": null }
    ]
  }

Quy tắc:
  * Mỗi check PASS khi: mã HTTP đúng expect_status · latency ≤ max_latency_ms (mặc định 500 ms, lấy từ NFR dự án)
    · expect_json_path/expect_body_contains khớp (nếu khai báo).
  * Token/secret: chuỗi dạng ${TEN_BIEN} được thay bằng biến môi trường; thiếu biến → check FAIL với lý do rõ (không gửi request).
  * Kết quả: bảng PASS/FAIL, tổng hợp và Go/No-Go (GO khi 100% PASS).
Exit: 0 = GO (tất cả PASS) · 1 = NO-GO (có FAIL) · 2 = đầu vào sai.
Chỉ dùng thư viện chuẩn; không dùng jq/curl để chạy được cả trên Windows.
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "a1-project-init" / "scripts"))
from i18n import add_lang_args, pick, resolve_lang  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

MESSAGES = {
    "vi": {
        "notobj": "body không phải JSON object", "nokey": "thiếu khóa '{k}'", "keyval": "'{k}' = {got!r}, kỳ vọng {exp!r}",
        "env": "thiếu biến môi trường {v}", "env_h": "thiếu biến môi trường {v} (header {k})", "conn": "lỗi kết nối: {e}",
        "http": "HTTP {got}, kỳ vọng {exp}", "lat": "latency {got} ms > {max} ms", "nobody": "body không chứa '{x}'",
        "title": "Smoke test", "h_id": "ID", "h_check": "Kiểm tra", "h_result": "Kết quả", "h_reason": "Lý do",
        "e_input": "không đọc được input: {e}", "e_nochecks": "không có check nào",
        "e_nobase": "thiếu base_url (hoặc url tuyệt đối ở từng check)",
    },
    "ja": {
        "notobj": "本文が JSON オブジェクトではありません", "nokey": "キー '{k}' がありません", "keyval": "'{k}' = {got!r}（期待値 {exp!r}）",
        "env": "環境変数 {v} が未設定です", "env_h": "環境変数 {v} が未設定です（ヘッダー {k}）", "conn": "接続エラー: {e}",
        "http": "HTTP {got}（期待 {exp}）", "lat": "レイテンシ {got} ms > {max} ms", "nobody": "本文に '{x}' が含まれていません",
        "title": "スモークテスト", "h_id": "ID", "h_check": "確認項目", "h_result": "結果", "h_reason": "理由",
        "e_input": "入力を読み込めません: {e}", "e_nochecks": "チェック項目がありません",
        "e_nobase": "base_url（または各チェックの絶対 URL）が必要です",
    },
    "en": {
        "notobj": "body is not a JSON object", "nokey": "missing key '{k}'", "keyval": "'{k}' = {got!r}, expected {exp!r}",
        "env": "environment variable {v} is not set", "env_h": "environment variable {v} is not set (header {k})", "conn": "connection error: {e}",
        "http": "HTTP {got}, expected {exp}", "lat": "latency {got} ms > {max} ms", "nobody": "body does not contain '{x}'",
        "title": "Smoke test", "h_id": "ID", "h_check": "Check", "h_result": "Result", "h_reason": "Reason",
        "e_input": "cannot read input: {e}", "e_nochecks": "no checks defined",
        "e_nobase": "base_url is missing (or give an absolute url on every check)",
    },
}

ENV_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


def expand_env(value: str):
    """Trả (giá_trị, tên_biến_thiếu|None)."""
    missing = []

    def rep(m):
        v = os.environ.get(m.group(1))
        if v is None:
            missing.append(m.group(1))
            return m.group(0)
        return v

    out = ENV_RE.sub(rep, value)
    return out, (missing[0] if missing else None)


def json_path_ok(data, expected: dict, M: dict) -> str | None:
    """Kiểm tra các khóa cấp 1 (đủ cho smoke test). Trả None nếu OK, nếu không trả lý do."""
    if not isinstance(data, dict):
        return M["notobj"]
    for k, v in expected.items():
        if k not in data:
            return M["nokey"].format(k=k)
        if data[k] != v:
            return M["keyval"].format(k=k, got=data[k], exp=v)
    return None


def run_check(chk: dict, base: str, timeout: float, M: dict) -> dict:
    cid = chk.get("id", "?")
    name = chk.get("name", "")
    url_path = chk.get("url") or (base.rstrip("/") + "/" + str(chk.get("path", "")).lstrip("/"))
    url, miss = expand_env(url_path)
    if miss:
        return {"id": cid, "name": name, "result": "FAIL", "status": None, "latency_ms": None,
                "reason": M["env"].format(v=miss)}
    headers = {}
    for k, v in (chk.get("headers") or {}).items():
        val, miss = expand_env(str(v))
        if miss:
            return {"id": cid, "name": name, "result": "FAIL", "status": None, "latency_ms": None,
                    "reason": M["env_h"].format(v=miss, k=k)}
        headers[k] = val
    body = None
    if chk.get("body") is not None:
        body = json.dumps(chk["body"]).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")

    req = urllib.request.Request(url, data=body, method=str(chk.get("method", "GET")).upper(), headers=headers)
    t0 = time.perf_counter()
    status, text = None, ""
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            text = resp.read(1_000_000).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        status = e.code
        try:
            text = e.read(1_000_000).decode("utf-8", errors="replace")
        except OSError:
            text = ""
    except (urllib.error.URLError, OSError, TimeoutError) as e:
        return {"id": cid, "name": name, "result": "FAIL", "status": None, "latency_ms": None,
                "reason": M["conn"].format(e=getattr(e, "reason", e))}
    latency = round((time.perf_counter() - t0) * 1000, 1)

    reasons = []
    exp_status = int(chk.get("expect_status", 200))
    if status != exp_status:
        reasons.append(M["http"].format(got=status, exp=exp_status))
    max_lat = float(chk.get("max_latency_ms", 500))
    if latency > max_lat:
        reasons.append(M["lat"].format(got=latency, max=max_lat))
    if chk.get("expect_json_path"):
        try:
            data = json.loads(text) if text else None
        except json.JSONDecodeError:
            data = None
        why = json_path_ok(data, chk["expect_json_path"], M)
        if why:
            reasons.append(why)
    if chk.get("expect_body_contains") and str(chk["expect_body_contains"]) not in text:
        reasons.append(M["nobody"].format(x=chk["expect_body_contains"]))
    return {"id": cid, "name": name, "result": "PASS" if not reasons else "FAIL",
            "status": status, "latency_ms": latency, "reason": "; ".join(reasons)}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Smoke test sau deploy, Go/No-Go (c8)")
    ap.add_argument("input")
    ap.add_argument("--format", choices=("md", "json"), default="md")
    ap.add_argument("--timeout", type=float, default=10.0)
    add_lang_args(ap, audience="client_facing")  # kết quả smoke đi vào Release Plan gửi khách
    a = ap.parse_args(argv)
    lang = resolve_lang(a.lang, a.context, a.audience)
    M = pick(MESSAGES, lang)
    try:
        spec = json.loads(Path(a.input).read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as e:
        print("ERROR " + M["e_input"].format(e=e), file=sys.stderr)
        return 2
    checks = spec.get("checks") or []
    if not checks:
        print("ERROR " + M["e_nochecks"], file=sys.stderr)
        return 2
    base = spec.get("base_url", "")
    if not base and not all(c.get("url") for c in checks):
        print("ERROR " + M["e_nobase"], file=sys.stderr)
        return 2

    results = [run_check(c, base, a.timeout, M) for c in checks]
    passed = sum(1 for r in results if r["result"] == "PASS")
    go = passed == len(results)
    verdict = "GO" if go else "NO-GO"

    if a.format == "json":
        print(json.dumps({"verdict": verdict, "passed": passed, "total": len(results), "lang": lang, "results": results},
                         ensure_ascii=False, indent=2))
    else:
        print(f"## {M['title']} — {verdict} ({passed}/{len(results)} PASS)\n")
        print(f"| {M['h_id']} | {M['h_check']} | {M['h_result']} | HTTP | Latency (ms) | {M['h_reason']} |")
        print("|---|---|---|---|---|---|")
        for r in results:
            print(f"| {r['id']} | {r['name']} | {r['result']} | {r['status'] or '-'} | {r['latency_ms'] or '-'} | {r['reason']} |")
    return 0 if go else 1


if __name__ == "__main__":
    sys.exit(main())
