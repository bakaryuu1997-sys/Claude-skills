#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""parse_npm_audit.py — bóc `npm audit --json` thành bảng triage cho Security_Audit_Report (c4).

Usage:
    npm audit --json > audit.json
    python parse_npm_audit.py audit.json [--package-json package.json] [--format md|json] [--fail-on critical|high|medium|low]

* Hỗ trợ định dạng npm v7+ (`vulnerabilities`) và npm v6 (`advisories`).
* Severity npm được ánh xạ về thang chuẩn của pipeline: critical→Critical, high→High, moderate→Medium, low/info→Low.
* Scope prod/dev: khi có --package-json, gói trực tiếp được phân loại theo dependencies / devDependencies;
  gói gián tiếp (transitive) ghi "transitive" (cần `npm ls <pkg>` để biết chuỗi) — script KHÔNG đoán.
* Reachability (Unreachable / Mitigated / Action Required) KHÔNG tự suy ra được: cột luôn là "Cần triage" —
  người kiểm toán đọc mã nguồn xác định app có gọi hàm/module bị lỗi hay không rồi điền vào báo cáo.
Exit: 0 bình thường · 1 khi có finding >= --fail-on (nếu đặt) · 2 khi file đầu vào không đọc/không nhận diện được.
Chỉ dùng thư viện chuẩn.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "a1-project-init" / "scripts"))
from i18n import add_lang_args, pick, resolve_lang  # noqa: E402

MESSAGES = {
    "vi": {"triage": "Cần triage", "via": "(qua gói khác)", "fix_yes": "có (npm audit fix)", "fix_no": "chưa có bản vá",
           "dep_on": "phụ thuộc vào gói có lỗ hổng: ", "unknown": "không rõ", "total": "Tổng", "type": "Loại",
           "direct": "direct", "transitive": "transitive", "e_read": "không đọc được {p}: {e}", "e_fmt": "định dạng không nhận diện (cần npm audit --json v6 hoặc v7+)",
           "w_pkg": "không đọc được package.json: {e}"},
    "ja": {"triage": "要トリアージ", "via": "（他パッケージ経由）", "fix_yes": "あり（npm audit fix）", "fix_no": "修正版なし",
           "dep_on": "脆弱性のあるパッケージに依存: ", "unknown": "不明", "total": "合計", "type": "種別",
           "direct": "direct", "transitive": "transitive", "e_read": "{p} を読み込めません: {e}", "e_fmt": "形式を認識できません（npm audit --json の v6 または v7 以降が必要）",
           "w_pkg": "package.json を読み込めません: {e}"},
    "en": {"triage": "Needs triage", "via": "(via another package)", "fix_yes": "yes (npm audit fix)", "fix_no": "no fix available",
           "dep_on": "depends on a vulnerable package: ", "unknown": "unknown", "total": "Total", "type": "Type",
           "direct": "direct", "transitive": "transitive", "e_read": "cannot read {p}: {e}", "e_fmt": "unrecognised format (need npm audit --json v6 or v7+)",
           "w_pkg": "cannot read package.json: {e}"},
}
M = pick(MESSAGES, "vi")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

SEV_MAP = {"critical": "Critical", "high": "High", "moderate": "Medium", "medium": "Medium", "low": "Low", "info": "Low"}
SEV_RANK = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}


def adv_id(url: str) -> str:
    """Lấy GHSA-xxxx từ URL advisory nếu có."""
    if url and "GHSA-" in url:
        return "GHSA-" + url.split("GHSA-", 1)[1].split("/")[0].split("?")[0]
    return url or ""


