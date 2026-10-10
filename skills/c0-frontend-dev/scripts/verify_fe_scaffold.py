#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_fe_scaffold.py — Kiểm tra tính toàn vẹn và tiêu chuẩn Zero-Mock của mã nguồn Frontend.
Usage: python3 verify_fe_scaffold.py <frontend_dir>
Exit code 0 = đạt chuẩn, 1 = vi phạm tiêu chuẩn.
"""
import os, sys, re
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def check_frontend(frontend_dir: Path):
    print(f"🔍 Đang kiểm tra mã nguồn Frontend tại: {frontend_dir}")
    if not frontend_dir.exists():
        print(f"❌ Thư mục không tồn tại: {frontend_dir}")
        return 1

    errors = []
    warnings = []

    # 1. Kiểm tra file cấu hình cốt lõi
    pkg_json = frontend_dir / "package.json"
    if not pkg_json.exists():
        errors.append("Thiếu package.json")
    else:
        content = pkg_json.read_text(encoding="utf-8", errors="ignore")
        if "@tanstack/react-query" not in content and "swr" not in content:
            warnings.append("Khuyến nghị cài đặt TanStack Query hoặc SWR để quản lý Server State")
        if "zod" not in content:
            warnings.append("Khuyến nghị cài đặt Zod để đồng bộ validation schema với Backend")

    # 2. Kiểm tra API Client tập trung
    api_client_found = False
    for p in frontend_dir.glob("**/api-client.*"):
        api_client_found = True
        break
    if not api_client_found:
        for p in frontend_dir.glob("**/apiClient.*"):
            api_client_found = True
            break
    if not api_client_found:
        errors.append("Không tìm thấy tệp API Client tập trung (ví dụ src/lib/api-client.ts)")

    # 3. Kiểm tra Test Suite E2E (Playwright)
    e2e_found = False
    for p in frontend_dir.glob("**/e2e/**/*.spec.*"):
        e2e_found = True
        break
    if not e2e_found:
        warnings.append("Khuyến nghị bổ sung E2E Test Suite (Playwright) để bảo đảm chất lượng UI trước khi bàn giao")

    # 3. Quét Anti-Mock: Tìm các file chứa mock-data hoặc hardcode dữ liệu giả
    for root, _, files in os.walk(frontend_dir):
        for f in files:
            if f.endswith((".ts", ".tsx", ".js", ".jsx")) and not f.endswith((".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx")):
                file_path = Path(root) / f
                rel_path = file_path.relative_to(frontend_dir)
                if "node_modules" in str(rel_path) or ".next" in str(rel_path):
                    continue
                
                try:
                    text = file_path.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue

                if "mockData" in text or "dummyData" in text or "fakeData" in text:
                    warnings.append(f"Tệp {rel_path} có thể chứa dữ liệu mock (cần thay bằng API live)")

                # Bắt comment cấm
                if re.search(r"//\s*TODO:\s*(tự code|tự làm|implement later)", text, re.IGNORECASE):
                    errors.append(f"Tệp {rel_path} chứa comment trốn tránh trách nhiệm: // TODO")

    print("\n--- KẾT QUẢ KIỂM TRA FRONTEND ---")
    if errors:
        print(f"❌ PHÁT HIỆN {len(errors)} LỖI VI PHẠM:")
        for err in errors:
            print(f"   - {err}")
    if warnings:
        print(f"⚠️ CẢNH BÁO ({len(warnings)} điểm cần lưu ý):")
        for w in warnings:
            print(f"   - {w}")

    if not errors:
        print("✅ MÃ NGUỒN FRONTEND ĐẠT CHUẨN CƠ BẢN")
        return 0
    return 1

if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("frontend")
    sys.exit(check_frontend(target))
