# -*- coding: utf-8 -*-
"""
Codebase Feature Scanner — Tự động quét và lập bản đồ tính năng mã nguồn.
Dùng cho skill /product-teardown để bóc tách hiện trạng thực tế của repo.
Usage: python codebase_feature_scanner.py [path_to_repo]
"""

import os
import re
import sys
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def scan_repo(repo_dir: Path):
    repo_path = repo_dir.resolve()
    result = {
        "repo_path": str(repo_path),
        "detected_stack": [],
        "database_orm": [],
        "api_endpoints": [],
        "frontend_pages": [],
        "auth_methods": [],
        "realtime_and_queue": [],
        "ux_maturity_signals": {
            "has_command_palette": False,
            "has_bulk_actions": False,
            "has_export_csv_or_pdf": False,
            "has_toast_notifications": False,
            "has_empty_states": False,
            "has_audit_log_or_history": False,
            "has_soft_delete": False,
            "has_rbac_or_roles": False,
        }
    }

    ignore_dirs = {".git", "node_modules", ".next", "dist", "build", "__pycache__", ".venv", "venv", ".gemini", "vendor"}

    # File patterns
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith(".")]
        rel_root = os.path.relpath(root, repo_path)

        for f in files:
            file_path = Path(root) / f
            rel_file = Path(rel_root) / f
            lower_name = f.lower()

            # 1. Detect Stack
            if f == "package.json":
                result["detected_stack"].append("Node.js / JavaScript / TypeScript")
                try:
                    pkg = json.loads(file_path.read_text(encoding="utf-8", errors="ignore"))
                    deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
                    if "next" in deps: result["detected_stack"].append(f"Next.js ({deps.get('next')})")
                    if "react" in deps: result["detected_stack"].append("React")
                    if "@nestjs/core" in deps: result["detected_stack"].append("NestJS")
                    if "express" in deps: result["detected_stack"].append("Express")
                    if "prisma" in deps or "@prisma/client" in deps: result["database_orm"].append("Prisma ORM")
                    if "typeorm" in deps: result["database_orm"].append("TypeORM")
                    if "socket.io" in deps or "ws" in deps: result["realtime_and_queue"].append("WebSocket")
                    if "bull" in deps or "bullmq" in deps: result["realtime_and_queue"].append("BullMQ / Redis Queue")
                    if "lucide-react" in deps or "@radix-ui/react-icons" in deps:
                        result["detected_stack"].append("Radix UI / Shadcn UI")
                    if "cmdk" in deps:
                        result["ux_maturity_signals"]["has_command_palette"] = True
                    if "sonner" in deps or "react-hot-toast" in deps or "notistack" in deps:
                        result["ux_maturity_signals"]["has_toast_notifications"] = True
                    if "jspdf" in deps or "@react-pdf/renderer" in deps or "xlsx" in deps or "exceljs" in deps:
                        result["ux_maturity_signals"]["has_export_csv_or_pdf"] = True
                except Exception:
                    pass

            if f in ["requirements.txt", "Pipfile", "pyproject.toml"]:
                result["detected_stack"].append("Python")
            if f == "schema.prisma":
                result["database_orm"].append("Prisma Schema")
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                models = re.findall(r"model\s+(\w+)\s+{", content)
                result["prisma_models"] = models[:25]
                if "isDeleted" in content or "deletedAt" in content:
                    result["ux_maturity_signals"]["has_soft_delete"] = True
                if "Role" in content or "role" in content:
                    result["ux_maturity_signals"]["has_rbac_or_roles"] = True
                if "AuditLog" in content or "History" in content or "Activity" in content:
                    result["ux_maturity_signals"]["has_audit_log_or_history"] = True

            # 2. Frontend Pages (Next.js App router / Pages router / Vue)
            if f in ["page.tsx", "page.jsx", "page.js"]:
                route = "/" + str(rel_file.parent).replace("\\", "/").replace("app", "").replace("src/app", "").strip("/")
                if route == "/": route = "/ (Root / Dashboard)"
                result["frontend_pages"].append(route)
            
            # 3. API Routes / Controllers
            if f in ["route.ts", "route.js"] or lower_name.endswith(".controller.ts") or lower_name.endswith(".router.ts"):
                result["api_endpoints"].append(str(rel_file).replace("\\", "/"))

            # 4. Content Scanning for UX & Business Signals (Only source files)
            if f.endswith((".ts", ".tsx", ".js", ".jsx", ".py")) and file_path.stat().st_size < 300_000:
                try:
                    code = file_path.read_text(encoding="utf-8", errors="ignore")
                    if "cmdk" in code or "CommandDialog" in code or "Ctrl+K" in code or "cmd+k" in code:
                        result["ux_maturity_signals"]["has_command_palette"] = True
                    if "toast" in code.lower() and ("toast(" in code or "useToast" in code):
                        result["ux_maturity_signals"]["has_toast_notifications"] = True
                    if "empty" in lower_name or "empty-state" in code.lower() or "no data found" in code.lower():
                        result["ux_maturity_signals"]["has_empty_states"] = True
                    if "selectedrows" in code.lower() or "bulkdelete" in code.lower() or "selectall" in code.lower():
                        result["ux_maturity_signals"]["has_bulk_actions"] = True
                    if "export" in code.lower() and ("csv" in code.lower() or "excel" in code.lower() or "pdf" in code.lower()):
                        result["ux_maturity_signals"]["has_export_csv_or_pdf"] = True
                    if "jwt" in code.lower() or "bearer" in code.lower() or "nextauth" in code.lower():
                        result["auth_methods"].append("JWT / Token Auth")
                except Exception:
                    pass

    # Deduplicate
    result["detected_stack"] = list(dict.fromkeys(result["detected_stack"]))
    result["database_orm"] = list(dict.fromkeys(result["database_orm"]))
    result["auth_methods"] = list(dict.fromkeys(result["auth_methods"]))
    result["realtime_and_queue"] = list(dict.fromkeys(result["realtime_and_queue"]))
    result["frontend_pages"] = sorted(list(set(result["frontend_pages"])))[:30]
    result["api_endpoints"] = sorted(list(set(result["api_endpoints"])))[:30]

    return result

