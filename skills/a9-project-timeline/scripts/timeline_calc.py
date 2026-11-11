#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""timeline_calc.py — tính capacity, số sprint, mốc M1–M6 và xuất file .ics (RFC 5545) cho a9-project-timeline.

Usage:
    python timeline_calc.py <workspace_folder> [--total-md <MD>] [--ics <out.ics>] [--json <out.json>]

Nguồn dữ liệu (project-context.json, đọc bằng json thuần):
    team[]                  : role, allocation (mặc định 1.0), md_per_sprint (mặc định theo role — BẮT BUỘC có nếu thiếu)
    settings.sprint_duration_weeks (mặc định 2)
    project.name, project.start_date (YYYY-MM-DD, BẮT BUỘC), project.go_live_target (tùy chọn)
    estimates.total_md (hoặc --total-md)

Công thức (cố định, không suy diễn khác):
    cap(người)      = md_per_sprint × allocation × (sprint_duration_weeks / 2)
    cap(team)       = Σ cap(người)                         (mọi role)
    base_sprints    = ceil(total_md / cap(team))
    buffer_sprints  = 2 nếu base > 10; 1 nếu base > 6; ngược lại 0
    total_sprints   = base + buffer
    Mốc: M1 = start; M2..M5 = cuối sprint round(N × p) với p = 5/11, 8/11, 9/11, 10/11 (đúng cho N = 11);
         M6 = cuối sprint N. "Cuối sprint k" = start + k × sprint_weeks × 7 ngày.
    Go-live kiểm tra: end = M6. Nếu project.go_live_target < end → cảnh báo số tuần lệch.

