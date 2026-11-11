# -*- coding: utf-8 -*-
"""gen_sample.py — dữ liệu dự án MẪU E2E: 勤怠承認システム（サンプル・架空）.
Không liên quan khách thật. Chạy qua build_all.py; output vào $E2E_WS (mặc định: thư mục tạm)."""
import json, math, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]  # skills/evals/e2e/gen_sample.py → gốc repo
import os, tempfile
sys.path.insert(0, str(REPO / "skills/a1-project-init/scripts"))
from xlsx_build import build  # noqa: E402

WS = Path(os.environ.get("E2E_WS", Path(tempfile.gettempdir()) / "attendance-e2e" / "ws"))
DOCS = WS / "docs"
PROJ = "Sample_Attendance"  # tên file không dấu, không chứa tên khách thật

# ---------------------------------------------------------------- context
ctx = {
    "version": "3.17.2",
    "created_at": "2026-11-12",
    "updated_at": "2026-11-12",
    "project": {"name": "勤怠承認システム（サンプル）", "client": "サンプル株式会社（架空）", "type": "web_app",
                "description": "社員の休暇・残業申請と上長承認をWebで行い、月次勤怠CSVを出力する社内システム（教材用の架空案件）。",
                "start_date": "2027-01-04", "go_live_target": "2027-03-31", "current_sprint": 0, "current_phase": "A"},
    "tech_stack": {"backend": "NestJS (TypeScript)", "database": "PostgreSQL 16", "cache": "Redis", "mobile": "なし",
                   "admin_cms": "なし", "auth": "JWT (access 15分 / refresh 7日)", "hosting": "Docker on VM",
                   "ci_cd": "GitHub Actions", "monitoring": "Grafana + Prometheus", "push_notification": "なし"},
    "team": [
        {"id": "pm1", "role": "PM", "name": "[担当者]", "allocation": 0.5, "md_per_sprint": 5},
        {"id": "be1", "role": "BE", "name": "[担当者]", "allocation": 1, "md_per_sprint": 8},
        {"id": "be2", "role": "BE", "name": "[担当者]", "allocation": 1, "md_per_sprint": 8},
        {"id": "fe1", "role": "FE", "name": "[担当者]", "allocation": 1, "md_per_sprint": 8},
        {"id": "qa1", "role": "QA", "name": "[担当者]", "allocation": 1, "md_per_sprint": 7},
    ],
    "settings": {"sprint_duration_weeks": 2, "working_days_per_week": 5, "md_per_person_month": 22, "buffer_percent": 15,
                 "languages": {"client_facing": "ja", "internal": "vi", "code": "en"},
                 "quality_gates": {"ut_pass_rate": 95, "ut_coverage_line": 80, "ut_coverage_branch": 70,
                                   "it_pass_rate": 95, "st_pass_rate": 98, "open_critical_high_max": 0}},
    "estimates": {}, "links": {}, "change_requests": [], "known_issues": [], "activity_log": [],
}

FEATS = [
    ("FEAT-AUTH-01", "AUTH", "ログイン・ロール制御", "社員番号とパスワードでログインし、役割（一般・上長・人事）で画面と操作を制限する。"),
    ("FEAT-LEAVE-01", "LEAVE", "休暇・残業申請の作成", "休暇種別・期間・理由を入力して申請を作成し、下書き保存と提出ができる。"),
    ("FEAT-LEAVE-02", "LEAVE", "申請一覧・検索", "自分の申請を状態・期間で絞り込み、詳細を参照できる。"),
    ("FEAT-APPR-01", "APPR", "承認・差戻し", "上長が申請を承認または理由付きで差し戻す。承認履歴を残す。"),
    ("FEAT-APPR-02", "APPR", "承認者代理設定", "不在期間中の承認権限を代理者に期限付きで委任する。"),
    ("FEAT-REPORT-01", "REPORT", "月次勤怠CSV出力", "人事が部門・月を指定して承認済み申請を集計し、CSVを出力する。"),
]

