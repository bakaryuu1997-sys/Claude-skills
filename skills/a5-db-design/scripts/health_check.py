#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""health_check.py — chấm Health Check W01–W10 + điểm Schema Health cho a5-db-design.

Usage:
    python health_check.py <schema_model.json> [--json <out.json>]

schema_model.json (do assistant dựng từ thiết kế — cùng dữ liệu dùng để sinh Excel/SQL):
{
  "tables": [
    {
      "name": "orders",
      "classification": "Core",            // Core | Lookup | Junction | Log
      "soft_delete": true,                 // tùy chọn: false = đã quyết định hard delete (W06 PASS)
      "est_rows": 2000000,                 // tùy chọn (W10)
      "partition_plan": false,             // tùy chọn (W10)
      "primary_key": ["id"],
      "unique": [["order_no"], ["user_id", "slot_id"]],
      "columns": [
        {"name": "id", "type": "BIGINT"},
        {"name": "user_id", "type": "BIGINT", "fk": "users.id"},
        {"name": "status", "type": "VARCHAR(50)", "check": true},
        {"name": "created_at", "type": "TIMESTAMPTZ"}
      ],
      "indexes": [{"name": "idx_orders_user_id", "columns": ["user_id"], "unique": false}]
    }
  ]
}

Điểm (công bằng, tái lập được):
  - Mỗi rule: PASS = 1, WARN = 0.5, FAIL = 0, N/A bị loại khỏi mẫu số.
  - Điểm bảng (x/10) = round(tổng điểm / số rule áp dụng * 10, 1).
  - Schema Health Score (x/100) = trung bình tỷ lệ của các bảng * 100, làm tròn 1 chữ số.
