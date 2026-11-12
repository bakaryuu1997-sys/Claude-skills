# -*- coding: utf-8 -*-
"""build_all.py — chạy chuỗi A1→D trên dự án mẫu bằng các script THẬT của repo.
Usage: python build_all.py  (output: $E2E_WS/docs, mặc định thư mục tạm)."""
import json, math, shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_sample as S  # noqa: E402
P1, P2, P3 = S.P1, S.P2, S.P3


def _ensure_audit(cols):
    # Mọi bảng đều có created_at / updated_at (health_check W03)
    names = [c[0] for c in cols]
    add = []
    if "created_at" not in names:
        add.append(("created_at", "TIMESTAMPTZ", "NOT NULL", "DEFAULT now()", "作成日時"))
    if "updated_at" not in names:
        add.append(("updated_at", "TIMESTAMPTZ", "NOT NULL", "DEFAULT now()", "更新日時（トリガーで更新）"))
    return cols + add


S.TABLES = [(t, l, _ensure_audit(c)) for t, l, c in S.TABLES]
# Chỉ mục bổ sung: mọi khóa ngoại + truy vấn danh sách (Q-07: sắp theo申請日 giảm dần)
EXTRA_INDEXES = [("leave_requests", ["applicant_id", "created_at"], "idx_leave_requests_applicant_created")]
from xlsx_build import build as xbuild  # noqa: E402

REPO = S.REPO
PY = [sys.executable, "-B"]
WS = S.WS
if WS.exists():
    shutil.rmtree(WS)
WS.mkdir(parents=True)
P = S.PROJ
DOCS = WS / "docs"


