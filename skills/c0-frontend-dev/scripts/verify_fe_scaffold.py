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


def walk(root: Path):
    """Duyệt cây, prune thư mục nặng ngay khi đi xuống (không liệt kê node_modules)."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in PRUNE]
        yield Path(dirpath), filenames


def in_test_dir(rel: Path) -> bool:
    return any(part in TEST_DIRS for part in rel.parts[:-1])


def check_frontend(frontend_dir: Path):
    print(f"Đang kiểm tra mã nguồn Frontend tại: {frontend_dir}")
    if not frontend_dir.is_dir():
        print(f"ERROR Thư mục không tồn tại: {frontend_dir}")
        return 2

    errors, warnings = [], []

    pkg_json = frontend_dir / "package.json"
    if not pkg_json.exists():
        errors.append("Thiếu package.json")
    else:
        content = pkg_json.read_text(encoding="utf-8", errors="ignore")
        if "@tanstack/react-query" not in content and '"swr"' not in content:
            warnings.append("Khuyến nghị TanStack Query hoặc SWR để quản lý Server State")
        if '"zod"' not in content:
            warnings.append("Khuyến nghị Zod để đồng bộ validation schema với Backend")

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
        errors.append("Không tìm thấy API Client tập trung (ví dụ src/lib/api-client.ts) ngoài node_modules/build")
    if not e2e_found:
        warnings.append("Chưa có E2E spec (tests/e2e/*.spec.ts) — c0 yêu cầu bộ E2E đi kèm")

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
                if PALT_RE.search(text):
                    warnings.append(f"{rel}: dùng font-feature-settings palt (nén chữ Đông Á) — xem SKILL mục Typography")
                continue

            is_test = in_test_dir(rel) or bool(TEST_FILE_RE.search(f))
            if is_test:
                continue

            if MOCK_NAME_RE.search(Path(f).stem):
                errors.append(f"{rel}: tên file mock/fake/dummy/fixture trong code production (mock chỉ đặt ở mocks/ hoặc tests/)")
            m = MOCK_DECL_RE.search(text)
            if m:
                line = text.count("\n", 0, m.start()) + 1
                errors.append(f"{rel}:{line}: khai báo dữ liệu giả tĩnh trong code production ({m.group(0).strip()[:40]}…)")
            if MOCK_IMPORT_RE.search(text):
                errors.append(f"{rel}: code production import từ thư mục mocks/tests")
            if TODO_RE.search(text):
                errors.append(f"{rel}: comment trốn việc // TODO")
            m = TOKEN_STORE_RE.search(text)
            if m:
                line = text.count("\n", 0, m.start()) + 1
                errors.append(f"{rel}:{line}: lưu token vào localStorage/sessionStorage (dùng cookie HttpOnly/BFF — live-api-wiring-protocol.md §3)")
            if PALT_RE.search(text):
                warnings.append(f"{rel}: dùng font-feature-settings palt")

    print("\n--- KẾT QUẢ KIỂM TRA FRONTEND ---")
    if errors:
        print(f"ERROR: {len(errors)} vi phạm:")
        for e in errors:
            print(f"   - {e}")
    if warnings:
        print(f"WARN: {len(warnings)} điểm cần lưu ý:")
        for w in warnings:
            print(f"   - {w}")
    if errors:
        return 1
    print("OK: mã nguồn Frontend đạt chuẩn cơ bản (script chỉ kiểm khung + Zero-Mock; không thay thế review)")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Kiểm tra Zero-Mock và khung cơ bản của Frontend (c0-frontend-dev)")
    ap.add_argument("frontend_dir", nargs="?", default="frontend", help="thư mục frontend (mặc định: ./frontend)")
    args = ap.parse_args(argv)
    return check_frontend(Path(args.frontend_dir))


if __name__ == "__main__":
    sys.exit(main())
