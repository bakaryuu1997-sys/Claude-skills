# -*- coding: utf-8 -*-
"""
Codebase Feature Scanner — quét heuristic để lập bản đồ tính năng mã nguồn (v1.1).
Dùng cho skill /product-teardown. KẾT QUẢ LÀ HEURISTIC: mọi tín hiệu phải được đối chiếu lại với code trước khi kết luận.

Usage: python codebase_feature_scanner.py <path_to_repo> [--json]
Chỉ đọc, không ghi file nào.
"""

import json
import os
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

IGNORE_DIRS = {".git", "node_modules", ".next", "dist", "build", "__pycache__", ".venv", "venv",
               "vendor", "target", "coverage", ".gemini"}
SRC_EXT = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".py", ".java", ".kt", ".php", ".go", ".cs")
MAX_BYTES = 300_000
ROUTE_RE = {
    "express/nest/koa": re.compile(r"\b(?:router|app|route)\.(get|post|put|patch|delete)\s*\(\s*[\"'`]"),
    "fastapi/flask": re.compile(r"@(?:router|app|bp)\.(get|post|put|patch|delete)\s*\("),
    "spring": re.compile(r"@(Get|Post|Put|Patch|Delete|Request)Mapping\s*\("),
    "laravel": re.compile(r"Route::(get|post|put|patch|delete)\s*\("),
}


def strip_group_segments(parts):
    """Bỏ 'src', 'app' đứng đầu và route group '(xxx)' của Next.js; giữ [param]."""
    out = list(parts)
    while out and out[0] in ("src", "app", "pages"):
        out.pop(0)
    return [p for p in out if not (p.startswith("(") and p.endswith(")"))]


def route_of(rel_dir: Path) -> str:
    segs = strip_group_segments(rel_dir.parts)
    return "/" + "/".join(segs) if segs else "/ (gốc)"


def read_deps(pkg_path: Path):
    try:
        pkg = json.loads(pkg_path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, ValueError):
        return {}
    return {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}


