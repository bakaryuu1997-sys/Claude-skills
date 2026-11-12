#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_architecture_html.py — sinh [TênDựÁn]_Architecture_v[N].html (1 file, CSS/JS/SVG inline, KHÔNG CDN).

Nguồn dữ liệu (chỉ render cái ĐỌC ĐƯỢC THẬT — thiếu thì hiện placeholder, không bịa):
  - compute_status.py (a1-project-init) → trạng thái tài liệu, gate, tiến độ
  - project-context.json                 → project, tech_stack, integrations, team, links
  - *_API_Design*.xlsx / *_DB_Design*.xlsx / *_BasicDesign_Workbook*.xlsx (openpyxl, read-only; thiếu openpyxl → placeholder)

Usage:
  python gen_architecture_html.py <workspace_folder> [--skills-dir <skills_dir>] [--out-dir <dir>] [--status <status.json>]
Mặc định ghi vào <workspace_folder>/docs/X2_project-architecture/ ; file đã có → sinh _v[N+1] (không ghi đè)
và đưa panel Changelog so với bản trước. In ra JSON tóm tắt (đường dẫn, số đếm) để skill ghi context."""
import html
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "a1-project-init" / "scripts"))
from i18n import pick, resolve_lang  # noqa: E402

esc = html.escape

# Nhãn giao diện theo ngôn ngữ tài liệu của dự án (settings.languages.client_facing — file này gửi cho khách).
LABELS = {
    "vi": {
        "nodata": "Chưa có dữ liệu{extra} — chạy /{skill} để bổ sung", "aria": "Sơ đồ hệ thống",
        "why_stack": "chưa có tech_stack/integrations trong context", "why_screen": "chưa đọc được sheet Screen_List",
        "why_status": "compute_status không trả dữ liệu",
        "navs": ["Tổng quan", "System", "Module & Screen", "API Map", "DB Overview", "Tài liệu", "Tiến độ", "Team & Links"],
        "chg_h": "Changelog so với bản trước", "chg_none": "Không có thay đổi số liệu.",
        "client": "Khách hàng", "phase": "giai đoạn", "sprint": "sprint", "gen": "sinh",
        "filter": "🔍 Lọc API / bảng DB theo từ khóa", "readonly": "View tổng hợp CHỈ ĐỌC — nguồn sự thật là các file gốc.",
        "th_screen": ["Mã MH", "Tên màn hình", "Module"], "ep": "endpoint",
        "th_api": ["Module", "Method", "URL", "Auth", "Mô tả"], "th_db": ["Bảng", "Tên logic", "Loại", "Mục đích"],
        "ok": "có", "stale": "lỗi thời", "missing": "chưa có",
        "th_doc": ["Bước", "Skill", "Trạng thái", "File"], "th_team": ["Vai trò", "Tên", "Bên"],
    },
    "ja": {
        "nodata": "データがありません{extra} — /{skill} を実行して追加してください", "aria": "システム構成図",
        "why_stack": "context に tech_stack/integrations がありません", "why_screen": "Screen_List シートを読み取れませんでした",
        "why_status": "compute_status がデータを返しませんでした",
        "navs": ["概要", "システム", "モジュールと画面", "API 一覧", "DB 概要", "ドキュメント", "進捗", "体制とリンク"],
        "chg_h": "前版からの変更点", "chg_none": "数値の変更はありません。",
        "client": "顧客", "phase": "フェーズ", "sprint": "スプリント", "gen": "生成",
        "filter": "🔍 API / DB テーブルをキーワードで絞り込み", "readonly": "集約ビュー（閲覧専用）— 正本は元のファイルです。",
        "th_screen": ["画面ID", "画面名", "モジュール"], "ep": "エンドポイント",
        "th_api": ["モジュール", "メソッド", "URL", "認証", "説明"], "th_db": ["テーブル", "論理名", "区分", "目的"],
        "ok": "あり", "stale": "古い", "missing": "未作成",
        "th_doc": ["工程", "スキル", "状態", "ファイル"], "th_team": ["役割", "氏名", "所属"],
    },
    "en": {
        "nodata": "No data{extra} — run /{skill} to add it", "aria": "System diagram",
        "why_stack": "no tech_stack/integrations in the context", "why_screen": "the Screen_List sheet could not be read",
        "why_status": "compute_status returned no data",
        "navs": ["Overview", "System", "Modules & Screens", "API Map", "DB Overview", "Documents", "Progress", "Team & Links"],
        "chg_h": "Changes since the previous version", "chg_none": "No figures changed.",
        "client": "Client", "phase": "phase", "sprint": "sprint", "gen": "generated",
        "filter": "🔍 Filter APIs / DB tables by keyword", "readonly": "Aggregated READ-ONLY view — the source files are the source of truth.",
        "th_screen": ["Screen ID", "Screen name", "Module"], "ep": "endpoint(s)",
        "th_api": ["Module", "Method", "URL", "Auth", "Description"], "th_db": ["Table", "Logical name", "Type", "Purpose"],
        "ok": "present", "stale": "outdated", "missing": "missing",
        "th_doc": ["Step", "Skill", "Status", "File"], "th_team": ["Role", "Name", "Side"],
    },
}
L = pick(LABELS, "vi")
LANG = "vi"

CSS = """
:root{--primary:#1F4E79;--secondary:#2E75B6;--accent:#ED7D31;--bg:#F5F7FA;--surface:#FFF;--text:#1F2937;--muted:#6B7280;
--success:#10B981;--warning:#F59E0B;--error:#EF4444;--border:#E5E7EB}
*{box-sizing:border-box}body{margin:0;font-family:"Segoe UI","Yu Gothic",system-ui,sans-serif;background:var(--bg);color:var(--text);display:flex;min-height:100vh}
nav{width:200px;background:var(--primary);color:#fff;padding:16px 0;position:sticky;top:0;height:100vh;flex-shrink:0}
nav h1{font-size:14px;margin:0 16px 12px;line-height:1.3}nav a{display:block;padding:8px 16px;color:#dbe7f3;text-decoration:none;font-size:14px;cursor:pointer}
nav a.on,nav a:hover{background:var(--secondary);color:#fff}main{flex:1;padding:24px;max-width:1200px;min-width:0}
section{display:none;background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:16px}section.on{display:block}
h2{margin:0 0 12px;color:var(--primary);font-size:20px}table{border-collapse:collapse;width:100%;font-size:14px}
th,td{border:1px solid var(--border);padding:6px 10px;text-align:left;vertical-align:top}th{background:var(--primary);color:#fff}tr:nth-child(even) td{background:#F9FAFB}
.cards{display:flex;gap:12px;flex-wrap:wrap;margin:12px 0}.card{border:1px solid var(--border);border-left:5px solid var(--secondary);border-radius:10px;padding:10px 14px;min-width:130px}
.card b{display:block;font-size:22px;color:var(--primary)}.muted{color:var(--muted)}.ph{border:1px dashed var(--border);padding:14px;border-radius:8px;color:var(--muted);background:#FAFAFA}
.badge{display:inline-block;padding:1px 8px;border-radius:10px;font-size:12px;color:#fff}.GET{background:var(--success)}.POST{background:var(--secondary)}
.PUT,.PATCH{background:var(--warning)}.DELETE{background:var(--error)}.OTHER{background:var(--muted)}
.ok{color:var(--success)}.stale{color:var(--warning)}.miss{color:var(--muted)}
#q{padding:8px 12px;border:1px solid var(--border);border-radius:8px;width:260px;margin-bottom:12px}svg text{font-family:inherit}
@media print{nav,#q{display:none}section{display:block;page-break-after:always;border:0}body{display:block}}
"""

JS = """
function go(id){document.querySelectorAll('section').forEach(function(s){s.classList.toggle('on',s.id==='sec-'+id)});
document.querySelectorAll('nav a').forEach(function(a){a.classList.toggle('on',a.dataset.go===id)});}
document.querySelectorAll('nav a').forEach(function(a){a.addEventListener('click',function(){go(a.dataset.go)})});
var q=document.getElementById('q');if(q){q.addEventListener('input',function(){var v=q.value.toLowerCase();
document.querySelectorAll('tr[data-s]').forEach(function(r){r.style.display=r.dataset.s.indexOf(v)<0?'none':''})})}
go('0');
"""


# ---------------------------------------------------------------- đọc dữ liệu
def load_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def newest(ws: Path, pattern: str):
    found = [f for f in list(ws.glob(pattern)) + list(ws.glob("docs/**/" + pattern)) if not f.name.startswith("~$")]
    return max(found, key=lambda f: f.stat().st_mtime) if found else None


def read_rows(xlsx: Path):
    """{sheet: [list rows]} bằng openpyxl read-only; ImportError → raise RuntimeError có thông điệp rõ."""
    try:
        import openpyxl
    except ImportError as e:  # noqa: F841
        raise RuntimeError("thiếu thư viện openpyxl (pip install openpyxl)")
    wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
    try:
        return {ws.title: [[("" if c is None else str(c).strip()) for c in row] for row in ws.iter_rows(values_only=True)]
                for ws in wb.worksheets}
    finally:
        wb.close()


def find_header(rows, needles, limit=10):
    for i, row in enumerate(rows[:limit]):
        low = [c.lower() for c in row]
        if all(any(n in c for c in low) for n in needles):
            return i, low
    return None, None


def col(low, *names):
    for n in names:
        for i, c in enumerate(low):
            if n in c:
                return i
    return None


def parse_api(xlsx: Path):
    mods = {}
    for sheet, rows in read_rows(xlsx).items():
        hi, low = find_header(rows, ["method", "url"])
        if hi is None:
            continue
        im, iu, ia, idesc = col(low, "method"), col(low, "url", "endpoint"), col(low, "auth"), col(low, "mô tả", "description", "summary", "chức năng")
        for r in rows[hi + 1:]:
            if im is None or iu is None or len(r) <= max(im, iu) or not r[iu] or r[iu].lower().startswith("total"):
                continue
            mods.setdefault(sheet, []).append({"method": r[im].upper(), "url": r[iu],
                                               "auth": r[ia] if ia is not None and ia < len(r) else "",
                                               "desc": r[idesc] if idesc is not None and idesc < len(r) else ""})
    return mods


def parse_db(xlsx: Path):
    tables = []
    for sheet, rows in read_rows(xlsx).items():
        hi, low = find_header(rows, ["table name"])
        if hi is None:
            continue
        it, il, ic, ik = col(low, "table name"), col(low, "logical"), col(low, "classification", "loại"), col(low, "purpose", "mục đích")
        for r in rows[hi + 1:]:
            if it is not None and len(r) > it and r[it] and not r[it].lower().startswith("total"):
                tables.append({"name": r[it], "logical": r[il] if il is not None and il < len(r) else "",
                               "type": r[ic] if ic is not None and ic < len(r) else "",
                               "purpose": r[ik] if ik is not None and ik < len(r) else ""})
        if tables:
            break
    return tables


def parse_screens(xlsx: Path):
    rows = read_rows(xlsx).get("Screen_List", [])
    hi, low = find_header(rows, ["mã", "tên"]) if rows else (None, None)
    if hi is None:
        hi, low = find_header(rows, ["id", "name"]) if rows else (None, None)
    if hi is None:
        return []
    ic, in_, im = 0, col(low, "tên", "name") or 1, col(low, "module")
    return [{"id": r[ic], "name": r[in_] if len(r) > in_ else "", "module": r[im] if im is not None and im < len(r) else ""}
            for r in rows[hi + 1:] if r and r[ic]]


# ---------------------------------------------------------------- render
def placeholder(skill: str, why: str = "") -> str:
    extra = f" ({esc(why)})" if why else ""
    return '<div class="ph">⬜ ' + L["nodata"].format(extra=extra, skill=esc(skill)) + "</div>"


def svg_system(stack: dict, integrations: list) -> str:
    clients = [(k, v) for k, v in stack.items() if k in ("mobile", "admin_cms") and v]
    backend = [(k, v) for k, v in stack.items() if k in ("backend", "auth", "cache", "hosting") and v]
    data = [(k, v) for k, v in stack.items() if k == "database" and v]
    ext = [(i.get("name", ""), i.get("status", ""), i.get("type", "")) for i in integrations if i.get("name")]
    if not (clients or backend or data or ext):
        return placeholder("a1-project-init", L["why_stack"])
    rows = max(len(clients), len(backend), len(data) + len(ext), 1)
    h = 60 + rows * 58
    out = [f'<svg viewBox="0 0 860 {h}" width="100%" role="img" aria-label="' + L["aria"] + '">']
    for x, title in ((10, "Clients"), (310, "Backend / API"), (610, "Data & External")):
        out.append(f'<text x="{x + 120}" y="22" text-anchor="middle" font-weight="700" fill="#1F4E79">{title}</text>')

    def box(x, y, label, sub, warn=False):
        stroke = "#ED7D31" if warn else "#2E75B6"
        flag = " ⚠️" if warn else ""
        return (f'<rect x="{x}" y="{y}" width="240" height="46" rx="8" fill="#fff" stroke="{stroke}" stroke-width="{3 if warn else 1.5}"/>'
                f'<text x="{x + 10}" y="{y + 20}" font-size="13" font-weight="700" fill="#1F2937">{esc(label)}{flag}</text>'
                f'<text x="{x + 10}" y="{y + 37}" font-size="12" fill="#6B7280">{esc(sub[:34])}</text>')

    for i, (k, v) in enumerate(clients):
        out.append(box(10, 40 + i * 58, k, v))
    for i, (k, v) in enumerate(backend):
        out.append(box(310, 40 + i * 58, k, v))
    right = [(k, v, False) for k, v in data] + [(n, (t or "integration") + (f" · {s}" if s else ""),
                                                  s.lower() not in ("ready", "done", "active", "live")) for n, s, t in ext]
    for i, (k, v, w) in enumerate(right):
        out.append(box(610, 40 + i * 58, k, v, w))
    if clients and backend:
        out.append('<line x1="250" y1="63" x2="310" y2="63" stroke="#2E75B6" stroke-width="2"/>')
    if backend and right:
        out.append('<line x1="550" y1="63" x2="610" y2="63" stroke="#2E75B6" stroke-width="2"/>')
    out.append("</svg>")
    return "".join(out)


def method_cls(m: str) -> str:
    return m if m in ("GET", "POST", "PUT", "PATCH", "DELETE") else "OTHER"


def build(ws: Path, skills_dir: Path, status: dict, notes: list):
    ctx = load_json(ws / "project-context.json")
    proj = ctx.get("project") if isinstance(ctx.get("project"), dict) else {}
    name = proj.get("name") or ws.name
    api = db = screens = None
    for label, pat, fn in (("api", "*_API_Design*.xlsx", parse_api), ("db", "*_DB_Design*.xlsx", parse_db),
                           ("scr", "*_BasicDesign_Workbook*.xlsx", parse_screens)):
        f = newest(ws, pat)
        if not f:
            continue
        try:
            val = fn(f)
        except Exception as e:  # noqa: BLE001
            notes.append(f"{f.name}: không đọc được ({e})")
            continue
        if label == "api":
            api = val
        elif label == "db":
            db = val
        else:
            screens = val
    docs = status.get("documents", [])
    present = [d for d in docs if d.get("status") in ("present", "stale")]
    return ctx, proj, name, api, db, screens, docs, present


def render(name, proj, ctx, api, db, screens, docs, present, status, version, prev):
    n_ep = sum(len(v) for v in (api or {}).values())
    counts = {"modules": len(api or {}), "endpoints": n_ep, "tables": len(db or []), "screens": len(screens or []),
              "docs_present": len(present), "docs_total": len(docs)}
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    P = []
    P.append(f"<!doctype html><html lang=\"{LANG}\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
             f"<title>{esc(name)} — Architecture v{version}</title><style>{CSS}</style></head><body>")
    navs = L["navs"]
    P.append("<nav><h1>" + esc(name) + "</h1>" + "".join(f'<a data-go="{i}">{i} {esc(t)}</a>' for i, t in enumerate(navs)) + "</nav><main>")
    # 0 header
    cards = "".join(f'<div class="card"><b>{v}</b>{esc(k)}</div>' for k, v in counts.items())
    chg = ""
    if prev:
        diff = [f"{k}: {prev.get(k, 0)} → {v}" for k, v in counts.items() if prev.get(k, 0) != v]
        chg = f"<h3>{esc(L['chg_h'])}</h3>" + ("<ul>" + "".join(f"<li>{esc(d)}</li>" for d in diff) + "</ul>" if diff
                                                         else f'<p class="muted">{esc(L["chg_none"])}</p>')
    P.append(f'<section id="sec-0"><h2>{esc(name)}</h2><p class="muted">{L["client"]}: {esc(str(proj.get("client", "—")))} · '
             f'{L["phase"]}: {esc(str(proj.get("current_phase", "—")))} · {L["sprint"]}: {esc(str(proj.get("current_sprint", "—")))} · '
             f'v{version} · {L["gen"]} {now}</p><div class="cards">{cards}</div>'
             f'<input id="q" placeholder="{esc(L["filter"])}"><p class="muted">{esc(L["readonly"])}</p>'
             f"{chg}</section>")
    # 1 system
    P.append('<section id="sec-1"><h2>System Diagram</h2>' + svg_system(ctx.get("tech_stack") or {}, ctx.get("integrations") or []) + "</section>")
    # 2 modules & screens
    if screens:
        body = "".join(f"<tr><td>{esc(s['id'])}</td><td>{esc(s['name'])}</td><td>{esc(s['module'])}</td></tr>" for s in screens)
        s2 = "<table><tr>" + "".join(f"<th>{esc(h)}</th>" for h in L["th_screen"]) + f"</tr>{body}</table>"
    else:
        s2 = placeholder("b2-basic-design", L["why_screen"])
    mods = "".join(f"<li><b>{esc(m)}</b> — {len(v)} {esc(L["ep"])}</li>" for m, v in (api or {}).items())
    P.append('<section id="sec-2"><h2>Module &amp; Screen</h2>' + (f"<ul>{mods}</ul>" if mods else "") + s2 + "</section>")
    # 3 API
    if api:
        rows = []
        for m, eps in api.items():
            for e in eps:
                s = f"{m} {e['method']} {e['url']} {e['desc']}".lower()
                rows.append(f'<tr data-s="{esc(s)}"><td>{esc(m)}</td><td><span class="badge {method_cls(e["method"])}">{esc(e["method"])}</span></td>'
                            f'<td>{esc(e["url"])}</td><td>{esc(e["auth"])}</td><td>{esc(e["desc"])}</td></tr>')
        s3 = "<table><tr>" + "".join(f"<th>{esc(h)}</th>" for h in L["th_api"]) + "</tr>" + "".join(rows) + "</table>"
    else:
        s3 = placeholder("a4-api-design")
    P.append(f'<section id="sec-3"><h2>API Map ({n_ep})</h2>{s3}</section>')
    # 4 DB
    if db:
        rows = "".join(f'<tr data-s="{esc((t["name"] + " " + t["logical"] + " " + t["purpose"]).lower())}"><td>{esc(t["name"])}</td>'
                       f'<td>{esc(t["logical"])}</td><td>{esc(t["type"])}</td><td>{esc(t["purpose"])}</td></tr>' for t in db)
        s4 = "<table><tr>" + "".join(f"<th>{esc(h)}</th>" for h in L["th_db"]) + "</tr>" + rows + "</table>"
    else:
        s4 = placeholder("a5-db-design")
    P.append(f'<section id="sec-4"><h2>DB Overview ({len(db or [])})</h2>{s4}</section>')
    # 5 docs
    icon = {"present": f'<span class="ok">✅ {esc(L["ok"])}</span>', "stale": f'<span class="stale">⚠️ {esc(L["stale"])}</span>', "missing": f'<span class="miss">⬜ {esc(L["missing"])}</span>'}
    rows = "".join(f"<tr><td>{esc(str(d.get('step', '')))}</td><td>{esc(d.get('skill', ''))}</td><td>{icon.get(d.get('status'), esc(str(d.get('status'))))}"
                   f"{' — ' + esc(', '.join(d.get('stale_because', []))) if d.get('stale_because') else ''}</td>"
                   f"<td>{esc(', '.join(f['file'] for f in d.get('files', [])[:3]))}</td></tr>" for d in docs)
    P.append('<section id="sec-5"><h2>Document Status</h2>' + ("<table><tr>" + "".join(f"<th>{esc(h)}</th>" for h in L["th_doc"]) + f"</tr>{rows}</table>"
                                                                if docs else placeholder("x3-project-status", L["why_status"])) + "</section>")
    # 6 progress
    prog = status.get("progress") or {}
    gates = (status.get("gates") or {}).get("raw", "")
    rows = "".join(f"<tr><td>{esc(k)}</td><td>{esc(str(v)) if v not in (None, '') else '—'}</td></tr>" for k, v in prog.items())
    P.append('<section id="sec-6"><h2>Progress</h2>' + (f"<table>{rows}</table>" if rows else placeholder("c6-sprint-review")) +
             (f"<h3>Gates</h3><pre>{esc(gates)}</pre>" if gates else "") + "</section>")
    # 7 team & links
    team = ctx.get("team") or []
    links = ctx.get("links") or {}
    t_rows = "".join(f"<tr><td>{esc(str(m.get('role', '')))}</td><td>{esc(str(m.get('name', '')))}</td><td>{esc(str(m.get('side', '')))}</td></tr>"
                     for m in team if isinstance(m, dict))
    l_rows = "".join(f"<tr><td>{esc(k)}</td><td>{esc(str(v))}</td></tr>" for k, v in links.items())
    P.append('<section id="sec-7"><h2>Team &amp; Links</h2>' + ("<table><tr>" + "".join(f"<th>{esc(h)}</th>" for h in L["th_team"]) + f"</tr>{t_rows}</table>" if t_rows else placeholder("a1-project-init"))
             + (f"<h3>Links</h3><table>{l_rows}</table>" if l_rows else "") + "</section>")
    P.append(f'</main><script type="application/json" id="arch-data">{json.dumps(counts)}</script><script>{JS}</script></body></html>')
    out = "".join(P)
    bad = [w for w in ("undefined", ">None<", "NaN") if w in out]
    if bad:
        raise RuntimeError(f"HTML chứa chuỗi lỗi {bad}")
    return out, counts


def main(argv):
    if not argv or argv[0].startswith("-"):
        print(__doc__)
        return 2
    ws = Path(argv[0]).resolve()
    opts = {"--skills-dir": None, "--out-dir": None, "--status": None, "--lang": "auto"}
    for i, a in enumerate(argv):
        if a in opts and i + 1 < len(argv):
            opts[a] = argv[i + 1]
    global L, LANG
    LANG = resolve_lang(opts["--lang"], ws / "project-context.json", "client_facing")  # X2 gửi cho khách xem
    L = pick(LABELS, LANG)
    skills_dir = Path(opts["--skills-dir"]).resolve() if opts["--skills-dir"] else Path(__file__).resolve().parents[2]
    if opts["--status"]:
        status = load_json(Path(opts["--status"]))
    else:
        cs = skills_dir / "a1-project-init" / "scripts" / "compute_status.py"
        try:
            r = subprocess.run([sys.executable, str(cs), str(ws), str(skills_dir)], capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=120)
            status = json.loads(r.stdout)
        except Exception as e:  # noqa: BLE001
            print(f"⚠️ compute_status lỗi: {e}", file=sys.stderr)
            status = {}
    notes = []
    ctx, proj, name, api, db, screens, docs, present = build(ws, skills_dir, status, notes)
    out_dir = Path(opts["--out-dir"]) if opts["--out-dir"] else ws / "docs" / "X2_project-architecture"
    out_dir.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^\w\-]+", "_", name).strip("_") or "Project"
    existing = sorted(out_dir.glob(f"{safe}_Architecture_v*.html"))
    nums = [int(m.group(1)) for f in existing if (m := re.search(r"_v(\d+)\.html$", f.name))]
    version = (max(nums) + 1) if nums else 1
    prev = None
    if nums:
        last = out_dir / f"{safe}_Architecture_v{max(nums)}.html"
        m = re.search(r'id="arch-data">(\{.*?\})</script>', last.read_text(encoding="utf-8", errors="replace"))
        prev = json.loads(m.group(1)) if m else None
    page, counts = render(name, proj, ctx, api, db, screens, docs, present, status, version, prev)
    target = out_dir / f"{safe}_Architecture_v{version}.html"
    target.write_text(page, encoding="utf-8", newline="\n")
    print(json.dumps({"file": str(target), "version": version, "counts": counts, "notes": notes}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
