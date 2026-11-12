#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""check_circular_fk.py — phát hiện chu trình khóa ngoại (FK) bằng Tarjan SCC (v2).

Usage:
    python check_circular_fk.py <schema.json> [--order]

schema.json: {"orders": ["users"], "order_items": ["orders", "dishes"],
              "employees": [{"table": "employees", "nullable": true, "column": "manager_id"}], ...}
  key   = bảng
  value = danh sách bảng nó tham chiếu qua FK. Mỗi phần tử là chuỗi tên bảng, hoặc object
          {"table": "<bảng đích>", "nullable": true|false, "column": "<tên cột FK>"}.

Quy tắc:
  - FK tự tham chiếu (employees.manager_id -> employees) là hợp lệ: chỉ ghi chú, KHÔNG phải lỗi.
  - Chu trình nhiều bảng mà MỌI FK đều NOT NULL  => LỖI (exit 1): không thể INSERT/CREATE theo thứ tự nào.
  - Chu trình có >= 1 FK nullable => CẢNH BÁO (exit 0): tạo bảng trước, thêm FK bằng ALTER TABLE sau
    (hoặc DEFERRABLE INITIALLY DEFERRED); ghi vào Assumptions/Migration Notes.
  - --order: in thứ tự tạo bảng gợi ý (bỏ qua FK tự tham chiếu và FK nullable nằm trong chu trình).

Mã thoát: 0 = không có chu trình cứng; 1 = có chu trình cứng; 2 = input sai / thiếu file.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "a1-project-init" / "scripts"))
from i18n import lang_from_argv, pick  # noqa: E402

MESSAGES = {
    "vi": {"nofile": "LỖI: không thấy file %s", "badjson": "LỖI: schema.json không hợp lệ — %s",
           "unknown": "CẢNH BÁO: tham chiếu tới bảng không có trong schema: %s",
           "selfref": "GHI CHÚ: %s có FK tự tham chiếu (cây/phân cấp) — hợp lệ, cột FK nên nullable.",
           "soft": "CẢNH BÁO: chu trình có FK nullable: %s → tạo bảng trước, thêm FK bằng ALTER TABLE hoặc DEFERRABLE INITIALLY DEFERRED; ghi vào Migration Notes.",
           "order": "THỨ TỰ TẠO BẢNG gợi ý: %s", "rest": "  (còn lại do chu trình cứng: %s)",
           "hard": "LỖI — CIRCULAR FK (mọi FK NOT NULL):", "fix": "→ Phá vòng: cho một FK nullable, hoặc tách bảng trung gian.",
           "ok": "OK: không có circular FK cứng (%d bảng)."},
    "ja": {"nofile": "エラー: ファイルが見つかりません %s", "badjson": "エラー: schema.json が不正です — %s",
           "unknown": "警告: スキーマに存在しないテーブルを参照しています: %s",
           "selfref": "注記: %s は自己参照 FK（ツリー/階層）を持ちます — 有効です。FK 列は nullable にしてください。",
           "soft": "警告: nullable な FK を含む循環があります: %s → 先にテーブルを作成し、ALTER TABLE または DEFERRABLE INITIALLY DEFERRED で FK を追加し、マイグレーションノートに記載してください。",
           "order": "推奨テーブル作成順: %s", "rest": "  （残りは強い循環のため: %s）",
           "hard": "エラー — 循環 FK（すべて NOT NULL の FK）:", "fix": "→ 循環の解消: いずれかの FK を nullable にするか、中間テーブルに分割してください。",
           "ok": "OK: 強い循環 FK はありません（%d テーブル）。"},
    "en": {"nofile": "ERROR: file not found %s", "badjson": "ERROR: invalid schema.json — %s",
           "unknown": "WARNING: references to tables that are not in the schema: %s",
           "selfref": "NOTE: %s has a self-referencing FK (tree/hierarchy) — valid; the FK column should be nullable.",
           "soft": "WARNING: cycle with nullable FKs: %s → create the tables first, add the FK with ALTER TABLE or DEFERRABLE INITIALLY DEFERRED; record it in the migration notes.",
           "order": "Suggested table creation order: %s", "rest": "  (remaining because of a hard cycle: %s)",
           "hard": "ERROR — CIRCULAR FK (all FKs NOT NULL):", "fix": "→ Break the cycle: make one FK nullable or split out a link table.",
           "ok": "OK: no hard circular FK (%d tables)."},
}
CM = pick(MESSAGES, "vi")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def normalize(raw):
    """-> {table: [(target, nullable)]}; ném ValueError nếu cấu trúc sai."""
    if not isinstance(raw, dict):
        raise ValueError("schema.json phải là object {bảng: [bảng tham chiếu…]}")
    graph = {}
    for tbl, refs in raw.items():
        if not isinstance(refs, list):
            raise ValueError("giá trị của '%s' phải là mảng" % tbl)
        edges = []
        for r in refs:
            if isinstance(r, str):
                edges.append((r, False))
            elif isinstance(r, dict) and isinstance(r.get("table"), str):
                edges.append((r["table"], bool(r.get("nullable", False))))
            else:
                raise ValueError("phần tử FK của '%s' không hợp lệ: %r" % (tbl, r))
        graph[tbl] = edges
    return graph