# ---------------------------------------------------------------- A2 requirement + QA tracker
qa_rows = [
    ("Q-01", "P1", "承認者が不在の場合、代理承認を許可するか。許可する場合の期限上限は。", "承認フロー・権限設計（FEAT-APPR-02）", "回答済", "許可する。代理期限は最長30日。", "顧客・人事課長", "2027-01-15"),
    ("Q-02", "P1", "残業申請に事前承認を必要とするか。", "申請ステータス遷移（FEAT-LEAVE-01）", "回答済", "必要。事前承認なしの残業は月次集計で警告表示。", "顧客・人事課長", "2027-01-15"),
    ("Q-03", "P1", "承認済み申請の取消（撤回）を誰ができるか。", "状態遷移・監査要件（FEAT-APPR-01）", "未回答", "", "顧客・人事課長", "2027-01-22"),
    ("Q-04", "P1", "CSV出力の文字コードと列順（人事の既存取込仕様）。", "出力仕様（FEAT-REPORT-01）", "未回答", "", "顧客・人事担当", "2027-01-22"),
    ("Q-05", "P2", "休暇種別の一覧（有給・特別・代休など）と付与日数の管理主体。", "マスタ設計（DB）", "回答済", "有給・特別・代休・慶弔の4種。付与は人事システム連携の後フェーズ。", "顧客・人事担当", "2027-01-20"),
    ("Q-06", "P2", "パスワード規則と初期パスワード配布方法。", "認証（FEAT-AUTH-01）", "回答済", "12文字以上、初回ログイン時変更。配布は社内メール。", "顧客・情報システム", "2027-01-20"),
    ("Q-07", "P3", "一覧の既定の並び順。", "UI（FEAT-LEAVE-02）", "回答済", "申請日の降順。", "顧客・人事担当", "2027-01-25"),
]

nfr = [
    ("NFR-PERF-01", "PERF", "申請一覧（1,000件・検索込み）の応答時間", "p95 ≤ 800 ms（社内LAN、同時利用50名）", "k6による負荷試験（8章 Performance Plan）", "Must"),
    ("NFR-AVAIL-01", "AVAIL", "業務時間内の稼働率", "平日 8:00–20:00 で 99.5% 以上（月次）", "監視（Grafana）の稼働率レポート", "Must"),
    ("NFR-SEC-01", "SEC", "認証と通信の保護", "全通信TLS1.2以上。JWT有効期限 access 15分 / refresh 7日。ログイン失敗5回で10分ロック。", "セキュリティ試験（TC-SEC系）・設定レビュー", "Must"),
    ("NFR-SEC-02", "SEC", "権限外データへのアクセス防止（IDOR）", "他人の申請IDを指定しても 403。全APIでオブジェクト所有権を検査。", "API試験（認可ケース）", "Must"),
    ("NFR-PRIV-01", "PRIV", "個人情報の保存期間", "申請データは退職後5年で削除（人事規程に従う）。", "削除バッチの試験と運用手順書", "Should"),
    ("NFR-MAINT-01", "MAINT", "変更容易性", "新しい休暇種別をマスタ追加のみで利用可能（コード変更不要）。", "設計レビュー", "Should"),
    ("NFR-COMPAT-01", "COMPAT", "対応ブラウザ", "Google Chrome・Microsoft Edge の最新版と1つ前の版。", "ブラウザ別の受入試験", "Must"),
]

