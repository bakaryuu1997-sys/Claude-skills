#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""update_context.py — nguồn DUY NHẤT cho việc GHI project-context.json (v3.5.0).
MỌI skill ghi context qua script này — KHÔNG tự viết code ghi.
Mảng object (activity_log, change_requests, known_issues) CHỈ nhận JSON object — chuỗi rác bị từ chối.

Usage:
    python3 update_context.py <workspace_folder> set <key.path> <value>
    python3 update_context.py <workspace_folder> append <key.path> '<json-item>'
    python3 update_context.py <workspace_folder> patch  <mảng> <id> '<json-object>'   # merge vào phần tử có "id" khớp
    python3 update_context.py <workspace_folder> set|append|patch ... --file <file.json>  # đọc giá trị từ file (an toàn với PowerShell)
    python3 update_context.py <workspace_folder> restore            # khôi phục từ snapshot gần nhất

POWERSHELL: PowerShell 5.1 làm mất dấu " trong đối số native → dùng --file hoặc `-` (đọc stdin):
    '{"skill":"x","date":"2026-01-01"}' | python update_context.py <ws> append activity_log -
    python3 update_context.py <workspace_folder> restore <tên-file-snapshot>

Đảm bảo:
- Lock file: chống 2 skill ghi đè nhau (chờ 5s, phá lock bỏ quên > 60s).
- Ghi atomic (tmp + os.replace) + tự cập nhật updated_at + validate schema sau ghi.
- SNAPSHOT: trước MỖI lần ghi, bản hiện tại được lưu vào .context-history/ (giữ 20 bản mới nhất)
  → hỏng/ghi nhầm → `restore`. Đây là cơ chế recovery thay cho việc chuyển SQLite
  (chỉ chuyển SQLite khi ≥ 2 agent ghi đồng thời THƯỜNG XUYÊN hoặc context > 1 MB — xem context-protocol.md).
- ROTATION: activity_log vượt 200 entry → 100 entry cũ nhất chuyển sang
  project-context.archive.jsonl (append-only, mỗi dòng 1 JSON) — context không phình vô hạn.
