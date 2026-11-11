# -*- coding: utf-8 -*-
"""phase2_ops.py — D1 (引継書・Runbook), D2 (検収書・UAT), D3 (マニュアル), X2/X3/X5/X7, báo cáo C5–C8 → docx,
và sheet 'API詳細' (A4). Dữ liệu mẫu hư cấu; giá trị không có trong nguồn được ghi rõ là mẫu."""
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _dbuild(spec, out):
    from docx_build import build
    out.parent.mkdir(parents=True, exist_ok=True)
    return build(spec, out)


def _xbuild(spec, out):
    from xlsx_build import build
    out.parent.mkdir(parents=True, exist_ok=True)
    return build(spec, out)


# ---------------------------------------------------------------- API詳細 (A4)
def _split_top(s):
    """Tách danh sách theo dấu phẩy ở mức ngoài cùng (không tách trong ngoặc)."""
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "([{（":
            depth += 1
        elif ch in ")]}）":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip()); cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def api_detail_sheet(APIS):
    rows = []
    for r in APIS:
        endpoint = r[2] + " /api/v1" + r[3].replace("/api/v1", "", 1)
        if r[5] == "Y":
            rows.append({"ep": endpoint, "kind": "header", "name": "Authorization", "type": "Bearer <accessToken>", "req": "必須", "note": "アクセストークン（JWT）"})
        for part in r[7].split(";"):
            part = part.strip()
            m = re.match(r"^(params|query|body):\s*(.*)$", part)
            if not m:
                continue
            kind, items = m.group(1), m.group(2)
            for it in _split_top(items):
                mm = re.match(r"^([A-Za-z_][\w]*)\s*\((.*)\)\s*$", it)
                if mm:
                    name, spec_txt = mm.group(1), mm.group(2)
                else:
                    name, spec_txt = it, ""
                req = "任意" if "任意" in spec_txt else "必須"
                if kind == "params":
                    req = "必須"
                rows.append({"ep": endpoint, "kind": kind, "name": name, "type": spec_txt.replace("任意", "").strip(" ,"), "req": req, "note": ""})
        out_items = r[8]
        m2 = re.search(r"\{(.*)\}", out_items)
        if m2:
            for it in _split_top(m2.group(1)):
                mm2 = re.match(r"^([A-Za-z_]\w*)\s*(?:\((.*)\))?\s*$", it)
                rname, rtype = (mm2.group(1), (mm2.group(2) or "")) if mm2 else (it, "")
                rows.append({"ep": endpoint, "kind": "response", "name": rname, "type": rtype, "req": "—", "note": f"成功 {r[9]}"})
    return {"name": "API詳細", "title": "API詳細（項目単位の定義）",
            "subtitle": "API一覧（エンドポイント単位）の各リクエスト・レスポンス項目を分解。型・制約は API 一覧の記述に基づく",
            "columns": [{"key": "ep", "header": "エンドポイント", "width": 40},
                        {"key": "kind", "header": "区分", "width": 12, "align": "center", "validate": ["header", "params", "query", "body", "response"]},
                        {"key": "name", "header": "項目名", "width": 22},
                        {"key": "type", "header": "型・制約", "width": 36, "wrap": True},
                        {"key": "req", "header": "必須", "width": 9, "align": "center"},
                        {"key": "note", "header": "備考", "width": 30, "wrap": True}],
            "rows": rows}


# ---------------------------------------------------------------- markdown → docx (C5–C8 reports)
def md_to_blocks(text):
    blocks, table = [], []

    def flush_table():
        nonlocal table
        if not table:
            return
        rows = [[c.strip() for c in ln.strip().strip("|").split("|")] for ln in table if not re.match(r"^\|?\s*:?-{2,}", ln.strip())]
        if rows:
            blocks.append({"type": "table", "columns": rows[0], "rows": rows[1:]})
        table = []

    for raw in text.splitlines():
        line = raw.rstrip()
        if line.strip().startswith("|"):
            table.append(line)
            continue
        flush_table()
        if not line.strip():
            continue
        if line.startswith("### "):
            blocks.append({"type": "h2", "text": line[4:].strip()})
        elif line.startswith("## ") or line.startswith("# "):
            blocks.append({"type": "h1", "text": line.lstrip("#").strip()})
        elif line.lstrip().startswith("- "):
            blocks.append({"type": "bullets", "items": [line.lstrip()[2:].strip()]})
        else:
            blocks.append({"type": "p", "text": line.strip()})
    flush_table()
    # gộp bullet liên tiếp
    merged = []
    for b in blocks:
        if b["type"] == "bullets" and merged and merged[-1]["type"] == "bullets":
            merged[-1]["items"].extend(b["items"])
        else:
            merged.append(b)
    return merged