def scan_repo(repo_dir: Path):
    repo_path = repo_dir.resolve()
    result = {
        "repo_path": str(repo_path),
        "note": "Kết quả heuristic — xác minh từng tín hiệu trước khi kết luận.",
        "detected_stack": [],
        "database_orm": [],
        "api_endpoints": {"count": 0, "files": [], "frameworks": []},
        "frontend_pages": [],
        "auth_methods": [],
        "realtime_and_queue": [],
        "ux_maturity_signals": {
            "has_command_palette": False, "has_bulk_actions": False, "has_export_csv_or_pdf": False,
            "has_toast_notifications": False, "has_empty_states": False, "has_audit_log_or_history": False,
            "has_soft_delete": False, "has_rbac_or_roles": False,
        },
    }
    sig = result["ux_maturity_signals"]
    endpoint_files, frameworks = {}, set()

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]
        root_p = Path(root)
        rel_root = root_p.relative_to(repo_path)

        for f in files:
            fp = root_p / f
            rel_file = rel_root / f
            low = f.lower()

            # 1. Stack & dependency
            if f == "package.json":
                deps = read_deps(fp)
                result["detected_stack"].append("Node.js / TypeScript (package.json)")
                for dep, label in (("next", "Next.js"), ("react", "React"), ("@nestjs/core", "NestJS"),
                                   ("express", "Express")):
                    if dep in deps:
                        result["detected_stack"].append(f"{label} ({deps[dep]})")
                if any(d.startswith("@radix-ui/") for d in deps):
                    result["detected_stack"].append("Radix UI (thư viện component)")
                if "lucide-react" in deps:
                    result["detected_stack"].append("lucide-react (thư viện icon)")
                if "prisma" in deps or "@prisma/client" in deps:
                    result["database_orm"].append("Prisma ORM")
                if "typeorm" in deps:
                    result["database_orm"].append("TypeORM")
                if "socket.io" in deps or "ws" in deps:
                    result["realtime_and_queue"].append("WebSocket (socket.io/ws)")
                if "bull" in deps or "bullmq" in deps:
                    result["realtime_and_queue"].append("Hàng đợi BullMQ/Redis")
                if "jsonwebtoken" in deps or "next-auth" in deps or "@auth/core" in deps:
                    result["auth_methods"].append("Thư viện auth (jsonwebtoken/next-auth) — heuristic")
                if "cmdk" in deps:
                    sig["has_command_palette"] = True
                if any(d in deps for d in ("sonner", "react-hot-toast", "notistack")):
                    sig["has_toast_notifications"] = True
                if any(d in deps for d in ("jspdf", "@react-pdf/renderer", "xlsx", "exceljs")):
                    sig["has_export_csv_or_pdf"] = True
            if f == "components.json":
                result["detected_stack"].append("shadcn/ui (components.json)")
            if low in ("requirements.txt", "pyproject.toml", "pipfile"):
                result["detected_stack"].append("Python")
                txt = fp.read_text(encoding="utf-8", errors="replace").lower()
                if "fastapi" in txt:
                    result["detected_stack"].append("FastAPI")
                if "django" in txt:
                    result["detected_stack"].append("Django")
                if "flask" in txt:
                    result["detected_stack"].append("Flask")
            if low == "pom.xml":
                result["detected_stack"].append("Java (Maven)")
                if "spring-boot" in fp.read_text(encoding="utf-8", errors="replace"):
                    result["detected_stack"].append("Spring Boot")
            if low == "composer.json":
                result["detected_stack"].append("PHP (Composer)")
                if "laravel/framework" in fp.read_text(encoding="utf-8", errors="replace"):
                    result["detected_stack"].append("Laravel")
            if low == "go.mod":
                result["detected_stack"].append("Go")
            if low == "schema.prisma":
                result["database_orm"].append("Prisma Schema")
                content = fp.read_text(encoding="utf-8", errors="replace")
                models = re.findall(r"^model\s+(\w+)\s*\{", content, re.M)
                result["prisma_models"] = models[:25]
                if re.search(r"\b(deletedAt|isDeleted)\b", content):
                    sig["has_soft_delete"] = True
                if re.search(r"\benum\s+Role\b|\broles?\b", content, re.I):
                    sig["has_rbac_or_roles"] = True
                if re.search(r"AuditLog|ActivityLog|History", content):
                    sig["has_audit_log_or_history"] = True

            # 2. Trang giao diện (Next.js App Router)
            if low in ("page.tsx", "page.jsx", "page.js") and "app" in rel_file.parts:
                result["frontend_pages"].append(route_of(rel_file.parent))

            # 3. Endpoint: file route/controller theo quy ước, hoặc có khai báo route
            if low in ("route.ts", "route.js") or low.endswith((".controller.ts", ".router.ts", "controller.java")):
                endpoint_files.setdefault(str(rel_file).replace("\\", "/"), 0)
            if low.endswith(SRC_EXT) and fp.stat().st_size < MAX_BYTES:
                try:
                    code = fp.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                n = 0
                for fw, rx in ROUTE_RE.items():
                    hits = len(rx.findall(code))
                    if hits:
                        n += hits
                        frameworks.add(fw)
                if n:
                    endpoint_files[str(rel_file).replace("\\", "/")] = n

                # 4. Tín hiệu UX (heuristic)
                if re.search(r"\bcmdk\b|CommandDialog|Ctrl\+K|cmd\+k", code, re.I):
                    sig["has_command_palette"] = True
                if re.search(r"toast\(|useToast\b", code):
                    sig["has_toast_notifications"] = True
                if re.search(r"selectedRows|bulkDelete|selectAll", code, re.I):
                    sig["has_bulk_actions"] = True
                if re.search(r"export", code, re.I) and re.search(r"\bcsv\b|\bexcel\b|\bpdf\b", code, re.I):
                    sig["has_export_csv_or_pdf"] = True
                if re.search(r"EmptyState|empty-state|No data found", code, re.I):
                    sig["has_empty_states"] = True

    result["detected_stack"] = list(dict.fromkeys(result["detected_stack"]))
    result["database_orm"] = list(dict.fromkeys(result["database_orm"]))
    result["auth_methods"] = list(dict.fromkeys(result["auth_methods"]))
    result["realtime_and_queue"] = list(dict.fromkeys(result["realtime_and_queue"]))
    result["frontend_pages"] = sorted(set(result["frontend_pages"]))[:40]
    result["api_endpoints"] = {
        "count": sum(endpoint_files.values()) or len(endpoint_files),
        "files": sorted(endpoint_files)[:40],
        "frameworks": sorted(frameworks),
    }
    return result