def sccs(nodes, adj):
    """Tarjan SCC lặp (không đệ quy). adj: {u: set(v)}. Trả về list các list nút."""
    index, low, on_stack, stack, out = {}, {}, set(), [], []
    counter = 0
    for root in nodes:
        if root in index:
            continue
        work = [(root, iter(sorted(adj.get(root, ()))))]
        index[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on_stack.add(root)
        while work:
            u, it = work[-1]
            advanced = False
            for v in it:
                if v not in index:
                    index[v] = low[v] = counter
                    counter += 1
                    stack.append(v)
                    on_stack.add(v)
                    work.append((v, iter(sorted(adj.get(v, ())))))
                    advanced = True
                    break
                if v in on_stack:
                    low[u] = min(low[u], index[v])
            if advanced:
                continue
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[u])
            if low[u] == index[u]:
                comp = []
                while True:
                    w = stack.pop()
                    on_stack.discard(w)
                    comp.append(w)
                    if w == u:
                        break
                out.append(comp)
    return out


def one_cycle(comp, adj):
    """Một chu trình cụ thể trong SCC (để in ra)."""
    cs = set(comp)
    start = sorted(comp)[0]
    path, seen = [start], {start: 0}
    cur = start
    while True:
        nxt = next((v for v in sorted(adj.get(cur, ())) if v in cs), None)
        if nxt is None:
            return path
        if nxt in seen:
            return path[seen[nxt]:] + [nxt]
        seen[nxt] = len(path)
        path.append(nxt)
        cur = nxt


def analyse(graph):
    """-> dict(self_refs, hard, soft, unknown)."""
    nodes = sorted(graph)
    unknown = sorted({t for edges in graph.values() for t, _ in edges if t not in graph})
    self_refs = sorted(t for t, edges in graph.items() if any(x == t for x, _ in edges))
    adj_all = {t: {x for x, _ in edges if x != t and x in graph} for t, edges in graph.items()}
    adj_hard = {t: {x for x, nl in edges if x != t and x in graph and not nl} for t, edges in graph.items()}
    hard = [c for c in sccs(nodes, adj_hard) if len(c) > 1]
    hard_nodes = {n for c in hard for n in c}
    soft = [c for c in sccs(nodes, adj_all) if len(c) > 1 and not set(c) <= hard_nodes]
    return {"self_refs": self_refs, "hard": [(c, one_cycle(c, adj_hard)) for c in hard],
            "soft": [(c, one_cycle(c, adj_all)) for c in soft], "unknown": unknown, "adj_hard": adj_hard}


def creation_order(graph, adj_hard):
    """Kahn trên các FK NOT NULL (bỏ self-ref). Nút còn lại trong chu trình cứng được nối cuối."""
    indeg = {t: len(adj_hard.get(t, ())) for t in graph}
    rev = {t: [] for t in graph}
    for t, deps in adj_hard.items():
        for d in deps:
            rev[d].append(t)
    ready = sorted(t for t, d in indeg.items() if d == 0)
    order = []
    while ready:
        t = ready.pop(0)
        order.append(t)
        for u in sorted(rev[t]):
            indeg[u] -= 1
            if indeg[u] == 0:
                ready.append(u)
        ready.sort()
    rest = sorted(t for t in graph if t not in order)
    return order, rest


def main(argv):
    global CM
    _lang, _rest = lang_from_argv(argv[1:], audience="internal")
    argv = [argv[0]] + _rest
    CM = pick(MESSAGES, _lang)
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args or "--help" in argv or "-h" in argv:
        print(__doc__)
        return 2
    path = Path(args[0])
    if not path.exists():
        print(CM["nofile"] % path)
        return 2
    try:
        graph = normalize(json.loads(path.read_text(encoding="utf-8-sig")))
    except (ValueError, OSError) as e:
        print(CM["badjson"] % e)
        return 2
    res = analyse(graph)
    if res["unknown"]:
        print(CM["unknown"] % ", ".join(res["unknown"]))
    for t in res["self_refs"]:
        print(CM["selfref"] % t)
    for _, cyc in res["soft"]:
        print(CM["soft"] % " → ".join(cyc))
    if "--order" in argv:
        order, rest = creation_order(graph, res["adj_hard"])
        print(CM["order"] % " → ".join(order))
        if rest:
            print(CM["rest"] % ", ".join(rest))
    if res["hard"]:
        print(CM["hard"])
        for _, cyc in res["hard"]:
            print("   ", " → ".join(cyc))
        print(CM["fix"])
        return 1
    print(CM["ok"] % len(graph))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