def from_v7(data: dict, dev: set, prod: set):
    rows = []
    for name, v in (data.get("vulnerabilities") or {}).items():
        direct = bool(v.get("isDirect"))
        fix = v.get("fixAvailable")
        if isinstance(fix, dict):
            patched = f"{fix.get('name')}@{fix.get('version')}" + (" (breaking)" if fix.get("isSemVerMajor") else "")
        else:
            patched = M["fix_yes"] if fix else M["fix_no"]
        advisories = [x for x in (v.get("via") or []) if isinstance(x, dict)]
        scope = ("prod" if name in prod else "dev" if name in dev else M["unknown"]) if direct else "transitive"
        if not advisories:   # chỉ là chuỗi phụ thuộc vào gói khác
            rows.append({"advisory": M["via"], "cve": "", "severity": SEV_MAP.get(v.get("severity", ""), "Low"),
                         "package": name, "vulnerable": v.get("range", ""), "patched_in": patched,
                         "type": "direct" if direct else "transitive", "scope": scope, "title": M["dep_on"] + ", ".join(str(x) for x in v.get("via", []))[:120],
                         "reachability": M["triage"]})
            continue
        for a in advisories:
            rows.append({"advisory": adv_id(a.get("url", "")) or str(a.get("source", "")),
                         "cve": ", ".join(a.get("cwe", []) or []),
                         "severity": SEV_MAP.get(a.get("severity", v.get("severity", "")), "Low"),
                         "package": a.get("name", name), "vulnerable": a.get("range", v.get("range", "")),
                         "patched_in": patched, "type": "direct" if direct else "transitive", "scope": scope,
                         "title": a.get("title", ""), "reachability": M["triage"]})
    return rows


def from_v6(data: dict, dev: set, prod: set):
    rows = []
    for aid, a in (data.get("advisories") or {}).items():
        name = a.get("module_name", "")
        paths = [p for f in a.get("findings", []) for p in f.get("paths", [])]
        direct = any(p == name for p in paths)
        rows.append({"advisory": str(a.get("id", aid)), "cve": ", ".join(a.get("cves", []) or []),
                     "severity": SEV_MAP.get(a.get("severity", ""), "Low"), "package": name,
                     "vulnerable": a.get("vulnerable_versions", ""), "patched_in": a.get("patched_versions", ""),
                     "type": "direct" if direct else "transitive",
                     "scope": ("prod" if name in prod else "dev" if name in dev else M["unknown"]) if direct else "transitive",
                     "title": a.get("title", ""), "reachability": M["triage"]})
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description="Parse npm audit --json thành bảng triage (c4)")
    ap.add_argument("audit_json")
    ap.add_argument("--package-json")
    ap.add_argument("--format", choices=("md", "json"), default="md")
    # "moderate" là nhãn của npm → đồng nghĩa với medium của thang chuẩn.
    ap.add_argument("--fail-on", choices=("critical", "high", "medium", "moderate", "low"))
    add_lang_args(ap, audience="internal")  # bảng triage vào báo cáo security audit (nội bộ)
    a = ap.parse_args(argv)
    global M
    M = pick(MESSAGES, resolve_lang(a.lang, a.context, a.audience))

    try:
        data = json.loads(Path(a.audit_json).read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as e:
        print("ERROR " + M["e_read"].format(p=a.audit_json, e=e), file=sys.stderr)
        return 2

    dev, prod = set(), set()
    if a.package_json:
        try:
            pkg = json.loads(Path(a.package_json).read_text(encoding="utf-8-sig"))
            prod = set((pkg.get("dependencies") or {}).keys())
            dev = set((pkg.get("devDependencies") or {}).keys())
        except (OSError, json.JSONDecodeError) as e:
            print("WARN " + M["w_pkg"].format(e=e), file=sys.stderr)

    if "vulnerabilities" in data:
        rows = from_v7(data, dev, prod)
    elif "advisories" in data:
        rows = from_v6(data, dev, prod)
    else:
        print("ERROR " + M["e_fmt"], file=sys.stderr)
        return 2

    rows.sort(key=lambda r: (-SEV_RANK[r["severity"]], r["package"]))
    counts = {s: sum(1 for r in rows if r["severity"] == s) for s in ("Critical", "High", "Medium", "Low")}

    if a.format == "json":
        print(json.dumps({"counts": counts, "rows": rows}, ensure_ascii=False, indent=2))
    else:
        print(f"{M['total']}: {len(rows)} | Critical {counts['Critical']} · High {counts['High']} · Medium {counts['Medium']} · Low {counts['Low']}\n")
        print(f"| Advisory | CWE/CVE | Severity | Package | Vulnerable | Patched in | {M['type']} | Scope | Reachability |")
        print("|---|---|---|---|---|---|---|---|---|")
        for r in rows:
            print(f"| {r['advisory']} | {r['cve']} | {r['severity']} | {r['package']} | {r['vulnerable']} | "
                  f"{r['patched_in']} | {r['type']} | {r['scope']} | {r['reachability']} |")

    if a.fail_on:
        thr = SEV_RANK[SEV_MAP[a.fail_on]]
        if any(SEV_RANK[r["severity"]] >= thr for r in rows):
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