"""
import json, os, sys, time
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROTATE_KEY, ROTATE_MAX, ROTATE_KEEP = "activity_log", 200, 100
SNAP_DIR, SNAP_KEEP = ".context-history", 20


def _parse(v: str):
    try:
        return json.loads(v)
    except (json.JSONDecodeError, ValueError):
        return v

OBJECT_ARRAYS = {"activity_log", "change_requests", "known_issues"}


def _read_value(raw: str, argv_file: str | None) -> str:
    """Giá trị từ --file, từ stdin (raw == '-') hoặc đối số trực tiếp."""
    if argv_file:
        return Path(argv_file).read_text(encoding="utf-8-sig")
    if raw == "-":
        return sys.stdin.read()
    return raw


def _step(node, k: str, create: bool):
    """Đi một bước theo khóa dict hoặc chỉ số mảng (known_issues.0.status)."""
    if isinstance(node, list):
        if not k.lstrip("-").isdigit():
            raise SystemExit(f"❌ '{k}' không phải chỉ số mảng (dùng known_issues.0.status hoặc lệnh patch)")
        i = int(k)
        if not -len(node) <= i < len(node):
            raise SystemExit(f"❌ chỉ số {i} ngoài phạm vi mảng (độ dài {len(node)})")
        return node[i]
    if not isinstance(node, dict):
        raise SystemExit(f"❌ không đi tiếp được qua '{k}' (giá trị hiện tại không phải object/mảng)")
    if create:
        return node.setdefault(k, {})
    if k not in node:
        raise SystemExit(f"❌ không có khóa '{k}'")
    return node[k]


def _set_last(node, k: str, val):
    if isinstance(node, list):
        node[int(k)] = val
    else:
        node[k] = val


def _acquire_lock(target: Path, timeout: float = 5.0, stale: float = 60.0) -> Path:
    lock = target.with_suffix(".json.lock")
    t0 = time.time()
    while True:
        try:
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            return lock
        except FileExistsError:
            try:
                if time.time() - lock.stat().st_mtime > stale:
                    lock.unlink(missing_ok=True)
                    continue
            except FileNotFoundError:
                continue
            if time.time() - t0 > timeout:
                raise SystemExit("❌ project-context.json đang bị khóa bởi tiến trình khác — thử lại sau")
            time.sleep(0.1)


def _snapshot(f: Path):
    """Lưu bản hiện tại vào .context-history/ trước khi ghi; giữ SNAP_KEEP bản mới nhất."""
    d = f.parent / SNAP_DIR
    d.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    (d / f"context-{ts}.json").write_bytes(f.read_bytes())
    snaps = sorted(d.glob("context-*.json"))
    for old in snaps[:-SNAP_KEEP]:
        old.unlink(missing_ok=True)


def _rotate(ctx: dict, ws: Path):
    """activity_log > ROTATE_MAX → đẩy phần cũ sang archive JSONL, giữ ROTATE_KEEP entry mới nhất."""
    log = ctx.get(ROTATE_KEY)
    if not isinstance(log, list) or len(log) <= ROTATE_MAX:
        return 0
    cut = len(log) - ROTATE_KEEP
    archived, ctx[ROTATE_KEY] = log[:cut], log[cut:]
    arch = ws / "project-context.archive.jsonl"
    with open(arch, "a", encoding="utf-8") as fh:
        for e in archived:
            fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    return cut


def _restore(ws: Path, name: str | None) -> int:
    f = ws / "project-context.json"
    d = ws / SNAP_DIR
    snaps = sorted(d.glob("context-*.json")) if d.exists() else []
    if not snaps:
        print("❌ không có snapshot nào trong .context-history/")
        return 1
    src = (d / name) if name else snaps[-1]
    if not src.exists():
        print(f"❌ không có snapshot {name}. Có sẵn: {[s.name for s in snaps[-5:]]}")
        return 1
    json.loads(src.read_text(encoding="utf-8-sig"))  # snapshot phải là JSON hợp lệ
    lock = _acquire_lock(f)
    try:
        tmp = f.with_suffix(".json.tmp")
        tmp.write_bytes(src.read_bytes())
        os.replace(tmp, f)
    finally:
        lock.unlink(missing_ok=True)
    print(f"✅ đã khôi phục context từ {src.name}")
    return 0


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    ws, op = Path(sys.argv[1]), sys.argv[2]
    f = ws / "project-context.json"
    if op == "restore":
        return _restore(ws, sys.argv[3] if len(sys.argv) > 3 else None)
    argv = sys.argv[:]
    argv_file = None
    if "--file" in argv:
        i = argv.index("--file")
        if i + 1 >= len(argv):
            print("❌ --file cần đường dẫn")
            return 2
        argv_file = argv[i + 1]
        del argv[i:i + 2]
        argv.append("")  # chỗ giữ cho <value>
    if op == "patch":
        if len(argv) < 6 and not (argv_file and len(argv) >= 5):
            print(__doc__)
            return 2
    elif len(argv) < 5:
        print(__doc__)
        return 2
    key = argv[3]
    if not f.exists():
        print("NO_CONTEXT: chưa có project-context.json — chạy /a1-project-init trước")
        return 1
    if op not in ("set", "append", "patch"):
        print(f"❌ op '{op}' không hợp lệ (set | append | patch | restore)")
        return 2
    if op == "patch":
        item_id = argv[4]
        raw = _read_value(argv[5] if len(argv) > 5 else "", argv_file)
    else:
        raw = _read_value(argv[4], argv_file)
    lock = _acquire_lock(f)
    try:
        _snapshot(f)  # N5: luôn có đường lùi trước mỗi lần ghi
        ctx = json.loads(f.read_text(encoding="utf-8-sig"))
        keys = key.split(".")
        tgt = ctx
        for k in keys[:-1]:
            tgt = _step(tgt, k, create=(op != "patch"))
        val = _parse(raw)
        if op == "set":
            _set_last(tgt, keys[-1], val)
        elif op == "append":
            arr = tgt.setdefault(keys[-1], []) if isinstance(tgt, dict) else _step(tgt, keys[-1], False)
            if not isinstance(arr, list):
                print(f"❌ {key} không phải mảng — không append được")
                return 1
            if keys[-1] in OBJECT_ARRAYS and not isinstance(val, dict):
                print(f"❌ {key} chỉ nhận JSON object, nhận được: {raw[:80]!r}. "
                      f"Trên PowerShell hãy dùng --file <file.json> hoặc truyền qua stdin (-).")
                return 2
            arr.append(val)
        else:  # patch
            arr = _step(tgt, keys[-1], False)
            if not isinstance(arr, list):
                print(f"❌ {key} không phải mảng — không patch được")
                return 1
            if not isinstance(val, dict):
                print(f"❌ patch cần JSON object, nhận được: {raw[:80]!r} (PowerShell: dùng --file)")
                return 2
            hit = [e for e in arr if isinstance(e, dict) and str(e.get("id")) == str(item_id)]
            if len(hit) != 1:
                print(f"❌ tìm thấy {len(hit)} phần tử có id='{item_id}' trong {key} (cần đúng 1)")
                return 1
            hit[0].update(val)
        n_rot = _rotate(ctx, ws)  # N3
        ctx["updated_at"] = datetime.now().strftime("%Y-%m-%d")
        tmp = f.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(ctx, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tmp, f)
    finally:
        lock.unlink(missing_ok=True)
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from validate_context import validate_context  # type: ignore
        errs = validate_context(json.loads(f.read_text(encoding="utf-8-sig")))
        if errs:
            print("⚠️ CONTEXT_INVALID sau khi ghi (nên sửa):", "; ".join(map(str, errs)))
    except Exception:
        pass
    print(f"✅ {op} {key} OK" + (f" (đã rotate {n_rot} entry activity_log → archive.jsonl)" if n_rot else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