# ---------------------------------------------------------------- A4 API endpoints
APIS = [
    # (module, no, method, path, desc, auth, middleware, input, output, status, tables, errors, tests, since, notes)
    ("AUTH", 1, "POST", "/api/v1/auth/login", "社員番号とパスワードでログインし、アクセストークンを発行する。", "N", "RateLimit(5/10min)",
     "body: employeeId(string,6桁), password(string,12文字以上)", "data: {accessToken, refreshToken, expiresIn, role}", 200,
     "READ: users · WRITE: auth_sessions", "400 形式不正 · 401 認証失敗 · 423 ロック中", "✓ 正常 → 200 · ✗ 誤パス → 401 · ✗ 5回失敗 → 423 · ✗ 形式不正 → 400", "v1.0", "ロック解除は人事のみ（別API）"),
    ("LEAVE", 1, "POST", "/api/v1/leave-requests", "休暇・残業の申請を作成する（下書きまたは提出）。", "Y", "Auth, RateLimit(30/min)",
     "body: type(enum), dateFrom(date), dateTo(date), hours(number,任意), reason(string,500字以内), submit(boolean)", "data: {id, status, createdAt}", 201,
     "WRITE: leave_requests, approval_steps", "400 入力不正 · 401 · 409 期間重複 · 422 残業の事前承認なし", "✓ 下書き → 201 · ✓ 提出 → 201 status=submitted · ✗ 期間逆転 → 400 · ✗ 重複 → 409 · ✗ 事前承認なし残業 → 422", "v1.0", "Q-02 により残業は事前承認必須"),
    ("LEAVE", 2, "GET", "/api/v1/leave-requests", "自分の申請を状態・期間で絞り込み一覧表示する。", "Y", "Auth, RateLimit(60/min)",
     "query: status(enum,任意), from(date,任意), to(date,任意), page(int≥1), pageSize(int 1–100)", "data: {items[], total}", 200,
     "READ: leave_requests", "400 クエリ不正 · 401", "✓ 既定 → 200 · ✓ 絞込 → 200 · ✗ pageSize=101 → 400 · ✗ 未認証 → 401", "v1.0", "既定の並びは申請日降順（Q-07）"),
    ("LEAVE", 3, "GET", "/api/v1/leave-requests/{id}", "申請の詳細と承認履歴を返す。本人または承認者のみ。", "Y", "Auth, Ownership",
     "params: id(uuid)", "data: {id, type, dateFrom, dateTo, hours, reason, status, steps[]}", 200,
     "READ: leave_requests, approval_steps, users", "401 · 403 他人の申請 · 404 不存在", "✓ 本人 → 200 · ✓ 承認者 → 200 · ✗ 他人 → 403 · ✗ 存在しないID → 404", "v1.0", "NFR-SEC-02"),
    ("APPR", 1, "POST", "/api/v1/leave-requests/{id}/approve", "承認者が申請を承認する。承認済みは監査ログに記録。", "Y", "Auth, Role(manager), Ownership(approver)",
     "params: id(uuid); body: comment(string,任意)", "data: {id, status}", 200,
     "WRITE: approval_steps, leave_requests, audit_logs", "401 · 403 承認権限なし · 404 · 409 状態が submitted でない", "✓ 承認 → 200 · ✗ 権限なし → 403 · ✗ 既に承認済み → 409", "v1.0", "Q-03 未決（取消は未実装）"),
    ("APPR", 2, "POST", "/api/v1/leave-requests/{id}/reject", "承認者が理由付きで差し戻す。理由は必須。", "Y", "Auth, Role(manager), Ownership(approver)",
     "params: id(uuid); body: reason(string,1–500字)", "data: {id, status}", 200,
     "WRITE: approval_steps, leave_requests, audit_logs", "400 理由なし · 401 · 403 · 409", "✓ 差戻し → 200 · ✗ 理由なし → 400 · ✗ 権限なし → 403", "v1.0", ""),
    ("APPR", 3, "PUT", "/api/v1/approver-delegations", "代理承認者を期限付きで設定する（上限30日）。", "Y", "Auth, Role(manager), RateLimit(10/min)",
     "body: delegateId(uuid), validFrom(date), validTo(date)", "data: {id, delegateId, validFrom, validTo}", 200,
     "WRITE: approver_delegations, audit_logs", "400 期間が31日以上 · 401 · 403 · 404 代理者不存在", "✓ 設定 → 200 · ✗ 31日 → 400 · ✗ 過去日 → 400 · ✗ 役割外 → 403", "v1.0", "Q-01: 最長30日"),
    ("REPORT", 1, "GET", "/api/v1/reports/monthly-attendance.csv", "部門と月を指定し、承認済み申請を集計したCSVを返す。", "Y", "Auth, Role(hr), RateLimit(5/min)",
     "query: departmentId(uuid), yearMonth(YYYY-MM)", "text/csv (Shift_JIS, CRLF)", 200,
     "READ: leave_requests, users, departments", "400 年月不正 · 401 · 403 · 404 部門なし", "✓ 集計 → 200 CSV · ✗ 年月 2027-13 → 400 · ✗ 人事以外 → 403", "v1.0", "Q-04 は未決（文字コード・列順）"),
    ("AUTH", 2, "POST", "/api/v1/auth/refresh", "refreshトークンでアクセストークンを再発行する。", "N", "RateLimit(20/min)",
     "body: refreshToken(string)", "data: {accessToken, expiresIn}", 200,
     "READ: auth_sessions · WRITE: auth_sessions", "401 無効・期限切れ", "✓ 有効 → 200 · ✗ 失効済み → 401", "v1.0", "refreshは1回使い切り（ローテーション）"),
]