Mã thoát: 0 = OK (có thể có cảnh báo); 2 = thiếu/sai dữ liệu đầu vào (không ghi file).
"""
import argparse
import datetime as dt
import json
import math
import sys
import uuid
from fractions import Fraction
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_MD_PER_SPRINT = {"Backend Dev": 8, "Frontend Dev": 8, "Mobile Dev": 8, "QA": 7, "PM": 5, "DevOps": 6}
MILESTONES = [  # (id, tên, tỷ lệ vị trí trong tổng sprint)
    ("M1", "Kickoff", Fraction(0)),
    ("M2", "API Freeze", Fraction(5, 11)),
    ("M3", "Feature Complete", Fraction(8, 11)),
    ("M4", "Code Freeze", Fraction(9, 11)),
    ("M5", "UAT Start", Fraction(10, 11)),
    ("M6", "Go-Live", Fraction(1)),
]
UID_NS = uuid.UUID("6f0c1d52-3a8e-4f4c-9b1e-2a7d5c1f0e11")


def fail(msg, code=2):
    print("LỖI:", msg)
    sys.exit(code)


def capacity(team, sprint_weeks):
    by_role, lines, warns = {}, [], []
    scale = sprint_weeks / 2.0
    for m in team:
        role = m.get("role")
        if not role:
            fail("team có thành viên thiếu 'role': %r" % (m,))
        alloc = m.get("allocation", 1.0)
        if not (0 < float(alloc) <= 1):
            fail("team[%s].allocation=%r phải trong (0,1]" % (m.get("id", role), alloc))
        mps = m.get("md_per_sprint", DEFAULT_MD_PER_SPRINT.get(role))
        if mps is None:
            fail("team[%s] thiếu md_per_sprint và role không có mặc định" % m.get("id", role))
        cap = float(mps) * float(alloc) * scale
        by_role[role] = by_role.get(role, 0.0) + cap
        lines.append({"id": m.get("id"), "role": role, "allocation": alloc, "md_per_sprint": mps,
                      "cap_per_sprint": round(cap, 2)})
        if float(alloc) < 1:
            warns.append("%s allocation=%s — capacity đã nhân hệ số (không cộng thêm buffer cho việc đó)" % (m.get("id"), alloc))
    return by_role, round(sum(by_role.values()), 2), lines, warns


def ics_escape(text):
    return str(text).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def fold(line):
    """Gấp dòng theo 75 octet UTF-8 (RFC 5545 §3.1), không cắt giữa ký tự."""
    out, cur, size = [], "", 0
    for ch in line:
        b = len(ch.encode("utf-8"))
        limit = 75 if not out else 74  # dòng tiếp theo có khoảng trắng đầu
        if size + b > limit:
            out.append(cur)
            cur, size = ch, b
        else:
            cur += ch
            size += b
    out.append(cur)
    return "\r\n ".join(out)


def build_ics(name, events, stamp):
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//claude-skill//a9-project-timeline//EN",
             "CALSCALE:GREGORIAN", "METHOD:PUBLISH"]
    for mid, title, date, desc in events:
        uid = "%s@claude-skill" % uuid.uuid5(UID_NS, "%s|%s" % (name, mid))
        d0 = date.strftime("%Y%m%d")
        d1 = (date + dt.timedelta(days=1)).strftime("%Y%m%d")
        lines += ["BEGIN:VEVENT", "UID:%s" % uid, "DTSTAMP:%s" % stamp,
                  "DTSTART;VALUE=DATE:%s" % d0, "DTEND;VALUE=DATE:%s" % d1,
                  "SUMMARY:%s" % ics_escape("%s %s — %s" % (name, mid, title)),
                  "DESCRIPTION:%s" % ics_escape(desc), "CATEGORIES:MILESTONE", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    return "\r\n".join(fold(l) for l in lines) + "\r\n"


def verify_ics(text, expected):
    """Parse lại: cấu trúc VCALENDAR, số VEVENT, mỗi VEVENT có UID/DTSTAMP/DTSTART/SUMMARY, UID duy nhất."""
    unfolded = text.replace("\r\n ", "")
    lines = [l for l in unfolded.split("\r\n") if l]
    if not lines or lines[0] != "BEGIN:VCALENDAR" or lines[-1] != "END:VCALENDAR":
        return "thiếu BEGIN/END VCALENDAR"
    if sum(1 for l in lines if l == "BEGIN:VEVENT") != expected or sum(1 for l in lines if l == "END:VEVENT") != expected:
        return "số VEVENT không khớp %d mốc" % expected
    uids = [l for l in lines if l.startswith("UID:")]
    if len(uids) != expected or len(set(uids)) != expected:
        return "UID thiếu hoặc trùng"
    for key in ("DTSTAMP:", "DTSTART;VALUE=DATE:", "SUMMARY:"):
        if sum(1 for l in lines if l.startswith(key)) != expected:
            return "thiếu %s ở một VEVENT" % key
    return None


def main(argv):
    ap = argparse.ArgumentParser(description="Tính timeline + .ics cho a9 (xem docstring).")
    ap.add_argument("workspace")
    ap.add_argument("--total-md", type=float)
    ap.add_argument("--ics")
    ap.add_argument("--json")
    a = ap.parse_args(argv[1:])

    ctx_p = Path(a.workspace) / "project-context.json"
    if not ctx_p.exists():
        fail("không thấy %s — chạy /a1-project-init trước" % ctx_p)
    try:
        ctx = json.loads(ctx_p.read_text(encoding="utf-8-sig"))
    except ValueError as e:
        fail("project-context.json lỗi cú pháp: %s" % e)

    proj = ctx.get("project") or {}
    settings = ctx.get("settings") or {}
    sprint_weeks = settings.get("sprint_duration_weeks", 2)
    team = ctx.get("team") or []
    if not team:
        fail("team[] trống — điền team trong context (a1) trước khi lập timeline")
    total_md = a.total_md if a.total_md is not None else (ctx.get("estimates") or {}).get("total_md")
    if total_md is None:
        fail("thiếu estimates.total_md — chạy /a6-estimate trước, hoặc truyền --total-md")
    try:
        total_md = float(total_md)
        assert total_md > 0
    except (TypeError, ValueError, AssertionError):
        fail("total_md phải là số > 0")
    try:
        start = dt.date.fromisoformat(str(proj.get("start_date")))
    except ValueError:
        fail("project.start_date phải dạng YYYY-MM-DD")

    by_role, team_cap, lines, warns = capacity(team, sprint_weeks)
    if team_cap <= 0:
        fail("capacity team = 0")
    base = math.ceil(total_md / team_cap)
    buffer = 2 if base > 10 else 1 if base > 6 else 0
    n = base + buffer
    if len(team) > 3:
        warns.append("team > 3 người: overhead giao tiếp 5–10% — kiểm xem đã nằm trong total_md của a6 chưa")

    weeks = 7 * sprint_weeks
    ms = []
    for mid, title, frac in MILESTONES:
        k = 0 if frac == 0 else int(round(n * frac))
        if mid == "M6":
            k = n
        date = start + dt.timedelta(days=k * weeks) if k else start
        ms.append({"id": mid, "name": title, "sprint_end": k, "date": date.isoformat()})
    end = start + dt.timedelta(days=n * weeks)
    seen = {}
    for m in ms[1:]:
        seen.setdefault(m["sprint_end"], []).append(m["id"])
    for k, ids in seen.items():
        if len(ids) > 1:
            warns.append("Các mốc %s cùng rơi vào cuối sprint %d (kế hoạch quá ngắn để tách) — gộp mốc hoặc tăng số sprint"
                         % (", ".join(ids), k))

    go_live = proj.get("go_live_target")
    gap_weeks = None
    if go_live:
        try:
            target = dt.date.fromisoformat(str(go_live))
            if end > target:
                gap_weeks = math.ceil((end - target).days / 7)
                warns.append("Ngày kết thúc tính được %s trễ %d tuần so với go_live_target %s — giảm scope, tăng team (nút thắt role) hoặc đàm phán lại mốc"
                             % (end.isoformat(), gap_weeks, go_live))
        except ValueError:
            warns.append("project.go_live_target không đúng YYYY-MM-DD — bỏ qua so sánh")

    result = {"total_md": total_md, "capacity_by_role": {k: round(v, 2) for k, v in by_role.items()},
              "team_capacity_per_sprint": team_cap, "members": lines,
              "base_sprints": base, "buffer_sprints": buffer, "total_sprints": n,
              "sprint_duration_weeks": sprint_weeks, "end_date": end.isoformat(),
              "go_live_target": go_live, "go_live_gap_weeks": gap_weeks,
              "milestones": ms, "warnings": warns}

    if a.ics:
        name = proj.get("name") or "Project"
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        events = [(m["id"], m["name"], dt.date.fromisoformat(m["date"]),
                   "Mốc %s (sprint %d) — %s" % (m["id"], m["sprint_end"], m["name"])) for m in ms]
        text = build_ics(name, events, stamp)
        err = verify_ics(text, len(events))
        if err:
            fail("verify .ics thất bại: %s (KHÔNG ghi file)" % err, code=1)
        out = Path(a.ics)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(text.encode("utf-8"))
        result["ics"] = str(out)

    if a.json:
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Capacity/sprint: %.2f MD (%s)" % (team_cap, ", ".join("%s=%.2f" % kv for kv in by_role.items())))
    print("Sprint: cơ sở %d + đệm %d = %d (sprint %d tuần) · kết thúc %s" % (base, buffer, n, sprint_weeks, end.isoformat()))
    for m in ms:
        print("  %s %-18s %s (sau sprint %d)" % (m["id"], m["name"], m["date"], m["sprint_end"]))
    for w in warns:
        print("CẢNH BÁO:", w)
    if a.ics:
        print("OK .ics (%d VEVENT, UID/DTSTAMP, CRLF, đã verify): %s" % (len(ms), a.ics))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