def run(S, DOCS, REPO, P, sh):
    ctx = S.ctx
    name = ctx["project"]["name"]
    client = ctx["project"]["client"]
    today = ctx["created_at"]
    tl = json.loads((DOCS / "A9_project-timeline" / "timeline.json").read_text(encoding="utf-8"))

    # ================================================================ D1 引継書
    d1_dir = DOCS / "D1_handover-doc"
    incidents = [
        ("INC-01", "全員がログインできない（ERR-AUTH 系が多発）", "P1", "GET /health を確認。DB 接続（連続失敗の増加）を確認し、認証サービスを再起動", "当番エンジニア（BE）", "PM → 情報システム責任者", "1 時間", "運用手順 9.1"),
        ("INC-02", "申請が保存できない（500 が増加）", "P2", "requestId でログを検索。DB のロック待ちを確認。必要ならアプリを再起動", "当番エンジニア（BE）", "PM", "4 時間", "運用手順 9.2"),
        ("INC-03", "承認・差戻しが反映されない（409 が連発）", "P2", "承認画面の再読込を案内。監査ログで二重処理がないか確認（APPR-CON-001）", "当番エンジニア（BE）", "PM", "4 時間", "運用手順 9.3"),
        ("INC-04", "月次CSVの出力がタイムアウト", "P3", "対象期間を分割して再出力。夜間に実行。集計クエリの実行計画を確認", "当番エンジニア（BE）", "PM", "1 営業日", "運用手順 9.4"),
        ("INC-05", "日次バックアップが失敗", "P2", "バックアップのログを確認。保存先の空き容量を確認。手動で再実行（pg_dump）", "当番エンジニア（BE）", "PM", "4 時間", "運用手順 9.5"),
        ("INC-06", "TLS 証明書の期限切れ警告", "P1", "証明書を更新（期限の 14 日前に更新作業を開始）。ロードバランサの設定を確認", "当番エンジニア（インフラ）", "PM → 情報システム責任者", "1 時間", "運用手順 9.6"),
    ]
    slo = [
        ("可用性", "平日 8:00–20:00 の稼働率 ≥ 99.5%（月次）", "NFR-AVAIL-01", "Grafana の稼働率"),
        ("API 応答時間", "p95 ≤ 800 ms（申請一覧）", "NFR-PERF-01", "Prometheus histogram"),
        ("エラー率", "5xx の割合 < 0.5%（5分窓）", "—", "Prometheus"),
        ("RPO（目標復旧時点）", "24 時間（日次バックアップ）", "—", "バックアップ監査"),
        ("RTO（目標復旧時間）", "4 時間（P2 以上）", "—", "インシデント記録"),
    ]
    known = [
        ("KI-01", "承認済み申請の取消（撤回）は未実装", "Q-03 の回答待ち（対象外）", "Low", "2027-03-31 までに決定"),
        ("KI-02", "月次CSVの文字コードと列順は仮仕様", "Q-04 の回答待ち", "Medium", "2027-01-22 までに決定"),
        ("KI-03", "通知の仕組みは対象外（メールでの連絡を運用で代替）", "対象外（SOW 第4条）", "Low", "—"),
        ("KI-04", "レポートの日付範囲検索にインデックス未整備（health_check W09 の提案）", "負荷試験で確認後に対応", "Low", "次のスプリント"),
    ]
    h1 = [
        {"type": "h1", "text": "1. エグゼクティブサマリー"},
        {"type": "p", "text": f"本書は {name} の引継書です。運用担当が本番の構成・手順・連絡先を把握し、障害に一次対応できることを目的とします。"},
        {"type": "bullets", "items": ["本番リリース: 2027-03-15（予定）", "主な機能: 認証、休暇・残業申請、承認・差戻し、承認者代理、月次CSV出力", "既知の問題: 4件（第11章）。重大（Critical/High）は 0 件"]},
        {"type": "h1", "text": "2. システム構成"},
        {"type": "p", "text": "ブラウザ（Chrome/Edge）→ 画面（Next.js）→ API（NestJS, /api/v1）→ PostgreSQL 16。認証は JWT（access 15分・refresh 7日）。配備は Docker（VM 1台、STG と本番で同構成）。"},
        {"type": "h1", "text": "3. 技術スタック"},
        {"type": "table", "columns": ["領域", "採用技術", "備考"], "widths": [3.6, 6.4, 6.0], "rows": [
            ["バックエンド", ctx["tech_stack"]["backend"], ""], ["データベース", ctx["tech_stack"]["database"], "日次バックアップ（pg_dump）"],
            ["認証", ctx["tech_stack"]["auth"], "パスワードは Argon2id"], ["配備", ctx["tech_stack"]["hosting"], ""],
            ["CI/CD", ctx["tech_stack"]["ci_cd"], "main への merge で STG へ自動配備"], ["監視", ctx["tech_stack"]["monitoring"], "稼働率・応答時間・エラー率"]]},
        {"type": "h1", "text": "4. 環境一覧"},
        {"type": "table", "columns": ["環境", "用途", "URL（参照先）", "データ"], "widths": [2.6, 4.6, 5.2, 4.6], "rows": [
            ["STG（検証）", "試験・UAT・デモ", "links.staging_url（PM に確認）", "テストデータのみ"],
            ["本番", "業務運用", "links.production_url（PM に確認）", "実データ（個人情報を含む）"]]},
        {"type": "h1", "text": "5. デプロイ手順"},
        {"type": "numbered", "items": ["main に merge → CI が UT・Security scan を実行", "STG へ自動配備 → smoke_test_runner.py（c8）で疎通確認", "Go/No-Go 会議で承認 → 本番へ canary（5%）→ 全体の順で配備", "migration は Expand → Migrate → Contract（DB設計書 参照）", "リリース後 60 分は監視を強化（ハイパーケア）"]},
        {"type": "h1", "text": "6. データベース概要"},
        {"type": "p", "text": f"テーブル {len(S.TABLES)} 件（users, departments, leave_types, leave_requests, approval_steps, approver_delegations, auth_sessions, audit_logs）。詳細は DB 設計書（A5）を参照。"},
        {"type": "h1", "text": "7. API 概要"},
        {"type": "p", "text": f"エンドポイント {len(S.APIS)} 件。詳細は API 設計書（A4）と api_spec.json を参照。エラーは共通形式 {{ error: {{ code, message }} }}。"},
        {"type": "h1", "text": "8. 主要な業務フロー（運用者向け）"},
        {"type": "bullets", "items": ["申請 → 承認待ち → 承認 または 差戻し（理由必須）", "残業は事前承認が必須（Q-02）", "月次CSV は人事が部門と年月を指定して出力"]},
        {"type": "h1", "text": "9. 障害対応（Runbook 要約）"},
        {"type": "p", "text": "インシデントごとに ID（INC-NN）で管理します。詳細手順は Runbook.md と Runbook_Matrix シートを参照。"},
        {"type": "table", "caption": "表 9-1 インシデント一覧（Runbook_Matrix と一致）", "columns": ["ID", "事象", "重大度", "一次対応", "担当", "目標復旧"], "widths": [1.8, 4.6, 1.6, 5.2, 2.6, 1.8],
         "rows": [[i[0], i[1], i[2], i[3], i[4], i[6]] for i in incidents]},
        {"type": "h1", "text": "10. 監視・アラート・SLO"},
        {"type": "table", "caption": "表 10-1 SLO", "columns": ["指標", "目標", "関連 NFR", "測定"], "widths": [3.2, 6.0, 3.2, 4.6], "rows": [list(s) for s in slo]},
        {"type": "bullets", "items": ["P1 のアラートは当番者へ即時通知（15 分以内に確認）", "P2 は当番者へ通知（4 時間以内）", "夜間の P1 は PM へエスカレーション"]},
        {"type": "h1", "text": "11. 既知の問題・技術的負債"},
        {"type": "table", "caption": "表 11-1 既知の問題", "columns": ["ID", "内容", "状況", "重大度", "期限"], "widths": [1.6, 6.6, 4.0, 1.8, 3.0], "rows": [list(k) for k in known]},
        {"type": "h1", "text": "12. 連絡先・エスカレーション"},
        {"type": "table", "caption": "表 12-1 連絡先（担当者名は PM が記入）", "columns": ["役割", "担当", "連絡方法", "対応時間"], "widths": [3.4, 4.0, 5.2, 4.4], "rows": [
            ["PM（一次エスカレーション）", "[担当者]", "社内チャット → 電話", "平日 9–18 時"],
            ["当番エンジニア（BE）", "[担当者]", "オンコール携帯", "24 時間（P1）"],
            ["顧客 情報システム責任者", "[担当者]", "電話", "平日 9–18 時"]]},
        {"type": "h1", "text": "付録 A. インシデント事後レビュー（ポストモーテム）テンプレート"},
        {"type": "table", "columns": ["項目", "内容"], "widths": [4.0, 12.0], "rows": [
            ["インシデント ID", "INC-NN"], ["発生日時 / 検知日時 / 復旧日時", ""], ["影響（利用者数・業務への影響）", ""],
            ["根本原因（責任追及ではなく仕組みの原因）", ""], ["タイムライン", ""], ["再発防止策（担当・期限）", ""], ["学んだこと", ""]]},
        {"type": "h1", "text": "付録 B. 引継ぎ確認"},
        {"type": "table", "columns": ["確認項目", "担当", "確認日", "署名"], "widths": [7.0, 3.0, 3.0, 3.0], "rows": [
            ["本番アクセス権の引継ぎ", "[担当者]", "", ""], ["バックアップの復元テスト（1回以上）", "[担当者]", "", ""], ["Runbook の読み合わせ", "[担当者]", "", ""]]},
    ]
    _dbuild({"language": "ja", "title": "引継書（運用・保守）", "subtitle": name,
             "meta": [["版", "1.0（本番リリース版）"], ["作成日", today], ["作成者", "[担当者]"], ["承認者（顧客）", "[担当者]"], ["注記", "架空の教材案件"]],
             "header_text": f"{name} 引継書 v1.0", "footer_text": "社外秘", "blocks": h1},
            d1_dir / f"{P}_Handover.docx")
    _xbuild({"title": "Handover Workbook", "language": "ja", "sheets": [
        {"name": "環境一覧", "title": "環境一覧（Environment Inventory）", "subtitle": "URL・アカウントは記載しない（PM が別途管理）",
         "columns": [{"key": "env", "header": "環境", "width": 14}, {"key": "host", "header": "配備先", "width": 30}, {"key": "db", "header": "DB", "width": 22},
                     {"key": "note", "header": "備考", "width": 46, "wrap": True}],
         "rows": [{"env": "STG", "host": "Docker（VM 1台）", "db": "PostgreSQL 16", "note": "テストデータのみ"},
                  {"env": "本番", "host": "Docker（VM 1台）", "db": "PostgreSQL 16", "note": "実データ。バックアップ 日次"}]},
        {"name": "Runbook_Matrix", "title": "Runbook マトリクス（インシデント一覧）", "subtitle": "INC-NN。重大度: P1 即時 ／ P2 当日 ／ P3 翌営業日",
         "columns": [{"key": "id", "header": "INC-ID", "width": 10, "align": "center"}, {"key": "ev", "header": "事象", "width": 36, "wrap": True},
                     {"key": "sev", "header": "重大度", "width": 9, "align": "center", "validate": ["P1", "P2", "P3"]},
                     {"key": "first", "header": "一次対応", "width": 52, "wrap": True}, {"key": "own", "header": "担当", "width": 22},
                     {"key": "esc", "header": "エスカレーション", "width": 24, "wrap": True}, {"key": "rto", "header": "目標復旧（RTO）", "width": 14, "align": "center"},
                     {"key": "ref", "header": "参照", "width": 14}],
         "rows": [{"id": i[0], "ev": i[1], "sev": {"value": i[2], "align": "center", "fill": "FDE9E7" if i[2] == "P1" else ("FFF2CC" if i[2] == "P2" else "E2EFDA")},
                   "first": i[3], "own": i[4], "esc": i[5], "rto": i[6], "ref": i[7]} for i in incidents]},
        {"name": "SLO", "title": "SLO・SLI", "subtitle": "目標値は NFR（A2）と一致。測定方法を明記",
         "columns": [{"key": "a", "header": "指標", "width": 24}, {"key": "b", "header": "目標", "width": 48, "wrap": True},
                     {"key": "c", "header": "関連 NFR", "width": 16}, {"key": "d", "header": "測定", "width": 30}],
         "rows": [{"a": s[0], "b": s[1], "c": s[2], "d": s[3]} for s in slo]},
        {"name": "Known_Issues", "title": "既知の問題・技術的負債", "subtitle": "Critical/High は 0 件（リリース判定の条件）",
         "columns": [{"key": "id", "header": "ID", "width": 9, "align": "center"}, {"key": "t", "header": "内容", "width": 52, "wrap": True},
                     {"key": "s", "header": "状況", "width": 34, "wrap": True}, {"key": "sev", "header": "重大度", "width": 10, "align": "center", "validate": ["Critical", "High", "Medium", "Low"]},
                     {"key": "due", "header": "期限", "width": 18}],
         "rows": [{"id": k[0], "t": k[1], "s": k[2], "sev": k[3], "due": k[4]} for k in known]},
        {"name": "連絡先", "title": "連絡先・エスカレーション", "subtitle": "氏名・電話は PM が記入",
         "columns": [{"key": "r", "header": "役割", "width": 30}, {"key": "p", "header": "担当", "width": 18}, {"key": "c", "header": "連絡方法", "width": 30}, {"key": "h", "header": "対応時間", "width": 20}],
         "rows": [{"r": "PM（一次エスカレーション）", "p": "[担当者]", "c": "社内チャット → 電話", "h": "平日 9–18 時"},
                  {"r": "当番エンジニア（BE）", "p": "[担当者]", "c": "オンコール携帯", "h": "24 時間（P1）"},
                  {"r": "顧客 情報システム責任者", "p": "[担当者]", "c": "電話", "h": "平日 9–18 時"}]},
    ]}, d1_dir / f"{P}_Handover_Workbook.xlsx")
    runbook = ["# Runbook（運用手順 cheat sheet）— " + name, "", "> 版 1.0 ／ 詳細は Handover.docx 第9章。事象 ID は INC-NN。", ""]
    for i in incidents:
        runbook += [f"## {i[0]}: {i[1]}（重大度 {i[2]}・目標復旧 {i[6]}）", f"- 一次対応: {i[3]}", f"- 担当: {i[4]} ／ エスカレーション: {i[5]}", ""]
    runbook += ["## 日常点検（毎朝）", "- Grafana で稼働率・エラー率を確認", "- 前日のバックアップが成功したことを確認", "- 証明書の有効期限を確認（残り 30 日未満で警告）", ""]
    (d1_dir / f"{P}_Runbook.md").write_text("\n".join(runbook) + "\n", encoding="utf-8")

    # ================================================================ D2 検収
    uat_rows = [
        ("UAT-01", "一般社員が有給を提出し、承認者が承認する", "一般社員・承認者", "合", "2027-03-03"),
        ("UAT-02", "承認者が理由付きで差戻し、社員が修正して再提出する", "承認者・一般社員", "合", "2027-03-03"),
        ("UAT-03", "承認者が不在の期間、代理者が承認し、期間後は承認できないことを確認", "承認者・代理者", "合", "2027-03-04"),
        ("UAT-04", "人事が当月の勤怠CSVを出力し、既存取込ツールで読み込める", "人事", "合（保留事項あり）", "2027-03-04"),
    ]
    punch = [
        ("PUNCH-01", "申請一覧の日付表示が YYYY-MM-DD と和暦が混在", "Medium", "表示の統一。機能に影響なし", "一覧の日付形式を YYYY/MM/DD に統一", "FE", "2027-03-12", "", "open"),
        ("PUNCH-02", "承認完了のトースト通知が 1 秒で消える", "Low", "読み取りにくい。機能に影響なし", "表示時間を 3 秒に延長", "FE", "2027-03-12", "", "open"),
        ("PUNCH-03", "代理期間が 31 日のときのエラー文言が分かりにくい", "Medium", "操作の迷いが出る", "文言を「代理期間は最長30日です」に変更", "BE", "2027-03-12", "", "open"),
    ]
    d2_dir = DOCS / "D2_uat-acceptance"
    cert = [
        {"type": "h1", "text": "1. 対象"},
        {"type": "p", "text": f"{name}（基本設計書 v1.0・詳細設計書 v1.0・SOW 第3条の機能範囲）。"},
        {"type": "h1", "text": "2. 実施概要"},
        {"type": "p", "text": "顧客（一般社員・承認者・人事の代表）が、STG 環境で受入試験（UAT）を 2027-03-03〜03-04 に実施しました。"},
        {"type": "table", "caption": "表 2-1 UAT の結果", "columns": ["ID", "業務シナリオ", "実施者", "結果"], "widths": [2.0, 8.0, 3.8, 3.2],
         "rows": [[u[0], u[1], u[2], u[3]] for u in uat_rows]},
        {"type": "h1", "text": "3. 検収の判定"},
        {"type": "p", "text": "全 4 シナリオの業務要件を満たすことを確認しました。重大（Critical/High）な欠陥は 0 件です。軽微な指摘 3 件（第4章）は保留事項として記録し、検収後の保証期間内に修補します。"},
        {"type": "h1", "text": "4. 保留事項（軽微な指摘）"},
        {"type": "table", "caption": "表 4-1 保留事項", "columns": ["ID", "内容", "重大度", "修補期限"], "widths": [2.0, 8.0, 2.4, 3.6],
         "rows": [[p_[0], p_[1], p_[2], p_[6]] for p_ in punch]},
        {"type": "h1", "text": "5. 検収の条件・保証"},
        {"type": "bullets", "items": [
            "検収後の保証期間は 3 か月（SOW 第10条・サンプル値）。期間中は仕様と合致しない不具合を無償で修補します。",
            "保留事項の修補完了は、顧客の確認をもって完了とします。",
            "本検収書の交付により、SOW 第6条の検収が完了し、第7条の最終支払の請求が可能となります。"]},
        {"type": "h1", "text": "6. 署名"},
        {"type": "table", "columns": ["", "顧客（検収者）", "受注者（PM）"], "widths": [3.0, 7.0, 7.0], "rows": [
            ["会社名", client, "[担当者]"], ["役職・氏名", "[担当者]", "[担当者]"], ["署名・押印", "", ""], ["日付", "2027-03-05", "2027-03-05"]]},
    ]
    _dbuild({"language": "ja", "title": "検収書（受入確認書）", "subtitle": name,
             "meta": [["版", "1.0"], ["作成日", "2027-03-05"], ["注記", "架空の教材案件。署名欄は記入前の状態で保存"]],
             "header_text": f"{name} 検収書", "footer_text": "社外秘", "blocks": cert},
            d2_dir / f"{P}_UAT_Acceptance_Certificate.docx")
    _xbuild({"title": "UAT SignOff Workbook", "language": "ja", "sheets": [
        {"name": "UAT_Checklist", "title": "UAT チェックリスト（結果）", "subtitle": "結果: 合 / 否 / 保留。『否』は欠陥を起票し、再試験後に記録",
         "columns": [{"key": "id", "header": "ID", "width": 10, "align": "center"}, {"key": "sc", "header": "業務シナリオ", "width": 56, "wrap": True},
                     {"key": "who", "header": "実施者", "width": 22}, {"key": "res", "header": "結果", "width": 18, "align": "center", "validate": ["合", "否", "保留", "合（保留事項あり）"]},
                     {"key": "dt", "header": "実施日", "width": 13, "align": "center"}],
         "rows": [{"id": u[0], "sc": u[1], "who": u[2], "res": u[3], "dt": u[4]} for u in uat_rows]},
        {"name": "Punch_List_Minor_Defects", "title": "保留事項（Punch List）", "subtitle": "Medium / Low のみ。Critical/High はこのシートに置けない（リリース前に修正）",
         "columns": [{"key": "a", "header": "Mã", "width": 11, "align": "center"}, {"key": "b", "header": "Mô tả", "width": 42, "wrap": True},
                     {"key": "c", "header": "Severity", "width": 11, "align": "center", "validate": ["Medium", "Low"]},
                     {"key": "d", "header": "Ảnh hưởng", "width": 30, "wrap": True}, {"key": "e", "header": "Kế hoạch khắc phục", "width": 40, "wrap": True},
                     {"key": "f", "header": "Fix owner", "width": 12, "align": "center"}, {"key": "g", "header": "Hạn (ngày)", "width": 13, "align": "center"},
                     {"key": "h", "header": "BUG ref", "width": 12, "align": "center"}, {"key": "i", "header": "Trạng thái", "width": 12, "align": "center", "validate": ["open", "in progress", "done"]}],
         "rows": [{"a": p_[0], "b": p_[1], "c": p_[2], "d": p_[3], "e": p_[4], "f": p_[5], "g": p_[6], "h": p_[7], "i": p_[8]} for p_ in punch]},
        {"name": "Warranty_Scope", "title": "保証の範囲", "subtitle": "SOW 第10条の要約（期間はサンプル値）",
         "columns": [{"key": "k", "header": "項目", "width": 22}, {"key": "v", "header": "内容", "width": 70, "wrap": True}],
         "rows": [{"k": "保証期間", "v": "検収完了日から 3 か月（サンプル値）"}, {"k": "対象", "v": "仕様（承認済み設計書）との不一致による不具合"},
                  {"k": "対象外", "v": "顧客による仕様外の改変、環境変更、第三者製品の不具合"},
                  {"k": "重大な不具合", "v": "業務停止: 受付から 1 営業日以内に一次対応"}]},
    ]}, d2_dir / f"{P}_UAT_SignOff_Workbook.xlsx")
    # punch_list_to_backlog (script thật)
    wb_path = d2_dir / f"{P}_UAT_SignOff_Workbook.xlsx"
    sh([str(REPO / "skills/d2-uat-acceptance/scripts/punch_list_to_backlog.py"), str(wb_path), "--out", str(d2_dir / "punch_list_warranty_backlog.json"), "--project", name])

    # ================================================================ D3 マニュアル
    faq = [
        ("申請を間違えて提出しました。取り消せますか？", "現時点では取消（撤回）機能はありません（Q-03 の回答待ち）。承認者に差戻しを依頼してください。"),
        ("承認者が休暇中です。どうすればよいですか？", "承認者は「承認者代理設定」で代理者と期間（最長30日）を登録します。代理者が承認できます。"),
        ("残業申請が提出できません（422）。", "残業は事前承認が必要です。上長に事前承認を依頼し、承認後に提出してください。"),
        ("パスワードを忘れました。", "人事に連絡してください。初回ログイン時にパスワードを変更します。"),
        ("CSVを開くと文字化けします。", "人事の取込仕様に合わせて文字コードを選んでください（Q-04 の決定後に既定値を確定します）。"),
    ]
    errors = [
        ("ERR-AUTH-001", "社員番号またはパスワードが正しくありません", "入力を確認してください。5回失敗すると10分間ロックされます。"),
        ("ERR-AUTH-002", "アカウントがロックされています", "表示された時刻以降に再度ログインするか、人事に連絡してください。"),
        ("ERR-LEAVE-001", "同じ期間に申請が存在します", "既存の申請を一覧で確認してください。"),
        ("ERR-LEAVE-002", "残業は事前承認が必要です", "上長に事前承認を依頼してください。"),
        ("ERR-APPR-002", "申請の状態が変更されました", "画面を更新して最新の状態を確認してください。"),
    ]
    user_manual = [
        {"type": "h1", "text": "1. はじめに"},
        {"type": "p", "text": "このマニュアルは、勤怠承認システムで休暇・残業を申請し、承認を受ける方（一般社員・承認者）向けです。"},
        {"type": "h1", "text": "2. ログイン"},
        {"type": "numbered", "items": ["ブラウザで画面 SCR-01（ログイン）を開きます。", "社員番号（6桁）とパスワード（12文字以上）を入力します。", "「ログイン」を押します。"]},
        {"type": "p", "text": "5回続けて入力を間違えると、10分間ログインできなくなります。"},
        {"type": "h1", "text": "3. 休暇・残業を申請する（SCR-02）"},
        {"type": "numbered", "items": ["申請一覧（SCR-03）で「新規作成」を押します。", "休暇種別（有給・特別・代休・慶弔）を選びます。", "開始日と終了日を入力します。", "残業の場合は残業時間（0〜24時間）を入力します。", "理由を入力します（500文字まで）。", "一時保存する場合は「下書き保存」、申請する場合は「提出」を押します。"]},
        {"type": "h1", "text": "4. 申請の状態を確認する（SCR-03・SCR-04）"},
        {"type": "bullets", "items": ["状態: 下書き・承認待ち・承認済み・差戻し", "絞り込みは状態・期間で行えます。", "行を選ぶと詳細（SCR-04）と承認履歴を確認できます。"]},
        {"type": "h1", "text": "5. 承認者の操作（SCR-05）"},
        {"type": "numbered", "items": ["承認待ち一覧を開きます。", "申請を選んで内容を確認します。", "「承認」、または理由を入力して「差戻し」を押します（差戻しの理由は必須）。"]},
        {"type": "h1", "text": "6. 承認者代理の設定（SCR-06）"},
        {"type": "p", "text": "不在の期間は代理者を設定します。期間は最長30日です。設定した期間の外では、代理者は承認できません。"},
        {"type": "h1", "text": "7. 画面の対応表"},
        {"type": "table", "caption": "表 7-1 画面一覧", "columns": ["画面ID", "画面名", "主な操作"], "widths": [2.4, 5.0, 9.6], "rows": [
            ["SCR-01", "ログイン", "社員番号・パスワードで認証"], ["SCR-02", "申請作成", "休暇・残業を申請（下書き・提出）"], ["SCR-03", "申請一覧", "自分の申請を絞り込み"],
            ["SCR-04", "申請詳細", "内容と承認履歴の確認"], ["SCR-05", "承認待ち一覧", "承認・差戻し（承認者）"], ["SCR-06", "承認者代理設定", "代理者の登録"], ["SCR-07", "月次勤怠CSV", "人事が CSV を出力"]]},
        {"type": "p", "text": "画面キャプチャは検収版（v1.0）で各手順に挿入します。"},
        {"type": "h1", "text": "8. よくある質問"},
        {"type": "table", "columns": ["質問", "回答"], "widths": [6.0, 10.0], "rows": [list(f) for f in faq]},
        {"type": "h1", "text": "9. エラーと対処"},
        {"type": "table", "caption": "表 9-1 エラーメッセージ", "columns": ["コード", "表示される内容", "対処"], "widths": [3.2, 6.0, 6.8], "rows": [list(e) for e in errors]},
        {"type": "h1", "text": "10. 用語集"},
        {"type": "table", "columns": ["用語", "意味"], "widths": [4.0, 12.0], "rows": [
            ["差戻し", "承認者が理由を付けて申請者へ戻すこと"], ["代理者", "不在の承認者に代わって承認する人"], ["下書き", "提出前の申請"], ["CSV", "カンマ区切りのテキスト形式（人事の取込用）"]]},
    ]
    _dbuild({"language": "ja", "title": "利用者マニュアル", "subtitle": name, "meta": [["版", "1.0"], ["対象", "一般社員・承認者"]],
             "header_text": f"{name} 利用者マニュアル", "footer_text": "社内", "blocks": user_manual},
            DOCS / "D3_user-guide-manual" / f"{P}_User_Manual_EndUser.docx")
    admin = [
        {"type": "h1", "text": "1. 役割と権限"},
        {"type": "table", "columns": ["役割", "できること"], "widths": [3.6, 12.4], "rows": [
            ["employee（一般）", "申請の作成・一覧・詳細"], ["manager（上長）", "一般の操作 + 承認・差戻し、代理者の設定"], ["hr（人事）", "月次勤怠CSVの出力、アカウントの管理"]]},
        {"type": "h1", "text": "2. マスタ管理"},
        {"type": "p", "text": "休暇種別（leave_types）は、利用可否（is_active）で管理します。新しい種別はマスタに追加するだけで利用できます（コード変更は不要）。廃止する種別は is_active を false にします。既存の申請は変更されません。"},
        {"type": "h1", "text": "3. アカウント管理"},
        {"type": "bullets", "items": ["新規社員の登録: 人事がマスタに登録し、初期パスワードを社内メールで通知します（Q-06）。", "ロック解除: 人事が解除します（ロック中は10分で自動解除）。", "退職者: 退職後5年で個人情報を削除します（NFR-PRIV-01）。"]},
        {"type": "h1", "text": "4. 月次勤怠CSVの出力"},
        {"type": "numbered", "items": ["SCR-07 を開きます。", "部門と年月（YYYY-MM）を選びます。", "「出力」を押し、CSV をダウンロードします。", "人事の取込ツールで読み込み、件数を確認します。"]},
        {"type": "h1", "text": "5. 監査ログ"},
        {"type": "p", "text": "承認・差戻し・代理設定の履歴は監査ログに記録されます（削除・変更は不可）。確認は人事の管理画面で行います（検索条件: 期間、実行者、対象の申請 ID）。"},
        {"type": "h1", "text": "6. 障害時"},
        {"type": "p", "text": "引継書（Handover.docx）第9章の Runbook に従ってください。P1 は 1 時間以内に PM へ連絡します。"},
        {"type": "h1", "text": "7. よくある質問"},
        {"type": "table", "columns": ["質問", "回答"], "widths": [6.0, 10.0], "rows": [
            ["代理者の期間を延ばせますか？", "最長30日です（Q-01）。延長は期間が切れる前に再設定します。"],
            ["CSV の列を増やせますか？", "変更管理（SOW 第9条）の対象です。"]]},
    ]
    _dbuild({"language": "ja", "title": "管理者ガイド", "subtitle": name, "meta": [["版", "1.0"], ["対象", "人事・システム管理者"]],
             "header_text": f"{name} 管理者ガイド", "footer_text": "社内", "blocks": admin},
            DOCS / "D3_user-guide-manual" / f"{P}_Admin_Guide.docx")
    qs = [f"# クイックスタートガイド — {name}", "", "## 1 分で始める", "1. 社員番号とパスワードでログインします（SCR-01）。", "2. 「新規作成」で休暇・残業を申請します（SCR-02）。", "3. 上長が承認すると、状態が「承認済み」に変わります。", "",
          "## よく使う操作", "- 申請の確認: 申請一覧（SCR-03）", "- 承認: 承認待ち一覧（SCR-05）", "- 代理の設定: 承認者代理設定（SCR-06）", "",
          "## 困ったとき", "- 残業が提出できない → 事前承認が必要です。", "- パスワードを忘れた → 人事に連絡してください。", "- 詳しい手順 → 利用者マニュアル（EndUser）を参照してください。", ""]
    (DOCS / "D3_user-guide-manual" / f"{P}_Quick_Start_Guide.md").write_text("\n".join(qs), encoding="utf-8")

    # ================================================================ X2 アーキテクチャ（生成スクリプト）
    sh([str(REPO / "skills/x2-project-architecture/scripts/gen_architecture_html.py"), str(DOCS.parent)])

    # ================================================================ X3 状況スナップショット（compute_status）
    st = subprocess.run([sys.executable, "-B", str(REPO / "skills/a1-project-init/scripts/compute_status.py"), str(DOCS.parent)],
                        capture_output=True, text=True, encoding="utf-8", errors="replace")
    status = json.loads(st.stdout)
    rows = [f"| {d['step']} | {d['skill']} | {d['status']} | {len(d['files'])} |" for d in status["documents"] if d.get("step")]
    snap = [f"# 進捗スナップショット — {name}", "", f"生成日時: {status['generated_at']}", "",
            "## 工程別の状態", "| 工程 | 文書 | 状態 | 件数 |", "|---|---|---|---|"] + rows + ["",
            "## ゲート", "```", status["gates"]["raw"], "```", "",
            "## 進捗", f"- 現在のスプリント: {status['progress']['current_sprint']}", f"- 合計スプリント: {status['progress']['total_sprints']}", f"- 目標リリース: {status['progress']['go_live_target']}"]
    (DOCS / "X3_project-status").mkdir(parents=True, exist_ok=True)
    (DOCS / "X3_project-status" / f"{P}_Status_Snapshot.md").write_text("\n".join(snap) + "\n", encoding="utf-8")

    # ================================================================ X5 技術標準（ENGINEERING_STANDARDS）
    std = f"""# Engineering Standards — {name}

> Phiên bản: `_v1` · Ngày: {today} · Người phê duyệt: [担当者]
> 数値は project-context.json（settings.quality_gates）と tech_stack を参照。

## 1. 技術スタック
| 領域 | 採用 | 備考 |
|---|---|---|
| バックエンド | {ctx['tech_stack']['backend']} | TypeScript strict モード |
| データベース | {ctx['tech_stack']['database']} | migration はバージョン管理（Expand → Contract） |
| 認証 | {ctx['tech_stack']['auth']} | refresh は1回使い切り（ローテーション） |
| フロントエンド | Next.js（React） | Tailwind CSS |
| CI/CD | {ctx['tech_stack']['ci_cd']} | main への merge で STG へ配備 |

## 2. ブランチ・コミット
- ブランチ: `feature/<課題番号>-<概要>`、`fix/<課題番号>-<概要>`。main への直接 push は禁止。
- コミット: Conventional Commits（`feat:`, `fix:`, `docs:`, `test:`, `refactor:`）。
- タグ: 本番リリースごとに `vX.Y.Z`（SemVer）。CHANGELOG（Keep a Changelog）を更新。

## 3. コードレビュー
- 1 PR の目安: 変更 400 行以内。レビュー依頼から 1 営業日以内に一次回答。
- 承認は 1 名以上（作成者以外）。セキュリティに関わる変更は 2 名以上。
- レビューの確認項目: 認可（所有権の検査）、入力検証、エラー形式、ログに個人情報を含めないこと。

## 4. テスト品質基準（settings.quality_gates）
| 指標 | 基準 |
|---|---|
| 単体試験の合格率 | ≥ {ctx['settings']['quality_gates']['ut_pass_rate']}% |
| 行カバレッジ | ≥ {ctx['settings']['quality_gates']['ut_coverage_line']}% |
| 分岐カバレッジ | ≥ {ctx['settings']['quality_gates']['ut_coverage_branch']}% |
| 結合試験の合格率 | ≥ {ctx['settings']['quality_gates']['it_pass_rate']}% |
| システム試験の合格率 | ≥ {ctx['settings']['quality_gates']['st_pass_rate']}% |
| Critical/High の未解決欠陥 | ≤ {ctx['settings']['quality_gates']['open_critical_high_max']} 件 |

## 5. セキュリティ
- パスワード: Argon2id で保存。平文・可逆暗号で保存しない。
- JWT: access 15分、refresh 7日（1回使い切り）。署名鍵は環境変数（リポジトリに置かない）。
- ログイン失敗 5 回で 10 分ロック。
- すべてのエンドポイントで認可（ロール）と所有権を検査（他人のデータは 403）。
- 出力はエスケープ（XSS 対策）。SQL はパラメータ化。

## 6. エラーとログ
- エラー形式: `{{ "error": {{ "code": "ERR-<DOMAIN>-<NNN>", "message": "...", "details": [...] }} }}`
- 例外は境界（コントローラ）で変換する。スタックトレースを利用者に返さない。
- ログ: 構造化（JSON）。個人情報・トークン・パスワードは記録しない。requestId を付与する。

## 7. API・データベース
- API は `/api/v1`。破壊的変更は `/v2`（api-versioning 参照）。
- テーブルは監査列 `created_at`・`updated_at` を持つ。外部キーには索引を付ける。
- 監査ログは追記のみ（削除・更新は不可）。

## 8. 既知の矛盾・例外
- 承認済み申請の取消は未決（Q-03）。実装は回答後。
- CSV の文字コードは仮仕様（Q-04）。

## 9. 承認
| 役割 | 氏名 | 日付 |
|---|---|---|
| PM | [担当者] | |
| テックリード | [担当者] | |
"""
    (DOCS / "X5_coding-standards").mkdir(parents=True, exist_ok=True)
    (DOCS / "X5_coding-standards" / f"{P}_ENGINEERING_STANDARDS.md").write_text(std, encoding="utf-8")

    # ================================================================ X7 デッキ（進捗報告 Sprint 2）
    sprint_done, sprint_plan = 22.0, 34.0  # Sprint 2: done 10+6+6 ; planned (không tính moved) 9+6+8+6+5
    deck = {"title": f"{name} 進捗報告（スプリント 2）", "subtitle": f"{client} · 2027-01-29", "slides": [
        {"type": "bullets", "title": "今回の報告", "points": ["スプリント 2 の結果と完了率", "テストの状況", "未決事項と次のスプリントの計画"]},
        {"type": "metrics", "title": "スプリント 2 の結果", "metrics": [
            {"value": f"{sprint_done / sprint_plan:.0%}", "label": "計画に対する完了率（MD）", "source": "C6 スプリントレビュー › sprint2_input.json（tasks）"},
            {"value": "3", "label": "完了した作業（件）", "source": "C6 スプリントレビュー › sprint2_input.json（tasks, status=done）"},
            {"value": "1", "label": "未解決のブロッカー", "source": "C6 スプリントレビュー › sprint2_input.json（blockers_unresolved）"}]},
        {"type": "metrics", "title": "テストの状況（システム試験 2 回目）", "metrics": [
            {"value": "100%", "label": f"合格率（実行 {len(S.cases_flat())} 件）", "source": "C5 テストレポート › Sample_Attendance_Test_Report_ST_20270214.md"},
            {"value": "0", "label": "未解決の Critical/High", "source": "C5 テストレポート › 欠陥（open_critical_high）"}]},
        {"type": "bullets", "title": "リスクと対応", "points": ["CI/CD の構築が遅延（インフラ申請）→ スプリント 3 へ移動", "OCC の 409 応答が未完（残 3 人日）→ スプリント 3 で完了", "未決 Q-03・Q-04 の回答期限 2027-01-22"]},
        {"type": "bullets", "title": "次のステップ", "points": ["スプリント 3 計画: 2027-01-25（PM）", "Q-03・Q-04 の回答取得（顧客）", "テスト環境の提供確認: 2027-01-15（顧客）"]},
    ]}
    dspec = DOCS / "X7_presentation-deck" / f"{P}_deck_spec.json"
    dspec.parent.mkdir(parents=True, exist_ok=True)
    dspec.write_text(json.dumps(deck, ensure_ascii=False, indent=2), encoding="utf-8")
    sh([str(REPO / "skills/x7-presentation-deck/scripts/build_deck.py"), str(dspec), str(DOCS / "X7_presentation-deck" / f"{P}_Progress_Deck_Sprint2.pptx")])

    # ================================================================ C5–C8 報告 md → docx
    for sub in ["C5_test-execution", "C6_sprint-review", "C7_change-request", "C8_release-deployment"]:
        for md in sorted((DOCS / sub).glob("*.md")):
            text = md.read_text(encoding="utf-8")
            title = next((ln.lstrip("# ").strip() for ln in text.splitlines() if ln.startswith("#")), md.stem)
            _dbuild({"language": "vi", "title": title, "subtitle": name, "meta": [["作成日", today], ["出典", md.name], ["区分", "社内用（内部文書: 言語 vi）"]],
                     "header_text": f"{name} {title}", "footer_text": "社内", "blocks": md_to_blocks(text)},
                    md.with_suffix(".docx"))

    cr_client_doc(S, DOCS, REPO, P, name, client, today)
    return {"d1": "ok", "d2": "ok", "d3": "ok"}