def sh(args, check=False):
    r = subprocess.run(PY + args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    out = (r.stdout + r.stderr).strip()
    print(f"$ {Path(args[0]).name} {' '.join(args[1:])[:90]}  → exit {r.returncode}")
    if out:
        for line in out.splitlines()[-12:]:
            print("    " + line)
    if check and r.returncode != 0:
        raise SystemExit(f"FAIL: {args[0]}")
    return r


def save_xlsx(spec, folder, name):
    out = DOCS / folder / name
    out.parent.mkdir(parents=True, exist_ok=True)
    xbuild(spec, out)
    return out


# ================================================================ 0. project-context
(WS / "project-context.json").write_text(json.dumps(S.ctx, ensure_ascii=False, indent=2), encoding="utf-8")
sh([str(REPO / "skills/a1-project-init/scripts/validate_context.py"), str(WS / "project-context.json")], check=True)

# ================================================================ A2 requirement + QA tracker
fs_rows = []
for fid, mod, name, desc in S.FEATS:
    fs_rows.append({"id": fid, "module": mod, "name": name, "desc": desc,
                    "moscow": "Must", "source": "顧客RFP 3.2"})
save_xlsx({
    "title": "Requirement Specification", "language": "ja",
    "sheets": [
        {"name": "機能スコープ", "title": "機能スコープ（Functional Scope）",
         "subtitle": f"{S.ctx['project']['name']} ／ 版 1.0 ／ 作成日 {S.ctx['created_at']}",
         "columns": [{"key": "id", "header": "機能ID", "width": 17},
                     {"key": "module", "header": "モジュール", "width": 12},
                     {"key": "name", "header": "機能名", "width": 26, "wrap": True},
                     {"key": "desc", "header": "概要", "width": 60, "wrap": True},
                     {"key": "moscow", "header": "優先度(MoSCoW)", "width": 14, "align": "center", "validate": ["Must", "Should", "Could", "Won't"]},
                     {"key": "source", "header": "根拠（出典）", "width": 18}],
         "rows": fs_rows},
        {"name": "非機能要件", "title": "非機能要件（NFR・ISO/IEC 25010）",
         "subtitle": "各要件は測定可能（数値・測定方法）で記述。測定方法は8章の試験計画に対応",
         "columns": [{"key": "id", "header": "NFR-ID", "width": 15},
                     {"key": "cat", "header": "特性", "width": 11},
                     {"key": "name", "header": "要件名", "width": 28, "wrap": True},
                     {"key": "target", "header": "目標値（測定可能）", "width": 46, "wrap": True},
                     {"key": "method", "header": "確認方法", "width": 34, "wrap": True},
                     {"key": "prio", "header": "優先度", "width": 10, "align": "center"}],
         "rows": [list(x) for x in S.nfr]},
    ]}, "A2_requirement-analysis", f"{P}_Requirement_Specification_v1.xlsx")

qa_spec = {
    "title": "QA Tracker（Q&A 管理表）", "language": "ja",
    "sheets": [{
        "name": "質問管理", "title": "質問管理表（Q&A Tracker）",
        "subtitle": "優先度 P1: 設計を止める質問（未回答3件超で見積・キックオフを保留） ／ P2: 設計に影響 ／ P3: 仕様の詳細",
        "columns": [{"key": "id", "header": "No.", "width": 9, "align": "center"},
                    {"key": "prio", "header": "優先度", "width": 10, "align": "center", "validate": ["P1", "P2", "P3"]},
                    {"key": "q", "header": "質問", "width": 50, "wrap": True},
                    {"key": "impact", "header": "影響箇所", "width": 32, "wrap": True},
                    {"key": "status", "header": "ステータス", "width": 11, "align": "center", "validate": ["未回答", "回答済"]},
                    {"key": "ans", "header": "回答", "width": 40, "wrap": True},
                    {"key": "owner", "header": "回答者", "width": 16},
                    {"key": "due", "header": "回答期限", "width": 12, "align": "center"}],
        "rows": [],
    }]}
for qid, prio, q, impact, status, ans, owner, due in S.qa_rows:
    style_status = {"status": {"value": status, "fill": "E2EFDA" if status == "Answered" else "FFF2CC", "align": "center"}}
    qa_spec["sheets"][0]["rows"].append({"id": qid, "prio": prio, "q": q, "impact": impact, "status": status, "ans": ans, "owner": owner, "due": due})
save_xlsx(qa_spec, "A2_requirement-analysis", f"{P}_QA_Tracker.xlsx")
sh([str(REPO / "skills/a1-project-init/scripts/check_gate.py"), str(WS)])

# ================================================================ A4 API design
apis_by_mod = {}
for row in S.APIS:
    apis_by_mod.setdefault(row[0], []).append(row)
MOD_NAME = {"AUTH": "認証", "LEAVE": "申請", "APPR": "承認", "REPORT": "帳票"}
api_sheets = [{
    "name": "概要", "title": "API設計書 概要",
    "subtitle": f"Base URL: /api/v1 ／ 認証: JWT Bearer ／ エラー形式: {{\"error\":{{\"code\",\"message\",\"details\"}}}}",
    "columns": [{"key": "k", "header": "項目", "width": 22}, {"key": "v", "header": "内容", "width": 90, "wrap": True}],
    "rows": [
        {"k": "バージョン", "v": "v1.0（初版）"},
        {"k": "成功レスポンス", "v": "{\"data\": <payload>, \"meta\": {...}}（meta は任意）"},
        {"k": "エラーレスポンス", "v": "{\"error\": {\"code\": \"ERR-<DOMAIN>-<NNN>\", \"message\": \"...\", \"details\": [...]}}"},
        {"k": "ページング", "v": "pageSize 既定20・上限100。レスポンスは total を含む"},
        {"k": "認可", "v": "役割 employee / manager / hr。オブジェクトの所有権は全APIで検査（NFR-SEC-02）"},
        {"k": "バージョン方針", "v": "破壊的変更は /v2 で提供。詳細は api-versioning（a4 references）"},
    ]}]
for mod, rows in apis_by_mod.items():
    api_sheets.append({
        "name": f"API {MOD_NAME[mod]}", "title": f"API一覧 — {MOD_NAME[mod]}（{mod}）",
        "subtitle": "Method は色で区別（GET 青 / POST 緑 / PUT 橙 / DELETE 赤）。Auth=Y は必須",
        "columns": [{"key": "no", "header": "No.", "width": 6, "align": "center"},
                    {"key": "method", "header": "メソッド", "width": 9, "align": "center"},
                    {"key": "url", "header": "エンドポイント", "width": 40},
                    {"key": "desc", "header": "説明", "width": 40, "wrap": True},
                    {"key": "auth", "header": "認証", "width": 8, "align": "center"},
                    {"key": "mw", "header": "ミドルウェア", "width": 26, "wrap": True},
                    {"key": "inp", "header": "入力（req）", "width": 46, "wrap": True},
                    {"key": "out", "header": "出力（res.body）", "width": 40, "wrap": True},
                    {"key": "st", "header": "成功", "width": 8, "align": "center"},
                    {"key": "tbl", "header": "DB（読/書）", "width": 30, "wrap": True},
                    {"key": "err", "header": "エラー", "width": 36, "wrap": True},
                    {"key": "tc", "header": "テストケース", "width": 46, "wrap": True},
                    {"key": "since", "header": "導入版", "width": 8, "align": "center"},
                    {"key": "note", "header": "備考", "width": 30, "wrap": True}],
        "rows": [{"no": r[1], "method": {"value": r[2], "bold": True, "font_color": {"GET": "1F4E79", "POST": "375623", "PUT": "C65911"}.get(r[2], "000000")},
                  "url": r[3], "desc": r[4], "auth": {"value": r[5], "align": "center", "font_color": "C00000" if r[5] == "Y" else "375623", "bold": True},
                  "mw": r[6], "inp": r[7], "out": r[8], "st": r[9], "tbl": r[10], "err": r[11], "tc": r[12], "since": r[13], "note": r[14]}
                 for r in rows],
    })
import phase2_ops  # noqa: E402
api_sheets.append(phase2_ops.api_detail_for_build(S.APIS))
save_xlsx({"title": "API Design", "language": "ja", "sheets": api_sheets}, "A4_api-design", f"{P}_API_Design.xlsx")

# api_spec.json (nguồn cho gen_postman / gen_openapi) — path tương đối với base_url
spec_mods = []
for mod, rows in apis_by_mod.items():
    eps = []
    for r in rows:
        path = r[3].replace("/api/v1", "", 1)
        body = None
        if "body:" in r[7]:
            body = {"example": "（シードデータの値）"}
        eps.append({"method": r[2], "path": path, "summary": r[4], "auth_required": r[5] == "Y",
                    "middleware": [m.strip() for m in r[6].split(",")],
                    "query": [], "body_example": {}, "body_schema": None,
                    "success_status": r[9], "response_example": {"data": {}},
                    "errors": [{"status": int(e.split(" ")[0]), "code": e.split(" ")[0], "message": e.split(" ", 1)[1] if " " in e else e} for e in []]})
        if "query:" in r[7]:
            eps[-1]["query"] = [{"name": "page", "type": "integer", "required": False, "example": 1},
                                {"name": "pageSize", "type": "integer", "required": False, "example": 20}]
    spec_mods.append({"name": mod, "endpoints": eps})
api_spec = {"project": S.PROJ, "version": "1.0.0", "base_url": "https://staging.example.com/api/v1",
            "servers": [{"url": "https://staging.example.com/api/v1", "description": "Staging（架空）"}],
            "auth": {"login_path": "/auth/login", "token_field": "accessToken",
                     "login_body_example": {"employeeId": "100001", "password": "（テスト用パスワード）"}},
            "modules": spec_mods}
spec_path = DOCS / "A4_api-design" / f"{P}_api_spec.json"
spec_path.parent.mkdir(parents=True, exist_ok=True)
spec_path.write_text(json.dumps(api_spec, ensure_ascii=False, indent=2), encoding="utf-8")
sh([str(REPO / "skills/a4-api-design/scripts/gen_openapi.py"), str(spec_path), str(spec_path.with_name(f"{P}_openapi.yaml"))])
sh([str(REPO / "skills/a4-api-design/scripts/gen_postman.py"), str(spec_path), str(spec_path.with_name(f"{P}_Postman_Collection.json"))])

# ================================================================ A5 DB design
def col_def(c):
    name, typ, null, cons, desc = c
    parts = [name, typ, null]
    if cons:
        parts.append(cons)
    return " ".join(p for p in parts if p)

def _sql_column(c):
    """c = (name, type, NULL|NOT NULL, constraint-text, desc) → 1 dòng cột SQL hợp lệ (không gồm FK/PK/UNIQUE)."""
    import re as _re
    name, typ, null, cons, _desc = c
    out = f"{name} {typ}"
    if null == "NOT NULL":
        out += " NOT NULL"
    m = _re.search(r"DEFAULT\s+('[^']*'|[A-Za-z_][\w()]*|\d+|TRUE|FALSE)", cons)
    if m:
        out += f" DEFAULT {m.group(1)}"
    i = cons.find("CHECK (")
    if i >= 0:
        depth, j = 0, i + len("CHECK ")
        for k in range(j, len(cons)):
            if cons[k] == "(":
                depth += 1
            elif cons[k] == ")":
                depth -= 1
                if depth == 0:
                    out += " " + cons[i:k + 1]
                    break
    return out


def _sql_table(tname, cols):
    parts = [f"    {_sql_column(c)}" for c in cols]
    pk = [c[0] for c in cols if "[PK]" in c[3]]
    if pk:
        parts.append(f"    PRIMARY KEY ({', '.join(pk)})")
    for c in cols:
        if "[UNIQUE]" in c[3]:
            parts.append(f"    CONSTRAINT uq_{tname}_{c[0]} UNIQUE ({c[0]})")
    return f"CREATE TABLE {tname} (\n" + ",\n".join(parts) + "\n);"


sql = ["-- Migration v1 — 勤怠承認システム（サンプル） — PostgreSQL 16",
       "-- 生成元: A5 設計（DB Design ワークブックと同一データ）。逆方向変更は 0001_down.sql（別途）",
       "BEGIN;", "CREATE EXTENSION IF NOT EXISTS pgcrypto;", ""]
# Thứ tự tạo bảng: bảng cha trước (theo FK), tránh phụ thuộc vòng
ORDER = ["departments", "leave_types", "users", "auth_sessions", "leave_requests", "approval_steps", "approver_delegations", "audit_logs"]
by_name = {t: (t, l, c) for t, l, c in S.TABLES}
for tname in ORDER:
    _, label, cols = by_name[tname]
    sql.append(f"-- {label}")
    sql.append(_sql_table(tname, cols))
    sql.append("")
sql.append("-- 外部キー（ON DELETE は制約欄の指定どおり）")
for tname in ORDER:
    _, _, cols = by_name[tname]
    for c in cols:
        if "[FK]" in c[3]:
            import re as _re
            ref = c[3].split("[FK] → ")[1].split(" ")[0]
            od = _re.search(r"ON DELETE (\w+)", c[3])
            sql.append(f"ALTER TABLE {tname} ADD CONSTRAINT fk_{tname}_{c[0]} FOREIGN KEY ({c[0]}) REFERENCES {ref}" + (f" ON DELETE {od.group(1)};" if od else ";"))
sql.append("")
sql.append("-- インデックス（Index Design: 全 FK 列 + 一覧の並び替え用）")
for tname in ORDER:
    _, _, cols = by_name[tname]
    for c in cols:
        if "[FK]" in c[3]:
            sql.append(f"CREATE INDEX idx_{tname}_{c[0]} ON {tname} ({c[0]});")
sql.append("CREATE INDEX idx_leave_requests_applicant_created ON leave_requests (applicant_id, created_at DESC);")
sql.append("CREATE INDEX idx_audit_logs_target ON audit_logs (target_type, target_id);")
sql.append("COMMIT;")
(DOCS / "A5_db-design").mkdir(parents=True, exist_ok=True)
(DOCS / "A5_db-design" / f"{P}_migration_v1.sql").write_text("\n".join(sql) + "\n", encoding="utf-8")

# schema_model.json → health_check.py
schema = {"tables": []}
for tname, label, cols in S.TABLES:
    tbl = {"name": tname, "classification": "Lookup" if tname in ("departments", "leave_types") else ("Log" if tname in ("audit_logs", "approval_steps") else "Core"),
           "soft_delete": tname == "users",
           "primary_key": [c[0] for c in cols if c[3].startswith("[PK]")],
           "unique": [[c[0]] for c in cols if "[UNIQUE]" in c[3]],
           "columns": [], "indexes": []}
    for c in cols:
        col = {"name": c[0], "type": c[1]}
        if "[FK]" in c[3]:
            col["fk"] = c[3].split("[FK] → ")[1].split("(")[0] + "." + c[3].split("(")[1].split(")")[0]
        if "CHECK" in c[3]:
            col["check"] = True
        tbl["columns"].append(col)
    idx = []
    for c in cols:
        if "[FK]" in c[3]:
            idx.append({"name": f"idx_{tname}_{c[0]}", "columns": [c[0]], "unique": False})
    for et, ecols, ename in EXTRA_INDEXES:
        if et == tname:
            idx.append({"name": ename, "columns": ecols, "unique": False})
    if tname == "audit_logs":
        idx.append({"name": "idx_audit_logs_target", "columns": ["target_type", "target_id"], "unique": False})
    tbl["indexes"] = idx
    schema["tables"].append(tbl)
schema_path = DOCS / "A5_db-design" / f"{P}_schema_model.json"
schema_path.write_text(json.dumps(schema, ensure_ascii=False, indent=2), encoding="utf-8")
sh([str(REPO / "skills/a5-db-design/scripts/health_check.py"), str(schema_path), "--json", str(DOCS / "A5_db-design" / f"{P}_health_check.json")])
graph = {}
for tname, label, cols in S.TABLES:
    refs = []
    for c in cols:
        if "[FK]" in c[3]:
            ref = c[3].split("[FK] → ")[1].split("(")[0]
            refs.append({"table": ref, "nullable": c[2] == "NULL", "column": c[0]})
    graph[tname] = refs
graph_path = DOCS / "A5_db-design" / f"{P}_fk_graph.json"
graph_path.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
sh([str(REPO / "skills/a5-db-design/scripts/check_circular_fk.py"), str(graph_path)])

# ERD (Mermaid)
erd = ["erDiagram"]
for tname, label, cols in S.TABLES:
    erd.append(f"    {tname} {{")
    for c in cols:
        erd.append(f"        {c[1].replace('(', '_').replace(')', '').replace(',', '_')} {c[0]}")
    erd.append("    }")
rels = []
for tname, label, cols in S.TABLES:
    for c in cols:
        if "[FK]" in c[3]:
            ref = c[3].split("[FK] → ")[1].split("(")[0]
            rels.append(f"    {ref} ||--o{{ {tname} : \"{c[0]}\"")
erd += rels
(DOCS / "A5_db-design" / f"{P}_ERD.md").write_text("# ERD — 勤怠承認システム（サンプル）\n\n```mermaid\n" + "\n".join(erd) + "\n```\n", encoding="utf-8")

# DB design workbook (flattened: 1 行 = 1 カラム)
db_rows = []
for tname, label, cols in S.TABLES:
    for c in cols:
        db_rows.append({"tbl": tname, "label": label, "col": c[0], "type": c[1], "null": c[2], "cons": c[3], "desc": c[4]})
rel_rows = []
for tname, label, cols in S.TABLES:
    for c in cols:
        if "[FK]" in c[3]:
            rel_rows.append({"from": f"{tname}.{c[0]}", "to": c[3].split("[FK] → ")[1].split(" ")[0], "on": "RESTRICT/CASCADE（制約欄を参照）"})
save_xlsx({"title": "DB Design", "language": "ja", "sheets": [
    {"name": "概要・テーブル一覧", "title": "データベース設計書 — テーブル一覧",
     "subtitle": "PostgreSQL 16 ／ 文字コード UTF-8 ／ タイムゾーン UTC 保存・表示は JST",
     "columns": [{"key": "t", "header": "テーブル名", "width": 22}, {"key": "l", "header": "論理名", "width": 20}, {"key": "n", "header": "カラム数", "width": 10, "align": "center"}],
     "rows": [{"t": t, "l": l, "n": {"value": len(c)}} for t, l, c in S.TABLES],
     "total_row": {"label": "合計カラム数", "sum": ["n"]}},
    {"name": "データモデル", "title": "データモデル（1行＝1カラム）",
     "subtitle": "型・NULL・制約・説明。外部キーは制約欄に [FK] → 参照先(列) ON DELETE 動作を明記",
     "columns": [{"key": "tbl", "header": "テーブル", "width": 18}, {"key": "label", "header": "論理名", "width": 16},
                 {"key": "col", "header": "カラム名", "width": 20}, {"key": "type", "header": "型", "width": 16, "align": "center"},
                 {"key": "null", "header": "NULL", "width": 10, "align": "center"}, {"key": "cons", "header": "制約・デフォルト", "width": 46, "wrap": True},
                 {"key": "desc", "header": "説明・業務ルール", "width": 46, "wrap": True}],
     "rows": db_rows},
    {"name": "リレーション", "title": "外部キー一覧", "subtitle": "削除時の動作は制約欄を参照",
     "columns": [{"key": "from", "header": "参照元（子）", "width": 34}, {"key": "to", "header": "参照先（親）", "width": 34}, {"key": "on", "header": "ON DELETE", "width": 36}],
     "rows": rel_rows},
]}, "A5_db-design", f"{P}_DB_Design.xlsx")

# ================================================================ A6 estimate (công thức tham chiếu Assumptions)
md_per_pm, buffer_pct, sprint_weeks = 22, 0.15, 2
capacity = sum(t["md_per_sprint"] for t in S.ctx["team"])  # sprint capacity (MD)
task_rows = [list(t) for t in S.TASKS] + [list(t) for t in S.QA_TASKS] + [list(t) for t in S.PM_TASKS]
N = len(task_rows)
first, last = 4, 4 + N - 1
detail_rows = []
for i, (m, t, role, bd, dd, dev, ut, it) in enumerate(task_rows):
    r = first + i
    detail_rows.append({"no": i + 1, "mod": m, "task": t, "role": role,
                        "bd": bd, "dd": dd, "dev": dev, "ut": ut, "it": it,
                        "tot": f"=SUM(E{r}:I{r})", "note": ""})
total_row_idx = last + 1
est_spec = {"title": "Effort Estimate", "language": "ja", "sheets": [
    {"name": "前提条件", "title": "前提条件",
     "subtitle": "ここに置いた値を「見積サマリー」と「役割別工数」が参照します（値を変えると全体が再計算されます）",
     "columns": [{"key": "item", "header": "項目", "width": 30}, {"key": "val", "header": "値", "width": 14, "align": "right"},
                 {"key": "unit", "header": "単位", "width": 12}, {"key": "basis", "header": "根拠", "width": 60, "wrap": True}],
     "rows": [
         {"item": "1人月あたりの人日（MD/PM）", "val": {"value": md_per_pm}, "unit": "MD", "basis": "社内基準（稼働日数 22 日）。settings.md_per_person_month"},
         {"item": "バッファ率", "val": {"value": buffer_pct, "numfmt": "0%"}, "unit": "%", "basis": "未確定要件（Q-03/Q-04）と結合試験の手戻り想定。settings.buffer_percent"},
         {"item": "スプリント期間", "val": {"value": sprint_weeks}, "unit": "週", "basis": "settings.sprint_duration_weeks"},
         {"item": "チーム能力（1スプリント）", "val": {"value": capacity}, "unit": "MD", "basis": "team[].md_per_sprint の合計（PM を含む）"},
         {"item": "想定開始日", "val": {"value": "2027-01-04"}, "unit": "日付", "basis": "顧客との合意（キックオフ予定）"},
         {"item": "想定リリース目標", "val": {"value": "2027-03-31"}, "unit": "日付", "basis": "顧客要望。達成性は a9 で検証"},
     ]},
    {"name": "工数明細", "title": "工数見積明細",
     "subtitle": "工程: 基本設計 / 詳細設計 / 開発 / 単体試験 / 結合試験（単位: 人日 MD）。合計は行ごとに SUM",
     "columns": [{"key": "no", "header": "No", "width": 6, "align": "center"},
                 {"key": "mod", "header": "モジュール", "width": 11},
                 {"key": "task", "header": "作業内容", "width": 44, "wrap": True},
                 {"key": "role", "header": "担当", "width": 8, "align": "center", "validate": ["PM", "BE", "FE", "QA", "DevOps"]},
                 {"key": "bd", "header": "基本設計", "width": 10, "numfmt": "0.00", "align": "right"},
                 {"key": "dd", "header": "詳細設計", "width": 10, "numfmt": "0.00", "align": "right"},
                 {"key": "dev", "header": "開発", "width": 10, "numfmt": "0.00", "align": "right"},
                 {"key": "ut", "header": "単体試験", "width": 10, "numfmt": "0.00", "align": "right"},
                 {"key": "it", "header": "結合試験", "width": 10, "numfmt": "0.00", "align": "right"},
                 {"key": "tot", "header": "合計（MD）", "width": 12, "numfmt": "0.00", "align": "right"},
                 {"key": "note", "header": "備考", "width": 26, "wrap": True}],
     "rows": detail_rows,
     "total_row": {"label": "合計", "sum": ["bd", "dd", "dev", "ut", "it", "tot"]}},
    {"name": "役割別工数", "title": "役割別工数",
     "subtitle": "「工数明細」の担当列で SUMIF 集計。人月は「前提条件」の値で換算",
     "columns": [{"key": "role", "header": "担当", "width": 12, "align": "center"},
                 {"key": "md", "header": "工数（MD）", "width": 14, "numfmt": "0.00", "align": "right"},
                 {"key": "pm", "header": "工数（PM）", "width": 14, "numfmt": "0.00", "align": "right"},
                 {"key": "share", "header": "構成比", "width": 12, "numfmt": "0.0%", "align": "right"}],
     "rows": [{"role": r, "md": f"=SUMIF('工数明細'!D{first}:D{last},A{4+i},'工数明細'!J{first}:J{last})",
               "pm": f"=ROUND(B{4+i}/前提条件!B4,2)",
               "share": f"=IFERROR(B{4+i}/SUM(B$4:B${4+3}),0)"} for i, r in enumerate(["PM", "BE", "FE", "QA"])],
     "total_row": {"label": "合計", "sum": ["md", "pm"]}},
    {"name": "見積サマリー", "title": "見積サマリー",
     "subtitle": "すべて数式。前提は「前提条件」シートを参照",
     "columns": [{"key": "item", "header": "項目", "width": 34}, {"key": "val", "header": "値", "width": 16, "numfmt": "#,##0.00", "align": "right"},
                 {"key": "unit", "header": "単位", "width": 10}, {"key": "calc", "header": "計算", "width": 52, "wrap": True}],
     "rows": [
         {"item": "開発工数（小計）", "val": f"='工数明細'!J{total_row_idx}", "unit": "MD", "calc": "「工数明細」の合計行"},
         {"item": "バッファ", "val": f"=ROUND(B4*前提条件!B5,2)", "unit": "MD", "calc": "小計 × バッファ率"},
         {"item": "見積合計（MD）", "val": "=B4+B5", "unit": "MD", "calc": "小計 + バッファ"},
         {"item": "見積合計（人月）", "val": "=ROUND(B6/前提条件!B4,2)", "unit": "PM", "calc": "見積合計 ÷ 1人月の人日"},
         {"item": "必要スプリント数", "val": "=ROUNDUP(B6/前提条件!B7,0)", "unit": "スプリント", "calc": "見積合計 ÷ チーム能力、切り上げ"},
         {"item": "必要期間（週）", "val": "=B8*前提条件!B6", "unit": "週", "calc": "スプリント数 × スプリント期間"},
     ]},
    {"name": "対象外", "title": "対象外",
     "subtitle": "本見積に含まれない項目。含めたい場合は変更要求（c7）で扱う",
     "columns": [{"key": "no", "header": "No", "width": 6, "align": "center"}, {"key": "item", "header": "対象外項目", "width": 50, "wrap": True},
                 {"key": "reason", "header": "理由", "width": 40, "wrap": True}],
     "rows": [
         {"no": 1, "item": "人事システムとの自動連携（勤怠データの取込・送信）", "reason": "後フェーズ（Q-05）"},
         {"no": 2, "item": "スマートフォン専用画面", "reason": "対応ブラウザは PC の Chrome/Edge（NFR-COMPAT-01）"},
         {"no": 3, "item": "申請の取消（撤回）機能", "reason": "Q-03 の回答後に見積を更新"},
         {"no": 4, "item": "休暇残高（付与日数）の管理", "reason": "人事システム側で管理（Q-05）"},
     ]},
    {"name": "リスク", "title": "リスク",
     "subtitle": "影響: 工数・期間への影響度。対応は担当者と期限を明記",
     "columns": [{"key": "no", "header": "No", "width": 6, "align": "center"}, {"key": "risk", "header": "リスク", "width": 46, "wrap": True},
                 {"key": "impact", "header": "影響", "width": 12, "align": "center"}, {"key": "resp", "header": "対応", "width": 46, "wrap": True},
                 {"key": "owner", "header": "担当", "width": 10, "align": "center"}],
     "rows": [
         {"no": 1, "risk": "Q-03（承認の取消）と Q-04（CSV仕様）が未回答のまま着手すると手戻りが発生", "impact": {"value": "High", "fill": "FDE9E7", "align": "center"}, "resp": "キックオフ前に回答期限を合意。未回答なら該当機能を後続スプリントへ", "owner": "PM"},
         {"no": 2, "risk": "人事の既存取込仕様（文字コード・列順）が変更される", "impact": {"value": "Medium", "fill": "FFF2CC", "align": "center"}, "resp": "CSV 仕様を Q-04 で凍結し、仕様変更は c7 で扱う", "owner": "PM"},
         {"no": 3, "risk": "承認者代理の期限計算（月末・時刻）の不具合", "impact": {"value": "Medium", "fill": "FFF2CC", "align": "center"}, "resp": "境界値試験（APPR2-BND-001）を結合試験に含める", "owner": "QA"},
     ]},
]}
save_xlsx(est_spec, "A6_estimate", f"{P}_Estimate.xlsx")

# ================================================================ A8 test plan
mods_tc = {"AUTH": "認証", "LEAVE": "休暇申請", "APPR": "承認", "REPORT": "帳票"}
TC_JA = {"AUTH": "認証", "LEAVE": "休暇", "APPR": "承認", "REPORT": "帳票"}
case_mod = {"AUTH": "AUTH", "LEAVE": "LEAVE", "LEAVE2": "LEAVE", "APPR": "APPR", "APPR2": "APPR", "REPORT": "REPORT"}
per_mod = {m: [] for m in mods_tc}
for k, cases in S.CASES.items():
    per_mod[case_mod[k]].extend(cases)
tc_cols = [
    {"key": "id", "header": "テストID", "width": 16}, {"key": "req", "header": "要件参照（機能ID）", "width": 16},
    {"key": "mod", "header": "モジュール", "width": 10}, {"key": "feat", "header": "機能", "width": 18, "wrap": True},
    {"key": "type", "header": "テスト種別", "width": 9, "align": "center", "validate": ["UT", "IT", "API", "E2E", "PERF", "SEC", "UAT", "REG", "SMK", "UI", "CON"]},
    {"key": "prio", "header": "優先度", "width": 14, "align": "center", "validate": [P1, P2, P3, "⚪ P4-Low"]},
    {"key": "pre", "header": "前提条件", "width": 26, "wrap": True},
    {"key": "steps", "header": "テスト手順", "width": 46, "wrap": True},
    {"key": "data", "header": "テストデータ", "width": 34, "wrap": True},
    {"key": "exp", "header": "期待結果", "width": 42, "wrap": True},
    {"key": "api", "header": "関連API", "width": 30, "wrap": True},
    {"key": "tbl", "header": "関連テーブル", "width": 22, "wrap": True},
    {"key": "auto", "header": "自動化", "width": 11, "align": "center", "validate": ["Y", "N", "Done"]},
    {"key": "note", "header": "備考", "width": 26, "wrap": True},
]
tc_sheets = []
for m, label in mods_tc.items():
    rows = []
    for c in per_mod[m]:
        rows.append({"id": c[0], "req": c[1], "mod": c[2], "feat": c[3], "type": c[4], "prio": c[5], "pre": c[6], "steps": c[7],
                     "data": c[8], "exp": c[9], "api": c[10], "tbl": c[11], "auto": c[12], "note": c[13]})
    tc_sheets.append({"name": f"TC {TC_JA[m]}", "title": f"テストケース — {label}（{m}）",
                      "subtitle": "1ケース＝1条件（アトミック）。実行結果は C5 の Test Execution に記録（本書には書かない）",
                      "columns": tc_cols, "rows": rows})
TC_SHEETS = [f"TC {TC_JA[m]}" for m in mods_tc]

COV_TYPES = ["UT", "IT", "API", "E2E", "PERF", "SEC", "CON", "UI", "REG", "SMK"]
SEC_SHEET = "セキュリティ・整合性"
ALL_CASE_SHEETS = None  # set after TC_SHEETS
from openpyxl.utils import get_column_letter


ALL_CASE_SHEETS = TC_SHEETS + [SEC_SHEET]


def cov_formula(sheet, ttype, row):
    return f"COUNTIFS('{sheet}'!$B$4:$B$200,$A{row},'{sheet}'!$E$4:$E$200,\"{ttype}\")"


feats = [f[0] for f in S.FEATS]
cov = []
for fid in feats:
    cov.append({"req": fid, "cnt": "=" + "+".join(f"COUNTIF('{s}'!B4:B200,A{{r}})" for s in ALL_CASE_SHEETS)})
trace_rows = []
for i, fid in enumerate(feats):
    r = 4 + i
    trace_rows.append({"req": fid, "name": next(f[2] for f in S.FEATS if f[0] == fid),
                       "cnt": "=" + "+".join(f"COUNTIF('{s}'!$B$4:$B$200,A{r})" for s in ALL_CASE_SHEETS),
                       "ok": f'=IF(C{r}>=6,"OK","GAP（6件未満）")'})
dash = [
    ("総ケース数", "=" + "+".join(f"COUNTA('{s}'!A4:A200)" for s in ALL_CASE_SHEETS)),
]
test_plan = {"title": "Test Plan", "language": "ja", "sheets": [
    {"name": "テスト戦略", "title": "テスト戦略書",
     "subtitle": "対象: 勤怠承認システム（サンプル）・Web（PC: Chrome/Edge）・API（staging）",
     "columns": [{"key": "k", "header": "項目", "width": 24}, {"key": "v", "header": "内容", "width": 100, "wrap": True}],
     "rows": [
         {"k": "対象範囲（In scope）", "v": "認証、休暇・残業申請、承認・差戻し、承認者代理、月次CSV出力、API全件（9件）"},
         {"k": "対象外（Out of scope）", "v": "人事システム連携、スマートフォン画面、休暇残高管理（見積の対象外と同じ）"},
         {"k": "テスト種別", "v": "UT（ロジック）・API・UI・結合（IT）・セキュリティ（SEC）・性能（PERF）・同時実行（CON）・UAT"},
         {"k": "環境", "v": "DEV（単体・結合）→ STG（ST・UAT・性能）。STG は本番と同構成（DB 16・同設定）"},
         {"k": "ツール", "v": "Jest + Supertest（API自動化）、Playwright（UI E2E）、k6（性能）、OWASP ZAP（SEC の一次スキャン）"},
         {"k": "入場基準（Entry）", "v": "ビルドが CI で成功。UT 合格率 ≥ 95%、行カバレッジ ≥ 80%（settings.quality_gates）"},
         {"k": "完了基準（Exit）", "v": "P1 のテストがすべて合格。ST 合格率 ≥ 98%。Critical/High の未解決欠陥 0 件（open_critical_high_max = 0）"},
         {"k": "欠陥の扱い", "v": "Critical: 即時修正・再試験 ／ High: リリース前に修正 ／ Medium・Low: 既知の問題として記録し期日を決める"},
         {"k": "リスク", "v": "Q-03・Q-04 未決（仮仕様で作成）。決定後、該当ケースを再確認する"},
     ]},
    {"name": "カバレッジ", "title": "カバレッジ・マトリクス（機能 × テスト種別）",
     "subtitle": "各セルはケース件数（COUNTIFS）。0 の種別は「テスト戦略」の備考に理由を記載。UAT は業務シナリオ単位（UATチェックリスト）",
     "columns": [{"key": "req", "header": "機能ID", "width": 18}] + [
         {"key": f"t{j}", "header": t, "width": 8, "align": "center"} for j, t in enumerate(COV_TYPES)] + [
         {"key": "cnt", "header": "合計", "width": 10, "align": "center"}],
     "rows": [dict({"req": fid}, **{f"t{j}": "=" + "+".join(cov_formula(s_name, t, 4 + i) for s_name in TC_SHEETS + ([SEC_SHEET] if t in ("IT", "SEC") else [])) for j, t in enumerate(COV_TYPES)},
                   cnt=f"=SUM(B{4+i}:{get_column_letter(1 + len(COV_TYPES))}{4+i})") for i, fid in enumerate(feats)],
     "total_row": {"label": "合計", "sum": [f"t{j}" for j in range(len(COV_TYPES))] + ["cnt"]}},
] + tc_sheets + [
    {"name": "セキュリティ・整合性", "title": "セキュリティ・データ整合性（DB制約に対応）",
     "subtitle": "データベースの制約（CHECK / UNIQUE / FK）ごとに 1 件以上の試験。関連テーブルを必ず記入",
     "columns": tc_cols, "rows": [
         {"id": "INT-DB-001", "req": "FEAT-LEAVE-01", "mod": "LEAVE", "feat": "期間の整合性", "type": "IT", "prio": P1, "pre": "—",
          "steps": "1. leave_requests に date_to < date_from の行を直接 INSERT", "data": "date_from=2027-02-05, date_to=2027-02-01", "exp": "CHECK 制約違反で失敗", "api": "—", "tbl": "leave_requests", "auto": "Y", "note": "CHECK (date_to >= date_from)"},
         {"id": "INT-DB-002", "req": "FEAT-AUTH-01", "mod": "AUTH", "feat": "社員番号の一意性", "type": "IT", "prio": P1, "pre": "社員番号 100001 が存在", "steps": "1. 同じ employee_id で INSERT", "data": "100001", "exp": "UNIQUE 違反", "api": "—", "tbl": "users", "auto": "Y", "note": ""},
         {"id": "INT-DB-003", "req": "FEAT-APPR-02", "mod": "APPR", "feat": "代理期間の上限", "type": "IT", "prio": P1, "pre": "—", "steps": "1. valid_to - valid_from = 31 で INSERT", "data": "31日間", "exp": "CHECK 違反（30日まで）", "api": "—", "tbl": "approver_delegations", "auto": "Y", "note": "Q-01"},
         {"id": "INT-DB-004", "req": "FEAT-LEAVE-01", "mod": "LEAVE", "feat": "参照整合性", "type": "IT", "prio": P2, "pre": "申請1件が存在", "steps": "1. 申請者（users）を DELETE", "data": "applicant_id", "exp": "ON DELETE RESTRICT により失敗", "api": "—", "tbl": "users, leave_requests", "auto": "Y", "note": ""},
         {"id": "INT-DB-005", "req": "FEAT-APPR-01", "mod": "APPR", "feat": "承認履歴の削除", "type": "IT", "prio": P2, "pre": "承認履歴あり", "steps": "1. 申請を DELETE", "data": "request_id", "exp": "承認履歴も CASCADE で削除（監査は audit_logs に残る）", "api": "—", "tbl": "approval_steps, audit_logs", "auto": "Y", "note": "CASCADE の業務妥当性を確認"},
         {"id": "INT-DB-006", "req": "FEAT-AUTH-01", "mod": "AUTH", "feat": "パスワード保存", "type": "SEC", "prio": P1, "pre": "ユーザー作成後", "steps": "1. users.password_hash を読む", "data": "—", "exp": "平文でなく Argon2id 形式（$argon2id$ で始まる）", "api": "—", "tbl": "users", "auto": "Y", "note": "NFR-SEC-01"},
     ]},
    {"name": "性能試験計画", "title": "性能試験計画",
     "subtitle": "k6 シナリオ。閾値は NFR に従う。STG で実施（本番では実施しない）",
     "columns": [{"key": "id", "header": "シナリオID", "width": 12}, {"key": "name", "header": "内容", "width": 36, "wrap": True},
                 {"key": "load", "header": "負荷", "width": 26, "wrap": True}, {"key": "thr", "header": "閾値（合格基準）", "width": 34, "wrap": True},
                 {"key": "nfr", "header": "NFR", "width": 14}],
     "rows": [
         {"id": "LIST-01", "name": "申請一覧（検索込み）", "load": "50 VU・10分・ランプ 2分", "thr": "p95 ≤ 800ms ／ エラー率 < 0.5%", "nfr": "NFR-PERF-01"},
         {"id": "APPR-01", "name": "承認API（同時承認の衝突含む）", "load": "20 VU・5分", "thr": "p95 ≤ 500ms ／ 409 は想定どおり（二重承認なし）", "nfr": "NFR-PERF-01"},
         {"id": "CSV-01", "name": "月次CSV（5,000件）", "load": "2 VU・3回", "thr": "30 秒以内", "nfr": "NFR-PERF-01"},
     ]},
    {"name": "UATチェックリスト", "title": "受入試験チェックリスト（UAT）",
     "subtitle": "顧客（人事・承認者・一般社員の代表）が実施。合否と署名は UAT_SignOff に記録",
     "columns": [{"key": "no", "header": "No", "width": 6, "align": "center"}, {"key": "scn", "header": "業務シナリオ", "width": 50, "wrap": True},
                 {"key": "role", "header": "実施者", "width": 14}, {"key": "res", "header": "結果（合 / 否）", "width": 14, "align": "center", "validate": ["合", "否", "保留"]}],
     "rows": [
         {"no": 1, "scn": "一般社員が有給を提出し、承認者が承認する（翌日に状態が反映される）", "role": "一般社員・承認者", "res": ""},
         {"no": 2, "scn": "承認者が理由付きで差し戻し、社員が修正して再提出する", "role": "承認者・一般社員", "res": ""},
         {"no": 3, "scn": "承認者が不在の期間、代理者が承認し、期間後は承認できないことを確認", "role": "承認者・代理者", "res": ""},
         {"no": 4, "scn": "人事が当月の勤怠CSVを出力し、既存取込ツールで読み込める", "role": "人事", "res": ""},
     ]},
    {"name": "トレーサビリティ", "title": "トレーサビリティ・マトリクス（機能 → テスト）",
     "subtitle": "機能ID（FEAT）ごとに件数を集計。6件未満は GAP。件数は TC シートから自動集計",
     "columns": [{"key": "req", "header": "機能ID", "width": 18}, {"key": "name", "header": "機能名", "width": 26, "wrap": True},
                 {"key": "cnt", "header": "ケース数", "width": 12, "align": "center"}, {"key": "ok", "header": "判定", "width": 18, "align": "center"}],
     "rows": trace_rows},
    {"name": "サマリー", "title": "テスト計画サマリー",
     "subtitle": "ケース数・自動化率。実行結果（合格率）は C5 の Dashboard を参照",
     "columns": [{"key": "k", "header": "指標", "width": 34}, {"key": "v", "header": "値", "width": 16, "align": "center"}, {"key": "n", "header": "備考", "width": 50, "wrap": True}],
     "rows": [
         {"k": "総ケース数", "v": "=" + "+".join(f"COUNTA('{s}'!A4:A200)" for s in ALL_CASE_SHEETS), "n": "各 TC シートのテストID の件数の合計"},
         {"k": "優先度 P1 の件数", "v": "=" + "+".join(f"COUNTIF('{s}'!F4:F200,\"{P1}\")" for s in ALL_CASE_SHEETS), "n": "P1 が 1 件でも Fail → リリースを止める"},
         {"k": "自動化率（自動化=Y の割合）", "v": "=ROUND((" + "+".join(f"COUNTIF('{s}'!M4:M200,\"Y\")" for s in ALL_CASE_SHEETS) + ")/(" + "+".join(f"COUNTA('{s}'!M4:M200)" for s in ALL_CASE_SHEETS) + "),2)", "n": "目標 0.8 以上（a8 の方針）"},
     ]},
]}
# tổng số case: dùng COUNTA trên cột A (đã loại dòng tiêu đề bằng vị trí bắt đầu từ dòng 4)
save_xlsx(test_plan, "A8_test-plan", f"{P}_Test_Plan.xlsx")

# ================================================================ A9 timeline (script thật)
sh([str(REPO / "skills/a1-project-init/scripts/update_context.py"), str(WS), "set", "estimates.total_md", str(sum(t[3] + t[4] + t[5] + t[6] + t[7] for t in task_rows) * (1 + buffer_pct))])
tl_dir = DOCS / "A9_project-timeline"
tl_dir.mkdir(parents=True, exist_ok=True)
sh([str(REPO / "skills/a9-project-timeline/scripts/timeline_calc.py"), str(WS), "--json", str(tl_dir / "timeline.json"), "--ics", str(tl_dir / f"{P}_Milestones.ics")])

print("\n== DONE: outputs in", DOCS)
# ================================================================ B3 CRUD matrix → check_crud_coverage
CRUD_TABLES = [t for t, _, _ in S.TABLES]
CRUD = {
    "POST /auth/login": {"users": "R", "auth_sessions": "C", "audit_logs": "C"},
    "POST /auth/refresh": {"auth_sessions": "RU"},
    "POST /leave-requests": {"leave_requests": "C", "approval_steps": "C", "users": "R", "leave_types": "R"},
    "GET /leave-requests": {"leave_requests": "R", "users": "R"},
    "GET /leave-requests/{id}": {"leave_requests": "R", "approval_steps": "R", "users": "R"},
    "POST /leave-requests/{id}/approve": {"approval_steps": "C", "leave_requests": "U", "audit_logs": "C", "users": "R"},
    "POST /leave-requests/{id}/reject": {"approval_steps": "C", "leave_requests": "U", "audit_logs": "C"},
    "PUT /approver-delegations": {"approver_delegations": "CU", "audit_logs": "C", "users": "R"},
    "GET /reports/monthly-attendance.csv": {"leave_requests": "R", "users": "R", "departments": "R"},
    "管理: 部門マスタ登録（バッチ）": {"departments": "CRUD"},
    "管理: 休暇種別マスタ登録（バッチ）": {"leave_types": "CRUD"},
    "管理: 社員マスタ登録・異動（人事の管理画面・CSV取込）": {"users": "CRU", "departments": "R"},
    "バッチ: 退職者の個人情報削除（NFR-PRIV-01）": {"users": "D", "leave_requests": "D", "approval_steps": "D", "audit_logs": "R"},
}
crud_rows = [{"fn": fn, **{t: m.get(t, "") for t in CRUD_TABLES}} for fn, m in CRUD.items()]
crud_cols = [{"key": "fn", "header": "機能（API / バッチ）", "width": 40, "wrap": True}] + [
    {"key": t, "header": t, "width": 13, "align": "center"} for t in CRUD_TABLES]
crud_spec = {"title": "DetailDesign Workbook", "language": "ja", "sheets": [
    {"name": "CRUD_Matrix", "title": "CRUD マトリクス（機能 × テーブル）",
     "subtitle": "C=作成 R=参照 U=更新 D=削除。空欄は関係なし。全テーブルに 1 つ以上の操作が必要（Zero Orphan Table）",
     "columns": crud_cols, "rows": crud_rows}]}
save_xlsx(crud_spec, "B3_detail-design", f"{P}_DetailDesign_Workbook.xlsx")
sh([str(REPO / "skills/b3-detail-design/scripts/check_crud_coverage.py"),
    str(DOCS / "A5_db-design" / f"{P}_migration_v1.sql"), str(DOCS / "B3_detail-design" / f"{P}_DetailDesign_Workbook.xlsx")])

# ================================================================ B2 基本設計書 (docx)
import sys as _sys
_sys.path.insert(0, str(REPO / "skills/a1-project-init/scripts"))
from docx_build import build as dbuild  # noqa: E402

SCREENS = [
    ("SCR-01", "ログイン", "AUTH", "社員番号・パスワードで認証する。ロック中は案内を表示。"),
    ("SCR-02", "休暇・残業申請（作成）", "LEAVE", "申請種別・期間・理由を入力し、下書き保存または提出する。"),
    ("SCR-03", "申請一覧", "LEAVE", "自分の申請を状態・期間で絞り込み、詳細へ遷移する。"),
    ("SCR-04", "申請詳細", "LEAVE/APPR", "申請内容と承認履歴を表示する。承認者には承認・差戻しのボタンを表示。"),
    ("SCR-05", "承認待ち一覧", "APPR", "承認者として処理すべき申請を一覧表示する。"),
    ("SCR-06", "承認者代理設定", "APPR", "不在期間の代理承認者を期限付きで設定する（上限30日）。"),
    ("SCR-07", "月次勤怠CSV出力", "REPORT", "人事が部門と年月を指定し、CSVをダウンロードする。"),
]
FUNCS = [
    ("FN-01", "FEAT-AUTH-01", "ログイン・ロール制御", "SCR-01", "POST /api/v1/auth/login"),
    ("FN-02", "FEAT-LEAVE-01", "休暇・残業申請の作成", "SCR-02", "POST /api/v1/leave-requests"),
    ("FN-03", "FEAT-LEAVE-02", "申請一覧・検索", "SCR-03, SCR-04", "GET /api/v1/leave-requests, GET /api/v1/leave-requests/{id}"),
    ("FN-04", "FEAT-APPR-01", "承認・差戻し", "SCR-04, SCR-05", "POST .../approve, POST .../reject"),
    ("FN-05", "FEAT-APPR-02", "承認者代理設定", "SCR-06", "PUT /api/v1/approver-delegations"),
    ("FN-06", "FEAT-REPORT-01", "月次勤怠CSV出力", "SCR-07", "GET /api/v1/reports/monthly-attendance.csv"),
]
ITEMS_LEAVE = [
    # (項目ID, 項目名, 型, 最大長, 必須, 入力規則, 初期値, 活性・表示制御, 備考)
    ("ITM-SCR02-01", "休暇種別", "ドロップダウン", "—", "必須", "leave_types.is_active = true の値のみ", "（未選択）", "常時活性", "マスタ由来"),
    ("ITM-SCR02-02", "開始日", "日付", "10（YYYY/MM/DD）", "必須", "今日以前の過去日は提出不可（下書きは可）", "今日", "常時活性", ""),
    ("ITM-SCR02-03", "終了日", "日付", "10（YYYY/MM/DD）", "必須", "開始日以上。既存の承認済み・提出済み申請と重複不可", "開始日", "常時活性", "重複時は 409 を画面表示"),
    ("ITM-SCR02-04", "残業時間", "数値（小数2桁）", "5（0.00〜24.00）", "種別=残業のとき必須", "0 ≤ 値 ≤ 24。事前承認がない場合は 422 を表示", "—", "種別=残業のとき表示", "Q-02"),
    ("ITM-SCR02-05", "理由", "テキストエリア", "500 文字", "任意", "全角・半角とも 500 文字まで（残り文字数を表示）", "（空）", "常時活性", "改行可"),
    ("ITM-SCR02-06", "下書き保存ボタン", "ボタン", "—", "—", "押下で status=draft を保存", "—", "入力エラーがあっても活性", ""),
    ("ITM-SCR02-07", "提出ボタン", "ボタン", "—", "—", "押下で status=submitted。二重押下防止のため送信中は非活性", "—", "必須項目が揃うまで非活性", "409 の場合は一覧へ誘導"),
]
ITEMS_LOGIN = [
    ("ITM-SCR01-01", "社員番号", "テキスト", "6（半角数字）", "必須", "数字6桁。形式不正は入力欄の直下に表示", "（空）", "常時活性", ""),
    ("ITM-SCR01-02", "パスワード", "パスワード", "12 以上", "必須", "12文字以上。画面にはマスク表示", "（空）", "常時活性", "表示切替は提供しない"),
    ("ITM-SCR01-03", "ログインボタン", "ボタン", "—", "—", "押下で POST /auth/login。423 のときはロック解除時刻を表示", "—", "必須項目が揃うまで非活性", ""),
]
MESSAGES = [
    ("ERR-VAL-001", "入力形式が正しくありません（{項目名}）", "400", "SCR-01, SCR-02", "入力欄直下に表示"),
    ("ERR-VAL-002", "終了日は開始日以降の日付を入力してください", "400", "SCR-02", "終了日欄の直下"),
    ("ERR-AUTH-001", "社員番号またはパスワードが正しくありません", "401", "SCR-01", "同じ文言（列挙防止）"),
    ("ERR-AUTH-002", "アカウントがロックされています。{解除時刻}以降に再度お試しください", "423", "SCR-01", "ロック解除時刻を表示"),
    ("ERR-LEAVE-001", "同じ期間に申請が存在します", "409", "SCR-02", "終了日欄の下、一覧へのリンク付き"),
    ("ERR-LEAVE-002", "残業は事前承認が必要です", "422", "SCR-02", "残業時間欄の下"),
    ("ERR-APPR-001", "この申請を承認・差戻しする権限がありません", "403", "SCR-04, SCR-05", "画面上部のバナー"),
    ("ERR-APPR-002", "申請の状態が変更されました。画面を更新してください", "409", "SCR-04", "更新ボタン付きのバナー"),
    ("ERR-SYS-001", "システムエラーが発生しました。時間をおいて再度お試しください", "500", "全画面", "問い合わせ用の requestId を表示"),
]
FLOW = """flowchart LR
  A([申請者: 申請作成 SCR-02]) -->|提出| B{残業か?}
  B -->|はい| C{事前承認あり?}
  C -->|いいえ| X[422 差戻し表示]
  C -->|はい| D[submitted]
  B -->|いいえ| D
  D --> E[承認者: 承認待ち SCR-05]
  E -->|承認| F([approved・監査ログ])
  E -->|差戻し（理由必須）| G([rejected → 申請者が修正して再提出])"""
SCREEN_FLOW = """flowchart TB
  L[SCR-01 ログイン] -->|成功・一般| M[SCR-03 申請一覧]
  L -->|成功・上長| N[SCR-05 承認待ち一覧]
  L -->|成功・人事| O[SCR-07 月次CSV]
  M -->|新規| Q[SCR-02 申請作成]
  Q -->|提出| M
  M -->|行選択| R[SCR-04 申請詳細]
  N -->|行選択| R
  R -->|承認・差戻し| N
  L -->|代理設定| T[SCR-06 代理設定]"""
blocks = [
    {"type": "h1", "text": "1. 目的・適用範囲"},
    {"type": "p", "text": "本書は勤怠承認システム（サンプル）の基本設計書である。業務要件（A2 機能スコープ・NFR）を画面・機能・入出力に展開し、顧客の承認を得るために作成する。詳細設計（B3）の入力となる。"},
    {"type": "p", "text": "本書で扱う範囲: 認証、休暇・残業申請、承認・差戻し、承認者代理、月次CSV出力。対象外: 人事システム連携、スマートフォン画面（見積書の対象外項目と一致）。"},
    {"type": "h1", "text": "2. 業務フロー"},
    {"type": "p", "text": "休暇・残業申請の基本フロー。残業は事前承認が必要（Q-02）。"},
    {"type": "table", "caption": "表 2-1 休暇・残業申請の処理手順", "columns": ["手順", "主体", "操作", "判定・分岐"],
     "widths": [1.4, 2.4, 6.6, 6.6], "rows": [
         ["1", "申請者", "申請を作成し提出する（SCR-02）", "残業 → 手順2 ／ 休暇 → 手順3"],
         ["2", "システム", "残業の事前承認（Q-02）を確認する", "事前承認あり → 手順3 ／ なし → 422（ERR-LEAVE-002）を表示し提出させない"],
         ["3", "システム", "申請を submitted にし、承認者の承認待ちに追加する", "—"],
         ["4", "承認者", "承認待ち一覧（SCR-05）で内容を確認する", "承認 → 手順5 ／ 差戻し（理由必須）→ 手順6"],
         ["5", "システム", "approved に更新し、監査ログ（LEAVE_APPROVED）を記録する", "完了"],
         ["6", "申請者", "差戻し理由を確認し、修正して再提出する（SCR-04）", "再提出 → 手順3"]]},
    {"type": "h1", "text": "3. 画面一覧・画面遷移"},
    {"type": "table", "caption": "表 3-1 画面一覧", "columns": ["画面ID", "画面名", "機能（FEAT）", "説明"], "widths": [2.2, 4.2, 3.2, 7.4],
     "rows": [list(s) for s in SCREENS]},
    {"type": "table", "caption": "表 3-2 画面遷移", "columns": ["遷移元", "操作", "遷移先", "条件"],
     "widths": [3.6, 4.6, 4.6, 4.8], "rows": [
         ["SCR-01 ログイン", "認証成功", "SCR-03 申請一覧", "role = employee（一般）"],
         ["SCR-01 ログイン", "認証成功", "SCR-05 承認待ち一覧", "role = manager（上長）"],
         ["SCR-01 ログイン", "認証成功", "SCR-07 月次勤怠CSV出力", "role = hr（人事）"],
         ["SCR-01 ログイン", "代理設定へ", "SCR-06 承認者代理設定", "role = manager 以上"],
         ["SCR-03 申請一覧", "新規作成", "SCR-02 申請作成", "—"],
         ["SCR-03 申請一覧 / SCR-05 承認待ち", "行を選択", "SCR-04 申請詳細", "—"],
         ["SCR-02 申請作成", "提出成功（201）", "SCR-03 申請一覧", "—"],
         ["SCR-04 申請詳細", "承認・差戻し", "SCR-05 承認待ち一覧", "権限 manager、状態 submitted"]]},
    {"type": "h1", "text": "4. 機能一覧（FN ↔ FEAT ↔ 画面 ↔ API）"},
    {"type": "p", "text": "機能ID（FN）は A2 の機能ID（FEAT）と 1 対 1 で対応する。API は A4 の api_spec.json と一致する。"},
    {"type": "table", "caption": "表 4-1 機能一覧", "columns": ["FN", "FEAT（A2）", "機能名", "画面", "API（A4）"], "widths": [1.6, 3.4, 4.2, 3.0, 5.2],
     "rows": [list(f) for f in FUNCS]},
    {"type": "h1", "text": "5. 画面項目定義"},
    {"type": "h2", "text": "5.1 SCR-01 ログイン"},
    {"type": "table", "caption": "表 5-1 SCR-01 項目定義", "columns": ["項目ID", "項目名", "型", "桁数/最大長", "必須", "入力規則", "初期値", "活性・表示制御", "備考"],
     "widths": [2.3, 2.2, 2.0, 2.1, 1.5, 3.6, 1.4, 2.1, 1.8], "rows": [list(i) for i in ITEMS_LOGIN]},
    {"type": "h2", "text": "5.2 SCR-02 休暇・残業申請（作成）"},
    {"type": "table", "caption": "表 5-2 SCR-02 項目定義", "columns": ["項目ID", "項目名", "型", "桁数/最大長", "必須", "入力規則", "初期値", "活性・表示制御", "備考"],
     "widths": [2.3, 2.2, 2.0, 2.1, 1.5, 3.6, 1.4, 2.1, 1.8], "rows": [list(i) for i in ITEMS_LEAVE]},
    {"type": "h1", "text": "6. メッセージ一覧"},
    {"type": "table", "caption": "表 6-1 メッセージ一覧（API のエラーコードと対応）", "columns": ["メッセージID", "文言", "HTTP", "表示画面", "表示方法"],
     "widths": [3.0, 7.0, 1.4, 2.8, 3.8], "rows": [list(m) for m in MESSAGES]},
    {"type": "h1", "text": "7. 非機能要件の反映"},
    {"type": "bullets", "items": [
        "応答時間: 申請一覧は p95 800ms 以内（NFR-PERF-01）。一覧は 20 件ずつ取得する。",
        "権限: 全画面でロールを検査。URL 直接入力でも権限外は 403 画面（NFR-SEC-02）。",
        "文字コード: 人事向け CSV は Shift_JIS（Q-04 の回答後に確定）。",
        "ブラウザ: Google Chrome・Microsoft Edge の最新版と 1 つ前の版（NFR-COMPAT-01）。"]},
    {"type": "h1", "text": "8. 未決事項"},
    {"type": "table", "caption": "表 8-1 未決事項（A2 QA Tracker と連動）", "columns": ["No.", "内容", "影響する画面・機能", "期限"],
     "widths": [1.6, 7.0, 5.0, 3.4], "rows": [["Q-03", "承認済み申請の取消（撤回）の権限", "SCR-04, FN-04", "2027-01-22"],
                                              ["Q-04", "人事CSVの文字コードと列順", "SCR-07, FN-06", "2027-01-22"]]},
]
meta = [["版", "1.0（顧客レビュー版）"], ["作成日", S.ctx["created_at"]], ["作成者", "[担当者]"], ["承認者（顧客）", "[担当者]"],
        ["対象システム", S.ctx["project"]["name"]], ["注記", "架空の教材案件。実在の企業・人物と無関係"]]
b2_out = dbuild({"language": "ja", "title": "基本設計書", "subtitle": S.ctx["project"]["name"], "meta": meta,
                 "header_text": "勤怠承認システム（サンプル） 基本設計書 v1.0", "footer_text": "社外秘", "blocks": blocks},
                DOCS / "B2_basic-design" / f"{P}_Basic_Design_v1.docx")
print("docx B2 →", b2_out)

# ================================================================ C5 テスト実行 (snapshot → test_metrics)
import itertools as _it
c5_dir = DOCS / "C5_test-execution"
c5_dir.mkdir(parents=True, exist_ok=True)
all_cases = S.cases_flat()
def snap(results, bugs, run_at, cov):
    tests = []
    for c in all_cases:
        tid = c[0]
        r = results.get(tid, "pass")
        tests.append({"id": tid, "module": c[2], "viewpoint": c[4], "result": r,
                      "bug_id": ("BUG-001" if (tid == "LEAVE-VAL-002" and r == "fail") else ""),
                      "duration_ms": 120, "evidence": "STG-run"})
    return {"phase": "ST", "run_at": run_at, "environment": "STG（本番同構成・DB PostgreSQL 16）", "tests": tests, "defects": bugs, "coverage": cov}
bug1_open = {"id": "BUG-001", "title": "申請理由が501文字でも受理される（上限500文字の検証漏れ）", "severity": "High", "status": "open",
             "found_in": "ST", "test_ids": ["LEAVE-VAL-002"]}
run1 = snap({"LEAVE-VAL-002": "fail", "LEAVE-CON-001": "notrun", "LEAVE2-PERF-001": "notrun", "REPORT-BND-001": "notrun"},
            [bug1_open], "2027-02-10T10:00:00+09:00", {"line": 84.0, "branch": 71.0, "source": "coverage-summary.json"})
(c5_dir / f"{P}_test_results_ST_20270210.json").write_text(json.dumps(run1, ensure_ascii=False, indent=2), encoding="utf-8")
bug1_closed = dict(bug1_open, status="verified", regression_test_id="LEAVE-VAL-002",
                   regression_impact_scope="leave/leave-request.dto.ts, leave/leave.service.ts",
                   required_regression_suites="leave_api, leave_validation", verified_commit="a1b2c3d")
run2 = snap({"LEAVE-CON-001": "pass", "LEAVE2-PERF-001": "pass", "REPORT-BND-001": "pass"},
            [bug1_closed], "2027-02-14T10:00:00+09:00", {"line": 86.5, "branch": 74.2, "source": "coverage-summary.json"})
(c5_dir / f"{P}_test_results_ST_20270214.json").write_text(json.dumps(run2, ensure_ascii=False, indent=2), encoding="utf-8")
ctx_path = str(WS / "project-context.json")
_r = sh([str(REPO / "skills/c5-test-execution/scripts/test_metrics.py"), str(c5_dir / f"{P}_test_results_ST_20270210.json"), "--context", ctx_path, "--format", "md"])
(c5_dir / f"{P}_Test_Report_ST_20270210.md").write_text(_r.stdout, encoding='utf-8')
_r = sh([str(REPO / "skills/c5-test-execution/scripts/test_metrics.py"), str(c5_dir / f"{P}_test_results_ST_20270214.json"), "--context", ctx_path, "--format", "md"])
(c5_dir / f"{P}_Test_Report_ST_20270214.md").write_text(_r.stdout, encoding='utf-8')

# ================================================================ C6 スプリントレビュー / C7 変更要求 / C8 リリース確認
import http.server as _hs, threading as _th
sprint_in = {
    "sprint": 2, "sprint_weeks": 2, "capacity_md": 36,
    "tasks": [
        {"id": "T-101", "title": "申請API（作成・検証・重複）", "planned_md": 9, "actual_md": 10, "status": "done", "reason": ""},
        {"id": "T-102", "title": "申請フォーム（下書き・提出）", "planned_md": 6, "actual_md": 6, "status": "done", "reason": ""},
        {"id": "T-103", "title": "承認API（状態遷移・OCC）", "planned_md": 8, "actual_md": 5, "status": "partial", "reason": "OCC の 409 応答が未完（残 3 MD）"},
        {"id": "T-104", "title": "認証基盤（JWT・ロック）", "planned_md": 6, "actual_md": 6, "status": "done", "reason": ""},
        {"id": "T-105", "title": "CI/CD 初期構築", "planned_md": 4, "actual_md": 0, "status": "moved", "reason": "インフラ申請の遅延により Sprint 3 へ"},
        {"id": "T-106", "title": "申請一覧 UI", "planned_md": 5, "actual_md": 0, "status": "not_started", "reason": ""},
    ],
    "bugs": {"found": 4, "fixed": 3, "carry_over": 1, "p1_open": 0, "p2": 1, "p3p4": 2},
    "demo": "partial", "blockers_unresolved": 1,
    "prev_actions": {"total": 3, "done": 2}, "unresolved_debt_md": 1.5, "remaining_md": 98.5, "team_daily_burn_md": 1.8,
    "history": [{"sprint": 1, "planned_md": 30, "completed_md": 24, "health": 72}],
}
sprint_path = DOCS / "C6_sprint-review" / f"{P}_sprint2_input.json"
sprint_path.parent.mkdir(parents=True, exist_ok=True)
sprint_path.write_text(json.dumps(sprint_in, ensure_ascii=False, indent=2), encoding="utf-8")
_r = sh([str(REPO / "skills/c6-sprint-review/scripts/sprint_metrics.py"), str(sprint_path), "--context", ctx_path, "--format", "md"])
(DOCS / "C6_sprint-review" / f"{P}_Sprint2_Review.md").write_text(_r.stdout, encoding='utf-8')

cr = {
    "cr_id": "CR-001", "cr_type": "ADDITION", "title": "月次CSVに部門別合計行を追加・申請一覧に残日数を表示",
    "items": [
        {"task": "CSV 部門別合計行（集計ロジック・出力）", "kind": "new", "bd": 0.5, "dd": 0.5, "dev": 2.0, "ut": 1.0, "it": 1.0},
        {"task": "申請一覧に有給残日数の表示（API 追加・UI）", "kind": "new", "bd": 0.5, "dd": 1.0, "dev": 3.5, "ut": 1.5, "it": 1.0},
        {"task": "既存 CSV 試験・取込確認の再実施", "kind": "regression", "bd": 0, "dd": 0, "dev": 0, "ut": 0.5, "it": 1.5},
    ],
    "settings": {"md_per_person_month": 22, "buffer_percent": 15, "sprint_duration_weeks": 2},
    "capacity_md": 36, "original_total_md": 113.27, "rate_per_pm": None, "currency": None,
}
cr_path = DOCS / "C7_change-request" / f"{P}_CR-001_input.json"
cr_path.parent.mkdir(parents=True, exist_ok=True)
cr_path.write_text(json.dumps(cr, ensure_ascii=False, indent=2), encoding="utf-8")
_r = sh([str(REPO / "skills/c7-change-request/scripts/cr_impact.py"), str(cr_path), "--context", ctx_path, "--format", "md"])
(DOCS / "C7_change-request" / f"{P}_CR-001_Impact_Summary.md").write_text(_r.stdout, encoding='utf-8')

# C8: smoke test trên stub staging (đúng hợp đồng API A4: /health 200, /api/v1/leave-requests không token → 401)
class _Stub(_hs.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            body, code = b'{"status":"ok"}', 200
        elif self.path.startswith("/api/v1/leave-requests") and "Authorization" not in self.headers:
            body, code = '{"error":{"code":"ERR-AUTH-003","message":"認証が必要です"}}'.encode('utf-8'), 401
        else:
            body, code = '{"error":{"code":"ERR-SYS-404","message":"not found"}}'.encode('utf-8'), 404
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
    def log_message(self, *a):
        pass
_srv = _hs.ThreadingHTTPServer(("127.0.0.1", 0), _Stub)
_th.Thread(target=_srv.serve_forever, daemon=True).start()
smoke = {"base_url": f"http://127.0.0.1:{_srv.server_address[1]}", "checks": [
    {"id": "SMK-01", "name": "Health", "method": "GET", "path": "/health", "expect_status": 200, "max_latency_ms": 500, "expect_json_path": {"status": "ok"}},
    {"id": "SMK-02", "name": "未認証で一覧 → 401", "method": "GET", "path": "/api/v1/leave-requests", "expect_status": 401},
    {"id": "SMK-03", "name": "存在しないAPI → 404（想定）", "method": "GET", "path": "/api/v1/nothing", "expect_status": 404},
]}
smoke_path = DOCS / "C8_release-deployment" / f"{P}_smoke.json"
smoke_path.parent.mkdir(parents=True, exist_ok=True)
smoke_path.write_text(json.dumps(smoke, ensure_ascii=False, indent=2), encoding="utf-8")
_r = sh([str(REPO / "skills/c8-release-deployment/scripts/smoke_test_runner.py"), str(smoke_path), "--context", ctx_path, "--format", "md"])
(DOCS / "C8_release-deployment" / f"{P}_Smoke_Test_Runbook.md").write_text(_r.stdout, encoding='utf-8')
_srv.shutdown()

# ================================================================ A9 プロジェクトスケジュール（Excel）
import datetime as _dt
tl = json.loads((tl_dir / "timeline.json").read_text(encoding="utf-8"))
start = _dt.date.fromisoformat(S.ctx["project"]["start_date"])
weeks = int(S.ctx["settings"]["sprint_duration_weeks"])
n_sprints = int(tl["total_sprints"])
cap = float(tl["team_capacity_per_sprint"])
total_md = float(tl["total_md"])
ms_by_sprint = {}
for m in tl["milestones"]:
    ms_by_sprint.setdefault(int(m["sprint_end"]), []).append(f'{m["id"]} {m["name"]}')
plan_rows = []
remaining = total_md
for k in range(1, n_sprints + 1):
    planned = round(min(cap, remaining), 2)
    remaining = round(remaining - planned, 4)
    s_from = start + _dt.timedelta(days=(k - 1) * weeks * 7)
    s_to = s_from + _dt.timedelta(days=weeks * 7 - 3)
    r = 3 + k  # 行番号（ヘッダ3行目の次から）
    plan_rows.append({"no": k, "from": s_from.isoformat(), "to": s_to.isoformat(), "cap": cap, "plan": planned,
                      "cum": f"=SUM($E$4:E{r})",
                      "left": f"=ROUND('プロジェクト概要'!$B$8-F{r},2)",
                      "ms": " / ".join(ms_by_sprint.get(k, [])) or "—"})
gap_days = (_dt.date.fromisoformat(tl["go_live_target"]) - _dt.date.fromisoformat(tl["end_date"])).days
sched = {"title": "Project Timeline", "language": "ja", "sheets": [
    {"name": "プロジェクト概要", "title": "プロジェクト概要（スケジュール）",
     "subtitle": "値は project-context.json と A6 見積、timeline_calc.py の結果から算出",
     "columns": [{"key": "k", "header": "項目", "width": 30}, {"key": "v", "header": "値", "width": 40, "wrap": True}],
     "rows": [
         {"k": "開始日", "v": S.ctx["project"]["start_date"]},
         {"k": "想定終了日（計算）", "v": tl["end_date"]},
         {"k": "目標リリース日", "v": tl["go_live_target"]},
         {"k": "目標との差（週・正=余裕 / 負=遅延）", "v": round(gap_days / 7, 1)},
         {"k": "見積合計（MD）", "v": total_md},
         {"k": "チーム能力（MD/スプリント）", "v": cap},
         {"k": "スプリント期間（週）", "v": weeks},
         {"k": "基本スプリント数", "v": tl["base_sprints"]},
         {"k": "バッファスプリント数", "v": tl["buffer_sprints"]},
         {"k": "合計スプリント数", "v": n_sprints},
         {"k": "計算上の注意", "v": "\n".join(tl["warnings"]) if tl["warnings"] else "なし", "wrap": True},
     ]},
    {"name": "マイルストーン", "title": "マイルストーン",
     "subtitle": "M1〜M6。日付は所属スプリントの末日。顧客との合意日は別途確定",
     "columns": [{"key": "id", "header": "ID", "width": 8, "align": "center"}, {"key": "name", "header": "マイルストーン", "width": 28},
                 {"key": "sp", "header": "所属スプリント（末）", "width": 16, "align": "center"}, {"key": "date", "header": "日付", "width": 14, "align": "center"},
                 {"key": "note", "header": "判定基準", "width": 50, "wrap": True}],
     "rows": [{"id": m["id"], "name": m["name"], "sp": m["sprint_end"], "date": m["date"],
               "note": {"M1": "キックオフ・計画承認", "M2": "API凍結（A4 の api_spec.json 確定）", "M3": "全機能 実装完了（UT 合格）", "M4": "コードフリーズ（IT 完了）", "M5": "UAT 開始（顧客受入）", "M6": "本番リリース（Go/No-Go 合格）"}.get(m["id"], "")}
              for m in tl["milestones"]]},
    {"name": "スプリント計画", "title": "スプリント計画（工数の積み上げ）",
     "subtitle": "計画MD は能力の範囲で見積合計を順に配分。累計・残りは数式",
     "columns": [{"key": "no", "header": "スプリント", "width": 11, "align": "center"},
                 {"key": "from", "header": "開始日", "width": 12, "align": "center"},
                 {"key": "to", "header": "終了日", "width": 12, "align": "center"},
                 {"key": "cap", "header": "能力（MD）", "width": 12, "numfmt": "0.00", "align": "right"},
                 {"key": "plan", "header": "計画（MD）", "width": 12, "numfmt": "0.00", "align": "right"},
                 {"key": "cum", "header": "累計（MD）", "width": 12, "numfmt": "0.00", "align": "right"},
                 {"key": "left", "header": "残り（MD）", "width": 12, "numfmt": "0.00", "align": "right"},
                 {"key": "ms", "header": "マイルストーン", "width": 36, "wrap": True}],
     "rows": plan_rows,
     "total_row": {"label": "合計", "sum": ["plan"]}},
]}
save_xlsx(sched, "A9_project-timeline", f"{P}_Project_Timeline.xlsx")


# ================================================================ B3 詳細設計書 (docx)
B3_BLOCKS = [
    {"type": "h1", "text": "1. 目的・前提"},
    {"type": "p", "text": "本書は基本設計書（B2）の画面・機能を、実装者が迷わず実装・試験できる粒度に分解した詳細設計である。API の入出力は api_spec.json（A4）、テーブルは migration（A5）と一致させる。"},
    {"type": "bullets", "items": [
        "技術: NestJS（TypeScript）・PostgreSQL 16・JWT（access 15分 / refresh 7日）",
        "トランザクション: 承認・差戻しは 1 トランザクション（状態更新・承認履歴・監査ログ）",
        "排他制御: leave_requests.version による楽観ロック。更新は WHERE version = :expected、0 件なら 409"]},
    {"type": "h1", "text": "2. 状態遷移"},
    {"type": "table", "caption": "表 2-1 休暇申請の状態遷移", "columns": ["現在の状態", "イベント", "次の状態", "実行者・条件", "副作用"],
     "widths": [2.6, 3.4, 2.6, 4.8, 4.2], "rows": [
         ["draft（下書き）", "提出", "submitted", "申請者本人。必須項目が揃うこと", "承認ステップを生成（上長）"],
         ["submitted（承認待ち）", "承認", "approved", "承認者 または 代理者（期間内）", "承認履歴 + 監査ログ LEAVE_APPROVED"],
         ["submitted（承認待ち）", "差戻し", "rejected", "承認者 または 代理者。理由必須（1〜500字）", "承認履歴 + 監査ログ LEAVE_REJECTED"],
         ["rejected（差戻し）", "再提出", "submitted", "申請者本人。内容を修正", "承認ステップを再生成"],
         ["approved（承認済み）", "（変更不可）", "—", "取消は未実装（Q-03 未決）", "—"]]},
    {"type": "h1", "text": "3. 処理フロー（承認 API）"},
    {"type": "p", "text": "POST /api/v1/leave-requests/{id}/approve の処理。各ステップで失敗した場合は以降を実行せず、トランザクションをロールバックする。"},
    {"type": "table", "caption": "表 3-1 承認 API の処理手順", "columns": ["No.", "処理", "検査・内容", "失敗時の応答"],
     "widths": [1.2, 3.4, 8.0, 4.4], "rows": [
         ["1", "認証", "Authorization の JWT を検証（期限・署名）", "401 ERR-AUTH-003"],
         ["2", "ロール検査", "role が manager 以上であること", "403 ERR-APPR-001"],
         ["3", "申請の取得", "leave_requests を id で取得。存在しなければ 404", "404 ERR-SYS-404"],
         ["4", "承認権限", "申請者の上長 または 有効な代理（approver_delegations: valid_from ≤ 今日 ≤ valid_to）", "403 ERR-APPR-001"],
         ["5", "状態検査", "status = submitted", "409 ERR-APPR-002"],
         ["6", "更新（OCC）", "UPDATE ... SET status='approved', version=version+1 WHERE id=:id AND version=:v", "0 件 → 409 ERR-APPR-002（再読込を促す）"],
         ["7", "承認履歴", "approval_steps に INSERT（approver_id = 実行者、代理の場合も実行者）", "ロールバック"],
         ["8", "監査ログ", "audit_logs に LEAVE_APPROVED（個人情報は含めない）", "ロールバック"],
         ["9", "応答", "200 { data: { id, status } }", "—"]]},
    {"type": "h1", "text": "4. 入力検証仕様"},
    {"type": "table", "caption": "表 4-1 申請作成 API（POST /api/v1/leave-requests）の検証", "columns": ["項目", "規則", "違反時", "DB制約との対応"],
     "widths": [3.0, 7.0, 3.6, 3.4], "rows": [
         ["type", "leave_types.is_active = true のコードのみ", "400 ERR-VAL-001", "FK → leave_types(code)"],
         ["dateFrom / dateTo", "dateTo ≥ dateFrom。過去日は submit 不可（draft は可）", "400 ERR-VAL-002", "CHECK (date_to >= date_from)"],
         ["hours", "type = OVERTIME のとき必須。0 ≤ hours ≤ 24（小数2桁）", "400 ERR-VAL-001 / 422 ERR-LEAVE-002", "CHECK (hours BETWEEN 0 AND 24)"],
         ["reason", "0〜500 文字", "400 ERR-VAL-001", "VARCHAR(500)"],
         ["重複", "同一申請者の approved / submitted と期間が重なる", "409 ERR-LEAVE-001", "アプリ層で検査 + 業務ルール"]]},
    {"type": "h1", "text": "5. エラーマップ"},
    {"type": "table", "caption": "表 5-1 エラーコード一覧（基本設計の表 6-1 と一致）", "columns": ["コード", "HTTP", "発生条件", "利用者への表示"],
     "widths": [3.2, 1.6, 6.8, 5.4], "rows": [
         ["ERR-VAL-001", "400", "入力形式の不正（項目名を含む）", "入力欄直下に表示"],
         ["ERR-VAL-002", "400", "期間の逆転", "終了日欄の直下"],
         ["ERR-AUTH-001", "401", "社員番号・パスワードの不一致", "同じ文言（列挙防止）"],
         ["ERR-AUTH-002", "423", "連続5回失敗によるロック（10分）", "解除時刻を表示"],
         ["ERR-AUTH-003", "401", "アクセストークンの期限切れ・不正", "再ログインへ誘導"],
         ["ERR-LEAVE-001", "409", "期間の重複", "一覧へのリンク付き"],
         ["ERR-LEAVE-002", "422", "残業の事前承認なし（Q-02）", "残業時間欄の下"],
         ["ERR-APPR-001", "403", "承認権限なし（ロール・所有者・代理期間外）", "画面上部のバナー"],
         ["ERR-APPR-002", "409", "状態の不一致・楽観ロック失敗", "更新ボタン付きのバナー"],
         ["ERR-SYS-404 / 500", "404 / 500", "対象なし / 想定外", "500 は requestId を表示"]]},
    {"type": "h1", "text": "6. モジュール構成（NestJS）"},
    {"type": "table", "caption": "表 6-1 モジュールと責務", "columns": ["モジュール", "主なクラス", "責務", "依存"],
     "widths": [3.0, 5.0, 5.2, 3.8], "rows": [
         ["AuthModule", "AuthController / AuthService / TokenService", "ログイン、refresh（1回使い切り）、ロック", "UsersRepository"],
         ["LeaveModule", "LeaveController / LeaveService / LeaveStateMachine", "申請の作成・一覧・詳細・状態遷移", "LeaveRepository, LeaveTypeRepository"],
         ["ApprovalModule", "ApprovalController / ApprovalService / DelegationService", "承認・差戻し、代理の判定", "LeaveRepository, AuditService"],
         ["ReportModule", "ReportController / MonthlyCsvBuilder", "月次集計と Shift_JIS 出力（Q-04）", "LeaveRepository, UsersRepository"],
         ["AuditModule", "AuditService", "監査ログの追記（削除・更新は不可）", "AuditRepository"]]},
    {"type": "h1", "text": "7. 試験との対応"},
    {"type": "p", "text": "各処理ステップ・検証規則・エラーコードは試験計画（A8 テストケース）の『関連API』『関連テーブル』と対応する。例: APPR-API-001 は表 3-1 の手順 1〜9 を、APPR-CON-001 は手順 6（OCC）を検証する。"},
    {"type": "h1", "text": "8. 未決事項"},
    {"type": "bullets", "items": [
        "Q-03（承認済みの取消）が決まるまで、approved からの遷移は設計しない（表 2-1）。",
        "Q-04（CSV の文字コード・列順）が決まるまで、ReportModule の列定義は仮。"]},
]
b3_out = dbuild({"language": "ja", "title": "詳細設計書", "subtitle": S.ctx["project"]["name"],
                 "meta": [["版", "1.0（顧客レビュー版）"], ["作成日", S.ctx["created_at"]], ["作成者", "[担当者]"], ["承認者（社内）", "[担当者]"],
                          ["注記", "架空の教材案件。実在の企業・人物と無関係"]],
                 "header_text": "勤怠承認システム（サンプル） 詳細設計書 v1.0", "footer_text": "社外秘", "blocks": B3_BLOCKS},
                DOCS / "B3_detail-design" / f"{P}_Detail_Design_v1.docx")
print("docx B3 →", b3_out)


# ================================================================ Giai đoạn 2 (B0, B1, X1, X4)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import phase2_business  # noqa: E402
_p2 = phase2_business.run(S, DOCS, REPO, P, sh)
print("phase2 business:", _p2)
print("phase2 ops:", phase2_ops.run(S, DOCS, REPO, P, sh))
