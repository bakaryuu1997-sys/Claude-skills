#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dien block 開発 cua sheet 見積明細書 trong template bao gia (見積書).
Giu NGUYEN 100% phan con lai (logo/anh, dinh dang, cac sheet & block khac) bang cach
sua truc tiep XML cua dung sheet thay vi dung openpyxl de luu (openpyxl lam mat drawing).

Usage:
    python fill_dev_estimate.py <tasks.json> <output.xlsx> [--unit md|mh] [--md-per-pm 20]
                                [--template <path>] [--sheet 見積明細書]

Don vi (--unit):
  md  (MAC DINH): cong so theo MD (人日). Tieu de cot H cua block 開発 -> "小計 (人日)";
                  divisor 人月 cua block 開発 doi tu /140 sang /<md-per-pm> (mac dinh 22).
  mh           : cong so theo MH (人時/gio). Giu nguyen template ("小計 (人時)", /140).

tasks.json: list, moi task: {"category","function","detail","dev"} - "dev" theo don vi da chon.
Suc chua block 開発 mac dinh = 52 dong (13-64). Vuot -> chi dien 52 task dau (canh bao).
"""
import sys, os, json, re, html, zipfile, tempfile, shutil
import openpyxl

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def parse_args(argv):
    if "--help" in argv or "-h" in argv:
        print(__doc__)
        sys.exit(0)
    pos = [a for a in argv[1:] if not a.startswith("--")]
    opt = {}
    i = 1
    while i < len(argv):
        if argv[i].startswith("--"):
            key = argv[i][2:]
            if i + 1 < len(argv) and not argv[i+1].startswith("--"):
                opt[key] = argv[i+1]
                i += 2
            else:
                opt[key] = "true"
                i += 1
        else:
            i += 1
    if len(pos) < 2:
        print(__doc__)
        sys.exit(1)
    here = os.path.dirname(os.path.abspath(__file__))
    default_tmpl = os.path.normpath(os.path.join(here, "..", "assets",
                                    "MPL-H12 App_IOS_見積書_template.xlsx"))
    unit = opt.get("unit", "md").lower()
    if unit not in ("md", "mh"): unit = "md"
    return {"tasks": pos[0], "out": pos[1],
            "template": opt.get("template", default_tmpl),
            "sheet": opt.get("sheet", "見積明細書"),
            "unit": unit,
            "md_per_pm": float(opt.get("md-per-pm", "22"))}

def locate_block(xlsx_path, sheet_name):
    wb = openpyxl.load_workbook(xlsx_path, data_only=False)
    ws = wb[sheet_name]
    header_row = None
    for r in range(1, ws.max_row + 1):
        if ws.cell(row=r, column=1).value == "開発":
            for rr in range(r + 1, r + 4):
                if ws.cell(row=rr, column=2).value == "カテゴリ":
                    header_row = rr; break
            break
    if not header_row:
        raise RuntimeError("Khong tim thay block 開発 / header カテゴリ")
    data_start = header_row + 1
    subtotal_row = None
    for r in range(data_start, ws.max_row + 1):
        if ws.cell(row=r, column=2).value == "小計":
            subtotal_row = r; break
    if not subtotal_row:
        raise RuntimeError("Khong tim thay dong 小計")
    return header_row, data_start, subtotal_row

def sheet_xml_name(tmpdir, sheet_name):
    wbxml = open(os.path.join(tmpdir, "xl", "workbook.xml"), encoding="utf-8").read()
    m = re.search(r'<sheet name="%s"[^>]*r:id="(rId\d+)"' % re.escape(sheet_name), wbxml)
    if not m:
        raise RuntimeError("Khong thay sheet %s" % sheet_name)
    rid = m.group(1)
    rels = open(os.path.join(tmpdir, "xl", "_rels", "workbook.xml.rels"), encoding="utf-8").read()
    m2 = re.search(r'<Relationship Id="%s"[^>]*Target="([^"]+)"' % rid, rels)
    return os.path.join(tmpdir, "xl", m2.group(1))

def col_styles(xml, row):
    m = re.search(r'<row r="%d"[^>]*>(.*?)</row>' % row, xml, re.S)
    styles = {}
    for cm in re.finditer(r'<c r="([A-H])%d"[^>]*?(?: s="(\d+)")?[^>]*?(?:/>|>)' % row, m.group(1)):
        styles[cm.group(1)] = cm.group(2) or "0"
    return styles

def esc(s): return html.escape(str(s), quote=False)

def auto_sanitize_template(tmpdir):
    """Tu dong scan va clean sach se 100% tieng Viet, Rikkei/vendor cu, va ma noi bo tu template"""
    vn_to_ja = [
        ("yêu cầu của khách hàng", "お客様要件仕様書・要求事項"),
        ("Hạng mục test", "テスト項目"),
        ("Hạng mục", "項目"),
        ("Phương pháp thực hiện", "実施方式・対応方針"),
        ("Nội dung xác nhận", "確認内容"),
        ("Ghi chú", "備考"),
        ("※Nếu có yêu cầu test trên nhiều môi trường hoặc thêm test case ngoài phạm vi trên, effort test sẽ được xem xét và báo giá lại.",
         "※複数環境での検証や上記スコープ外のテストケース追加が必要な場合は、別途テスト工数を精算・再見積りいたします。"),
        ("・Các tài liệu/cấu hình dưới đây được dự kiến là deliverables của phạm vi này.",
         "・本スコープにおける納品成果物（ドキュメントおよび設定一式）は以下の通りです。"),
        ("■Danh sách deliverables", "■納品成果物一覧"),
        ("Tên deliverable", "成果物名称"),
        ("Mô tả", "概要・詳細"),
        ("Lập tài liệu hoàn công: 構成図, パラメータ, 試験結果", "納品ドキュメント作成（システム構成図、各種パラメータ設定書、試験結果報告書）"),
        ("Tiếng Nhật, mức chi tiết tiêu chuẩn", "日本語、標準詳細度"),
        ("Bàn giao & giải thích tài liệu", "運用引継ぎおよび各種設計・手順ドキュメントの説明・質疑応答"),
        ("Lập test plan & test case (単体 / 結合)", "テスト計画書・テストケース作成（単体テスト・結合テスト仕様）"),
        ("Kịch bản end-to-end: web会議 thông, luồng khác bị chặn", "エンドツーエンド結合テストシナリオ検証・不具合修正"),
        ("Môi trường test sẵn sàng", "テスト検証環境提供前提"),
        ("Khởi tạo project, kiến trúc phân tầng, cấu hình build", "プロジェクト初期化・階層アーキテクチャ設計・ビルド構成"),
        ("Màn hình splash (logo, version)", "スプラッシュ画面実装（企業ロゴ・バージョン表示）"),
        ("Màn chọn receiver/transmitter + navigation", "モード選択画面・ナビゲーション実装"),
        ("Xin quyền vị trí/BT/media/thông báo + dialog + thoát app", "権限リクエストダイアログ（位置情報/BLE/通知）実装"),
        ("Theme, asset, component thông báo/toast/dialog dùng chung", "共通UIテーマ・トースト・ダイアログコンポーネント実装"),
        ("CBCentralManager setup + quản lý state", "Bluetooth Centralマネージャー初期化・状態管理"),
        ("Quét + lọc (MPL R / MPL T) + danh sách thiết bị", "デバイススキャン・フィルタリング・デバイス一覧表示"),
        ("Connect/disconnect/cancel/timeout 10s + thông điệp", "接続・切断・タイムアウト制御・エラーメッセージ表示"),
        ("Tự kết nối thiết bị đã nhớ + tự reconnect", "登録済みデバイス自動再接続ロジック実装"),
        ("Giám sát RSSI + đổi màu trạng thái tín hiệu", "RSSIシグナル監視・電波強度ステータスカラー反映"),
        ("Ghi/notify GATT + ghép gói (chunking) theo \\r\\n", "GATTデータ送受信・パケットチャンキング処理"),
        ("Background mode + State Preservation/Restoration (rủi ro cao)", "バックグラウンドモード・状態復元処理"),
        ("Encode/decode lệnh dùng chung", "コマンドエンコード/デコード共通ライブラリ実装"),
        ("Màn chính + UI/trạng thái kết nối", "メイン画面UI・接続ステータスインジケーター"),
        ("Nhận dữ liệu đo (parse *RMD, list, append)", "測定データ受信パース・リスト追記処理"),
        ("Tải dữ liệu lưu (&TMD, progress, abort)", "保存データダウンロード・プログレスバー・中断処理"),
        ("Xem chi tiết dữ liệu (swipe/tap)", "測定詳細データ閲覧画面（スワイプ/タップ操作）"),
        ("Xoá từng + xoá tất cả + dialog xác nhận", "データ個別削除・一括削除・確認ダイアログ"),
        ("Tạo 現場データ: form, validation, 7 loại ống, check trùng tên", "現場データ登録フォーム・バリデーション・重複チェック"),
        ("Màn xem/danh sách log + xoá", "ログ一覧画面・ログクリア機能"),
        ("Màn chính (nút tần số/output/điều chỉnh)", "周波数・出力設定メインコントロールUI"),
        ("Lệnh điều khiển + answerback (bảng 1/2/3)", "制御コマンド送信・応答アンサーバリュー照合"),
        ("Điều chỉnh dòng (直接法) + nhãn giới hạn/max", "電流直接調整制御・リミット上限表示"),
        ("Hiển thị pin + cập nhật dữ liệu", "バッテリー残量表示・定期ポーリング更新"),
        ("Chức năng sleep (dialog, trạng thái)", "スリープモード移行・ステータスダイアログ"),
        ("Duy trì kết nối nền (riêng TX) + ánh xạ thông báo", "送信機バックグラウンドキープアライブ制御"),
        ("Xử lý timeout 3s + gửi lại x2", "3秒タイムアウト制御・最大2回リトライ処理"),
        ("GPS nội bộ (Core Location) + UI chuyển nguồn", "内部GPS測位連携・測位ソース切替UI"),
        ("GPS ngoài (Geode/BLE): connect/chọn/pin/disconnect (rủi ro cao)", "外部GPSレシーバー連携・BLE接続管理"),
        ("Gắn dữ liệu GPS vào dữ liệu đo (lat/long/sai số/độ cao)", "GPS座標（緯度/経度/高度/誤差）メタデータ付与"),
        ("Cấu hình map SDK (Google Maps iOS / MapKit) + key", "地図SDK構成設定・APIキー認証組み込み"),
        ("Marker + màu theo loại ống + nối line", "マップマーカー描画・属性別カラーライン描画"),
        ("Vị trí hiện tại/recenter/realtime/popup chi tiết", "現在位置追従・リセンター・詳細ポップアップ表示"),
        ("Sinh KML + màu/line + chia sẻ", "KML地理空間データ生成・共有機能"),
        ("Sinh CSV (cột theo spec) + chia sẻ", "CSVエクスポート・ファイル共有連携"),
        ("Tích hợp share sheet + dialog lỗi", "OS標準シェアシート連携・エラーダイアログ"),
        ("Mô hình dữ liệu + persistence + giới hạn dung lượng", "データ永続化モデリング・ローカルストレージ容量制御"),
        ("Local notification (trạng thái TX) + chỉ báo foreground", "ローカルプッシュ通知・フォアグラウンドインジケーター")
    ]

    brand_replacements = [
        ("株式会社リッケイ", "システム開発受託チーム"),
        ("リッケイ", "システム開発チーム"),
        ("Rikkeisoft", "Development Team"),
        ("Rikkei Japan", "Development Team"),
        ("Rikkei", "Development Team"),
        ("rikkei", "development team"),
        ("RIKKEISOFT", "DEVELOPMENT TEAM"),
        ("RIKKEI", "DEVELOPMENT TEAM")
    ]

    internal_steps = [
        ("A3プロトタイプ準拠", "画面UIプロトタイプ合意仕様準拠"),
        ("A5設計書準拠", "データベース物理設計書準拠"),
        ("A4設計書準拠", "API設計仕様書準拠"),
        ("A2要件仕様", "要件定義書・業務フロー仕様"),
        ("D1ハンドオーバー", "運用保守引継書・Runbook")
    ]

    for root, _, files in os.walk(tmpdir):
        for fn in files:
            if fn.endswith(".xml"):
                fpath = os.path.join(root, fn)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                    orig = content
                    for vn, ja in vn_to_ja:
                        content = content.replace(vn, ja)
                    for b_old, b_new in brand_replacements:
                        content = content.replace(b_old, b_new)
                    for s_old, s_new in internal_steps:
                        content = content.replace(s_old, s_new)
                    if content != orig:
                        with open(fpath, "w", encoding="utf-8") as f:
                            f.write(content)
                except Exception:
                    pass

def main():
    a = parse_args(sys.argv)
    tasks = json.load(open(a["tasks"], encoding="utf-8-sig"))
    if not os.path.exists(a["template"]):
        print("Khong tim thay template:", a["template"]); sys.exit(1)
    header_row, data_start, subtotal_row = locate_block(a["template"], a["sheet"])
    capacity = subtotal_row - data_start
    n = len(tasks)
    if n > capacity:
        print("CANH BAO: %d task > suc chua %d dong. Chi dien %d task dau." % (n, capacity, capacity))
        tasks = tasks[:capacity]; n = capacity
    last = data_start + n - 1
    tmp = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(a["template"]) as z:
            z.extractall(tmp)
        auto_sanitize_template(tmp)
        sxml_path = sheet_xml_name(tmp, a["sheet"])
        xml = open(sxml_path, encoding="utf-8").read()
        st = col_styles(xml, data_start)
        sub_st = col_styles(xml, subtotal_row)
        mb = re.search(r'<c r="B%d".*?(?:</c>|/>)' % subtotal_row, xml, re.S)
        b_subtotal_cell = mb.group(0)

        def s(col): return st.get(col, "0")
        def ss(col): return sub_st.get(col, "0")
        def num(ref, sty, v): return '<c r="%s" s="%s"><v>%s</v></c>' % (ref, sty, v)
        def istr(ref, sty, t): return ('<c r="%s" s="%s" t="inlineStr"><is><t xml:space="preserve">%s</t></is></c>'
                                       % (ref, sty, esc(t)))
        def empt(ref, sty): return '<c r="%s" s="%s"/>' % (ref, sty)
        def fml(ref, sty, f): return '<c r="%s" s="%s"><f>%s</f></c>' % (ref, sty, f)

        def replace_inner(xml, rn, inner):
            return re.sub(r'(<row r="%d"[^>]*>).*?(</row>)' % rn,
                          lambda m: m.group(1) + inner + m.group(2), xml, count=1, flags=re.S)

        for i, t in enumerate(tasks):
            r = data_start + i
            cells = (num("A%d" % r, s("A"), i + 1)
                     + istr("B%d" % r, s("B"), t.get("category", ""))
                     + istr("C%d" % r, s("C"), t.get("function", ""))
                     + istr("D%d" % r, s("D"), t.get("detail", ""))
                     + num("E%d" % r, s("E"), round(float(t.get("dev", 0)), 1))
                     + fml("F%d" % r, s("F"), "CEILING((E%d)*0.4, 0.1)" % r)
                     + fml("G%d" % r, s("G"), "CEILING((E%d)*0.1, 0.1)" % r)
                     + fml("H%d" % r, s("H"), "SUM(E%d:G%d)" % (r, r)))
            xml = replace_inner(xml, r, cells)

        for r in range(last + 1, subtotal_row):
            cells = "".join(empt("%s%d" % (c, r), s(c)) for c in "ABCDEFGH")
            xml = replace_inner(xml, r, cells)

        sub = (empt("A%d" % subtotal_row, ss("A")) + b_subtotal_cell
               + empt("C%d" % subtotal_row, ss("C")) + empt("D%d" % subtotal_row, ss("D"))
               + fml("E%d" % subtotal_row, ss("E"), "SUM(E%d:E%d)" % (data_start, last))
               + fml("F%d" % subtotal_row, ss("F"), "SUM(F%d:F%d)" % (data_start, last))
               + fml("G%d" % subtotal_row, ss("G"), "SUM(G%d:G%d)" % (data_start, last))
               + fml("H%d" % subtotal_row, ss("H"), "SUM(H%d:H%d)" % (data_start, last)))
        xml = replace_inner(xml, subtotal_row, sub)

        # --- Don vi: cap nhat tieu de cot H (block 開発) + divisor 人月 ---
        if a["unit"] == "md":
            hstyle = col_styles(xml, header_row).get("H", "0")
            new_h = ('<c r="H%d" s="%s" t="inlineStr"><is><t xml:space="preserve">小計 (人日)</t></is></c>'
                     % (header_row, hstyle))
            xml = re.sub(r'<c r="H%d"[^>]*?(?:/>|>.*?</c>)' % header_row,
                         lambda m: new_h, xml, count=1, flags=re.S)
            mpm = a["md_per_pm"]
            mpm_str = str(int(mpm)) if mpm == int(mpm) else str(mpm)
            xml = xml.replace("H%d/140" % subtotal_row, "H%d/%s" % (subtotal_row, mpm_str))
        # unit == mh: giu nguyen template (人時, /140)

        open(sxml_path, "w", encoding="utf-8").write(xml)

        if os.path.exists(a["out"]): os.remove(a["out"])
        files = []
        for root, _, fs in os.walk(tmp):
            for f in fs:
                files.append(os.path.relpath(os.path.join(root, f), tmp))
        files.sort(key=lambda x: (x != "[Content_Types].xml", x))
        with zipfile.ZipFile(a["out"], "w", zipfile.ZIP_DEFLATED) as z:
            for arc in files:
                z.write(os.path.join(tmp, arc), arc)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    total = sum(round(float(t.get("dev", 0)), 1) for t in tasks)
    if a["unit"] == "md":
        unit_lbl = "人日 (MD)"; pm = round(total / a["md_per_pm"], 2)
    else:
        unit_lbl = "人時 (MH)"; pm = round(total / 140.0, 2)
    print("OK: dien %d task (dong %d-%d), 小計 dong %d. don vi=%s. 開発 = %s %s (~ %s 人月)."
          % (n, data_start, last, subtotal_row, a["unit"].upper(), total, unit_lbl, pm))

if __name__ == "__main__":
    main()
