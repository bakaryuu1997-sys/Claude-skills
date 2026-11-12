#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""i18n.py — chọn ngôn ngữ đầu ra cho script báo cáo, theo `settings.languages` trong project-context.json.

Nguồn quyết định duy nhất vẫn là `references/i18n-policy.md`; module này chỉ hiện thực hóa cho script:

    from i18n import add_lang_args, resolve_lang, pick
    add_lang_args(ap, audience="client_facing")          # thêm --lang auto|vi|ja|en, --context, --audience
    lang = resolve_lang(args.lang, args.context, args.audience)
    M = pick(MESSAGES, lang)                             # MESSAGES = {"vi": {...}, "ja": {...}, "en": {...}}

Quy tắc:
  * `--lang vi|ja|en` luôn thắng.
  * `--lang auto` (mặc định): đọc `settings.languages[<audience>]` từ `--context`; không có context hoặc thiếu khóa → `vi`
    (giữ hành vi cũ, đầu ra cũ không đổi).
  * `audience`: `client_facing` (tài liệu khách đọc/ký) hoặc `internal` (tài liệu nội bộ team) — xem bảng trong i18n-policy.
Mã trạng thái máy đọc (QUALIFIED, GO, NO-GO, PASS, FAIL, Critical/High…) KHÔNG dịch: chỉ câu chữ mô tả mới theo ngôn ngữ.
Chỉ thư viện chuẩn.
"""
import json
from pathlib import Path

LANGS = ("vi", "ja", "en")
AUDIENCES = ("client_facing", "internal", "code")


# Nhãn dùng chung xuất hiện TRONG tài liệu giao (không phải thông báo công cụ):
PLACEHOLDER = {"vi": "[CẦN ĐIỀN]", "ja": "[要記入]", "en": "[TO BE FILLED]"}
PLACEHOLDER_RE = r"\[CẦN ĐIỀN\]|\[要記入\]|\[TO BE FILLED\]"   # xlsx_verify chấp nhận cả ba
COMMON = {
    "vi": {"total": "Tổng", "dv_msg": "Chọn giá trị trong danh sách", "dv_title": "Giá trị không hợp lệ",
           "source": "Nguồn", "ok_resp": "Thành công", "err_resp": "Lỗi", "image": "ảnh"},
    "ja": {"total": "合計", "dv_msg": "リストから値を選択してください", "dv_title": "無効な値",
           "source": "出典", "ok_resp": "成功", "err_resp": "エラー", "image": "画像"},
    "en": {"total": "Total", "dv_msg": "Select a value from the list", "dv_title": "Invalid value",
           "source": "Source", "ok_resp": "Success", "err_resp": "Error", "image": "image"},
}


def placeholder(lang):
    return PLACEHOLDER.get(lang, PLACEHOLDER["vi"])


def common(lang):
    return pick(COMMON, lang)


def lang_from_argv(argv, default="vi", audience="client_facing"):
    """Đọc --lang / --context trực tiếp từ argv (cho script dùng sys.argv thô): trả (lang, argv_đã_bỏ_cờ)."""
    args, lang, ctx, i = [], "auto", None, 0
    while i < len(argv):
        if argv[i] == "--lang" and i + 1 < len(argv):
            lang = argv[i + 1]; i += 2
        elif argv[i] == "--context" and i + 1 < len(argv):
            ctx = argv[i + 1]; i += 2
        else:
            args.append(argv[i]); i += 1
    return resolve_lang(lang, ctx, audience, default), args


def add_lang_args(ap, audience="internal"):
    ap.add_argument("--lang", choices=("auto",) + LANGS, default="auto",
                    help="ngôn ngữ đầu ra; auto = theo settings.languages trong --context (mặc định vi)")
    if not _has_option(ap, "--context"):
        ap.add_argument("--context", help="project-context.json để đọc settings.languages")
    ap.add_argument("--audience", choices=AUDIENCES, default=audience,
                    help="loại người đọc để chọn khóa trong settings.languages (mặc định %s)" % audience)


def _has_option(ap, flag):
    return any(flag in a.option_strings for a in ap._actions)


def resolve_lang(explicit="auto", context_path=None, audience="internal", default="vi"):
    if explicit in LANGS:
        return explicit
    if context_path:
        try:
            ctx = json.loads(Path(context_path).read_text(encoding="utf-8-sig"))
            langs = (ctx.get("settings") or {}).get("languages") or {}
            v = langs.get(audience)
            if v not in LANGS and audience == "internal":
                v = langs.get("client_facing")  # thiếu internal → theo ngôn ngữ tài liệu chung của dự án
            if v in LANGS:
                return v
        except (OSError, json.JSONDecodeError, AttributeError):
            pass
    return default


def pick(messages, lang):
    """Bảng chuỗi theo ngôn ngữ; thiếu khóa trong ngôn ngữ đích → rơi về vi (không để KeyError làm hỏng báo cáo)."""
    base = dict(messages["vi"])
    base.update(messages.get(lang, {}))
    return base