Mã thoát: 0 = không có FAIL; 1 = có FAIL; 2 = input sai.
"""
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "a1-project-init" / "scripts"))
from i18n import lang_from_argv, pick  # noqa: E402

MESSAGES = {
    "vi": {"cols": "%d cột (>20)", "fk_noidx": "FK chưa có index: ", "lack": "thiếu ", "nolen": "không giới hạn độ dài: ", "float": "FLOAT cho tiền: ",
           "softdel": "bảng Core chưa có deleted_at và chưa ghi quyết định hard delete", "junction": "thiếu UNIQUE/PK tổng hợp trên các cột FK",
           "nocheck": "chưa có CHECK/lookup: ", "noindex": "chưa có index: ", "partition": "~%s dòng, chưa có kế hoạch partition",
           "bad": "LỖI: schema_model.json không hợp lệ (%s). Cần {\"tables\": [...]}", "tbl": "Bảng",
           "score": "Schema Health Score: %s/100 | FAIL: %d | WARN: %d | sạch nhất: %s | cần chú ý nhất: %s"},
    "ja": {"cols": "%d 列（20 超）", "fk_noidx": "FK にインデックスがありません: ", "lack": "不足: ", "nolen": "長さ制限なし: ", "float": "金額に FLOAT を使用: ",
           "softdel": "Core テーブルに deleted_at がなく、物理削除の決定も記録されていません", "junction": "FK 列に複合 UNIQUE/PK がありません",
           "nocheck": "CHECK/参照テーブルがありません: ", "noindex": "インデックスがありません: ", "partition": "約 %s 行、パーティション計画がありません",
           "bad": "エラー: schema_model.json が不正です（%s）。{\"tables\": [...]} が必要です", "tbl": "テーブル",
           "score": "スキーマヘルススコア: %s/100 | FAIL: %d | WARN: %d | 最良: %s | 要注意: %s"},
    "en": {"cols": "%d columns (>20)", "fk_noidx": "FK without index: ", "lack": "missing ", "nolen": "no length limit: ", "float": "FLOAT used for money: ",
           "softdel": "Core table has no deleted_at and no recorded hard-delete decision", "junction": "missing composite UNIQUE/PK on the FK columns",
           "nocheck": "no CHECK/lookup: ", "noindex": "no index: ", "partition": "~%s rows, no partition plan",
           "bad": "ERROR: invalid schema_model.json (%s). Expected {\"tables\": [...]}", "tbl": "Table",
           "score": "Schema Health Score: %s/100 | FAIL: %d | WARN: %d | best: %s | needs attention: %s"},
}
HM = pick(MESSAGES, "vi")

RULES = ["W01", "W02", "W03", "W04", "W05", "W06", "W07", "W08", "W09", "W10"]
MONEY_RE = re.compile(r"(price|amount|total|fee|cost|balance|tax|money|salary|fare|charge)", re.I)
SHORT_TEXT_RE = re.compile(r"(^|_)(name|title|email|code|slug|username|phone|sku|no)($|_)", re.I)
STATUS_RE = re.compile(r"(^|_)(status|state|type|role|kind)($|_)", re.I)
SORT_COLS = ("created_at", "updated_at", "sort_order")


def base_type(t):
    return re.sub(r"\(.*\)", "", str(t or "")).strip().upper()


def index_leads(table, col):
    """Cột là cột ĐẦU của PK / UNIQUE / index nào đó."""
    for pk in [table.get("primary_key") or []]:
        if pk and pk[0] == col:
            return True
    for u in table.get("unique") or []:
        if u and u[0] == col:
            return True
    for ix in table.get("indexes") or []:
        cols = ix.get("columns") or []
        if cols and cols[0] == col:
            return True
    return False


def index_has(table, col):
    for grp in [table.get("primary_key") or []] + list(table.get("unique") or []) + \
            [ix.get("columns") or [] for ix in table.get("indexes") or []]:
        if col in grp:
            return True
    return False


def evaluate(t):
    cols = t.get("columns") or []
    names = [c.get("name") for c in cols]
    cls = str(t.get("classification", "Core")).title()
    fkcols = [c for c in cols if c.get("fk")]
    res = {}

    res["W01"] = ("WARN", HM["cols"] % len(cols)) if len(cols) > 20 else ("PASS", "")

    miss = [c["name"] for c in fkcols if not index_leads(t, c["name"])]
    res["W02"] = ("FAIL", HM["fk_noidx"] + ", ".join(miss)) if miss else \
        ("PASS", "") if fkcols else ("N/A", "")

    lack = [n for n in ("created_at", "updated_at") if n not in names]
    res["W03"] = ("FAIL", HM["lack"] + ", ".join(lack)) if lack else ("PASS", "")

    bad = [c["name"] for c in cols
           if (base_type(c.get("type")) == "VARCHAR" and "(" not in str(c.get("type")))
           or (base_type(c.get("type")) == "TEXT" and SHORT_TEXT_RE.search(c.get("name", "")))]
    res["W04"] = ("WARN", HM["nolen"] + ", ".join(bad)) if bad else ("PASS", "")

    fl = [c["name"] for c in cols
          if base_type(c.get("type")) in ("FLOAT", "REAL", "DOUBLE", "DOUBLE PRECISION")
          and MONEY_RE.search(c.get("name", ""))]
    res["W05"] = ("FAIL", HM["float"] + ", ".join(fl)) if fl else ("PASS", "")

    if cls != "Core":
        res["W06"] = ("N/A", "")
    elif "deleted_at" in names or t.get("soft_delete") is False:
        res["W06"] = ("PASS", "")
    else:
        res["W06"] = ("WARN", HM["softdel"])

    if cls != "Junction":
        res["W07"] = ("N/A", "")
    else:
        fk_names = {c["name"] for c in fkcols}
        pk = set(t.get("primary_key") or [])
        ok = (len(fk_names) >= 2 and fk_names <= pk) or any(set(u) >= fk_names and len(fk_names) >= 2
                                                            for u in t.get("unique") or [])
        res["W07"] = ("PASS", "") if ok else ("FAIL", HM["junction"])

    st = [c["name"] for c in cols if STATUS_RE.search(c.get("name", ""))
          and base_type(c.get("type")) in ("VARCHAR", "TEXT", "CHAR") and not c.get("check") and not c.get("fk")]
    # cột có fk trỏ tới bảng lookup (ví dụ leave_types.code) đã là ràng buộc miền → không cảnh báo W08
    res["W08"] = ("WARN", HM["nocheck"] + ", ".join(st)) if st else ("PASS", "")

    sc = [n for n in SORT_COLS if n in names and not index_has(t, n)]
    res["W09"] = ("WARN", HM["noindex"] + ", ".join(sc)) if sc else ("PASS", "")

    est = t.get("est_rows")
    if est is None:
        res["W10"] = ("N/A", "")
    elif est > 10_000_000 and not t.get("partition_plan"):
        res["W10"] = ("WARN", HM["partition"] % format(int(est), ","))
    else:
        res["W10"] = ("PASS", "")
    return res


SCORE = {"PASS": 1.0, "WARN": 0.5, "FAIL": 0.0}


def main(argv):
    global HM
    _lang, _rest = lang_from_argv(argv[1:], audience="internal")
    argv = [argv[0]] + _rest
    HM = pick(MESSAGES, _lang)
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args or "--help" in argv or "-h" in argv:
        print(__doc__)
        return 2
    out_json = None
    if "--json" in argv:
        i = argv.index("--json")
        out_json = argv[i + 1] if i + 1 < len(argv) else None
        args = [a for a in args if a != out_json]
    try:
        model = json.loads(Path(args[0]).read_text(encoding="utf-8-sig"))
        tables = model["tables"]
        assert isinstance(tables, list) and tables
    except (OSError, ValueError, KeyError, AssertionError) as e:
        print(HM["bad"] % e)
        return 2

    rows, n_fail, n_warn, ratios = [], 0, 0, []
    for t in tables:
        res = evaluate(t)
        applic = [v for v in res.values() if v[0] != "N/A"]
        pts = sum(SCORE[v[0]] for v in applic)
        ratio = pts / len(applic) if applic else 1.0
        ratios.append(ratio)
        n_fail += sum(1 for v in applic if v[0] == "FAIL")
        n_warn += sum(1 for v in applic if v[0] == "WARN")
        rows.append({"table": t.get("name"), "results": {k: {"status": res[k][0], "detail": res[k][1]} for k in RULES},
                     "score10": round(ratio * 10, 1)})
    total = round(sum(ratios) / len(ratios) * 100, 1)
    best = max(rows, key=lambda r: r["score10"])["table"]
    worst = min(rows, key=lambda r: r["score10"])["table"]

    sym = {"PASS": "OK ", "WARN": "WRN", "FAIL": "ERR", "N/A": " - "}
    print("%-24s %s  Score" % (HM["tbl"], " ".join(RULES)))
    for r in rows:
        print("%-24s %s  %s/10" % (r["table"], " ".join(sym[r["results"][k]["status"]] for k in RULES), r["score10"]))
    print("\n" + HM["score"] % (total, n_fail, n_warn, best, worst))
    actions = []
    for r in rows:
        for k in RULES:
            v = r["results"][k]
            if v["status"] in ("FAIL", "WARN"):
                actions.append({"priority": "CRITICAL" if v["status"] == "FAIL" else "WARN",
                                "table": r["table"], "rule": k, "issue": v["detail"]})
    actions.sort(key=lambda a: 0 if a["priority"] == "CRITICAL" else 1)
    for a in actions:
        print("  [%s] %s %s: %s" % (a["priority"], a["table"], a["rule"], a["issue"]))
    if out_json:
        Path(out_json).write_text(json.dumps({"score": total, "fail": n_fail, "warn": n_warn, "tables": rows,
                                              "actions": actions}, ensure_ascii=False, indent=2), encoding="utf-8")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
