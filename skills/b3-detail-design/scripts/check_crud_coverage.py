#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""check_crud_coverage.py — kiểm "Zero Orphan Table": mọi bảng trong migration.sql (a5) phải có
ít nhất 1 thao tác C/R/U/D trong sheet CRUD_Matrix của DetailDesign_Workbook (b3).

Usage:
  python check_crud_coverage.py <migration.sql> <DetailDesign_Workbook.xlsx|crud.csv>
         [--sheet CRUD_Matrix] [--ignore bang1,bang2]

Ma trận có thể đặt bảng ở CỘT (hàng = chức năng, mặc định theo spec b3) hoặc ở HÀNG — script tự nhận diện.
Ô thao tác hợp lệ: chuỗi chỉ gồm C/R/U/D, ngăn bởi dấu cách , / + & (vd "CRU", "C, R", "R/U").

Exit 0 = đủ; 1 = có bảng mồ côi / cột bảng rỗng; 3 = KHÔNG kiểm được (thiếu file, thiếu openpyxl,
không đọc được bảng nào…) — exit 3 KHÔNG được coi là "đã qua"."""
import argparse
import csv
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_IGNORE = {
    "_prisma_migrations", "schema_migrations", "flyway_schema_history", "alembic_version",
    "knex_migrations", "knex_migrations_lock", "django_migrations", "migrations",
}
OP_CELL = re.compile(r"^[CRUD](?:[\s,/+&・、]*[CRUD])*$")
CREATE_RE = re.compile(
    r"CREATE\s+(?:GLOBAL\s+|LOCAL\s+)?(?:UNLOGGED\s+|TEMP(?:ORARY)?\s+)?TABLE\s+"
    r"(?:IF\s+NOT\s+EXISTS\s+)?((?:[`\"\[]?[\w$]+[`\"\]]?\s*\.\s*)*[`\"\[]?[\w$]+[`\"\]]?)",
    re.IGNORECASE,
)


def norm(name: str) -> str:
    """Bỏ quote/schema, về chữ thường: "public"."Users" -> users."""
    last = re.split(r"\s*\.\s*", str(name).strip())[-1]
    return last.strip('`"[] ').lower()


def parse_sql_tables(path: Path) -> list:
    text = path.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"--[^\n]*", " ", text)
    seen, out = set(), []
    for m in CREATE_RE.finditer(text):
        t = norm(m.group(1))
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def read_matrix(path: Path, sheet: str):
    """Trả (grid, nhãn nguồn) — grid là list[list[str]]."""
    ext = path.suffix.lower()
    if ext == ".csv":
        with path.open(encoding="utf-8-sig", newline="") as f:
            return [[(c or "").strip() for c in row] for row in csv.reader(f)], "csv"
    try:
        import openpyxl
    except ImportError:
        raise RuntimeError("thiếu thư viện openpyxl — chạy: python -m pip install openpyxl "
                           "(hoặc xuất sheet CRUD_Matrix ra .csv UTF-8 rồi truyền file .csv)")
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        names = wb.sheetnames
        target = next((n for n in names if n == sheet), None) \
            or next((n for n in names if sheet.lower() in n.lower()), None) \
            or next((n for n in names if "crud" in n.lower()), None)
        if not target:
            raise RuntimeError(f"không có sheet '{sheet}' (có: {names})")
        grid = [["" if c is None else str(c).strip() for c in row]
                for row in wb[target].iter_rows(values_only=True)]
        return grid, target
    finally:
        wb.close()


def locate(grid: list, tables: set):
    """Nhận diện hướng ma trận. Trả (orientation, vị trí header, {bảng: [ô thao tác]})."""
    best_row = (0, None)
    for ri, row in enumerate(grid):
        n = sum(1 for c in row if norm(c) in tables)
        if n > best_row[0]:
            best_row = (n, ri)
    width = max((len(r) for r in grid), default=0)
    best_col = (0, None)
    for ci in range(width):
        n = sum(1 for r in grid if ci < len(r) and norm(r[ci]) in tables)
        if n > best_col[0]:
            best_col = (n, ci)
    if best_row[0] == 0 and best_col[0] == 0:
        return None, None, {}
    ops = {}
    if best_row[0] >= best_col[0]:
        hr = best_row[1]
        for ci, head in enumerate(grid[hr]):
            t = norm(head)
            if t in tables:
                ops.setdefault(t, []).extend(
                    r[ci] for r in grid[hr + 1:] if ci < len(r) and r[ci].strip())
        return "columns", hr + 1, ops
    hc = best_col[1]
    for r in grid:
        if hc < len(r) and norm(r[hc]) in tables:
            ops.setdefault(norm(r[hc]), []).extend(c for i, c in enumerate(r) if i != hc and c.strip())
    return "rows", hc + 1, ops


def valid_ops(cells: list) -> set:
    found = set()
    for c in cells:
        u = c.strip().upper()
        if OP_CELL.match(u):
            found.update(ch for ch in u if ch in "CRUD")
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sql")
    ap.add_argument("matrix")
    ap.add_argument("--sheet", default="CRUD_Matrix")
    ap.add_argument("--ignore", default="")
    a = ap.parse_args()

    sql_p, mx_p = Path(a.sql), Path(a.matrix)
    for p in (sql_p, mx_p):
        if not p.is_file():
            print(f"⛔ KHÔNG KIỂM ĐƯỢC: không thấy file {p}")
            return 3
    ignore = DEFAULT_IGNORE | {norm(x) for x in a.ignore.split(",") if x.strip()}
    tables = [t for t in parse_sql_tables(sql_p) if t not in ignore]
    if not tables:
        print(f"⛔ KHÔNG KIỂM ĐƯỢC: không tìm thấy CREATE TABLE nào trong {sql_p.name}")
        return 3
    try:
        grid, src = read_matrix(mx_p, a.sheet)
    except RuntimeError as e:
        print(f"⛔ KHÔNG KIỂM ĐƯỢC: {e}")
        return 3
    except Exception as e:  # file hỏng / khóa
        print(f"⛔ KHÔNG KIỂM ĐƯỢC: không đọc được {mx_p.name} ({e})")
        return 3

    orient, start, ops = locate(grid, set(tables))
    if orient is None:
        print(f"⛔ KHÔNG KIỂM ĐƯỢC: sheet '{src}' không có ô tiêu đề nào trùng tên bảng trong SQL "
              f"({', '.join(tables[:5])}…). Tiêu đề cột phải là TÊN BẢNG đúng như migration.")
        return 3

    missing = [t for t in tables if t not in ops]
    empty = [t for t in tables if t in ops and not valid_ops(ops[t])]
    no_create = [t for t in tables if t in ops and valid_ops(ops[t]) and "C" not in valid_ops(ops[t])]
    tbl_like = []
    if orient == "columns":
        head = grid[start - 1]
        tbl_like = [h for h in head if re.fullmatch(r"[a-z][a-z0-9_]*", h or "") and norm(h) not in set(tables)]

    print(f"Bảng trong SQL: {len(tables)} | nhận diện ma trận theo {orient.upper()} (sheet '{src}')")
    for t in tables:
        flag = "OK " if t in ops and valid_ops(ops[t]) else "THIẾU"
        print(f"  [{flag}] {t:<32} {''.join(ch for ch in 'CRUD' if ch in valid_ops(ops.get(t, []))) or '-'}")
    if no_create:
        print(f"⚠️ {len(no_create)} bảng không có thao tác C (nguồn dữ liệu ở đâu? seed/import/admin?): {', '.join(no_create)}")
    if tbl_like:
        print(f"⚠️ Cột trông như tên bảng nhưng KHÔNG có trong migration.sql (sai tên hoặc bảng cũ?): {', '.join(tbl_like)}")
    if missing or empty:
        if missing:
            print(f"⛔ BẢNG MỒ CÔI (không có cột/hàng trong CRUD_Matrix): {', '.join(missing)}")
        if empty:
            print(f"⛔ BẢNG CÓ CỘT NHƯNG KHÔNG Ô C/R/U/D NÀO: {', '.join(empty)}")
        return 1
    print(f"✅ CRUD_Matrix phủ 100% ({len(tables)}/{len(tables)} bảng)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