def api_detail_for_build(APIS):
    return api_detail_sheet(APIS)


def cr_client_doc(S, DOCS, REPO, P, name, client, today):
    """CR-001 bản tiếng Nhật cho khách (tính bằng cr_impact.py --format json). Bản tiếng Việt của script là nội bộ."""
    import subprocess as _sp
    cr_path = DOCS / "C7_change-request" / f"{P}_CR-001_input.json"
    r = _sp.run([sys.executable, "-B", str(REPO / "skills/c7-change-request/scripts/cr_impact.py"), str(cr_path), "--format", "json"],
                capture_output=True, text=True, encoding="utf-8", errors="replace")
    d = json.loads(r.stdout)
    sub = d["subtotal"]
    blocks = [
        {"type": "h1", "text": "1. 変更の内容"},
        {"type": "p", "text": "月次勤怠CSVに部門別の合計行を追加し、申請一覧に有給の残日数を表示します。"},
        {"type": "h1", "text": "2. 工数の内訳"},
        {"type": "table", "caption": "表 2-1 工数（人日）", "columns": ["区分", "人日（MD）", "内容"], "widths": [3.6, 3.0, 9.4], "rows": [
            ["新規開発", f"{sub['new']:.2f}", "CSV の部門別合計行、申請一覧の残日数表示（API・UI）"],
            ["手戻り", f"{sub['rework']:.2f}", "既存機能の変更はなし"],
            ["回帰試験", f"{sub['regression']:.2f}", "既存 CSV の取込確認を含む"],
            ["バッファ", f"{d['buffer_md']:.2f}", f"新規開発と手戻りの {int(d['buffer_md'] / max(sub['new'] + sub['rework'], 1) * 100)}%（SOW の基準）"],
            ["合計", f"{d['total_cr_md']:.2f}", f"{d['person_month']:.3f} 人月"]]},
        {"type": "h1", "text": "3. 影響"},
        {"type": "bullets", "items": [
            f"当初見積（{d['original_total_md']:.2f} 人日）に対して約 {d['impact_pct_of_original']:.1f}% の増加。",
            f"スケジュール: 最低 {d['sprint_delay_min']} スプリント（約 {d['timeline_delay_weeks_min']} 週）の延期が必要。",
            "費用: 単価を契約書で定める場合のみ算出（本件はサンプルのため未算出）。"]},
        {"type": "h1", "text": "4. 承認"},
        {"type": "p", "text": "本変更は、お客様の書面による承認をもって実施します（SOW 第9条）。承認後に SOW と計画を更新します。"},
        {"type": "table", "columns": ["", "顧客（承認者）", "受注者（PM）"], "widths": [3.0, 7.0, 7.0], "rows": [
            ["会社名", client, "[担当者]"], ["署名・押印", "", ""], ["日付", "", ""]]},
    ]
    _dbuild({"language": "ja", "title": "変更要求の影響分析（CR-001）", "subtitle": name,
             "meta": [["変更番号", "CR-001"], ["作成日", today], ["状態", "承認待ち"]],
             "header_text": f"{name} 変更要求 CR-001", "footer_text": "社外秘", "blocks": blocks},
            DOCS / "C7_change-request" / f"{P}_CR-001_Change_Request_JA.docx")