# ---------------------------------------------------------------- A5 DB tables
TABLES = [
    ("users", "社員", [
        ("id", "UUID", "NOT NULL", "[PK] DEFAULT gen_random_uuid()", "社員の内部ID"),
        ("employee_id", "VARCHAR(6)", "NOT NULL", "[UNIQUE] CHECK (employee_id ~ '^[0-9]{6}$')", "社員番号（6桁）"),
        ("name", "VARCHAR(100)", "NOT NULL", "", "氏名"),
        ("department_id", "UUID", "NOT NULL", "[FK] → departments(id) ON DELETE RESTRICT", "所属部門"),
        ("role", "VARCHAR(20)", "NOT NULL", "CHECK (role IN ('employee','manager','hr'))", "役割"),
        ("password_hash", "VARCHAR(255)", "NOT NULL", "", "Argon2id のハッシュ（平文は保存しない）"),
        ("failed_login_count", "SMALLINT", "NOT NULL", "DEFAULT 0", "連続ログイン失敗回数（成功で0）"),
        ("locked_until", "TIMESTAMPTZ", "NULL", "", "ロック解除時刻（NULLは未ロック）"),
        ("deleted_at", "TIMESTAMPTZ", "NULL", "", "論理削除（NFR-PRIV-01 の保存期間で物理削除）"),
    ]),
    ("departments", "部門", [
        ("id", "UUID", "NOT NULL", "[PK] DEFAULT gen_random_uuid()", ""),
        ("code", "VARCHAR(20)", "NOT NULL", "[UNIQUE]", "部門コード"),
        ("name", "VARCHAR(100)", "NOT NULL", "", "部門名"),
    ]),
    ("leave_types", "休暇種別マスタ", [
        ("code", "VARCHAR(20)", "NOT NULL", "[PK]", "例: ANNUAL / SPECIAL / SUBSTITUTE / CONDOLENCE"),
        ("name", "VARCHAR(50)", "NOT NULL", "", "表示名"),
        ("is_active", "BOOLEAN", "NOT NULL", "DEFAULT TRUE", "利用可否（マスタ追加のみで拡張，NFR-MAINT-01）"),
    ]),
    ("leave_requests", "休暇・残業申請", [
        ("id", "UUID", "NOT NULL", "[PK] DEFAULT gen_random_uuid()", ""),
        ("applicant_id", "UUID", "NOT NULL", "[FK] → users(id) ON DELETE RESTRICT", "申請者"),
        ("type_code", "VARCHAR(20)", "NOT NULL", "[FK] → leave_types(code)", "休暇種別（残業は OVERTIME を別途マスタ化）"),
        ("date_from", "DATE", "NOT NULL", "CHECK (date_to >= date_from)", "開始日"),
        ("date_to", "DATE", "NOT NULL", "", "終了日"),
        ("hours", "NUMERIC(5,2)", "NULL", "CHECK (hours IS NULL OR hours BETWEEN 0 AND 24)", "残業時間（残業のみ）"),
        ("reason", "VARCHAR(500)", "NULL", "", "理由"),
        ("status", "VARCHAR(20)", "NOT NULL", "DEFAULT 'draft' CHECK (status IN ('draft','submitted','approved','rejected'))", "状態"),
        ("version", "INTEGER", "NOT NULL", "DEFAULT 1", "楽観ロック（更新ごとに+1，409の判定に使用）"),
        ("created_at", "TIMESTAMPTZ", "NOT NULL", "DEFAULT now()", ""),
        ("updated_at", "TIMESTAMPTZ", "NOT NULL", "DEFAULT now()", "トリガーで更新（migration参照）"),
    ]),
    ("approval_steps", "承認履歴", [
        ("id", "UUID", "NOT NULL", "[PK] DEFAULT gen_random_uuid()", ""),
        ("request_id", "UUID", "NOT NULL", "[FK] → leave_requests(id) ON DELETE CASCADE", ""),
        ("approver_id", "UUID", "NOT NULL", "[FK] → users(id)", "実際に承認した人（代理含む）"),
        ("action", "VARCHAR(20)", "NOT NULL", "CHECK (action IN ('approved','rejected'))", ""),
        ("comment", "VARCHAR(500)", "NULL", "", ""),
        ("acted_at", "TIMESTAMPTZ", "NOT NULL", "DEFAULT now()", ""),
    ]),
    ("approver_delegations", "承認者代理", [
        ("id", "UUID", "NOT NULL", "[PK] DEFAULT gen_random_uuid()", ""),
        ("principal_id", "UUID", "NOT NULL", "[FK] → users(id)", "委任者"),
        ("delegate_id", "UUID", "NOT NULL", "[FK] → users(id)", "代理者"),
        ("valid_from", "DATE", "NOT NULL", "", ""),
        ("valid_to", "DATE", "NOT NULL", "CHECK (valid_to >= valid_from AND valid_to - valid_from <= 30)", "最長30日（Q-01）"),
    ]),
    ("auth_sessions", "認証セッション（refresh トークン）", [
        ("id", "UUID", "NOT NULL", "[PK] DEFAULT gen_random_uuid()", ""),
        ("user_id", "UUID", "NOT NULL", "[FK] → users(id) ON DELETE CASCADE", "所有者"),
        ("refresh_token_hash", "VARCHAR(255)", "NOT NULL", "[UNIQUE]", "refresh トークンのハッシュ（平文は保存しない）"),
        ("expires_at", "TIMESTAMPTZ", "NOT NULL", "", "有効期限（7日）"),
        ("revoked_at", "TIMESTAMPTZ", "NULL", "", "ローテーションで使用済みになった時刻（NULL=有効）"),
    ]),
    ("audit_logs", "監査ログ（追記のみ）", [
        ("id", "BIGSERIAL", "NOT NULL", "[PK]", ""),
        ("actor_id", "UUID", "NOT NULL", "[FK] → users(id)", ""),
        ("action", "VARCHAR(50)", "NOT NULL", "", "例: LEAVE_APPROVED"),
        ("target_type", "VARCHAR(50)", "NOT NULL", "", ""),
        ("target_id", "UUID", "NOT NULL", "", ""),
        ("payload", "JSONB", "NULL", "", "変更前後の要約（個人情報は含めない）"),
        ("occurred_at", "TIMESTAMPTZ", "NOT NULL", "DEFAULT now()", ""),
    ]),
]

