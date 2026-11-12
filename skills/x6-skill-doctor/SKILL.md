---
name: x6-skill-doctor
version: "3.17.0"
description: >-
  Audit CHÍNH BỘ SKILL (meta — dành cho người bảo trì skill): chạy linter kiểm tra frontmatter,
  độ dài, anti-pattern (copy-paste block, hardcode pipeline, công thức Excel sai), đồng bộ
  manifest ↔ folder, version. Trigger: "skill doctor", "kiểm tra skill", "audit skills",
  "lint skill", "skill nào lỗi thời", sau mỗi lần thêm/sửa skill. Bước X6.
---

# Skill Doctor — Linter cho bộ skill

## Mục tiêu

Bắt lại đúng lớp lỗi đã từng lọt trong quá khứ (số cột lệch, công thức Excel sai cú pháp, menu lỗi thời, block copy-paste, pipeline vẽ lại mâu thuẫn) **bằng máy, không bằng mắt**. Chạy sau MỖI lần thêm/sửa skill — như CI cho skill repo.

## Cách chạy

```bash
python <skills_dir>/x6-skill-doctor/scripts/skill_doctor.py <skills_dir>
```

Exit code 0 = sạch (có thể còn WARN); 1 = có FAIL. Script tự `reconfigure` stdout UTF-8 nên chạy được trên console cp932/cp1252 của Windows.

**Phạm vi lint:**
- Skill có trong `skills-manifest.json` → lint ĐẦY ĐỦ.
- Folder NGOÀI manifest có `SKILL.md` (vd `ui-ux-pro-max`, `product-teardown`) → lint TỐI THIỂU: `name` khớp folder, `description` tồn tại và ≤ 700 ký tự, không còn block copy-paste (D04), tham chiếu chết (D14), script Windows-safe (D15). Nếu SKILL.md trỏ `pipeline.md` của bộ mà chưa đăng ký → FAIL D08 (skill mới quên đăng ký).
- Description chấp nhận mọi kiểu YAML: `>-`, `>`, `|`, chuỗi một dòng có/không ngoặc kép.

Kèm 3 script của /menu:

```bash
python <skills_dir>/menu/scripts/check_menu_sync.py <skills_dir>
python <skills_dir>/menu/scripts/gen_menu_table.py <skills_dir>     # xem nhanh description có ổn không
python <skills_dir>/menu/scripts/test_intents.py <skills_dir>       # tỉ lệ định tuyến top-1 so với bảng AGENTS.md (≥ 95%)
```

## Bộ rule (định nghĩa trong script — sửa rule Ở SCRIPT, không sửa mô tả này)