def format_markdown_report(data: dict) -> str:
    md = ["# BÁO CÁO HIỆN TRẠNG MÃ NGUỒN (heuristic)",
          f"**Đường dẫn quét:** `{data['repo_path']}`",
          f"> {data['note']}", "",
          "### 1. Công nghệ phát hiện"]
    md += [f"- {s}" for s in data["detected_stack"]] or ["- *Chưa nhận diện được stack — kiểm tra thủ công*"]
    if data["database_orm"]:
        md.append(f"- **CSDL / ORM:** {', '.join(data['database_orm'])}")
    if data.get("prisma_models"):
        md.append(f"- **Bảng (Prisma):** {len(data['prisma_models'])} — `{', '.join(data['prisma_models'][:15])}`")

    api = data["api_endpoints"]
    md += ["", "### 2. Giao diện & API", f"- **Trang UI (App Router):** {len(data['frontend_pages'])}"]
    md += [f"  * `{p}`" for p in data["frontend_pages"][:8]]
    if len(data["frontend_pages"]) > 8:
        md.append(f"  * … và {len(data['frontend_pages']) - 8} trang khác")
    md.append(f"- **Endpoint (ước lượng từ khai báo route):** {api['count']} — framework: {', '.join(api['frameworks']) or 'không nhận diện'}")
    md += [f"  * `{f}`" for f in api["files"][:8]]

    sig = data["ux_maturity_signals"]
    rows = [
        ("Command palette (Cmd+K)", "has_command_palette", "Chuẩn Linear/Notion", "Nên có để tăng tốc điều hướng"),
        ("Thao tác hàng loạt (bulk)", "has_bulk_actions", "Xử lý dữ liệu lớn tốt", "Người dùng phải thao tác từng dòng"),
        ("Xuất CSV/Excel/PDF", "has_export_csv_or_pdf", "Có báo cáo xuất", "Thường được yêu cầu ở doanh nghiệp"),
        ("Toast phản hồi", "has_toast_notifications", "Có phản hồi tức thì", "Nên báo thành công/thất bại"),
        ("Trạng thái rỗng (empty state)", "has_empty_states", "Có gợi ý khi rỗng", "Màn hình trống khi chưa có dữ liệu"),
        ("Nhật ký thay đổi (audit)", "has_audit_log_or_history", "Có truy vết", "Chưa thấy truy vết ai làm gì"),
        ("Xóa mềm (soft delete)", "has_soft_delete", "Có xóa mềm", "Bấm nhầm có thể mất dữ liệu"),
        ("Phân quyền vai trò (RBAC)", "has_rbac_or_roles", "Có vai trò", "Chưa thấy phân quyền rõ"),
    ]
    md += ["", "### 3. Tín hiệu UX (heuristic — xác minh trước khi kết luận)",
           "| Tín hiệu | Phát hiện | Ghi chú |", "|---|:---:|---|"]
    for label, key, yes, no in rows:
        md.append(f"| {label} | {'có dấu hiệu' if sig[key] else 'không thấy'} | {yes if sig[key] else no} |")
    return "\n".join(md)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    target = Path(args[0]) if args else Path.cwd()
    if not target.is_dir():
        print(f"❌ Không phải thư mục: {target}")
        sys.exit(2)
    data = scan_repo(target)
    print(format_markdown_report(data))
    if "--json" in sys.argv:
        print(json.dumps(data, indent=2, ensure_ascii=False))
