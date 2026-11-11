# -*- coding: utf-8 -*-
"""extra_cases.py — case bổ sung cho các loại E2E, SMK (smoke sau deploy), REG (hồi quy).
Được gen_sample.py nạp vào CASES để đủ 10 loại test theo đặc tả a8 (coverage matrix)."""

P1 = "🔴 P1-Critical"
P2 = "🟠 P2-High"


def tc(tid, feat, module, feature, ttype, prio, pre, steps, data, expect, api, tbl, auto, note=""):
    return [tid, feat, module, feature, ttype, prio, pre, steps, data, expect, api, tbl, auto, note]


EXTRA = {
    "AUTH": [
        tc("AUTH-E2E-001", "FEAT-AUTH-01", "AUTH", "ログイン〜画面遷移", "E2E", P1,
           "社員100001（一般）が未ログイン",
           "1. SCR-01 で社員番号とパスワードを入力して認証\n2. SCR-03（申請一覧）へ遷移することを確認\n3. ログアウト後に SCR-03 を直接開く",
           "社員100001 / 正しいパスワード",
           "2. 申請一覧が表示される\n3. SCR-01 にリダイレクトされ、一覧データは表示されない",
           "POST /api/v1/auth/login", "users, auth_sessions", "Y", "E2E（Playwright）"),
        tc("AUTH-SMK-001", "FEAT-AUTH-01", "AUTH", "デプロイ後の疎通", "SMK", P1,
           "STG へのデプロイ完了",
           "1. GET /health を実行\n2. POST /auth/login（テストアカウント）を実行",
           "テストアカウント（SMOKE_PASSWORD は環境変数）",
           "health 200、login 200 で accessToken を取得",
           "GET /health, POST /api/v1/auth/login", "users", "Y", "c8 smoke_test_runner"),
    ],
    "LEAVE": [
        tc("LEAVE-E2E-001", "FEAT-LEAVE-01", "LEAVE", "申請〜承認の一連の流れ", "E2E", P1,
           "一般社員と承認者（上長）が存在し、社員の上長が承認者として設定済み",
           "1. 社員が有給を提出（SCR-02）\n2. 承認者がログインし承認待ち一覧で承認（SCR-05）\n3. 社員が一覧で「承認済み」を確認（SCR-03）",
           "有給 2027-02-01 / 承認者 100002",
           "3. 状態が「承認済み」、承認履歴に承認者名が表示される",
           "POST /api/v1/leave-requests, POST .../approve", "leave_requests, approval_steps", "Y", "E2E（Playwright）"),
    ],
    "APPR": [
        tc("APPR-E2E-001", "FEAT-APPR-01", "APPR", "差戻し〜再提出の一連の流れ", "E2E", P1,
           "submitted の申請が承認者の承認待ちにある",
           "1. 承認者が理由付きで差戻し\n2. 申請者が詳細画面で理由を確認し、修正して再提出\n3. 承認者の承認待ちに再表示される",
           "理由: 日付を確認してください",
           "2. 差戻し理由が画面に表示される\n3. 状態が submitted に戻り、承認待ちに現れる",
           "POST .../reject, POST /api/v1/leave-requests/{id}/submit", "leave_requests, approval_steps", "Y", "E2E（Playwright）"),
    ],
    "REPORT": [
        tc("REPORT-REG-001", "FEAT-REPORT-01", "REPORT", "CR-001 後の既存CSV回帰", "REG", P1,
           "CR-001（部門別合計行の追加）を適用済み",
           "1. 既存の受入データ（2027-02）で CSV を取得\n2. 列順と既存行を基準CSV（ベースライン）と比較",
           "departmentId=既存部門, yearMonth=2027-02",
           "既存の列・行は基準と完全一致。追加行は末尾の「部門合計」のみ",
           "GET /api/v1/reports/monthly-attendance.csv", "leave_requests, users", "Y", "CR-001 の回帰（C7 の再試験範囲）"),
        tc("REPORT-SMK-001", "FEAT-REPORT-01", "REPORT", "デプロイ後のCSV疎通", "SMK", P2,
           "STG デプロイ完了・人事テストアカウント",
           "1. 人事アカウントで CSV を 1 件取得",
           "yearMonth=当月",
           "200、text/csv、ヘッダ行あり",
           "GET /api/v1/reports/monthly-attendance.csv", "—", "Y", "c8 smoke"),
    ],
}

EXTRA["APPR"].append(
    tc("APPR-UT-001", "FEAT-APPR-01", "APPR", "状態遷移ルール（単体）", "UT", P1,
       "—",
       "1. 状態遷移関数に次の組を入力する: draft→submitted / submitted→approved / submitted→rejected / approved→submitted\n2. 各遷移の戻り値を確認する",
       "from/to の 4 組（上記）",
       "許可される遷移（draft→submitted, submitted→approved, submitted→rejected）は成功。approved→submitted は例外 INVALID_TRANSITION",
       "（単体。API を経由しない）", "leave_requests.status", "Y", "状態遷移表と一致させる（a5 の CHECK 制約）"))
EXTRA["LEAVE2"] = [
    tc("LEAVE2-E2E-001", "FEAT-LEAVE-02", "LEAVE", "一覧の絞り込みと詳細遷移", "E2E", P2,
       "申請が状態の異なる 3 件（draft / submitted / approved）ある",
       "1. SCR-03 で状態 = submitted に絞り込む\n2. 1 件を選び SCR-04 へ遷移する\n3. 戻るボタンで一覧の絞り込みが保持されることを確認",
       "状態 = submitted",
       "2. 申請詳細が表示 ／ 3. 絞り込み条件が保持される（URL のクエリで再現可能）",
       "GET /api/v1/leave-requests, GET /api/v1/leave-requests/{id}", "leave_requests", "Y", "E2E（Playwright）"),
]