| # | Rule | Mức |
|---|---|---|
| D01 | Frontmatter: `name` khớp tên folder, có `version`, có `description` | FAIL |
| D02 | Description ≤ 700 ký tự (chuẩn Anthropic: ngắn, chi tiết để trong body) | WARN |
| D03 | SKILL.md ≤ 500 dòng (dài hơn → tách references/) | WARN |
| D04 | Không còn block context copy-paste cũ (chuỗi nhận diện định nghĩa trong script) | FAIL |
| D05 | Đúng 1 section Workflow Integration, và CHÍNH section đó (tới heading `## ` kế tiếp) trỏ `pipeline.md` | FAIL |
| D06 | Không vẽ lại pipeline dài (chuỗi `→ [` xuất hiện > 3 lần ngoài pipeline.md) | WARN |
| D07 | Không có anti-pattern công thức Excel (`$<chữ>:$<chữ>` không phải cột đơn) | FAIL |
| D08 | Manifest ↔ folder đồng bộ 2 chiều, version khớp | FAIL |
| D09 | Không còn ASCII box dài (> 15 dòng `━`) trong SKILL.md | WARN |
| D10 | Skill có ví dụ FPT/F-Pay phải có dòng cảnh báo "VÍ DỤ MINH HỌA" | FAIL |
| D11 | Header "Cấu trúc file Excel (N sheets)" phải khớp số mục `### Sheet` liệt kê bên dưới | FAIL |
| D12 | Mỗi skill trong manifest phải có `intents[]` (nguồn decision tree của /menu) | WARN |
| D14 | Tham chiếu chết: đường dẫn file (`.py/.md/.json/…`) trong backtick của SKILL.md + `references/*.md` phải tồn tại sau khi thay `<skills_dir>`. Bỏ qua dòng ví dụ ("ví dụ", "e.g."), template (`<…>`, `[N]`, `*`), đường dẫn workspace (`docs/`, `src/`…). Tên `.py` trần không tìm thấy → WARN, có thư mục → FAIL | FAIL / WARN |
| D15 | Script Windows-safe: `scripts/**/*.py` phải `compile()` được; script có `print` chuỗi non-ASCII phải `sys.stdout.reconfigure(encoding="utf-8")`; đường dẫn `/tmp` → WARN | FAIL / WARN |
| D16 | Số liệu khớp nguồn: số "N rule" của x6 (manifest summary, README, AGENTS, SKILL này) = số rule trong script; "N skill" trong README/AGENTS/menu = số folder hoặc số skill manifest | FAIL (rule) / WARN (skill) |
| D18 | Skill có `outputs[]` trong manifest phải dẫn chiếu `i18n-policy.md` trong SKILL.md (ngôn ngữ tài liệu theo `settings.languages`, không tự quyết) | FAIL |
| D17 | Version đồng bộ: `manifest_version` = mọi `version` trong `plugin.json`, `marketplace.json`, `.claude-plugin/*.json` (ở thư mục cha của `<skills_dir>`) | FAIL |

> D13 được dành riêng cho kiểm tra khối Self-Improvement (bổ sung ở giai đoạn riêng). Mỗi rule đã được thử bằng "đột biến" (sửa một bản sao để rule phải bắt được) — khi thêm rule mới hãy làm tương tự.

## Sau khi chạy

- Có FAIL → liệt kê từng lỗi kèm file:dòng, đề xuất sửa cụ thể, **sửa xong chạy lại đến khi sạch**.
- Chỉ WARN → cân nhắc từng cái, được phép chấp nhận có lý do (ghi rõ lý do trong response).
- Sạch → in bảng tổng kết + nhắc bump version skill vừa sửa + thêm dòng CHANGELOG.

## Khi nào MỞ RỘNG rule

Mỗi lần phát hiện một lỗi mới "lọt lưới" trong output thực tế → thêm 1 rule Dxx vào script (regression test cho prompt). Đây là regression test cho prompt. **Eval đầy đủ đã có — chạy CÙNG skill-doctor sau mỗi lần sửa:**

```bash
python <skills_dir>/evals/run_evals.py <skills_dir>   # tầng 1 tự động (scripts + gen + linter)
```

Tầng 2 (golden LLM cases khi sửa prompt skill sinh file): `<skills_dir>/evals/README.md`.

---

## 🔗 Workflow Integration

**Nguồn sự thật pipeline: `<skills_dir>/a1-project-init/references/pipeline.md`.**

- **Bước hiện tại:** X6 — Skill Doctor (meta, không thuộc pipeline dự án)
- **Input từ:** toàn bộ thư mục skills + manifest
- **Output cho:** người bảo trì skill (báo cáo PASS/WARN/FAIL trong chat)
- **Bước kế tiếp:** sửa FAIL → chạy lại; sạch → commit/đóng gói skill

Skill này KHÔNG đụng vào project-context của dự án.


---

## Self-Improvement Loop
Cuối tác vụ tự trả lời 3 câu: có lỗi/workaround không? người dùng có đính chính không? có quy tắc mới giúp lần sau không? Không có gì → im lặng.
Có phát hiện HỆ THỐNG → in `💡 Đề xuất cải thiện` (≤ 3 dòng) rồi áp dụng theo quy trình duy nhất: `a1-project-init/references/self-improvement.md`.
Áp dụng: 1 skill/tác vụ, ≤ 40 dòng thêm, không xóa quy tắc, chạy `scripts/skill_self_update.py`; báo skill · thay đổi · commit · `git revert <hash>`.
