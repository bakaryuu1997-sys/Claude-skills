---
name: menu
version: "3.17.0"
description: >-
  Menu điều hướng toàn bộ skill — sinh ĐỘNG từ skills-manifest.json + frontmatter thực tế
  (không hardcode, không bao giờ lỗi thời). Trigger: "/menu", "menu", "có những skill gì",
  "dùng skill gì để", "skill nào cho", "help", "danh sách skill".
---

# Menu — Master Navigation (sinh động, không hardcode)

Khi skill này được kích hoạt, hiển thị menu **ngay trong chat** (không tạo file). Danh sách skill, nhãn giai đoạn và khoảng bước (A1 → A9, C0 → C8…) SINH TỰ ĐỘNG mỗi lần chạy từ manifest + `pipeline.md` + frontmatter — trong file này KHÔNG có nội dung hardcode.

## Nguồn dữ liệu

| Nguồn | Dùng cho |
|---|---|
| `a1-project-init/assets/skills-manifest.json` | skill trong pipeline: bước, phase, summary, outputs, `intents[]` |
| `a1-project-init/references/pipeline.md` | tiêu đề các GIAI ĐOẠN (dòng `GIAI ĐOẠN X — …`) |
| folder skill NGOÀI manifest (vd `ui-ux-pro-max`, `product-teardown`) | "Skill bổ trợ": tên + description lấy từ frontmatter |
| `menu/assets/extras.json` | summary/outputs/intents cho skill bổ trợ (khai khi thêm skill ngoài manifest) |
| `menu/assets/intent_aliases.json` | cụm từ tiếng Việt bổ sung cho bất kỳ skill nào (không cần sửa manifest) |

## Quy trình hiển thị (4 bước)

### 1. Lấy danh sách skill THỰC TẾ

```bash
# Bảng tổng quan: pipeline theo giai đoạn + META + skill bổ trợ ngoài manifest:
python <skills_dir>/menu/scripts/gen_menu_table.py <skills_dir>

# Kiểm tra đồng bộ (folder ↔ manifest, skill bổ trợ có description, assets không trỏ skill ma):
python <skills_dir>/menu/scripts/check_menu_sync.py <skills_dir>
```

### 2. Trình bày theo giai đoạn vòng đời

Dùng đúng thứ tự và nhãn script in ra (A → B → C → D → X → META → BỔ TRỢ). Mỗi skill hiển thị 3 dòng: `Bước + /tên-lệnh` · "Dùng khi" (1 câu từ summary/description) · 1 ví dụ gõ được ngay (KHÔNG bịa tham số phức tạp). Skill `optional` ghi "tùy chọn".

### 3. Plugin ngoài bộ (Figma, Engineering, Product Management…)

**CHỈ liệt kê plugin/skill đang thật sự tồn tại trong môi trường hiện tại** — kiểm tra danh sách available skills trước khi in. KHÔNG in từ trí nhớ, KHÔNG liệt kê plugin đã gỡ (in lệnh chết = người dùng gõ theo sẽ thất bại). Người dùng hỏi về loại plugin chưa cài → gợi ý tìm qua marketplace thay vì giả vờ nó có sẵn.

### 4. Decision tree (khi người dùng mô tả task thay vì hỏi danh sách)

```bash
python <skills_dir>/menu/scripts/match_intent.py <skills_dir> "<mô tả task của người dùng>"
# top 3 skill khớp (điểm, bước, cụm intent). Không khớp → script nói rõ, KHÔNG đoán bừa.
```

Chấm điểm: cụm intent khớp nguyên văn > đủ token (mọi thứ tự) > token hiếm (IDF, bỏ stopword "tôi/muốn/làm/cho…") > bigram. Trả lời người dùng: skill đứng đầu + lý do + 1 ví dụ lệnh. Top 1 và top 2 chênh < 2 điểm → nêu cả hai kèm điểm khác biệt (vd /a8-test-plan sinh case ≠ /c5-test-execution chạy & báo cáo).

**Thêm skill mới:** trong pipeline → khai `intents[]` ở manifest. Ngoài pipeline → thêm mục vào `menu/assets/extras.json`. Cụm tiếng Việt khẩu ngữ → `menu/assets/intent_aliases.json`. KHÔNG sửa file này.

**Test hồi quy định tuyến** (sau khi sửa intents/aliases hoặc bảng trong AGENTS.md):

```bash
python <skills_dir>/menu/scripts/test_intents.py <skills_dir>   # parse bảng AGENTS.md, báo tỉ lệ top-1; exit 1 nếu < 95%
```

## Quy tắc thực thi

- **Không tạo file** — in trực tiếp trong chat. Menu là skill đọc-only: KHÔNG ghi `project-context.json`.
- **Không hardcode** — mọi tên skill/mô tả/số lượng lấy từ script lúc chạy. Không sao chép output cũ.
- Người dùng hỏi sâu về 1 skill → đọc SKILL.md của skill đó và tóm tắt (mục tiêu, input, output, ví dụ).
- Kết thúc menu bằng 1 dòng: `💡 Gõ /menu bất cứ lúc nào · Pipeline đầy đủ: a1-project-init/references/pipeline.md`.

---

## Self-Improvement Loop
Cuối tác vụ tự trả lời 3 câu: có lỗi/workaround không? người dùng có đính chính không? có quy tắc mới giúp lần sau không? Không có gì → im lặng.
Có phát hiện HỆ THỐNG → in `💡 Đề xuất cải thiện` (≤ 3 dòng) rồi áp dụng theo quy trình duy nhất: `a1-project-init/references/self-improvement.md`.
Áp dụng: 1 skill/tác vụ, ≤ 40 dòng thêm, không xóa quy tắc, chạy `scripts/skill_self_update.py`; báo skill · thay đổi · commit · `git revert <hash>`.