# ---------------------------------------------------------------- A8 test cases (mỗi FEAT ≥ 6 case nguyên tử)
def tc(tid, feat, module, feature, ttype, prio, pre, steps, data, expect, api, tbl, auto, note=""):
    return [tid, feat, module, feature, ttype, prio, pre, steps, data, expect, api, tbl, auto, note]

P1, P2, P3 = "🔴 P1-Critical", "🟠 P2-High", "🟡 P3-Medium"
CASES = {
 "AUTH": [
  tc("AUTH-API-001", "FEAT-AUTH-01", "AUTH", "ログイン", "API", P1, "社員マスタに employee_id=100001 が存在し未ロック", "1. POST /api/v1/auth/login を送信\n2. レスポンスを確認", "employeeId: 100001 / password: 正しい値（12文字）", "200、data.accessToken と refreshToken が返る、expiresIn=900", "POST /api/v1/auth/login", "users, auth_sessions", "Y"),
  tc("AUTH-API-002", "FEAT-AUTH-01", "AUTH", "ログイン", "API", P1, "同上", "1. 誤ったパスワードで送信", "password: 誤り（12文字）", "401、本文にどの項目が誤りか（ID/パスワード）を示さない", "POST /api/v1/auth/login", "users", "Y", "列挙攻撃対策"),
  tc("AUTH-API-003", "FEAT-AUTH-01", "AUTH", "ログイン", "API", P1, "同上", "1. 誤りで5回連続送信\n2. 6回目に正しいパスワードで送信", "5回誤り → 6回目は正しい値", "5回目まで401、6回目は423（10分間ロック）、failed_login_count=5", "POST /api/v1/auth/login", "users", "Y", "NFR-SEC-01"),
  tc("AUTH-VAL-001", "FEAT-AUTH-01", "AUTH", "ログイン", "UT", P2, "—", "1. employeeId を 5 桁・6 桁・数字以外で送信（3ケース）", "\"12345\" / \"1234567\" / \"12A456\"", "3ケースとも 400、エラーコードが VAL_001", "POST /api/v1/auth/login", "—", "Y", "EP/BVA"),
  tc("AUTH-VAL-002", "FEAT-AUTH-01", "AUTH", "ログイン", "UT", P2, "—", "1. password を 11 文字・12 文字で送信", "11文字 / 12文字", "11文字は 400、12文字は受理（認証は別途）", "POST /api/v1/auth/login", "—", "Y", "境界値"),
  tc("AUTH-SEC-001", "FEAT-AUTH-01", "AUTH", "ログイン", "SEC", P1, "社員Aの refresh_token を取得済み", "1. 社員Aのrefresh で /auth/refresh を2回送信", "同一トークン 2回", "1回目 200（新トークン発行）、2回目 401（ローテーション）", "POST /api/v1/auth/refresh", "auth_sessions", "Y", "NFR-SEC-01"),
  tc("AUTH-SEC-002", "FEAT-AUTH-01", "AUTH", "権限", "SEC", P1, "一般社員のアクセストークン", "1. 人事用 CSV API を一般社員のトークンで呼ぶ", "GET .../monthly-attendance.csv", "403（役割 hr 以外）", "GET /api/v1/reports/monthly-attendance.csv", "users", "Y", "RBAC"),
 ],
 "LEAVE": [
  tc("LEAVE-API-001", "FEAT-LEAVE-01", "LEAVE", "休暇申請の作成", "API", P1, "一般社員でログイン済み", "1. 有給（ANNUAL）を 2027-02-01〜02-01 で提出", "type=ANNUAL, dateFrom=2027-02-01, dateTo=2027-02-01, submit=true", "201、status=submitted、承認者へ承認ステップが生成", "POST /api/v1/leave-requests", "leave_requests, approval_steps", "Y"),
  tc("LEAVE-API-002", "FEAT-LEAVE-01", "LEAVE", "休暇申請の作成", "API", P2, "同上", "1. 下書き（submit=false）で作成", "submit=false", "201、status=draft、承認ステップは生成されない", "POST /api/v1/leave-requests", "leave_requests", "Y"),
  tc("LEAVE-VAL-001", "FEAT-LEAVE-01", "LEAVE", "休暇申請の作成", "UT", P1, "同上", "1. dateTo < dateFrom で送信", "dateFrom=2027-02-05, dateTo=2027-02-01", "400、VAL_002（期間が逆転）", "POST /api/v1/leave-requests", "—", "Y"),
  tc("LEAVE-VAL-002", "FEAT-LEAVE-01", "LEAVE", "休暇申請の作成", "UT", P2, "同上", "1. reason を 500 字・501 字で送信", "500字 / 501字", "500字は 201、501字は 400", "POST /api/v1/leave-requests", "—", "Y", "境界値"),
  tc("LEAVE-BIZ-001", "FEAT-LEAVE-01", "LEAVE", "残業申請", "API", P1, "事前承認のある残業申請が存在しない", "1. type=OVERTIME を提出（事前承認なし）", "type=OVERTIME, hours=2", "422（Q-02: 事前承認が必要）", "POST /api/v1/leave-requests", "leave_requests", "Y"),
  tc("LEAVE-BIZ-002", "FEAT-LEAVE-01", "LEAVE", "休暇申請の作成", "API", P1, "同日に承認済みの休暇がある", "1. 同じ日付範囲で再申請", "date_from/date_to が既存と重複", "409（期間重複）、DB に行は増えない", "POST /api/v1/leave-requests", "leave_requests", "Y"),
  tc("LEAVE-BND-001", "FEAT-LEAVE-01", "LEAVE", "残業時間", "UT", P2, "—", "1. hours を 0, 24, 24.01, -1 で送信", "0 / 24 / 24.01 / -1", "0・24 は受理、24.01 と -1 は 400", "POST /api/v1/leave-requests", "leave_requests", "Y", "CHECK 制約と一致"),
  tc("LEAVE-UI-001", "FEAT-LEAVE-01", "LEAVE", "申請フォーム", "UI", P3, "ブラウザ Chrome 最新", "1. 理由欄に 500 字入力中に残り文字数を確認", "500字", "残り文字数が 0 と表示。超過入力は不可", "—", "—", "N", "表示と入力制限"),
  tc("LEAVE-CON-001", "FEAT-LEAVE-01", "LEAVE", "申請の二重送信", "CON", P1, "同一ユーザーが2タブで同じ下書きを開く", "1. 両タブで提出を同時に押す", "同一 id", "1件のみ submitted。もう一方は 409（version 不一致）", "POST /api/v1/leave-requests/{id}/submit", "leave_requests", "N", "OCC（version）"),
 ],
 "LEAVE2": [
  tc("LEAVE2-API-001", "FEAT-LEAVE-02", "LEAVE", "申請一覧", "API", P2, "自分の申請が3件", "1. GET /api/v1/leave-requests", "既定", "200、items が申請日の降順、total=3", "GET /api/v1/leave-requests", "leave_requests", "Y", "Q-07"),
  tc("LEAVE2-API-002", "FEAT-LEAVE-02", "LEAVE", "申請一覧", "API", P2, "同上", "1. status=approved で絞込", "status=approved", "承認済みのみ", "GET /api/v1/leave-requests", "leave_requests", "Y"),
  tc("LEAVE2-BND-001", "FEAT-LEAVE-02", "LEAVE", "ページング", "UT", P2, "—", "1. pageSize=1, 100, 101, 0", "各値", "1 と 100 は 200、101 と 0 は 400", "GET /api/v1/leave-requests", "—", "Y", "EP/BVA"),
  tc("LEAVE2-SEC-001", "FEAT-LEAVE-02", "LEAVE", "他人の申請", "SEC", P1, "社員Bの申請IDを把握", "1. 社員A のトークンで社員B の申請詳細を取得", "id=社員Bの申請", "403（IDOR 防止）、本文に申請内容を含まない", "GET /api/v1/leave-requests/{id}", "leave_requests", "Y", "NFR-SEC-02"),
  tc("LEAVE2-SEC-002", "FEAT-LEAVE-02", "LEAVE", "一覧の範囲", "SEC", P1, "社員A と B が申請を持つ", "1. 社員A で一覧を取得", "既定", "社員A の申請のみ。B の行が含まれない", "GET /api/v1/leave-requests", "leave_requests", "Y"),
  tc("LEAVE2-PERF-001", "FEAT-LEAVE-02", "LEAVE", "一覧性能", "PERF", P2, "1,000件の申請データ", "1. 検索込みで 50 同時ユーザー", "k6 シナリオ LIST-01", "p95 ≤ 800 ms（NFR-PERF-01）", "GET /api/v1/leave-requests", "leave_requests", "Y"),
 ],
 "APPR": [
  tc("APPR-API-001", "FEAT-APPR-01", "APPR", "承認", "API", P1, "上長Mが承認者の submitted 申請", "1. POST .../approve", "comment=なし", "200、status=approved、approval_steps に action=approved、audit_logs に LEAVE_APPROVED", "POST /api/v1/leave-requests/{id}/approve", "approval_steps, leave_requests, audit_logs", "Y"),
  tc("APPR-API-002", "FEAT-APPR-01", "APPR", "差戻し", "API", P1, "同上", "1. reject で reason を空で送信", "reason=\"\"", "400（理由必須）、状態は submitted のまま", "POST /api/v1/leave-requests/{id}/reject", "leave_requests", "Y"),
  tc("APPR-API-003", "FEAT-APPR-01", "APPR", "差戻し", "API", P1, "同上", "1. 理由付きで差戻し", "reason=\"日付を確認してください\"", "200、status=rejected、申請者は再提出可能", "POST /api/v1/leave-requests/{id}/reject", "leave_requests, approval_steps", "Y"),
  tc("APPR-BIZ-001", "FEAT-APPR-01", "APPR", "承認", "API", P1, "申請は既に approved", "1. 再度 approve", "—", "409（状態が submitted でない）", "POST /api/v1/leave-requests/{id}/approve", "leave_requests", "Y", "状態遷移"),
  tc("APPR-SEC-001", "FEAT-APPR-01", "APPR", "承認権限", "SEC", P1, "申請者の上長は M、社員 C は無関係", "1. 社員 C のトークンで approve", "—", "403、状態は変わらない", "POST /api/v1/leave-requests/{id}/approve", "leave_requests", "Y", "NFR-SEC-02"),
  tc("APPR-CON-001", "FEAT-APPR-01", "APPR", "同時承認", "CON", P1, "承認者 M と代理者 D が同時に承認", "1. 両者が同時に approve", "同一 id", "1件のみ成功、もう一方は 409。approval_steps は 1 行のみ", "POST /api/v1/leave-requests/{id}/approve", "approval_steps", "N", "OCC"),
  tc("APPR-SEC-002", "FEAT-APPR-01", "APPR", "XSS", "SEC", P2, "理由欄に script タグを含むコメント", "1. comment に <script>alert(1)</script> を入れて承認 → 一覧で表示", "comment", "スクリプトは実行されず文字列として表示", "POST /api/v1/leave-requests/{id}/approve", "approval_steps", "N", "出力エスケープ"),
 ],
 "APPR2": [
  tc("APPR2-API-001", "FEAT-APPR-02", "APPR", "代理設定", "API", P1, "上長M・代理D が有効", "1. PUT /api/v1/approver-delegations（30日）", "validFrom=今日, validTo=今日+30日", "200、approver_delegations に保存", "PUT /api/v1/approver-delegations", "approver_delegations, audit_logs", "Y"),
  tc("APPR2-BND-001", "FEAT-APPR-02", "APPR", "代理期間", "UT", P1, "—", "1. 期間を 30 日・31 日で送信", "30日 / 31日", "30日は 200、31日は 400", "PUT /api/v1/approver-delegations", "approver_delegations", "Y", "Q-01 上限30日"),
  tc("APPR2-VAL-001", "FEAT-APPR-02", "APPR", "代理期間", "UT", P2, "—", "1. validTo < validFrom", "逆転", "400", "PUT /api/v1/approver-delegations", "—", "Y"),
  tc("APPR2-BIZ-001", "FEAT-APPR-02", "APPR", "代理の効力", "API", P1, "代理期間内", "1. 代理者 D が M の submitted 申請を承認", "—", "200。approval_steps.approver_id=D（代理を記録）", "POST .../approve", "approval_steps", "Y"),
  tc("APPR2-BIZ-002", "FEAT-APPR-02", "APPR", "代理の効力", "API", P1, "代理期間の翌日", "1. 代理者 D が承認を試みる", "—", "403（期間外）", "POST .../approve", "approver_delegations", "Y"),
  tc("APPR2-SEC-001", "FEAT-APPR-02", "APPR", "代理設定の権限", "SEC", P1, "一般社員 E がログイン", "1. E が代理設定を試みる", "—", "403（役割 manager 以上のみ）", "PUT /api/v1/approver-delegations", "—", "Y"),
 ],
 "REPORT": [
  tc("REPORT-API-001", "FEAT-REPORT-01", "REPORT", "月次CSV", "API", P1, "人事ロールでログイン、対象部門に承認済み申請あり", "1. departmentId, yearMonth=2027-02 で取得", "—", "200、Content-Type text/csv、Shift_JIS、CRLF、列順は Q-04 の決定どおり", "GET /api/v1/reports/monthly-attendance.csv", "leave_requests, users, departments", "Y", "Q-04 未決のため仮仕様"),
  tc("REPORT-VAL-001", "FEAT-REPORT-01", "REPORT", "月次CSV", "UT", P2, "—", "1. yearMonth=2027-13, 2027-1, 2027-02", "各値", "2027-13 と 2027-1 は 400、2027-02 は 200", "GET /api/v1/reports/monthly-attendance.csv", "—", "Y"),
  tc("REPORT-BIZ-001", "FEAT-REPORT-01", "REPORT", "集計", "API", P1, "承認済み・差戻し・下書きが混在", "1. 当月CSVを取得し件数を照合", "—", "承認済みのみ集計。差戻し・下書きは 0 件", "GET /api/v1/reports/monthly-attendance.csv", "leave_requests", "Y"),
  tc("REPORT-SEC-001", "FEAT-REPORT-01", "REPORT", "権限", "SEC", P1, "一般社員ログイン", "1. CSV を取得", "—", "403", "GET /api/v1/reports/monthly-attendance.csv", "—", "Y"),
  tc("REPORT-BND-001", "FEAT-REPORT-01", "REPORT", "件数", "PERF", P3, "対象 5,000 件", "1. 出力時間を計測", "—", "30 秒以内（社内目安）、メモリ 512MB 以内", "GET /api/v1/reports/monthly-attendance.csv", "leave_requests", "Y"),
  tc("REPORT-ENC-001", "FEAT-REPORT-01", "REPORT", "文字コード", "UT", P1, "氏名に「髙」「﨑」など環境依存文字を含む", "1. CSV を Shift_JIS でデコード", "—", "文字化けなし。変換不能文字は既定の代替規則（Q-04）に従う", "GET /api/v1/reports/monthly-attendance.csv", "users", "Y"),
 ],
}

