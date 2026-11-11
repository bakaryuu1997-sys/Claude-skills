# -*- coding: utf-8 -*-
"""phase2_business.py — B0 (提案・SOW), B1 (キックオフ), X4 (議事録), X1 (オンボーディング), X3 (状況).
Dữ liệu mẫu hư cấu (勤怠承認システム). Mọi số liệu lấy từ gen_sample.py / timeline.json / estimate;
giá trị hợp đồng KHÔNG có trong nguồn được đặt là "（サンプル値）" để không bị nhầm là số thật."""
import json
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


def run(S, DOCS, REPO, P, sh):
    ctx = S.ctx
    name = ctx["project"]["name"]
    client = ctx["project"]["client"]
    today = ctx["created_at"]
    tl = json.loads((DOCS / "A9_project-timeline" / "timeline.json").read_text(encoding="utf-8"))
    ms = tl["milestones"]
    total_md = float(tl["total_md"])
    gap_wk = (date.fromisoformat(ctx["project"]["go_live_target"]) - date.fromisoformat(tl["end_date"])).days / 7
    pm = round(total_md / 22, 2)
    RATE = 1_000_000  # 円/人月 — SAMPLE VALUE (không có trong nguồn)
    price = round(pm * RATE, -3)
    tax = round(price * 0.10, -3)

    # ================================================================ B0 提案書 (docx)
    proposal = [
        {"type": "h1", "text": "1. 背景と目的"},
        {"type": "p", "text": f"{client}の勤怠申請・承認業務は紙と電子メールで行われており、承認状況の把握と月次集計に多くの工数がかかっています。本提案は、休暇・残業申請と上長承認をWebで一元化し、月次勤怠CSVを自動出力することを目的とします。"},
        {"type": "h1", "text": "2. 要件の理解と対象範囲（概要）"},
        {"type": "p", "text": "機能スコープは6機能（認証、申請作成、申請一覧、承認・差戻し、承認者代理、月次CSV出力）です。詳細は別紙SOWの第3条・第4条および『SOW_Scope_Matrix』に定義します。"},
        {"type": "table", "caption": "表 2-1 機能の概要", "columns": ["機能ID", "機能名", "概要"], "widths": [3.6, 4.6, 8.8],
         "rows": [[f[0], f[2], f[3]] for f in S.FEATS]},
        {"type": "h1", "text": "3. 解決方針（アーキテクチャ）"},
        {"type": "bullets", "items": [
            f"バックエンド: {ctx['tech_stack']['backend']}",
            f"データベース: {ctx['tech_stack']['database']}（監査ログは追記のみ）",
            f"認証: {ctx['tech_stack']['auth']}",
            f"配備: {ctx['tech_stack']['hosting']}、CI/CD: {ctx['tech_stack']['ci_cd']}",
            "API: REST（/api/v1）。エラーは共通形式 { error: { code, message } } で返却。"]},
        {"type": "h1", "text": "4. 主な業務フロー"},
        {"type": "p", "text": "申請者が休暇・残業を申請し、上長が承認または差戻し（理由必須）します。残業は事前承認を必須とします（Q-02の回答）。承認済みの申請は人事が月次でCSV出力します。"},
        {"type": "h1", "text": "5. セキュリティと性能"},
        {"type": "bullets", "items": [
            "通信はTLS1.2以上。パスワードはArgon2idで保存。5回連続の認証失敗で10分間ロック。",
            "全APIで権限と所有権を検査（他人の申請は403）。",
            "申請一覧（1,000件・検索込み）は p95 800ms 以内（同時利用50名）を目標とし、k6で検証します。"]},
        {"type": "h1", "text": "6. 体制"},
        {"type": "table", "caption": "表 6-1 プロジェクト体制（サンプル）", "columns": ["役割", "人数", "主担当", "工数配分"], "widths": [3.2, 2.0, 7.4, 4.4],
         "rows": [["プロジェクトマネージャ", "1", "計画、顧客窓口、リスク管理", "50%"], ["バックエンド開発", "2", "API、認証、CSV出力", "100%"],
                  ["フロントエンド開発", "1", "画面（SCR-01〜07）", "100%"], ["品質保証", "1", "テスト設計・実施・UAT支援", "100%"]]},
        {"type": "h1", "text": "7. 進め方とマイルストーン"},
        {"type": "table", "caption": "表 7-1 マイルストーン", "columns": ["ID", "マイルストーン", "日付", "判定基準"], "widths": [1.6, 5.0, 3.0, 7.8],
         "rows": [[m["id"], m["name"], m["date"], {"M1": "キックオフ・計画承認", "M2": "API凍結", "M3": "全機能の実装完了（UT合格）", "M4": "コードフリーズ（IT完了）", "M5": "UAT開始", "M6": "本番リリース（Go/No-Go合格）"}.get(m["id"], "")] for m in ms]},
        {"type": "h1", "text": "8. 価格と支払条件"},
        {"type": "p", "text": f"見積合計 {total_md:.2f}人日（{pm:.2f}人月）に基づく概算 {price:,.0f}円（税別）。消費税10%を加算。単価 {RATE:,}円/人月は本書の作成にあたってのサンプル値です。"},
        {"type": "p", "text": "支払条件は別紙SOWの第7条による（契約時30%・中間30%・UAT開始20%・検収20%）。"},
        {"type": "h1", "text": "9. 前提・リスク・お客様にお願いすること"},
        {"type": "table", "caption": "表 9-1 未決事項（お客様のご回答が必要）", "columns": ["No.", "内容", "期限"], "widths": [1.8, 11.0, 3.6],
         "rows": [["Q-03", "承認済み申請の取消（撤回）の権限", "2027-01-22"], ["Q-04", "人事CSVの文字コードと列順", "2027-01-22"]]},
        {"type": "bullets", "items": [
            "テスト用アカウントと検証環境（STG）を2027-01-15までにご提供ください。",
            "人事の既存取込仕様（文字コード・列順）の資料を2027-01-15までにご提供ください。",
            "未決事項の回答が遅れた場合は、影響する機能を後続スプリントへ移し、スケジュールを見直します。"]},
        {"type": "h1", "text": "10. 品質へのコミットメント"},
        {"type": "bullets", "items": [
            "単体試験の合格率 95% 以上、行カバレッジ 80% 以上（品質基準）。",
            "STの合格率 98% 以上。Critical/High の未解決欠陥は 0 件で検収に進みます。",
            "UATは顧客が実施し、合否と署名を記録します。"]},
        {"type": "h1", "text": "11. 付録"},
        {"type": "p", "text": "付録A 用語集: 検収（受入れの確認）、契約不適合責任（納品物が合意した仕様と異なる場合の修補責任）、CSV（カンマ区切りのテキスト形式）。詳細な条件は別紙SOWに従う。"},
    ]
    _dbuild({"language": "ja", "title": "技術提案書", "subtitle": name,
             "meta": [["版", "1.0（提出版）"], ["作成日", today], ["提出先", client], ["提出元", "[担当者]"], ["注記", "架空の教材案件。価格は見積の計算に基づくサンプル値"]],
             "header_text": f"{name} 技術提案書 v1.0", "footer_text": "社外秘", "blocks": proposal},
            DOCS / "B0_proposal-sow" / f"{P}_Technical_Proposal_v1.docx")

    # ================================================================ B0 SOW (docx)
    sow = [
        {"type": "h1", "text": "第1条（目的・定義・契約文書）"},
        {"type": "p", "text": "本契約は、本件業務（勤怠承認システムの開発）に関する条件を定める。定義は本条に定めるもののほか、提案書の用語による。契約文書の優先順位は、本契約書、別紙SOW、提案書の順とする。"},
        {"type": "h1", "text": "第2条（契約形態・期間）"},
        {"type": "p", "text": "本件は請負契約（成果物の完成を約し、検収を経て引き渡す）とする。【サンプルの前提】契約形態は請負として作成しており、顧客の確認を経ていない。契約期間は2027年1月4日から2027年3月31日までとする。"},
        {"type": "h1", "text": "第3条（業務の範囲）"},
        {"type": "p", "text": "業務範囲は別紙『SOW_Scope_Matrix』のシート In_Scope に定める機能（FEAT-AUTH-01、FEAT-LEAVE-01、FEAT-LEAVE-02、FEAT-APPR-01、FEAT-APPR-02、FEAT-REPORT-01）とする。"},
        {"type": "h1", "text": "第4条（対象外・前提・制約）"},
        {"type": "p", "text": "対象外事項は同 Out_Of_Scope に定める。対象外事項を追加する場合は第9条の変更管理による。"},
        {"type": "h1", "text": "第5条（マイルストーン・成果物・受入基準）"},
        {"type": "p", "text": "マイルストーン、成果物、受入基準は同 Milestone_Deliverables に定める。"},
        {"type": "h1", "text": "第6条（検収）"},
        {"type": "p", "text": "乙は各マイルストーンの成果物を納品する。甲は納品日から10営業日以内に検収を行う【サンプルの前提】。甲が期間内に指摘しない場合は検収完了とみなす（甲と協議のうえ確定）。指摘事項は軽微なもの（Medium/Low）を保留事項として記録し、検収後の保証期間内に修補する。"},
        {"type": "h1", "text": "第7条（報酬・支払）"},
        {"type": "p", "text": f"報酬は税別 {price:,.0f}円（サンプル値）とし、消費税を別途支払う。支払は契約時30%・中間（M3完了時）30%・UAT開始（M5）20%・検収完了時20%とし、請求締め日は月末、支払期限は請求書受領後30日以内とする。"},
        {"type": "h1", "text": "第8条（甲乙の責任分担・協力事項）"},
        {"type": "p", "text": "甲は、テスト用アカウント・検証環境・人事の既存取込仕様を2027年1月15日までに提供する。甲の協力が遅れた場合、乙は影響を受けるマイルストーンを同期間分だけ延期できる。"},
        {"type": "h1", "text": "第9条（変更管理）"},
        {"type": "p", "text": "甲または乙が仕様の変更を希望する場合、乙は影響分析（工数・期間・費用）を書面で提示し、甲が書面で承認した後に実施する。承認前の作業は行わない。"},
        {"type": "h1", "text": "第10条（保証・契約不適合責任・サポート）"},
        {"type": "p", "text": "検収完了日から3か月間（【サンプルの前提】）、納品物が合意した仕様に適合しないことに起因する不具合について、乙は無償で修補する。ただし、甲による仕様外の改変、環境変更、甲が指定した第三者の製品に起因する不具合を除く。保証期間中の重大な不具合（業務停止）は、受付から1営業日以内に一次対応する。"},
        {"type": "h1", "text": "第11条（知的財産権）"},
        {"type": "p", "text": "納品物の著作権は、報酬の全額支払時に乙から甲へ移転する。乙が従前から保有する技術・ライブラリ（オープンソースを含む）の権利は乙に留保する。"},
        {"type": "h1", "text": "第12条（秘密保持）"},
        {"type": "p", "text": "両当事者は本契約に関連して知り得た相手方の秘密情報を、本契約の目的以外に使用・開示しない。秘密保持義務は契約終了後3年間存続する。"},
        {"type": "h1", "text": "第13条（個人情報の取扱い）"},
        {"type": "p", "text": "乙は社員の個人情報を、甲の指示に従い、個人情報保護法その他の適用法令に従って取り扱う。個人情報の保存期間は退職後5年とし、期間経過後に削除する。"},
        {"type": "h1", "text": "第14条（再委託）"},
        {"type": "p", "text": "乙は、甲の書面による事前承認なく、業務の全部または主要部分を第三者に再委託しない。再委託先の行為について乙が責任を負う。"},
        {"type": "h1", "text": "第15条（契約の解除・損害賠償の上限）"},
        {"type": "p", "text": "一方の当事者が重大な違反を行い、相当の期間を定めた催告後も是正されない場合、相手方は本契約を解除できる。損害賠償の上限は、解除時点までに支払われた報酬の総額（【サンプルの前提】）とし、間接損害は賠償の対象外とする。"},
        {"type": "h1", "text": "第16条（準拠法・管轄・署名）"},
        {"type": "p", "text": "本契約は日本法に準拠する。本契約に関する紛争は東京地方裁判所を第一審の専属的合意管轄裁判所とする【サンプルの前提】。本契約の成立を証するため、本書2通を作成し、各自記名押印の上、各1通を保有する。"},
        {"type": "table", "caption": "署名欄", "columns": ["", "甲（顧客）", "乙（受注者）"], "widths": [3.0, 7.0, 7.0],
         "rows": [["会社名", client, "[担当者]"], ["代表者 役職・氏名", "[担当者]", "[担当者]"], ["署名・押印", "", ""], ["日付", "", ""]]},
    ]
    _dbuild({"language": "ja", "title": "業務委託契約書（SOW）", "subtitle": name,
             "meta": [["版", "1.0（案）"], ["作成日", today], ["注記", "【サンプルの前提】を付した条項は顧客の確認が必要。架空の教材案件"]],
             "header_text": f"{name} SOW v1.0", "footer_text": "秘密", "blocks": sow},
            DOCS / "B0_proposal-sow" / f"{P}_Statement_Of_Work.docx")

    # SOW_Scope_Matrix (xlsx): In_Scope · Out_Of_Scope · Milestone_Deliverables · Customer_Dependencies
    deliv = {"M1": "計画書・キックオフ資料", "M2": "API設計書（凍結版）・画面一覧", "M3": "全機能の実装（UT合格）・単体試験結果",
             "M4": "結合試験結果・欠陥一覧", "M5": "UAT用環境・UATチェックリスト", "M6": "本番リリース・運用手順書"}
    pct = {"M1": 0.30, "M3": 0.30, "M5": 0.20, "M6": 0.20}
    mrows = []
    for i, m in enumerate(ms):
        r = 4 + i
        p_ = pct.get(m["id"], 0.0)
        mrows.append({"id": m["id"], "name": m["name"], "date": m["date"], "del": deliv.get(m["id"], ""),
                      "crit": {"M1": "計画書の承認", "M2": "全APIがAPI設計書と一致（試験で確認）", "M3": "UT合格率95%以上・行カバレッジ80%以上",
                               "M4": "IT合格・Critical/High 0件", "M5": "UATの全項目を実施し、合否を記録", "M6": "Go/No-Go 合格・本番で疎通確認"}.get(m["id"], ""),
                      "pct": {"value": p_, "numfmt": "0%"}, "amt": f"=ROUND({price}*F{r},0)"})
    _xbuild({"title": "SOW Scope Matrix", "language": "ja", "sheets": [
        {"name": "In_Scope", "title": "業務範囲（In Scope）", "subtitle": "SOW 第3条の根拠。機能ID（FEAT）は要件定義（A2）と一致",
         "columns": [{"key": "id", "header": "機能ID", "width": 17}, {"key": "name", "header": "機能名", "width": 26, "wrap": True},
                     {"key": "desc", "header": "含む内容", "width": 56, "wrap": True}, {"key": "scr", "header": "関連画面", "width": 18},
                     {"key": "api", "header": "関連API", "width": 40, "wrap": True}],
         "rows": [{"id": f[0], "name": f[2], "desc": f[3], "scr": {"FEAT-AUTH-01": "SCR-01", "FEAT-LEAVE-01": "SCR-02", "FEAT-LEAVE-02": "SCR-03, SCR-04",
                                                                  "FEAT-APPR-01": "SCR-04, SCR-05", "FEAT-APPR-02": "SCR-06", "FEAT-REPORT-01": "SCR-07"}[f[0]],
                   "api": {"FEAT-AUTH-01": "POST /api/v1/auth/login, POST /api/v1/auth/refresh", "FEAT-LEAVE-01": "POST /api/v1/leave-requests",
                           "FEAT-LEAVE-02": "GET /api/v1/leave-requests, GET /api/v1/leave-requests/{id}", "FEAT-APPR-01": "POST .../approve, POST .../reject",
                           "FEAT-APPR-02": "PUT /api/v1/approver-delegations", "FEAT-REPORT-01": "GET /api/v1/reports/monthly-attendance.csv"}[f[0]]}
                 for f in S.FEATS]},
        {"name": "Out_Of_Scope", "title": "対象外（Out Of Scope）", "subtitle": "SOW 第4条の根拠。対象外の追加は第9条の変更管理による",
         "columns": [{"key": "no", "header": "No.", "width": 6, "align": "center"}, {"key": "item", "header": "対象外事項", "width": 52, "wrap": True},
                     {"key": "why", "header": "扱い", "width": 46, "wrap": True}],
         "rows": [{"no": 1, "item": "人事システムとの自動連携（勤怠データの取込・送信）", "why": "後フェーズ。別途見積（CR）"},
                  {"no": 2, "item": "スマートフォン専用画面", "why": "対応ブラウザは PC の Chrome / Edge"},
                  {"no": 3, "item": "申請の取消（撤回）機能", "why": "Q-03 の回答後に追加を判断"},
                  {"no": 4, "item": "休暇残高（付与日数）の管理", "why": "人事システム側で管理"}]},
        {"name": "Milestone_Deliverables", "title": "マイルストーン・成果物・支払", "subtitle": "支払割合の合計は 100%（下段で検算）。金額は税別・サンプル値",
         "columns": [{"key": "id", "header": "マイルストーン", "width": 14, "align": "center"}, {"key": "name", "header": "名称", "width": 22},
                     {"key": "date", "header": "日付", "width": 12, "align": "center"}, {"key": "del", "header": "成果物", "width": 36, "wrap": True},
                     {"key": "crit", "header": "受入基準（測定可能）", "width": 40, "wrap": True},
                     {"key": "pct", "header": "支払割合", "width": 11, "align": "center", "numfmt": "0%"},
                     {"key": "amt", "header": "金額（税別・円）", "width": 16, "numfmt": "#,##0", "align": "right"}],
         "rows": mrows,
         "total_row": {"label": "合計", "sum": ["pct", "amt"]}},
        {"name": "Customer_Dependencies", "title": "お客様の協力事項", "subtitle": "SOW 第8条の根拠。期限を過ぎた場合は影響するマイルストーンを延期",
         "columns": [{"key": "no", "header": "No.", "width": 6, "align": "center"}, {"key": "item", "header": "協力事項", "width": 50, "wrap": True},
                     {"key": "due", "header": "期限", "width": 12, "align": "center"}, {"key": "owner", "header": "担当（顧客）", "width": 18}],
         "rows": [{"no": 1, "item": "テスト用アカウントと検証環境（STG）の提供", "due": "2027-01-15", "owner": "情報システム"},
                  {"no": 2, "item": "人事の既存取込仕様（文字コード・列順）の資料", "due": "2027-01-15", "owner": "人事担当"},
                  {"no": 3, "item": "Q-03（承認済み申請の取消）の決定", "due": "2027-01-22", "owner": "人事課長"},
                  {"no": 4, "item": "UATの実施者（一般社員・承認者・人事）の確保", "due": "2027-02-22", "owner": "人事担当"}]},
    ]}, DOCS / "B0_proposal-sow" / f"{P}_SOW_Scope_Matrix.xlsx")

    # ================================================================ B1 キックオフ
    slides = [
        {"type": "bullets", "title": "本日のアジェンダ", "points": ["プロジェクトの目的と範囲", "体制・役割分担（RACI）", "スケジュールとマイルストーン", "リスクと未決事項", "次のステップ"]},
        {"type": "bullets", "title": "背景と目的", "points": [
            "紙と電子メールで行われている休暇・残業申請と承認を、Webで一元化する",
            "承認の進捗を見える化し、月次の勤怠集計の手作業をなくす",
            "導入の成功基準: 申請から承認までの平均日数を短縮（測定方法はNFR-PERF/AVAILで定義）"]},
        {"type": "metrics", "title": "スコープの規模", "metrics": [
            {"value": str(len(S.FEATS)), "label": "機能（FEAT）", "source": "A2 要件定義書 › 機能スコープ"},
            {"value": str(sum(len(a) for a in [S.APIS])), "label": "API（エンドポイント）", "source": "A4 API設計書 › api_spec.json"},
            {"value": str(len(S.TABLES)), "label": "データベーステーブル", "source": "A5 DB設計書 › 概要・テーブル一覧"}]},
        {"type": "metrics", "title": "スケジュールの概要", "metrics": [
            {"value": str(tl["total_sprints"]), "label": "スプリント（2週間）", "source": "A9 タイムライン › timeline.json"},
            {"value": f"{total_md:.1f}", "label": "見積合計（人日）", "source": "A6 見積 › 見積サマリー"},
            {"value": ms[-1]["date"], "label": "本番リリース（M6）", "source": "A9 タイムライン › マイルストーン"}]},
        {"type": "bullets", "title": "体制", "points": [
            "プロジェクトマネージャ（PM）: 計画、顧客窓口、リスク管理",
            "バックエンド 2名・フロントエンド 1名: 実装",
            "品質保証（QA） 1名: テスト設計・実施・UAT支援",
            "顧客: 人事課長（意思決定）・人事担当（仕様・CSV）・情報システム（環境）"]},
        {"type": "bullets", "title": "マイルストーン", "points": [f"{m['id']} {m['name']}: {m['date']}" for m in ms]},
        {"type": "bullets", "title": "リスクと未決事項", "points": [
            "未決 Q-03（承認の取消）・Q-04（CSV仕様）: 2027-01-22 までに回答が必要",
            "テスト環境の提供が遅れた場合、結合試験の開始を後ろ倒し",
            "人事の既存取込仕様の変更: 変更管理（SOW 第9条）で扱う"]},
        {"type": "bullets", "title": "次のステップ", "points": [
            "2027-01-15: テスト環境・取込仕様の提供（顧客）",
            "2027-01-22: 未決事項 Q-03・Q-04 の回答（顧客）",
            "2027-01-25: 最初のスプリント計画会議（PM）"]},
    ]
    deck_spec = {"title": f"{name} キックオフ", "subtitle": f"{client} · {today}", "slides": slides}
    deck_spec_path = DOCS / "B1_project-kickoff" / f"{P}_deck_spec.json"
    deck_spec_path.parent.mkdir(parents=True, exist_ok=True)
    deck_spec_path.write_text(json.dumps(deck_spec, ensure_ascii=False, indent=2), encoding="utf-8")
    sh([str(REPO / "skills/x7-presentation-deck/scripts/build_deck.py"), str(deck_spec_path),
        str(DOCS / "B1_project-kickoff" / f"{P}_Kickoff_Deck.pptx")])

    charter = [
        {"type": "h1", "text": "1. 目的"}, {"type": "p", "text": "紙と電子メールで行われている休暇・残業申請と承認を、Webで一元化し、月次勤怠集計の手作業をなくす。"},
        {"type": "h1", "text": "2. 範囲"}, {"type": "p", "text": "機能6件（認証、申請作成、申請一覧、承認・差戻し、承認者代理、月次CSV出力）。対象外は SOW Scope_Matrix の Out_Of_Scope に定める。"},
        {"type": "h1", "text": "3. 成果物"},
        {"type": "table", "caption": "表 3-1 主要成果物", "columns": ["成果物", "形式", "担当", "期限"], "widths": [6.0, 3.0, 3.6, 3.6],
         "rows": [["要件定義書・QA管理表", "xlsx", "BA / PM", "2027-01-08"], ["API設計書", "xlsx・OpenAPI", "BE", "2027-02-01"],
                  ["DB設計書・migration", "xlsx・sql", "BE", "2027-02-01"], ["基本設計書・詳細設計書", "docx", "BA / BE", "2027-01-22"],
                  ["試験計画書・試験結果", "xlsx", "QA", "2027-02-15"], ["リリース計画・運用手順書", "docx・md", "PM / BE", "2027-03-01"]]},
        {"type": "h1", "text": "4. スケジュール"},
        {"type": "table", "caption": "表 4-1 マイルストーン", "columns": ["ID", "名称", "日付"], "widths": [2.0, 9.0, 4.0],
         "rows": [[m["id"], m["name"], m["date"]] for m in ms]},
        {"type": "h1", "text": "5. 体制（RACI は別表）"}, {"type": "p", "text": "PMが全体を統括する。役割と責任の詳細は Kickoff_Workbook の RACI シートによる。"},
        {"type": "h1", "text": "6. 予算"}, {"type": "p", "text": f"見積合計 {total_md:.2f} 人日（{pm:.2f} 人月）。契約金額は SOW 第7条による。"},
        {"type": "h1", "text": "7. 主要リスク"}, {"type": "p", "text": "RAID_Log シートの R-01〜R-03 を参照。"},
        {"type": "h1", "text": "8. 前提条件"},
        {"type": "bullets", "items": ["テスト環境を2027-01-15までに提供いただく。", "人事の既存取込仕様を2027-01-15までに提供いただく。", "UATの実施者を2027-02-22までに確保いただく。"]},
        {"type": "h1", "text": "9. コミュニケーション"}, {"type": "p", "text": "週次定例（毎週火曜 10:00・30分）、スプリントレビュー（隔週金曜）、月次の経営報告。詳細は Communication_Plan シート。"},
        {"type": "h1", "text": "10. 承認"},
        {"type": "table", "caption": "承認欄", "columns": ["役割", "氏名", "署名", "日付"], "widths": [4.0, 4.0, 4.0, 4.0],
         "rows": [["顧客 承認者（人事課長）", "[担当者]", "", ""], ["PM（受注者）", "[担当者]", "", ""]]},
        {"type": "h1", "text": "11. 変更管理"}, {"type": "p", "text": "範囲・期限・予算の変更は SOW 第9条の変更管理により、影響分析の上、書面で承認を得る。"},
    ]
    _dbuild({"language": "ja", "title": "プロジェクト憲章（Project Charter）", "subtitle": name,
             "meta": [["版", "1.0（承認版案）"], ["作成日", today], ["PM", "[担当者]"], ["顧客責任者", "[担当者]"]],
             "header_text": f"{name} プロジェクト憲章", "footer_text": "社外秘", "blocks": charter},
            DOCS / "B1_project-kickoff" / f"{P}_Project_Charter.docx")

    # Kickoff workbook: RACI · RAID_Log · Communication_Plan · DoR_DoD · Action_Items
    roles = ["PM", "BE", "FE", "QA", "顧客・人事課長", "顧客・人事担当", "顧客・情報システム"]
    acts = [
        ("要件の確定（Q&A 回答の取りまとめ）", ["A", "C", "I", "I", "R", "C", "I"]),
        ("SOW・見積の承認", ["R", "C", "I", "I", "A", "C", "I"]),
        ("テスト環境・取込仕様の提供", ["R", "I", "I", "I", "I", "C", "A"]),
        ("API設計の凍結（M2）", ["A", "R", "R", "C", "I", "I", "I"]),
        ("機能の実装（M3）", ["A", "R", "R", "C", "I", "I", "I"]),
        ("結合試験・欠陥管理（M4）", ["A", "C", "C", "R", "I", "I", "I"]),
        ("UATの実施（M5）", ["C", "C", "C", "C", "A", "R", "R"]),
        ("本番リリース判定（M6）", ["R", "C", "C", "C", "A", "I", "C"]),
    ]
    raci_rows = []
    for i, (act, cells) in enumerate(acts):
        r = 4 + i
        d = {"act": act}
        for role, cell in zip(roles, cells):
            d[role] = cell
        d["chk"] = f'=IF(COUNTIF(B{r}:H{r},"A")=1,"OK","要確認（A は1つ）")'
        raci_rows.append(d)
    raid = [
        ("R-01", "R", "未決 Q-03・Q-04 が期限までに回答されず、設計が手戻りする", "High", "Medium", "PM", "期限を合意し、遅れる場合は機能を後続スプリントへ移す", "2027-01-22", "Open"),
        ("R-02", "R", "テスト環境の提供が遅れ、結合試験の開始が後ろ倒しになる", "High", "Medium", "PM", "2027-01-15 を期限とし、代替の環境（ローカル Docker）を準備", "2027-01-15", "Open"),
        ("R-03", "R", "人事の取込仕様（文字コード・列順）の変更", "Medium", "Medium", "PM", "CSV 仕様を Q-04 で凍結し、変更は CR で扱う", "2027-01-22", "Open"),
        ("A-01", "A", "承認者不在時は代理承認を許可し、代理期間は最長30日（Q-01 の回答）", "Medium", "—", "PM", "回答済み。設計に反映", "2027-01-15", "Closed"),
        ("I-01", "I", "（キックオフ時点で顕在化なし）", "—", "—", "PM", "—", "—", "Closed"),
        ("D-01", "D", "UAT の実施者（一般社員・承認者・人事）の確保", "High", "—", "顧客・人事担当", "2027-02-22 までに日程を確定", "2027-02-22", "Open"),
    ]
    comm = [
        ("週次定例", "PM・顧客・人事担当", "毎週火曜 10:00–10:30", "議事録（X4）、Open 課題の確認", "PM"),
        ("スプリントレビュー", "全員 + 顧客代表", "隔週金曜 15:00–16:00", "デモ・受入の進捗・次スプリントの計画", "PM"),
        ("月次経営報告", "顧客・経営層", "毎月第1営業日", "進捗・予算・主要リスク（1 枚）", "PM"),
        ("障害・緊急連絡", "PM・BE・顧客情報システム", "随時（電話 → チャット）", "1 時間以内に一次回答", "BE"),
    ]
    dor_dod = [
        ("DoR（着手条件）", "要件が受入基準付きで記述されている", "API 設計が凍結され、試験データが準備されている", "関連する未決事項（P1）が 0 件"),
        ("DoD（完了条件）", "コードレビュー済み・UT 合格率 ≥ 95%・行カバレッジ ≥ 80%", "IT 合格・Critical/High 欠陥 0 件", "ドキュメント（API・DB・運用）が更新済み"),
    ]
    actions = [
        ("ACT-01", "テスト環境の提供依頼（STG アカウント・ネットワーク）", "顧客・情報システム", "2027-01-15", "Open"),
        ("ACT-02", "人事の既存取込仕様の資料を入手", "顧客・人事担当", "2027-01-15", "Open"),
        ("ACT-03", "Q-03・Q-04 の回答を取得", "顧客・人事課長", "2027-01-22", "Open"),
        ("ACT-04", "第1スプリント計画の作成", "PM", "2027-01-18", "Open"),
    ]
    _xbuild({"title": "Kickoff Workbook", "language": "ja", "sheets": [
        {"name": "RACI", "title": "RACI マトリクス", "subtitle": "R=実行 A=説明責任（1つだけ） C=相談 I=報告。右端の検算で A が 1 つか確認",
         "columns": [{"key": "act", "header": "活動", "width": 36, "wrap": True}] + [{"key": r_, "header": r_, "width": 13, "align": "center", "validate": ["R", "A", "C", "I"]} for r_ in roles]
                    + [{"key": "chk", "header": "検算（A は 1 つ）", "width": 20, "align": "center"}],
         "rows": raci_rows},
        {"name": "RAID_Log", "title": "RAID ログ（リスク・前提・課題・依存）", "subtitle": "R=リスク A=前提 I=課題 D=依存。リスクは点数 = 影響 × 確率で管理（Critical/High は優先）",
         "columns": [{"key": "id", "header": "RAID-ID", "width": 10, "align": "center"}, {"key": "t", "header": "区分", "width": 8, "align": "center"},
                     {"key": "d", "header": "内容", "width": 52, "wrap": True}, {"key": "imp", "header": "影響", "width": 11, "align": "center"},
                     {"key": "pr", "header": "確率", "width": 11, "align": "center"}, {"key": "own", "header": "担当", "width": 16},
                     {"key": "resp", "header": "対応", "width": 46, "wrap": True}, {"key": "due", "header": "期限", "width": 12, "align": "center"},
                     {"key": "st", "header": "ステータス", "width": 12, "align": "center", "validate": ["Open", "Closed"]}],
         "rows": [{"id": a, "t": b, "d": c, "imp": d_, "pr": e, "own": f_, "resp": g, "due": h, "st": i_} for a, b, c, d_, e, f_, g, h, i_ in raid]},
        {"name": "Communication_Plan", "title": "コミュニケーション計画", "subtitle": "会議・報告の頻度と参加者。議事録は X4 の形式で作成",
         "columns": [{"key": "m", "header": "会議・報告", "width": 22}, {"key": "p", "header": "参加者", "width": 30, "wrap": True},
                     {"key": "f", "header": "頻度・時間", "width": 28, "wrap": True}, {"key": "o", "header": "目的・出力", "width": 44, "wrap": True},
                     {"key": "own", "header": "担当", "width": 12}],
         "rows": [{"m": a, "p": b, "f": c, "o": d_, "own": e} for a, b, c, d_, e in comm]},
        {"name": "DoR_DoD", "title": "完了条件（DoR / DoD）", "subtitle": "DoR: 着手してよい条件 ／ DoD: 完了とみなす条件",
         "columns": [{"key": "k", "header": "区分", "width": 18}, {"key": "a", "header": "条件 1", "width": 40, "wrap": True},
                     {"key": "b", "header": "条件 2", "width": 40, "wrap": True}, {"key": "c", "header": "条件 3", "width": 40, "wrap": True}],
         "rows": [{"k": a, "a": b, "b": c, "c": d_} for a, b, c, d_ in dor_dod]},
        {"name": "Action_Items", "title": "アクションアイテム", "subtitle": "ACT-NN。期限超過は x3 が報告",
         "columns": [{"key": "id", "header": "ACT-ID", "width": 10, "align": "center"}, {"key": "t", "header": "内容", "width": 52, "wrap": True},
                     {"key": "own", "header": "担当", "width": 22}, {"key": "due", "header": "期限", "width": 13, "align": "center"},
                     {"key": "st", "header": "ステータス", "width": 12, "align": "center", "validate": ["Open", "In progress", "Done"]}],
         "rows": [{"id": a, "t": b, "own": c, "due": d_, "st": e} for a, b, c, d_, e in actions]},
    ]}, DOCS / "B1_project-kickoff" / f"{P}_Kickoff_Workbook.xlsx")

    # Meeting minutes template (blank, for the next meeting)
    tmpl = [
        {"type": "h1", "text": "1. 会議情報"},
        {"type": "table", "columns": ["項目", "内容"], "widths": [4.0, 12.0], "rows": [["会議名", ""], ["日時", ""], ["場所・方式", ""], ["出席者", ""], ["欠席者", ""], ["議事録作成者", ""]]},
        {"type": "h1", "text": "2. 議題と議論"},
        {"type": "table", "columns": ["No.", "議題", "発表者", "議論の要約"], "widths": [1.4, 5.0, 3.0, 7.6], "rows": [["1", "", "", ""]]},
        {"type": "h1", "text": "3. 決定事項"},
        {"type": "table", "columns": ["ID", "決定内容", "承認者", "日付"], "widths": [1.8, 9.0, 3.2, 3.0], "rows": [["DEC-01", "", "", ""]]},
        {"type": "h1", "text": "4. アクションアイテム"},
        {"type": "table", "columns": ["ACT-ID", "内容", "担当", "期限", "状態"], "widths": [2.0, 7.0, 3.0, 2.5, 2.5], "rows": [["ACT-01", "", "", "", ""]]},
        {"type": "h1", "text": "5. 次回"},
        {"type": "p", "text": "日時・議題:"},
        {"type": "p", "text": "（この欄は会議後に記入します。決定事項の承認は署名欄で行います）"},
    ]
    _dbuild({"language": "ja", "title": "議事録（テンプレート）", "subtitle": name, "meta": [["版", "テンプレート"]],
             "header_text": f"{name} 議事録", "footer_text": "社内", "blocks": tmpl},
            DOCS / "B1_project-kickoff" / f"{P}_Meeting_Minutes_Template.docx")

    # ================================================================ X4 議事録（キックオフ会議）
    mtg = [
        {"type": "h1", "text": "1. 会議情報"},
        {"type": "table", "columns": ["項目", "内容"], "widths": [4.0, 12.0], "rows": [
            ["会議名", "キックオフ会議"], ["日時", "2027-01-05 10:00–11:30"], ["場所・方式", "顧客会議室（Web会議併用）"],
            ["出席者", "PM、BE 2名、FE 1名、QA 1名（乙）／人事課長、人事担当、情報システム（甲）"], ["議事録作成", "PM"]]},
        {"type": "h1", "text": "2. 議題と議論の要約"},
        {"type": "table", "columns": ["No.", "議題", "議論の要約"], "widths": [1.4, 5.0, 9.6], "rows": [
            ["1", "目的・範囲の確認", "機能6件の範囲を確認。対象外（人事連携・スマートフォン）を再確認した。"],
            ["2", "スケジュール", f"{ctx['project']['go_live_target']} のリリース目標を確認。計画上は {tl['total_sprints']} スプリントで完了する見込み（余裕 {gap_wk:.1f} 週）。"],
            ["3", "未決事項", "Q-03（承認の取消）と Q-04（CSV 仕様）が未回答。期限 2027-01-22 を合意。"],
            ["4", "体制・連絡", "週次定例（火曜 10:00）とスプリントレビュー（隔週金曜）を合意。"]]},
        {"type": "h1", "text": "3. 決定事項"},
        {"type": "table", "columns": ["ID", "決定内容", "承認者", "日付"], "widths": [1.8, 9.2, 3.0, 3.0], "rows": [
            ["DEC-01", "承認者が不在の期間は代理承認を許可し、代理期間は最長30日とする（Q-01 回答）", "人事課長", "2027-01-05"],
            ["DEC-02", "残業申請は事前承認を必須とする（Q-02 回答）", "人事課長", "2027-01-05"],
            ["DEC-03", "承認済み申請の取消は未決。Q-03 の回答まで設計・見積の対象外とする", "PM / 人事課長", "2027-01-05"]]},
        {"type": "h1", "text": "4. アクションアイテム"},
        {"type": "table", "columns": ["ACT-ID", "内容", "担当", "期限", "状態"], "widths": [2.0, 7.0, 3.0, 2.5, 2.5], "rows": [
            ["ACT-01", "テスト環境の提供依頼", "顧客・情報システム", "2027-01-15", "Open"],
            ["ACT-02", "取込仕様の資料提供", "顧客・人事担当", "2027-01-15", "Open"],
            ["ACT-03", "Q-03・Q-04 の回答", "顧客・人事課長", "2027-01-22", "Open"],
            ["ACT-04", "第1スプリント計画", "PM", "2027-01-18", "Open"]]},
        {"type": "h1", "text": "5. 次回"}, {"type": "p", "text": "2027-01-12（火）10:00 週次定例。議題: Q-03・Q-04 の回答状況、テスト環境の準備状況。"},
        {"type": "h1", "text": "6. 承認"},
        {"type": "table", "columns": ["役割", "氏名", "署名"], "widths": [5.0, 5.0, 6.0], "rows": [["議事録作成者（PM）", "[担当者]", ""], ["顧客 確認者（人事課長）", "[担当者]", ""]]},
    ]
    _dbuild({"language": "ja", "title": "議事録（キックオフ会議）", "subtitle": name, "meta": [["会議日", "2027-01-05"], ["版", "1.0（確定）"]],
             "header_text": f"{name} 議事録", "footer_text": "社内", "blocks": mtg},
            DOCS / "X4_meeting-minutes" / f"{P}_Minutes_2027-01-05.docx")
    _xbuild({"title": "Minutes", "language": "ja", "gridlines": True, "sheets": [
        {"name": "Meeting_Profile", "title": "会議概要", "subtitle": "KPI: 決定 3 件 ／ アクション 4 件（下段は数式）",
         "columns": [{"key": "k", "header": "項目", "width": 26}, {"key": "v", "header": "内容", "width": 60, "wrap": True}],
         "rows": [{"k": "会議名", "v": "キックオフ会議"}, {"k": "日時", "v": "2027-01-05 10:00–11:30"}, {"k": "出席者数", "v": 7},
                  {"k": "決定事項の数", "v": "=COUNTA(Decisions_Register!A4:A100)"}, {"k": "アクション数", "v": "=COUNTA(Action_Tracker!A4:A100)"}]},
        {"name": "Discussion_Details", "title": "議論の詳細", "subtitle": "議題ごとの発表者と要約",
         "columns": [{"key": "no", "header": "No.", "width": 6, "align": "center"}, {"key": "t", "header": "議題", "width": 26, "wrap": True},
                     {"key": "p", "header": "発表者", "width": 16}, {"key": "s", "header": "要約", "width": 70, "wrap": True}],
         "rows": [{"no": 1, "t": "目的・範囲の確認", "p": "PM", "s": "機能6件の範囲を確認。対象外を再確認"},
                  {"no": 2, "t": "スケジュール", "p": "PM", "s": f"{ctx['project']['go_live_target']} を目標。余裕 {gap_wk:.1f} 週"},
                  {"no": 3, "t": "未決事項", "p": "PM", "s": "Q-03・Q-04 の期限 2027-01-22 を合意"}]},
        {"name": "Decisions_Register", "title": "決定事項の登録", "subtitle": "DEC-NN。変更時は新しい ID を付けて旧 ID を『撤回』と記録",
         "columns": [{"key": "id", "header": "DEC-ID", "width": 10, "align": "center"}, {"key": "d", "header": "決定内容", "width": 64, "wrap": True},
                     {"key": "a", "header": "承認者", "width": 18}, {"key": "dt", "header": "日付", "width": 12, "align": "center"}],
         "rows": [{"id": "DEC-01", "d": "代理承認を許可（代理期間は最長30日）", "a": "人事課長", "dt": "2027-01-05"},
                  {"id": "DEC-02", "d": "残業申請は事前承認必須", "a": "人事課長", "dt": "2027-01-05"},
                  {"id": "DEC-03", "d": "承認済み申請の取消は未決（Q-03 回答まで対象外）", "a": "PM / 人事課長", "dt": "2027-01-05"}]},
        {"name": "Action_Tracker", "title": "アクショントラッカー", "subtitle": "ACT-NN。期限超過は赤、完了は緑（条件付き書式は Excel 側で設定）",
         "columns": [{"key": "id", "header": "ACT-ID", "width": 10, "align": "center"}, {"key": "t", "header": "内容", "width": 46, "wrap": True},
                     {"key": "own", "header": "担当", "width": 22}, {"key": "due", "header": "期限", "width": 13, "align": "center"},
                     {"key": "st", "header": "ステータス", "width": 12, "align": "center", "validate": ["Open", "In progress", "Done"]}],
         "rows": [{"id": "ACT-01", "t": "テスト環境の提供依頼", "own": "顧客・情報システム", "due": "2027-01-15", "st": "Open"},
                  {"id": "ACT-02", "t": "取込仕様の資料提供", "own": "顧客・人事担当", "due": "2027-01-15", "st": "Open"},
                  {"id": "ACT-03", "t": "Q-03・Q-04 の回答", "own": "顧客・人事課長", "due": "2027-01-22", "st": "Open"},
                  {"id": "ACT-04", "t": "第1スプリント計画", "own": "PM", "due": "2027-01-18", "st": "Open"}]},
    ]}, DOCS / "X4_meeting-minutes" / f"{P}_Minutes_2027-01-05.xlsx")

    # ================================================================ X1 オンボーディング（設計から作成・コード調査は別途）
    onboard = f"""# オンボーディングガイド — {name}

> 版 1.0 ／ 作成日 {today} ／ 対象: 新しく参加するメンバー
> 注意: このガイドは設計書から作成しました。実コードの構造調査（Architecture_Survey）は、リポジトリ作成後に /x1 で行ってください。

## 1. プロジェクトの概要
勤怠（休暇・残業）の申請と上長承認をWebで行い、月次の勤怠CSVを人事に出力するシステムです（架空の教材案件）。

## 2. 関係者
| 役割 | 担当 | 相談内容 |
|---|---|---|
| PM | [担当者] | スケジュール、顧客との調整、リスク |
| バックエンド | [担当者] | API、認証、CSV出力、DB |
| フロントエンド | [担当者] | 画面（SCR-01〜07） |
| QA | [担当者] | テスト計画、テストケース、試験結果 |
| 顧客（人事課長・人事担当・情報システム） | [担当者] | 業務ルール、CSVの仕様、テスト環境 |

## 3. 環境とアクセス
- リポジトリ・検証環境（STG）のURLは、PM に依頼してください。パスワードや鍵はこのガイドに書きません。
- 必要なアクセスは、PM が申請のうえ付与します。

## 4. 環境を整える（目安 30 分）
1. 開発環境: Node.js（LTS）、Docker、PostgreSQL 16（Docker で起動）。
2. リポジトリを clone し、`.env.example` を `.env` にコピーして値を設定します（値は PM から受け取ります）。
3. `docker compose up -d` で DB を起動し、migration（`migration_v1.sql`）を適用します。
4. テストを実行し、すべて成功することを確認します。

## 5. 全体の構成
- `API`（NestJS）: 認証・申請・承認・代理・CSV の各モジュール（設計書 詳細設計 6章）
- `DB`（PostgreSQL）: 8テーブル（DB設計書 参照）
- `Frontend`（Next.js）: SCR-01〜SCR-07

## 6. 主要な業務フロー
1. 申請者が休暇・残業を申請（SCR-02）→ 残業は事前承認が必要
2. 承認者が承認待ち一覧で承認または差戻し（SCR-05）
3. 人事が月次CSVを出力（SCR-07）

## 7. 最初に読む資料（順番どおり）
1. 基本設計書（画面・機能）→ 2. 詳細設計書（処理・エラー）→ 3. API設計書（API一覧）→ 4. テスト計画（テストケース）

## 8. 最初の作業（2〜3日）
- 文言の修正（画面のメッセージ）を1件行い、PR を出す。
- 既存テストに1ケース追加する。

## 9. よくある質問
- **Q: 申請の取消はできますか？** A: 未決事項です（Q-03）。回答が出るまで実装しません。
- **Q: CSVの文字コードは？** A: Shift_JIS の予定ですが、Q-04 の回答後に確定します。
- **Q: パスワードの規則は？** A: 12文字以上、初回ログイン時に変更（Q-06）。
- **Q: 本番の情報はどこで確認しますか？** A: 運用手順書（Runbook）を参照し、アクセスは PM に依頼します。

## 10. 困ったとき
PM に連絡してください。緊急時は運用手順書の連絡先に従います。

## 11. 改訂履歴
| 版 | 日付 | 変更内容 | 担当 |
|---|---|---|---|
| 1.0 | {today} | 初版 | [担当者] |
"""
    (DOCS / "X1_acquire-codebase-knowledge").mkdir(parents=True, exist_ok=True)
    (DOCS / "X1_acquire-codebase-knowledge" / f"{P}_Onboarding_Guide.md").write_text(onboard, encoding="utf-8")

    return {"price": price, "pm": pm, "total_md": total_md}
