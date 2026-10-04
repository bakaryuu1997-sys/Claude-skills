---
name: menu
version: "3.8.0"
description: >-
  Menu điều hướng toàn bộ skill — sinh ĐỘNG từ skills-manifest.json + frontmatter thực tế
  (không hardcode, không bao giờ lỗi thời). Trigger: "/menu", "menu", "có những skill gì",
  "dùng skill gì để", "skill nào cho", "help", "danh sách skill".
---

# Menu — Master Navigation (sinh động, không hardcode)

Khi skill này được kích hoạt, hiển thị menu **ngay trong chat** (không tạo file). Danh sách skill SINH TỰ ĐỘNG mỗi lần chạy từ script + manifest. Decision tree cũng sinh từ manifest (`intents[]` + `match_intent.py`) — trong file này KHÔNG còn nội dung hardcode nào.

## Quy trình hiển thị (4 bước)

### 1. Lấy danh sách skill THỰC TẾ

```bash
# Bảng tổng quan sinh từ frontmatter của mọi skill folder đang tồn tại:
python3 <skills_dir>/menu/scripts/gen_menu_table.py <skills_dir>

# Kiểm tra đồng bộ (skill nào có folder mà thiếu mô tả, hoặc ngược lại):
python3 <skills_dir>/menu/scripts/check_menu_sync.py <skills_dir>
```

Đọc thêm `<skills_dir>/a1-project-init/assets/skills-manifest.json` để lấy bước pipeline (A1–D3), phase, gate của từng skill.

### 2. Trình bày theo các giai đoạn vòng đời (thứ tự từ `a1-project-init/references/pipeline.md`)

```
📦 GIAI ĐOẠN A — CHUẨN BỊ & THIẾT KẾ     (A1 → A9, chạy một lần)
🚀 GIAI ĐOẠN B — KHỞI ĐỘNG & ĐẶC TẢ      (B0 → B3, sau khi ký hợp đồng)
🔄 GIAI ĐOẠN C — VẬN HÀNH & PHÁT TRIỂN   (C1 → C8, lặp lại mỗi task/PR/sprint)
🏁 GIAI ĐOẠN D — KẾT THÚC & BÀN GIAO     (D1 → D3, sau go-live)
🛠️ GIAI ĐOẠN X — CROSS-CUTTING          (X1 → X7, chạy bất kỳ lúc nào)
🧭 META — ĐIỀU HƯỚNG & KIỂM ĐỊNH         (/menu, /x6-skill-doctor)
```

Mỗi skill hiển thị 3 dòng: `Bước + /tên-lệnh` · "Dùng khi" (1 câu, lấy từ description) · 1 ví dụ gõ được ngay (tự sinh ví dụ ngắn phù hợp description — KHÔNG bịa tham số phức tạp).

### 3. Plugin ngoài bộ (Figma, Engineering, Product Management…)

**CHỈ liệt kê plugin/skill đang thật sự tồn tại trong môi trường hiện tại** — kiểm tra danh sách available skills trước khi in. KHÔNG in từ trí nhớ, KHÔNG liệt kê plugin đã gỡ (in lệnh chết = người dùng gõ theo sẽ thất bại). Nếu người dùng hỏi về loại plugin chưa cài → gợi ý tìm qua marketplace thay vì giả vờ nó có sẵn.

### 4. Decision tree (khi người dùng mô tả task thay vì hỏi danh sách)

Decision tree SINH TỪ MANIFEST — mỗi skill khai `intents[]` trong `skills-manifest.json`; thêm skill mới chỉ cần khai intents ở đó, KHÔNG sửa file này:

```bash
python3 <skills_dir>/menu/scripts/match_intent.py <skills_dir> "<mô tả task của người dùng>"
# In top 3 skill khớp (điểm + bước + lý do). Không khớp → script nói rõ, KHÔNG đoán bừa.
```

Trả lời người dùng: skill đứng đầu + tại sao + 1 ví dụ lệnh gõ được ngay. Điểm top 1 và top 2 sát nhau (chênh < 2) → nêu cả hai kèm điểm khác biệt (vd /a8-test-plan sinh case ≠ /c5-test-execution chạy & báo cáo).

## Quy tắc thực thi

- **Không tạo file** — in trực tiếp trong chat.
- **Không hardcode** — mọi tên skill/mô tả lấy từ script + manifest lúc chạy. Không sao chép output cũ từ lần chạy trước.
- Thêm/xóa skill → chỉ cần cập nhật `skills-manifest.json` + `pipeline.md` (trong /a1-project-init); menu tự phản ánh, KHÔNG sửa file này.
- Người dùng hỏi sâu về 1 skill → đọc SKILL.md của skill đó và tóm tắt (mục tiêu, input, output, ví dụ).
- Kết thúc menu bằng 1 dòng: `💡 Gõ /menu bất cứ lúc nào · Pipeline đầy đủ: a1-project-init/references/pipeline.md`.

---

## Self-Improvement Loop

Trước khi kết thúc tác vụ, hãy tự đánh giá lại quá trình thực hiện theo 3 câu hỏi:
1. Có bước nào thất bại, gặp lỗi hoặc phải dùng cách xử lý tạm (workaround) không?
2. Người dùng có phải đính chính, chỉnh sửa hoặc từ chối kết quả nào đáng chú ý không?
3. Có phát hiện thêm ngữ cảnh hay quy tắc mới nào giúp các lần chạy sau làm tốt hơn không?

Nếu có thay đổi thực sự giá trị, hãy đề xuất 1–2 điểm ngắn gọn để cập nhật vào skill này và chờ người dùng duyệt. Không tự ý sửa file nếu chưa có xác nhận.

**Hai lưu ý quan trọng khi áp dụng:**
- **Bắt buộc phải có bước xác nhận:** Luôn chặn quyền tự ý ghi đè file của AI. Bạn phải là người gật đầu duyệt đề xuất để tránh việc AI tự tiện làm loãng hoặc làm hỏng bộ quy tắc ban đầu.
- **Chỉ cập nhật lỗi quy trình, bỏ qua lỗi tức thời:** Lọc kỹ xem phản hồi của bạn ở lần chạy đó là sở thích nhất thời cho một đầu việc cá biệt hay là tiêu chuẩn chung cần chuẩn hóa. Chỉ đưa vào skill những thứ mang tính hệ thống để tránh phình dung lượng prompt không cần thiết.