def format_markdown_report(data: dict) -> str:
    md = []
    md.append("# 🔎 BÁO CÁO TỔNG QUAN HIỆN TRẠNG MÃ NGUỒN (CODEBASE INVENTORY)")
    md.append(f"**Đường dẫn quét:** `{data['repo_path']}`\n")
    
    md.append("### 1. Công nghệ phát hiện (Tech Stack)")
    if data["detected_stack"]:
        for s in data["detected_stack"]: md.append(f"- {s}")
    else:
        md.append("- *Chưa phát hiện rõ framework (kiểm tra lại thư mục)*")
    
    if data["database_orm"]:
        md.append(f"- **CSDL / ORM:** {', '.join(data['database_orm'])}")
    if data.get("prisma_models"):
        md.append(f"- **Bảng dữ liệu phát hiện ({len(data['prisma_models'])} entities):** `{', '.join(data['prisma_models'][:15])}`")

    md.append("\n### 2. Giao diện người dùng & API phát hiện")
    md.append(f"- **Số màn hình/trang UI tìm thấy:** {len(data['frontend_pages'])}")
    for p in data['frontend_pages'][:8]: md.append(f"  * `{p}`")
    if len(data['frontend_pages']) > 8: md.append(f"  * *... và {len(data['frontend_pages'])-8} màn hình khác*")

    md.append(f"- **Số API Module / Endpoint tìm thấy:** {len(data['api_endpoints'])}")
    for a in data['api_endpoints'][:8]: md.append(f"  * `{a}`")
    if len(data['api_endpoints']) > 8: md.append(f"  * *... và {len(data['api_endpoints'])-8} module API khác*")

    md.append("\n### 3. Tín hiệu Trải nghiệm Người dùng (UX & Enterprise Signals)")
    signals = data["ux_maturity_signals"]
    md.append("| Tính năng Trải nghiệm Chuẩn Tier-1 | Tình trạng trong Codebase | Đánh giá |")
    md.append("|---|:---:|---|")
    md.append(f"| Phím tắt Command Palette (Cmd+K) | {'✅ Có' if signals['has_command_palette'] else '❌ Chưa có'} | {'Chuẩn Linear/Notion' if signals['has_command_palette'] else 'Nên bổ sung để tăng tốc điều hướng'} |")
    md.append(f"| Thao tác hàng loạt (Bulk Actions) | {'✅ Có' if signals['has_bulk_actions'] else '❌ Chưa có'} | {'Xử lý dữ liệu lớn tốt' if signals['has_bulk_actions'] else 'Người dùng phải click từng dòng, dễ nản'} |")
    md.append(f"| Xuất dữ liệu báo cáo (CSV/Excel/PDF) | {'✅ Có' if signals['has_export_csv_or_pdf'] else '❌ Chưa có'} | {'Đã hỗ trợ báo cáo' if signals['has_export_csv_or_pdf'] else 'Tính năng bắt buộc cho doanh nghiệp'} |")
    md.append(f"| Thông báo Toast & Phản hồi trạng thái | {'✅ Có' if signals['has_toast_notifications'] else '❌ Chưa có'} | {'Tốt' if signals['has_toast_notifications'] else 'Cần thêm để báo thành công/thất bại tức thì'} |")
    md.append(f"| Trạng thái dữ liệu rỗng (Smart Empty State) | {'✅ Có' if signals['has_empty_states'] else '❌ Chưa có'} | {'Thân thiện' if signals['has_empty_states'] else 'Màn hình trắng trơn khi chưa có data'} |")
    md.append(f"| Lịch sử thao tác & Nhật ký (Audit Trail) | {'✅ Có' if signals['has_audit_log_or_history'] else '❌ Chưa có'} | {'Độ tin cậy cao' if signals['has_audit_log_or_history'] else 'Chưa truy vết được ai làm gì lúc nào'} |")
    md.append(f"| Xóa mềm an toàn (Soft Delete) | {'✅ Có' if signals['has_soft_delete'] else '❌ Chưa có'} | {'An toàn dữ liệu' if signals['has_soft_delete'] else 'Dễ mất dữ liệu vĩnh viễn khi bấm nhầm'} |")
    md.append(f"| Phân quyền vai trò người dùng (RBAC) | {'✅ Có' if signals['has_rbac_or_roles'] else '❌ Chưa có'} | {'Bảo mật phân tầng' if signals['has_rbac_or_roles'] else 'Mọi user có quyền ngang nhau'} |")

    return "\n".join(md)

if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    data = scan_repo(target)
    print(format_markdown_report(data))
    
    # Also write JSON summary if flag provided
    if "--json" in sys.argv:
        print(json.dumps(data, indent=2, ensure_ascii=False))
