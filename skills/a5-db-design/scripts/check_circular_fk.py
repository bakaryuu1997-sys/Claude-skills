#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_circular_fk.py — phát hiện chu trình FK bằng DFS 3 màu (v3.3.0).
Usage: python3 check_circular_fk.py <schema.json>
  schema.json: {"orders": ["users"], "order_items": ["orders","dishes"], ...}
  (key = bảng, value = danh sách bảng nó tham chiếu qua FK)
Exit 0 = không có chu trình; 1 = in các chu trình tìm thấy."""
import json, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def detect_circular_fk(tables_fk: dict) -> list:
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {t: WHITE for t in tables_fk}
    cycles = []

    def dfs(u, stack):
        color[u] = GRAY
        for v in tables_fk.get(u, ()):
            if color.get(v) == GRAY:
                cycles.append(" → ".join(stack[stack.index(v):] + [v]))
                return True
            if color.get(v, BLACK) == WHITE and dfs(v, stack + [v]):
                return True
        color[u] = BLACK
        return False

    for t in list(tables_fk):
        if color[t] == WHITE:
            dfs(t, [t])
    return cycles


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    fk = json.loads(open(sys.argv[1], encoding="utf-8").read())
    cyc = detect_circular_fk({k: list(v) for k, v in fk.items()})
    if cyc:
        print("⛔ CIRCULAR FK:")
        for c in cyc:
            print("  ", c)
        print("→ Phá vòng bằng nullable FK hoặc bảng trung gian")
        sys.exit(1)
    print("✅ Không có circular FK")
    sys.exit(0)
