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


@t("T14 xlsx_build + xlsx_verify: spec tiếng Nhật dựng ĐẠT; ô placeholder [CẦN ĐIỀN] bị bắt khi --client-facing")
def t14():
    tmp = Path(tempfile.mkdtemp(prefix="ev_t14_"))
    spec = {"title": "t", "language": "ja", "sheets": [{"name": "テスト", "title": "見出し", "subtitle": "副題",
            "columns": [{"key": "id", "header": "テストID", "width": 12}, {"key": "st", "header": "ステータス", "width": 12, "validate": ["未回答", "回答済"]}],
            "rows": [{"id": "A-1", "st": "回答済"}, {"id": "A-2", "st": "未回答"}],
            "total_row": {"label": "合計", "sum": []}}]}
    (tmp / "s.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    out = tmp / "ok.xlsx"
    r = run([str(SKILLS / "a1-project-init/scripts/xlsx_build.py"), str(tmp / "s.json"), str(out)])
    assert r.returncode == 0, r.stderr[-300:]
    v = run([str(SKILLS / "a1-project-init/scripts/xlsx_verify.py"), str(out), "--client-facing"])
    assert v.returncode == 0 and "ĐẠT" in v.stdout, v.stdout[-400:]
    spec["sheets"][0]["rows"].append({"id": "[CẦN ĐIỀN]", "st": "未回答"})
    (tmp / "bad.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    bad = tmp / "bad.xlsx"
    run([str(SKILLS / "a1-project-init/scripts/xlsx_build.py"), str(tmp / "bad.json"), str(bad)])
    v2 = run([str(SKILLS / "a1-project-init/scripts/xlsx_verify.py"), str(bad), "--client-facing"])
    assert v2.returncode == 1 and "placeholder" in v2.stdout, v2.stdout[-400:]


@t("T15 docx_build: spec B2 dựng được; có heading Word, bảng, font eastAsia = Yu Gothic (ja)")
def t15():
    from docx import Document  # noqa
    tmp = Path(tempfile.mkdtemp(prefix="ev_t15_"))
    spec = {"language": "ja", "title": "基本設計書", "subtitle": "サンプル", "meta": [["版", "1.0"]],
            "blocks": [{"type": "h1", "text": "1. 目的"}, {"type": "p", "text": "本書は…"},
                       {"type": "table", "columns": ["ID", "名前"], "rows": [["SCR-01", "ログイン"]], "widths": [3, 6]},
                       {"type": "code", "text": "flowchart LR\n A-->B"}]}
    (tmp / "d.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    out = tmp / "d.docx"
    r = run([str(SKILLS / "a1-project-init/scripts/docx_build.py"), str(tmp / "d.json"), str(out)])
    assert r.returncode == 0, r.stderr[-300:]
    d = Document(str(out))
    heads = [p.text for p in d.paragraphs if p.style.name.startswith("Heading")]
    assert heads == ["1. 目的"], heads
    # bảng 0 = metadata bìa (spec.meta), bảng 1 = bảng nội dung
    assert len(d.tables) == 2 and len(d.tables[1].rows) == 2, len(d.tables)
    ea = {r._element.rPr.rFonts.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia")
          for p in d.paragraphs for r in p.runs if r._element.rPr is not None and r._element.rPr.rFonts is not None}
    assert "Yu Gothic" in ea, ea


@t("T16 check_gate: tiêu đề tiếng Nhật (優先度/ステータス) vẫn đếm được P1 mở; 未回答 không bị coi là đã trả lời")
def t16():
    tmp = Path(tempfile.mkdtemp(prefix="ev_t16_"))
    from openpyxl import Workbook
    wb = Workbook(); ws = wb.active; ws.title = "質問管理"
    ws["A1"] = "質問管理表"; ws["A2"] = "副題"
    ws.append(["No.", "優先度", "質問", "ステータス"])
    for i in range(5):
        ws.append([f"Q-{i}", "P1", "質問", "未回答"])
    ws.append(["Q-9", "P1", "質問", "回答済"])
    ws.append(["Q-10", "P2", "質問", "未回答"])
    (tmp / "Proj_QA_Tracker.xlsx").parent.mkdir(exist_ok=True)
    wb.save(tmp / "Proj_QA_Tracker.xlsx")
    r = run([str(SKILLS / "a1-project-init/scripts/check_gate.py"), str(tmp)])
    assert r.returncode == 1 and "5 câu P1" in r.stdout, (r.returncode, r.stdout[-300:])


@t("T17 E2E: chạy chuỗi mẫu 勤怠承認（A4→A9, C5, C7, C8, B3）— mọi xlsx ĐẠT, CRUD phủ, gate đúng 2 lần")
def t17():
    e2e = SKILLS / "evals" / "e2e" / "build_all.py"
    tmp = Path(tempfile.mkdtemp(prefix="ev_t17_"))
    env = dict(os.environ, E2E_WS=str(tmp / "ws"), PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([PY, "-B", str(e2e)], capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=600)
    assert r.returncode == 0, (r.stdout + r.stderr)[-600:]
    docs = tmp / "ws" / "docs"
    xlsx = sorted(docs.rglob("*.xlsx"))
    assert len(xlsx) >= 8, len(xlsx)
    for f in xlsx:
        v = run([str(SKILLS / "a1-project-init/scripts/xlsx_verify.py"), str(f), "--client-facing"])
        assert v.returncode == 0, f"{f.name}: {v.stdout[-300:]}"
    assert "CRUD_Matrix phủ 100%" in r.stdout or "phủ 100%" in r.stdout, "CRUD chưa phủ 100%"
    c5 = docs / "C5_test-execution"
    snaps = sorted(c5.glob("*_test_results_ST_*.json"))
    assert len(snaps) == 2, [x.name for x in snaps]
    first = run([str(SKILLS / "c5-test-execution/scripts/test_metrics.py"), str(snaps[0]), "--format", "md"])
    second = run([str(SKILLS / "c5-test-execution/scripts/test_metrics.py"), str(snaps[1]), "--format", "md"])
    assert first.returncode == 1 and "NOT QUALIFIED" in first.stdout, (first.returncode, first.stdout[-300:])
    assert second.returncode == 0 and "NOT QUALIFIED" not in second.stdout, (second.returncode, second.stdout[-300:])
    assert (docs / "B2_basic-design").exists() and any((docs / "B2_basic-design").glob("*.docx"))
    assert any((docs / "B3_detail-design").glob("*.docx")), "thiếu tài liệu B3 (docx)"
    assert any((docs / "A9_project-timeline").glob("*.xlsx")), "thiếu lịch dự án (A9 xlsx)"
    # Giai đoạn 2: B0/B1/D/X — mỗi loại phải có file đúng định dạng
    need = {"B0_proposal-sow": ["*Statement_Of_Work.docx", "*Technical_Proposal*.docx", "*SOW_Scope_Matrix.xlsx"],
            "B1_project-kickoff": ["*Kickoff_Deck.pptx", "*Project_Charter.docx", "*Kickoff_Workbook.xlsx", "*Meeting_Minutes_Template.docx"],
            "D1_handover-doc": ["*Handover.docx", "*Handover_Workbook.xlsx", "*Runbook.md"],
            "D2_uat-acceptance": ["*UAT_Acceptance_Certificate.docx", "*UAT_SignOff_Workbook.xlsx", "punch_list_warranty_backlog.json"],
            "D3_user-guide-manual": ["*User_Manual_EndUser.docx", "*Admin_Guide.docx", "*Quick_Start_Guide.md"],
            "X1_acquire-codebase-knowledge": ["*Onboarding_Guide.md"], "X2_project-architecture": ["*.html"],
            "X3_project-status": ["*Status_Snapshot.md"], "X4_meeting-minutes": ["*Minutes*.docx", "*Minutes*.xlsx"],
            "X5_coding-standards": ["*ENGINEERING_STANDARDS.md"], "X7_presentation-deck": ["*Progress_Deck*.pptx"]}
    for folder, pats in need.items():
        for pat in pats:
            assert list((docs / folder).glob(pat)), f"thiếu {folder}/{pat}"
    # API詳細 phải có trong API design
    from openpyxl import load_workbook as _lw
    _ws = _lw(next((docs / "A4_api-design").glob("*API_Design.xlsx")))
    assert "API詳細" in _ws.sheetnames, "thiếu sheet API詳細"
    # Ma trận RACI: mỗi dòng đúng 1 chữ A (kiểm bằng công thức cột 検算)
    _raci = _lw(next((docs / "B1_project-kickoff").glob("*Kickoff_Workbook.xlsx")))["RACI"]
    for _r in range(4, _raci.max_row + 1):
        _row = [_raci.cell(row=_r, column=_c).value for _c in range(2, 9)]
        if any(_row):
            assert _row.count("A") == 1, f"RACI dòng {_r}: phải có đúng 1 chữ A, thấy {_row.count('A')}"
    # Báo cáo CR gửi khách phải là tiếng Nhật (không có nhãn tiếng Việt của script)
    _cr = next((docs / "C7_change-request").glob("*CR-001_Change_Request_JA.docx"))
    from docx import Document as _D
    _txt = " ".join(x.text for x in _D(str(_cr)).paragraphs)
    assert "Sprint delay" not in _txt and "tối thiểu" not in _txt, "CR gửi khách còn tiếng Việt"


@t("T18 verify_fe_scaffold: 'palt' trong chú thích CSS không bị cảnh báo; 'palt' thật vẫn bị bắt; mock/token/localStorage vẫn là ERROR")
def t18():
    tmp = Path(tempfile.mkdtemp(prefix="ev_t18_"))
    (tmp / "package.json").write_text('{"dependencies":{"@tanstack/react-query":"5","zod":"3"}}', encoding="utf-8")
    (tmp / "src/lib").mkdir(parents=True)
    (tmp / "src/lib/api-client.ts").write_text("export {}", encoding="utf-8")
    (tmp / "tests/e2e").mkdir(parents=True)
    (tmp / "tests/e2e/a.spec.ts").write_text("", encoding="utf-8")
    script = str(SKILLS / "c0-frontend-dev/scripts/verify_fe_scaffold.py")
    (tmp / "src/a.css").write_text('/* never use font-feature-settings: "palt" on body */\nbody{line-height:1.6}', encoding="utf-8")
    r = run([script, str(tmp)])
    assert r.returncode == 0 and "palt" not in r.stdout, r.stdout[-300:]
    (tmp / "src/a.css").write_text('body{font-feature-settings:"palt";}', encoding="utf-8")
    assert "palt" in run([script, str(tmp)]).stdout
    (tmp / "src/lib/mock-users.ts").write_text("export const mockUsers = [{id:1}];", encoding="utf-8")
    (tmp / "src/lib/store.ts").write_text("localStorage.setItem('accessToken', t)", encoding="utf-8")
    r = run([script, str(tmp)])
    assert r.returncode == 1 and r.stdout.count("ERROR") >= 1 and "mock" in r.stdout and "localStorage" in r.stdout, r.stdout[-400:]


@t("T19 coverage_summary + parse_npm_audit: test todo tách riêng; --fail-on moderate = medium")
def t19():
    tmp = Path(tempfile.mkdtemp(prefix="ev_t19_"))
    (tmp / "jest.json").write_text(json.dumps({"numTotalTests": 10, "numPassedTests": 9, "numFailedTests": 0,
                                               "numPendingTests": 0, "numTodoTests": 1, "numTotalTestSuites": 2}), encoding="utf-8")
    r = run([str(SKILLS / "c3-code-review/scripts/coverage_summary.py"), "--repo", str(tmp), "--coverage", "none.json",
             "--tests", str(tmp / "jest.json"), "--format", "md"])
    assert "9/10 pass, 0 fail, 1 skip/todo" in r.stdout, r.stdout
    audit = {"auditReportVersion": 2, "vulnerabilities": {"pkg": {"name": "pkg", "severity": "moderate", "isDirect": True, "via": [
        {"source": 1, "name": "pkg", "title": "t", "url": "https://github.com/advisories/GHSA-aaaa-bbbb-cccc", "severity": "moderate", "range": "<2"}],
        "range": "<2", "fixAvailable": True}}}
    (tmp / "audit.json").write_text(json.dumps(audit), encoding="utf-8")
    script = str(SKILLS / "c4-trailofbits-security-skills/scripts/parse_npm_audit.py")
    assert run([script, str(tmp / "audit.json"), "--fail-on", "moderate"]).returncode == 1
    assert run([script, str(tmp / "audit.json"), "--fail-on", "high"]).returncode == 0


@t("T20 c0 assets: không còn chuỗi tiếng Việt trong asset sao chép vào dự án khách; props văn bản UI bắt buộc")
def t20():
    assets = SKILLS / "c0-frontend-dev/assets"
    vi = re.compile(r"[ăâđêôơưáàảãạéèẻẽẹíìỉĩịóòỏõọúùủũụýỳỷỹỵ]", re.I)
    for f in assets.glob("*"):
        bad = [l for l in f.read_text(encoding="utf-8").splitlines() if vi.search(l)]
        assert not bad, f"{f.name}: {bad[:2]}"
    eb = (assets / "error-boundary.tsx").read_text(encoding="utf-8")
    cp = (assets / "command-palette.tsx").read_text(encoding="utf-8")
    assert "message: string; retryLabel: string" in eb
    assert "placeholder: string;" in cp and "dialogLabel: string;" in cp and "placeholder =" not in cp


if __name__ == "__main__":
    for fn in [t1, t1b, t1c, t2a, t2b, t2c, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14, t15, t16, t17, t18, t19, t20]:
        fn()
    n_fail = sum(1 for _, ok, _ in results if not ok)
    print(f"\n🧪 EVALS TẦNG 1 — {len(results)} test | {len(results) - n_fail} PASS | {n_fail} FAIL\n")
    for name, ok, msg in results:
        print(("✅" if ok else "❌"), name, ("" if ok else f"\n     → {msg}"))
    if n_fail == 0:
        print("\n✅ Tầng 1 sạch. Tầng 2 (golden LLM cases): evals/README.md")
    sys.exit(1 if n_fail else 0)
