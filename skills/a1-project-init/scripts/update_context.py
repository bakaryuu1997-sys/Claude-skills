#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""update_context.py — nguồn DUY NHẤT cho việc GHI project-context.json (v3.5.0).
MỌI skill ghi context qua script này — KHÔNG tự viết code ghi.

Usage:
    python3 update_context.py <workspace_folder> set <key.path> <value>
    python3 update_context.py <workspace_folder> append <key.path> '<json-item>'
    python3 update_context.py <workspace_folder> restore            # khôi phục từ snapshot gần nhất
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
    if len(sys.argv) < 5:
        print(__doc__)
        return 2
    key, raw = sys.argv[3], sys.argv[4]
    if not f.exists():
        print("NO_CONTEXT: chưa có project-context.json — chạy /a1-project-init trước")
        return 1
    if op not in ("set", "append"):
        print(f"❌ op '{op}' không hợp lệ (set | append | restore)")
        return 2
    lock = _acquire_lock(f)
    try:
        _snapshot(f)  # N5: luôn có đường lùi trước mỗi lần ghi
        ctx = json.loads(f.read_text(encoding="utf-8-sig"))
        keys = key.split(".")
        tgt = ctx
        for k in keys[:-1]:
            tgt = tgt.setdefault(k, {})
        val = _parse(raw)
        if op == "set":
            tgt[keys[-1]] = val
        else:
            arr = tgt.setdefault(keys[-1], [])
            if not isinstance(arr, list):
                print(f"❌ {key} không phải mảng — không append được")
                return 1
            arr.append(val)
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
