#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nguồn DUY NHẤT cho logic đọc project-context.json — MỌI skill gọi script này,
KHÔNG copy code đọc context vào từng SKILL.md (DRY).

Usage:
    python3 load_context.py "<workspace_folder>"

Output:
    - JSON context (đã validate schema nếu validator khả dụng) → dùng cget() để đọc field
    - "NO_CONTEXT: <lý do>" nếu chưa có / file lỗi → skill tiếp tục ở chế độ nhập thủ công
"""
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def load_context(workspace_folder: str):
    """Trả về (ctx_dict | None, err_msg | None)."""
    p = Path(workspace_folder) / "project-context.json"
    if not p.exists():
        return None, "NO_CONTEXT: chưa có project-context.json — gợi ý chạy /a1-project-init, hoặc nhập thủ công"
    try:
        return json.loads(p.read_text(encoding="utf-8-sig")), None
    except (json.JSONDecodeError, OSError) as e:
        return None, f"NO_CONTEXT: project-context.json lỗi ({e}) — sửa file hoặc nhập thủ công"


def cget(ctx, path, default=None):
    """Đọc field an toàn: cget(ctx, "tech_stack.database", "PostgreSQL").
    KHÔNG BAO GIỜ truy cập cứng ctx['a']['b'] — context cũ/thiếu key sẽ crash."""
    cur = ctx or {}
    for k in path.split("."):
        cur = cur.get(k) if isinstance(cur, dict) else None
        if cur is None:
            return default
    return cur


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else "."
    ctx, err = load_context(folder)
    if ctx is None:
        print(err)
        return 1
    # Validate schema nếu validator có mặt (a1-project-init/scripts/validate_context.py)
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from validate_context import validate_context  # type: ignore
        errs = validate_context(ctx)
        if errs:
            print("⚠️ CONTEXT_INVALID (vẫn dùng được, nên sửa):", "; ".join(map(str, errs)), file=sys.stderr)
    except Exception:
        pass  # validator không bắt buộc
    print(json.dumps(ctx, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
