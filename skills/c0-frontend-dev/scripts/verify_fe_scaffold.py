#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""verify_fe_scaffold.py — Kiểm tra tiêu chuẩn Zero-Mock và khung cơ bản của mã nguồn Frontend.

Usage:
    python verify_fe_scaffold.py <frontend_dir>        (mặc định: ./frontend)
    python verify_fe_scaffold.py --help

Exit code: 0 = đạt chuẩn cơ bản · 1 = có vi phạm (ERROR) · 2 = tham số sai / thư mục không tồn tại.

Quy tắc (nguồn: SKILL.md c0, mục Zero-Mock):
  ERROR  thiếu package.json
  ERROR  không có API Client tập trung (api-client.* / apiClient.*) NGOÀI node_modules/.next/dist…
  ERROR  file nguồn trong src/ (hoặc app/, pages/, components/…) có tên mock*/fake*/dummy*/*fixture*/*stub*
  ERROR  `const|let|var mock… = [` / `= {` hoặc fake…/dummy… trong code production
  ERROR  code production import từ thư mục mocks/ hoặc tests/ (mock chỉ được sống ở <frontend>/mocks/ hoặc tests/)
  ERROR  comment trốn việc: // TODO: tự code / implement later
  ERROR  localStorage/sessionStorage.setItem với khóa chứa token (xem live-api-wiring-protocol.md §3)
  WARN   thiếu TanStack Query/SWR, Zod, E2E spec (tests/e2e)
  WARN   `font-feature-settings: "palt"` áp lên body/*/html
Thư mục bị bỏ qua (prune, không đi vào): node_modules, .next, dist, build, out, coverage, .turbo, .git,
.cache, storybook-static. Thư mục test/mock hợp lệ (không quét ERROR mock): tests, test, __tests__, __mocks__,
e2e, mocks, cypress, playwright-report.
"""
import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "a1-project-init" / "scripts"))
from i18n import add_lang_args, pick, resolve_lang  # noqa: E402

MESSAGES = {
    "vi": {"checking": "Đang kiểm tra mã nguồn Frontend tại: {d}", "nodir": "ERROR Thư mục không tồn tại: {d}", "nopkg": "Thiếu package.json",
           "w_query": "Khuyến nghị TanStack Query hoặc SWR để quản lý Server State", "w_zod": "Khuyến nghị Zod để đồng bộ validation schema với Backend",
           "noclient": "Không tìm thấy API Client tập trung (ví dụ src/lib/api-client.ts) ngoài node_modules/build",
           "w_e2e": "Chưa có E2E spec (tests/e2e/*.spec.ts) — c0 yêu cầu bộ E2E đi kèm",
           "w_palt_css": "{f}: dùng font-feature-settings palt (nén chữ Đông Á) — xem SKILL mục Typography",
           "mockname": "{f}: tên file mock/fake/dummy/fixture trong code production (mock chỉ đặt ở mocks/ hoặc tests/)",
           "mockdecl": "{f}:{n}: khai báo dữ liệu giả tĩnh trong code production ({x}…)", "mockimp": "{f}: code production import từ thư mục mocks/tests",
           "todo": "{f}: comment trốn việc // TODO", "token": "{f}:{n}: lưu token vào localStorage/sessionStorage (dùng cookie HttpOnly/BFF — live-api-wiring-protocol.md §3)",
           "w_palt": "{f}: dùng font-feature-settings palt", "h_result": "--- KẾT QUẢ KIỂM TRA FRONTEND ---", "errs": "ERROR: {n} vi phạm:",
           "warns": "WARN: {n} điểm cần lưu ý:", "ok": "OK: mã nguồn Frontend đạt chuẩn cơ bản (script chỉ kiểm khung + Zero-Mock; không thay thế review)"},
    "ja": {"checking": "フロントエンドのソースを検査中: {d}", "nodir": "ERROR ディレクトリが存在しません: {d}", "nopkg": "package.json がありません",
           "w_query": "サーバー状態の管理に TanStack Query または SWR の利用を推奨します", "w_zod": "バックエンドとバリデーションスキーマを揃えるため Zod の利用を推奨します",
           "noclient": "集約された API クライアント（例: src/lib/api-client.ts）が node_modules/ビルド出力の外に見つかりません",
           "w_e2e": "E2E テスト（tests/e2e/*.spec.ts）がありません — 実装には E2E の同梱が必要です",
           "w_palt_css": "{f}: font-feature-settings の palt を使用（東アジア文字が詰まります）— スキルのタイポグラフィ節を参照",
           "mockname": "{f}: 本番コードに mock/fake/dummy/fixture という名前のファイル（モックは mocks/ または tests/ のみ）",
           "mockdecl": "{f}:{n}: 本番コードに固定のダミーデータ宣言（{x}…）", "mockimp": "{f}: 本番コードが mocks/tests ディレクトリから import しています",
           "todo": "{f}: 未実装を先送りする // TODO コメント", "token": "{f}:{n}: トークンを localStorage/sessionStorage に保存（HttpOnly Cookie/BFF を使用 — live-api-wiring-protocol.md §3）",
           "w_palt": "{f}: font-feature-settings の palt を使用", "h_result": "--- フロントエンド検査結果 ---", "errs": "ERROR: 違反 {n} 件:",
           "warns": "WARN: 注意点 {n} 件:", "ok": "OK: フロントエンドは基本基準を満たしています（枠組みと Zero-Mock のみの検査で、レビューの代わりにはなりません）"},
    "en": {"checking": "Checking the Frontend source at: {d}", "nodir": "ERROR Directory does not exist: {d}", "nopkg": "package.json is missing",
           "w_query": "TanStack Query or SWR is recommended for server state", "w_zod": "Zod is recommended to keep validation schemas aligned with the Backend",
           "noclient": "No central API client (for example src/lib/api-client.ts) found outside node_modules/build output",
           "w_e2e": "No E2E spec (tests/e2e/*.spec.ts) — an E2E suite must ship with the frontend",
           "w_palt_css": "{f}: uses font-feature-settings palt (squeezes East Asian text) — see the Typography section of the skill",
           "mockname": "{f}: file name mock/fake/dummy/fixture in production code (mocks live only in mocks/ or tests/)",
           "mockdecl": "{f}:{n}: static fake data declared in production code ({x}…)", "mockimp": "{f}: production code imports from a mocks/tests directory",
           "todo": "{f}: deferring comment // TODO", "token": "{f}:{n}: token stored in localStorage/sessionStorage (use HttpOnly cookie/BFF — live-api-wiring-protocol.md §3)",
           "w_palt": "{f}: uses font-feature-settings palt", "h_result": "--- FRONTEND CHECK RESULT ---", "errs": "ERROR: {n} violation(s):",
           "warns": "WARN: {n} point(s) to note:", "ok": "OK: the Frontend meets the basic standard (checks structure and Zero-Mock only; not a replacement for review)"},
}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PRUNE = {"node_modules", ".next", "dist", "build", "out", "coverage", ".turbo", ".git", ".cache", "storybook-static"}
TEST_DIRS = {"tests", "test", "__tests__", "__mocks__", "e2e", "mocks", "cypress", "playwright-report"}
CODE_EXT = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs")
TEST_FILE_RE = re.compile(r"\.(test|spec|stories)\.[cm]?[jt]sx?$")
MOCK_NAME_RE = re.compile(r"(^|[._-])(mock|mocks|fake|dummy|stub|fixture|fixtures)([._-]|$)", re.IGNORECASE)
MOCK_DECL_RE = re.compile(
    r"\b(?:const|let|var)\s+(?:mock|fake|dummy|stub)\w*\s*(?::[^=]+)?=\s*[\[{]", re.IGNORECASE)
MOCK_IMPORT_RE = re.compile(r"""(?:from|require\()\s*['"][^'"]*(?:/mocks?/|/tests?/|__mocks__)[^'"]*['"]""")
TODO_RE = re.compile(r"//\s*TODO:\s*(tự code|tự làm|implement later)", re.IGNORECASE)
TOKEN_STORE_RE = re.compile(
    r"""(?:localStorage|sessionStorage)\s*\.\s*setItem\(\s*['"][^'"]*(?:token|jwt|secret)[^'"]*['"]""", re.IGNORECASE)
PALT_RE = re.compile(r"font-feature-settings\s*:\s*['\"]palt['\"]", re.IGNORECASE)
CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)


def walk(root: Path):
    """Duyệt cây, prune thư mục nặng ngay khi đi xuống (không liệt kê node_modules)."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in PRUNE]
        yield Path(dirpath), filenames


def in_test_dir(rel: Path) -> bool:
    return any(part in TEST_DIRS for part in rel.parts[:-1])


def check_frontend(frontend_dir: Path, M=None):
    M = M or pick(MESSAGES, "vi")
    print(M["checking"].format(d=frontend_dir))
    if not frontend_dir.is_dir():
        print(M["nodir"].format(d=frontend_dir))
        return 2

    errors, warnings = [], []

    pkg_json = frontend_dir / "package.json"
    if not pkg_json.exists():
        errors.append(M["nopkg"])
    else:
        content = pkg_json.read_text(encoding="utf-8", errors="ignore")
        if "@tanstack/react-query" not in content and '"swr"' not in content:
            warnings.append(M["w_query"])
        if '"zod"' not in content:
            warnings.append(M["w_zod"])

    api_client_found = False
    e2e_found = False
    for d, files in walk(frontend_dir):
        for f in files:
            low = f.lower()
            if low.startswith(("api-client.", "apiclient.")) and low.endswith(CODE_EXT):
                api_client_found = True
            if ".spec." in low and "e2e" in {p.lower() for p in d.relative_to(frontend_dir).parts}:
                e2e_found = True
    if not api_client_found:
        errors.append(M["noclient"])
    if not e2e_found:
        warnings.append(M["w_e2e"])

    for d, files in walk(frontend_dir):
        for f in files:
            if not f.endswith(CODE_EXT + (".css", ".scss")):
                continue
            path = d / f
            rel = path.relative_to(frontend_dir)
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            if f.endswith((".css", ".scss")):
                # Chú thích CSS có thể nhắc tới palt để cấm nó (như font-stack.css) — không phải vi phạm.
                if PALT_RE.search(CSS_COMMENT_RE.sub("", text)):
                    warnings.append(M["w_palt_css"].format(f=rel))
                continue

            is_test = in_test_dir(rel) or bool(TEST_FILE_RE.search(f))
            if is_test:
                continue

            if MOCK_NAME_RE.search(Path(f).stem):
                errors.append(M["mockname"].format(f=rel))
            m = MOCK_DECL_RE.search(text)
            if m:
                line = text.count("\n", 0, m.start()) + 1
                errors.append(M["mockdecl"].format(f=rel, n=line, x=m.group(0).strip()[:40]))
            if MOCK_IMPORT_RE.search(text):
                errors.append(M["mockimp"].format(f=rel))
            if TODO_RE.search(text):
                errors.append(M["todo"].format(f=rel))
            m = TOKEN_STORE_RE.search(text)
            if m:
                line = text.count("\n", 0, m.start()) + 1
                errors.append(M["token"].format(f=rel, n=line))
            if PALT_RE.search(text):
                warnings.append(M["w_palt"].format(f=rel))

    print("\n" + M["h_result"])
    if errors:
        print(M["errs"].format(n=len(errors)))
        for e in errors:
            print(f"   - {e}")
    if warnings:
        print(M["warns"].format(n=len(warnings)))
        for w in warnings:
            print(f"   - {w}")
    if errors:
        return 1
    print(M["ok"])
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Kiểm tra Zero-Mock và khung cơ bản của Frontend (c0-frontend-dev)")
    ap.add_argument("frontend_dir", nargs="?", default="frontend", help="thư mục frontend (mặc định: ./frontend)")
    add_lang_args(ap, audience="code")  # báo cáo C0 viết theo ngôn ngữ `code` (mặc định en nếu có context)
    args = ap.parse_args(argv)
    return check_frontend(Path(args.frontend_dir), pick(MESSAGES, resolve_lang(args.lang, args.context, args.audience)))


if __name__ == "__main__":
    sys.exit(main())
