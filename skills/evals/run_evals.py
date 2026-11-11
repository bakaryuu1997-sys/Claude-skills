#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""run_evals.py — eval harness TẦNG 1 (tự động, không cần LLM) cho bộ skill (v3.5.0).
Kiểm toàn bộ lớp deterministic: scripts dùng chung + gen Postman/OpenAPI + linter.
Chạy sau MỖI lần sửa script/skill, cùng với skill_doctor.

Usage: python3 run_evals.py [<skills_dir>]
Exit 0 = tất cả PASS, 1 = có FAIL. Tầng 2 (golden LLM cases): xem evals/README.md."""
import json, os, re, shutil, subprocess, sys, tempfile, time
from pathlib import Path

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

if sys.flags.isolated:
    # `python -I` bỏ user-site nên KHÔNG thấy openpyxl (pip cài --user). Harness tự chạy lại KHÔNG kèm -I.
    _rc = subprocess.run([sys.executable, "-B", os.path.abspath(__file__)] + sys.argv[1:],
                         env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1")).returncode
    sys.exit(_rc)

SKILLS = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
PY = sys.executable
results = []  # (name, ok, msg)


def run(cmd, **kw):
    kw.setdefault("encoding", "utf-8")
    kw.setdefault("errors", "replace")
    kw.setdefault("env", dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    return subprocess.run([PY, "-B"] + cmd, capture_output=True, text=True, timeout=120, **kw)


def t(name):
    def deco(fn):
        def wrap():
            try:
                fn()
                results.append((name, True, ""))
            except AssertionError as e:
                results.append((name, False, str(e)))
            except Exception as e:
                results.append((name, False, f"{type(e).__name__}: {e}"))
        wrap.__name__ = name
        return wrap
    return deco


def make_ws(known_issue=False):
    ws = Path(tempfile.mkdtemp(prefix="eval_ws_"))
    ctx = {"version": "1.0",
           "project": {"name": "Eval Demo", "type": "web_app", "current_sprint": 1},
           "tech_stack": {"backend": "FastAPI"},
           "team": [{"id": "BE-1", "role": "Backend Dev", "allocation": 1.0}],
           "settings": {"working_days_per_week": 5},
           "known_issues": ([{"severity": "Critical", "status": "Open", "title": "x"}] if known_issue else []),
           "change_requests": [], "activity_log": []}
    (ws / "project-context.json").write_text(json.dumps(ctx, ensure_ascii=False, indent=2), encoding="utf-8")
    return ws


def make_qa_tracker(ws: Path, n_open_p1: int):
    import openpyxl
    wb = openpyxl.Workbook()
    s = wb.active
    s.append(["#", "Chủ đề", "Câu hỏi", "Priority", "Lý do", "Câu trả lời", "Người", "Ngày", "Trạng thái"])
    for i in range(n_open_p1):
        s.append([f"A{i}", "Auth", f"Q{i}?", "🔴 P1", "-", "", "", "", "⬜ Pending"])
    s.append(["B1", "Auth", "done?", "🔴 P1", "-", "OK", "PO", "01/07", "✅ Answered"])
    s.append(["C1", "NFR", "later?", "🟠 P2", "-", "", "", "", "⬜ Pending"])
    wb.save(ws / "Eval_Demo_QA_Tracker.xlsx")


@t("T1 update_context: set + append + atomic + validate")
def t1():
    ws = make_ws()
    r = run([str(SKILLS / "a1-project-init/scripts/update_context.py"), str(ws), "set", "estimates.total_md", "329"])
    assert r.returncode == 0, r.stdout + r.stderr
    r = run([str(SKILLS / "a1-project-init/scripts/update_context.py"), str(ws), "append", "activity_log",
             '{"skill":"estimate","date":"2026-07-09","outputs":["a.xlsx"]}'])
    assert r.returncode == 0, r.stdout + r.stderr
    ctx = json.loads((ws / "project-context.json").read_text(encoding="utf-8"))
    assert ctx["estimates"]["total_md"] == 329, "set không ăn"
    assert len(ctx["activity_log"]) == 1 and ctx["activity_log"][0]["skill"] == "estimate", "append không ăn"
    assert "updated_at" in ctx, "thiếu updated_at"
    assert not (ws / "project-context.json.lock").exists(), "lock không được dọn"
    shutil.rmtree(ws)


@t("T1b rotation: activity_log > 200 → archive JSONL, giữ 100")
def t1b():
    ws = make_ws()
    ctx = json.loads((ws / "project-context.json").read_text(encoding="utf-8"))
    ctx["activity_log"] = [{"skill": f"s{i}", "date": "2026-07-09"} for i in range(205)]
    (ws / "project-context.json").write_text(json.dumps(ctx), encoding="utf-8")
    r = run([str(SKILLS / "a1-project-init/scripts/update_context.py"), str(ws), "append", "activity_log",
             '{"skill":"last","date":"2026-07-09"}'])
    assert r.returncode == 0 and "rotate" in r.stdout, r.stdout
    ctx = json.loads((ws / "project-context.json").read_text(encoding="utf-8"))
    assert len(ctx["activity_log"]) == 100, f"log còn {len(ctx['activity_log'])}, phải 100"
    assert ctx["activity_log"][-1]["skill"] == "last", "entry mới nhất phải được giữ"
    arch = (ws / "project-context.archive.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(arch) == 106 and json.loads(arch[0])["skill"] == "s0", f"archive {len(arch)} dòng"
    shutil.rmtree(ws)


@t("T1c snapshot + restore: ghi nhầm → khôi phục được")
def t1c():
    ws = make_ws()
    r = run([str(SKILLS / "a1-project-init/scripts/update_context.py"), str(ws), "set", "project.name", "SAI"])
    assert r.returncode == 0, r.stdout
    assert list((ws / ".context-history").glob("context-*.json")), "không có snapshot"
    r = run([str(SKILLS / "a1-project-init/scripts/update_context.py"), str(ws), "restore"])
    assert r.returncode == 0, r.stdout + r.stderr
    ctx = json.loads((ws / "project-context.json").read_text(encoding="utf-8"))
    assert ctx["project"]["name"] == "Eval Demo", f"restore sai: {ctx['project']['name']}"
    shutil.rmtree(ws)


@t("T8 match_intent: map task → skill đúng + không đoán bừa")
def t8():
    r = run([str(SKILLS / "menu/scripts/match_intent.py"), str(SKILLS), "khách muốn đổi scope giữa sprint"])
    assert r.returncode == 0 and "/c7-change-request" in r.stdout.splitlines()[1], r.stdout
    r = run([str(SKILLS / "menu/scripts/match_intent.py"), str(SKILLS), "nấu phở bò"])
    assert r.returncode == 1 and "Không skill nào khớp" in r.stdout, "phải từ chối task ngoài phạm vi"


@t("T2a check_gate: 5 P1 mở → CHẶN (exit 1)")
def t2a():
    ws = make_ws()
    make_qa_tracker(ws, 5)
    r = run([str(SKILLS / "a1-project-init/scripts/check_gate.py"), str(ws)])
    assert r.returncode == 1, f"exit={r.returncode}, phải 1\n{r.stdout}"
    assert "GATE P1" in r.stdout and "5" in r.stdout, r.stdout
    shutil.rmtree(ws)


@t("T2b check_gate: 2 P1 mở + 0 bug → PASS (exit 0)")
def t2b():
    ws = make_ws()
    make_qa_tracker(ws, 2)
    r = run([str(SKILLS / "a1-project-init/scripts/check_gate.py"), str(ws)])
    assert r.returncode == 0, f"exit={r.returncode}\n{r.stdout}"
    shutil.rmtree(ws)


@t("T2c check_gate: bug Critical mở → CHẶN go-live")
def t2c():
    ws = make_ws(known_issue=True)
    r = run([str(SKILLS / "a1-project-init/scripts/check_gate.py"), str(ws)])
    assert r.returncode == 1 and "GATE BUG" in r.stdout, r.stdout
    shutil.rmtree(ws)


@t("T3 compute_status: staleness input mới hơn output")
def t3():
    ws = make_ws()
    now = time.time()
    for fname, age in [("Eval_Demo_Estimate.xlsx", 3600), ("Eval_Demo_API_Design.xlsx", 60),
                       ("Eval_Demo_DB_Design.xlsx", 60)]:
        f = ws / fname
        f.touch()
        os.utime(f, (now - age, now - age))
    r = run([str(SKILLS / "a1-project-init/scripts/compute_status.py"), str(ws), str(SKILLS)])
    assert r.returncode == 0, r.stderr
    d = json.loads(r.stdout)
    import re
    st = {}
    for x in d["documents"]:
        st[x["skill"]] = x["status"]
        st[re.sub(r'^[a-z]\d+-', '', x["skill"])] = x["status"]
    assert st.get("estimate") == "stale", f"estimate phải stale, được: {st.get('estimate')}"
    assert st.get("api-design") == "present", st.get("api-design")
    shutil.rmtree(ws)


@t("T4 check_circular_fk: bắt chu trình + pass đồ thị sạch")
def t4():
    p = Path(tempfile.mktemp(suffix=".json"))
    p.write_text('{"orders":["users"],"users":["orders"]}', encoding="utf-8")
    r = run([str(SKILLS / "a5-db-design/scripts/check_circular_fk.py"), str(p)])
    assert r.returncode == 1 and "CIRCULAR" in r.stdout, r.stdout
    p.write_text('{"orders":["users"],"users":[]}', encoding="utf-8")
    r = run([str(SKILLS / "a5-db-design/scripts/check_circular_fk.py"), str(p)])
    assert r.returncode == 0, r.stdout
    p.unlink()


@t("T5 gen_postman + gen_openapi: golden spec → cấu trúc đúng")
def t5():
    spec = SKILLS / "evals/golden/a4-api-design/api_spec.json"
    if not spec.exists():
        spec = SKILLS / "evals/golden/api-design/api_spec.json"
    tmp = Path(tempfile.mkdtemp(prefix="eval_gen_"))
    r = run([str(SKILLS / "a4-api-design/scripts/gen_postman.py"), str(spec), str(tmp / "c.json")])
    assert r.returncode == 0, r.stdout + r.stderr
    coll = json.loads((tmp / "c.json").read_text(encoding="utf-8"))
    folders = [f["name"] for f in coll["item"]]
    assert "⚙️ Setup & Auth" in folders and "Rooms" in folders, folders
    rooms_get = coll["item"][folders.index("Rooms")]["item"][0]["request"]
    assert any(h["key"] == "Authorization" for h in rooms_get["header"]), "thiếu Bearer header cho auth_required"
    r = run([str(SKILLS / "a4-api-design/scripts/gen_openapi.py"), str(spec), str(tmp / "o.yaml")])
    assert r.returncode == 0, r.stdout + r.stderr
    try:
        import yaml
        doc = yaml.safe_load((tmp / "o.yaml").read_text(encoding="utf-8"))
        assert doc["openapi"] == "3.0.3" and len(doc["paths"]) == 3, "openapi paths sai"
        assert "parameters" in doc["paths"]["/rooms/{roomId}/bookings"]["post"], "thiếu path param"
    except ImportError:
        pass
    shutil.rmtree(tmp)


@t("T6 skill_doctor: bộ skill hiện tại phải 0 FAIL")
def t6():
    r = run([str(SKILLS / "x6-skill-doctor/scripts/skill_doctor.py"), str(SKILLS)])
    assert r.returncode == 0, "skill_doctor có FAIL:\n" + r.stdout


@t("T7 check_xlsx: tự kiểm checker (bắt lỗi thật, pass file đúng)")
def t7():
    import openpyxl
    tmp = Path(tempfile.mkdtemp(prefix="eval_chk_"))
    wb = openpyxl.Workbook()
    s = wb.active; s.title = "Summary"
    s.append(["Category", "BD", "DD", "Dev", "UT", "IT", "Total"])
    s.append(["Backend", 1, 2, 10, 3, 2, "=SUM(B2:F2)"])
    wb.create_sheet("Detail Estimate").append(["No", "Task"])
    wb.save(tmp / "ok.xlsx")
    exp = tmp / "exp.json"
    exp.write_text(json.dumps({"required_sheets": ["Summary"], "must_have_formula": ["Summary"],
                               "min_columns": {"Summary": 7}, "forbid_strings": ["fpt-canteen"]}), encoding="utf-8")
    r = run([str(SKILLS / "evals/checkers/check_xlsx.py"), str(tmp / "ok.xlsx"), str(exp)])
    assert r.returncode == 0, r.stdout
    wb2 = openpyxl.Workbook()
    s2 = wb2.active; s2.title = "Summary"
    s2.append(["Category", "Total"]); s2.append(["Backend", 18])
    s2.append(["Ghi chú", "deploy tại fpt-canteen.vn"])
    wb2.save(tmp / "bad.xlsx")
    r = run([str(SKILLS / "evals/checkers/check_xlsx.py"), str(tmp / "bad.xlsx"), str(exp)])
    assert r.returncode == 1, "checker phải FAIL file thiếu công thức + leak chuỗi cấm"
    assert "công thức" in r.stdout and "fpt-canteen" in r.stdout, r.stdout
    shutil.rmtree(tmp)


@t("T9 đồng bộ số liệu: số skill (thư mục = AGENTS.md = README = menu) và version plugin = manifest_version")
def t9():
    repo = SKILLS.parent
    folders = sorted(p.name for p in SKILLS.iterdir() if (p / "SKILL.md").is_file())
    n = len(folders)
    manifest = json.loads((SKILLS / "a1-project-init/assets/skills-manifest.json").read_text(encoding="utf-8"))
    mv = manifest["manifest_version"]
    problems = []
    for rel in ("AGENTS.md", "rules/AGENTS.md", "README.md"):
        fp = repo / rel
        if not fp.exists():
            problems.append(f"thiếu {rel}")
            continue
        nums = {int(x) for x in re.findall(r"(\d+)\s*skills? chuẩn", fp.read_text(encoding="utf-8"))}
        if nums != {n}:
            problems.append(f"{rel}: ghi {sorted(nums)} skill chuẩn, thư mục có {n}")
    if (repo / "AGENTS.md").exists() and (repo / "rules/AGENTS.md").exists():
        if (repo / "AGENTS.md").read_bytes() != (repo / "rules/AGENTS.md").read_bytes():
            problems.append("rules/AGENTS.md khác AGENTS.md (gốc là nguồn duy nhất)")
    r = run([str(SKILLS / "menu/scripts/check_menu_sync.py"), str(SKILLS)])
    m = re.search(r"(\d+) skill folder", r.stdout)
    if not m or int(m.group(1)) != n:
        problems.append(f"check_menu_sync đếm {m.group(1) if m else '?'} folder, thư mục có {n}")
    def versions(o, acc):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "version" and isinstance(v, str):
                    acc.append(v)
                else:
                    versions(v, acc)
        elif isinstance(o, list):
            for v in o:
                versions(v, acc)
        return acc
    for rel in ("plugin.json", "marketplace.json", ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"):
        fp = repo / rel
        if not fp.exists():
            problems.append(f"thiếu {rel}")
            continue
        for v in versions(json.loads(fp.read_text(encoding="utf-8")), []):
            if v != mv:
                problems.append(f"{rel}: version {v} != manifest_version {mv}")
    assert not problems, "\n".join(problems)


def _json_out(cmd_args):
    r = run(cmd_args)
    return r.returncode, r.stdout, r.stderr


@t("T10 test_metrics (c5): UT đạt → QUALIFIED exit 0; có test fail → NOT QUALIFIED exit 1")
def t10():
    tmp = Path(tempfile.mkdtemp(prefix="ev_t10_"))
    ok = {"phase": "UT", "tests": [{"id": "T-1", "result": "pass", "viewpoint": "Functional"},
                                   {"id": "T-2", "result": "pass", "viewpoint": "Security"}],
          "defects": [], "coverage": {"line": 90, "branch": 85}}
    bad = dict(ok, tests=[{"id": "T-1", "result": "pass"}, {"id": "T-2", "result": "fail"}])
    (tmp / "ok.json").write_text(json.dumps(ok), encoding="utf-8")
    (tmp / "bad.json").write_text(json.dumps(bad), encoding="utf-8")
    r1 = run([str(SKILLS / "c5-test-execution/scripts/test_metrics.py"), str(tmp / "ok.json")])
    assert r1.returncode == 0 and "QUALIFIED" in r1.stdout and "NOT QUALIFIED" not in r1.stdout, (r1.returncode, r1.stdout[-300:])
    r2 = run([str(SKILLS / "c5-test-execution/scripts/test_metrics.py"), str(tmp / "bad.json")])
    assert r2.returncode == 1 and "NOT QUALIFIED" in r2.stdout, (r2.returncode, r2.stdout[-300:])


@t("T11 cr_impact (c7): 10 new + 2 regression, buffer 15% trên new → 13.5 MD, 0.614 PM (tính tay)")
def t11():
    tmp = Path(tempfile.mkdtemp(prefix="ev_t11_"))
    cr = {"cr_id": "CR-001", "cr_type": "ADDITION", "title": "t",
          "items": [{"task": "A", "kind": "new", "dev": 10}, {"task": "B", "kind": "regression", "dev": 2}],
          "settings": {"md_per_person_month": 22, "buffer_percent": 15, "sprint_duration_weeks": 2},
          "capacity_md": 10, "original_total_md": 100}
    (tmp / "cr.json").write_text(json.dumps(cr), encoding="utf-8")
    r = run([str(SKILLS / "c7-change-request/scripts/cr_impact.py"), str(tmp / "cr.json"), "--format", "json"])
    assert r.returncode == 0, r.stderr[-300:]
    d = json.loads(r.stdout)
    assert d["total_cr_md"] == 13.5, d["total_cr_md"]
    assert d["person_month"] == 0.614, d["person_month"]
    # thiếu md_per_person_month phải DỪNG (không tự đặt số 22)
    bad = dict(cr, settings={"buffer_percent": 15})
    (tmp / "bad.json").write_text(json.dumps(bad), encoding="utf-8")
    r2 = run([str(SKILLS / "c7-change-request/scripts/cr_impact.py"), str(tmp / "bad.json")])
    assert r2.returncode != 0, "thiếu md_per_person_month mà vẫn chạy — vi phạm quy tắc một nguồn"


@t("T12 timeline_calc (a9): 329 MD / 23 MD sprint → 17 sprint; 6 VEVENT có UID; cảnh báo trễ go-live")
def t12():
    tmp = Path(tempfile.mkdtemp(prefix="ev_t12_"))
    ws = tmp / "ws"; ws.mkdir()
    ctx = {"version": "3.17.0", "project": {"name": "T", "type": "web_app", "start_date": "2026-07-01", "go_live_target": "2026-10-15"},
           "tech_stack": {}, "team": [{"id": "be1", "role": "BE", "md_per_sprint": 8, "allocation": 1},
                                      {"id": "fe1", "role": "FE", "md_per_sprint": 8, "allocation": 1},
                                      {"id": "qa1", "role": "QA", "md_per_sprint": 7, "allocation": 1}],
           "settings": {"sprint_duration_weeks": 2, "working_days_per_week": 5, "md_per_person_month": 22, "buffer_percent": 15},
           "estimates": {"total_md": 329}}
    (ws / "project-context.json").write_text(json.dumps(ctx), encoding="utf-8")
    out = tmp / "tl.json"; ics = tmp / "tl.ics"
    r = run([str(SKILLS / "a9-project-timeline/scripts/timeline_calc.py"), str(ws), "--json", str(out), "--ics", str(ics)])
    assert r.returncode == 0, r.stdout[-300:] + r.stderr[-300:]
    d = json.loads(out.read_text(encoding="utf-8"))
    assert d["total_sprints"] == 17, d["total_sprints"]
    ms = [m["id"] for m in d["milestones"]]
    assert ms == ["M1", "M2", "M3", "M4", "M5", "M6"], ms
    assert any("trễ" in w for w in d["warnings"]), d["warnings"]
    text = ics.read_text(encoding="utf-8")
    assert text.count("BEGIN:VEVENT") == 6 and text.count("\r\nUID:") + text.count("UID:") >= 6, "ICS thiếu UID"


@t("T13 smoke_test_runner (c8): endpoint 200 + JSON đúng → GO exit 0; endpoint 500 → NO-GO exit 1; không check → exit 2")
def t13():
    import http.server, threading
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith("/ok"):
                body = b'{"status":"ok"}'; code = 200
            else:
                body = b'{"error":"boom"}'; code = 500
            self.send_response(code); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
        def log_message(self, *a):
            pass
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    th = threading.Thread(target=srv.serve_forever, daemon=True); th.start()
    try:
        base = f"http://127.0.0.1:{srv.server_address[1]}"
        tmp = Path(tempfile.mkdtemp(prefix="ev_t13_"))
        good = {"base_url": base, "checks": [{"id": "S1", "name": "health", "method": "GET", "path": "/ok",
                                              "expect_status": 200, "expect_json_path": {"status": "ok"}}]}
        badc = {"base_url": base, "checks": [{"id": "S2", "name": "down", "method": "GET", "path": "/down", "expect_status": 200}]}
        empty = {"base_url": base, "checks": []}
        for name, obj in (("good", good), ("bad", badc), ("empty", empty)):
            (tmp / f"{name}.json").write_text(json.dumps(obj), encoding="utf-8")
        r1 = run([str(SKILLS / "c8-release-deployment/scripts/smoke_test_runner.py"), str(tmp / "good.json")])
        assert r1.returncode == 0 and "GO" in r1.stdout and "NO-GO" not in r1.stdout, (r1.returncode, r1.stdout[-300:])
        r2 = run([str(SKILLS / "c8-release-deployment/scripts/smoke_test_runner.py"), str(tmp / "bad.json")])
        assert r2.returncode == 1 and "NO-GO" in r2.stdout, (r2.returncode, r2.stdout[-300:])
        r3 = run([str(SKILLS / "c8-release-deployment/scripts/smoke_test_runner.py"), str(tmp / "empty.json")])
        assert r3.returncode == 2, r3.returncode
    finally:
        srv.shutdown()


if __name__ == "__main__":
    for fn in [t1, t1b, t1c, t2a, t2b, t2c, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13]:
        fn()
    n_fail = sum(1 for _, ok, _ in results if not ok)
    print(f"\n🧪 EVALS TẦNG 1 — {len(results)} test | {len(results) - n_fail} PASS | {n_fail} FAIL\n")
    for name, ok, msg in results:
        print(("✅" if ok else "❌"), name, ("" if ok else f"\n     → {msg}"))
    if n_fail == 0:
        print("\n✅ Tầng 1 sạch. Tầng 2 (golden LLM cases): evals/README.md")
    sys.exit(1 if n_fail else 0)