# Case bổ sung E2E / SMK / REG (extra_cases.py) — đủ 10 loại test theo a8
from extra_cases import EXTRA as _EXTRA  # noqa: E402
for _k, _cases in _EXTRA.items():
    CASES[_k].extend(_cases)


def cases_flat():
    out = []
    for k in ["AUTH", "LEAVE", "LEAVE2", "APPR", "APPR2", "REPORT"]:
        out.extend(CASES[k])
    return out

# ---------------------------------------------------------------- A6 estimate tasks (md)
TASKS = [
    # (module, task, role, bd, dd, dev, ut, it)
    ("AUTH", "認証基盤（JWT・refresh・ロック）", "BE", 0.5, 1, 4, 1.5, 1),
    ("AUTH", "ログイン画面・ロール別メニュー", "FE", 0.5, 1, 3, 1, 0.5),
    ("LEAVE", "申請作成API・検証・重複チェック", "BE", 0.5, 1, 5, 2, 1.5),
    ("LEAVE", "申請フォーム（下書き・提出・残り文字数）", "FE", 0.5, 1, 4, 1.5, 0.5),
    ("LEAVE", "申請一覧・検索・詳細API", "BE", 0.5, 0.5, 3, 1.5, 1),
    ("LEAVE", "申請一覧・詳細画面", "FE", 0.5, 0.5, 3.5, 1, 0.5),
    ("APPR", "承認・差戻しAPI（状態遷移・OCC・監査ログ）", "BE", 0.5, 1, 4, 2, 1.5),
    ("APPR", "承認画面・差戻し理由入力", "FE", 0.5, 0.5, 3, 1, 0.5),
    ("APPR", "承認者代理API・期限チェック", "BE", 0.25, 0.5, 2.5, 1, 0.5),
    ("APPR", "代理設定画面", "FE", 0.25, 0.5, 1.5, 0.5, 0.25),
    ("REPORT", "月次CSV集計・Shift_JIS出力", "BE", 0.5, 1, 3.5, 1.5, 1),
    ("REPORT", "CSV出力画面", "FE", 0.25, 0.25, 1, 0.5, 0.25),
    ("ALL", "DB設計・migration・シード", "BE", 0.5, 1.5, 2, 0.5, 0.5),
    ("ALL", "CI/CD・Docker・監視の初期構築", "BE", 0, 0.5, 3, 0, 0.5),
    ("ALL", "結合試験（QA主担当）", "QA", 0, 0, 0, 0, 0),
]
QA_TASKS = [
    ("ALL", "テスト設計（テストケース作成・レビュー・データ準備）", "QA", 0, 3, 0, 0, 0),
    ("ALL", "結合試験の実施・欠陥起票・再試験", "QA", 0, 0, 0, 0, 6),
    ("ALL", "総合試験・受入試験（UAT）の支援", "QA", 0, 0, 0, 0, 2),
]
PM_TASKS = [
    ("ALL", "プロジェクト管理・会議・顧客対応（PM）", "PM", 0.5, 0.5, 0.5, 0.5, 0.5),
]

def estimate_rows():
    rows = []
    for m, t, role, bd, dd, dev, ut, it in TASKS:
        rows.append((m, t, role, bd, dd, dev, ut, it))
    return rows

if __name__ == "__main__":
    print("ok data loaded", len(FEATS), "feats", len(APIS), "apis", len(TABLES), "tables", len(cases_flat()), "cases")
