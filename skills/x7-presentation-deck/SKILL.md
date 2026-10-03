---
name: x7-presentation-deck
version: "3.7.0"
description: >-
  Tạo slide thuyết trình chuyên nghiệp (PowerPoint pptx 16:9 + HTML interactive slide Marp):
  thiết kế dạng thẻ (Card-based), bảng màu doanh nghiệp, biểu đồ số liệu trực quan, không
  placeholder TBD. Dùng cho pitch, demo, kickoff, sprint review, kiến trúc. Trigger:
  "slide thuyết trình", "tạo slide", "presentation", "powerpoint", "pptx", "pitch deck",
  "slide báo cáo", "thuyết trình dự án". Bước X7.
---

# Presentation Deck — Tạo Slide Thuyết Trình Chuyên Nghiệp

## Mục tiêu

Tạo bộ slide thuyết trình kỹ thuật và quản trị đẳng cấp cao: **Pitching giải pháp, Họp Kickoff, Trình bày Kiến trúc, Sprint Review / Demo sản phẩm, và Báo cáo Ban Lãnh đạo**.

Kế thừa tinh hoa từ các skill mã nguồn mở hàng đầu (*Deck-as-Code*, *Template-first*, *Action Titles*, *Proportional Spacing*, *Anti-Slop Design*), bộ kỹ năng xuất ra song hành 2 định dạng:
1. **PowerPoint (`.pptx`) 16:9 Widescreen**: Thiết lập layout thông minh bằng `python-pptx`, typography phân cấp với font hiện đại (`Segoe UI`), cân bằng khoảng trắng, thẻ nổi glassmorphism và icon badges.
2. **HTML Presentation (`.html`) Tự Vận Hành**: Trình chiếu web chuẩn 16:9 với Tailwind CSS, Dark Glassmorphism, phím tắt (`←`, `→`, `Space`), Fullscreen (`F`) và nhúng ảnh Base64 tự chứa 100%.

---

## Bước -1 — Đọc Project Context (nếu có)

> **Giao thức chuẩn — chi tiết: `a1-project-init/references/pipeline.md`** (KHÔNG chép lại vào skill):
> đọc bằng `load_context.py` + `cget()`; ghi bằng `update_context.py`; gate bằng `check_gate.py`.
> `NO_CONTEXT` → chạy chế độ hỏi/suy luận thủ công.

Trích xuất: `project.name`, `client`, `tech_stack`, `team`, `estimates`, `milestones`, `activity_log`, và các hiện vật thực tế (`docs/C2_test-execution/screenshots/`, sơ đồ kiến trúc SVG/HTML).

---

## 4 Quy Tắc Thiết Kế Slide Đỉnh Cao

### 1. Quy tắc Action Title (Bắt buộc 100%)
- **CẤM**: Đặt tiêu đề là danh từ chung chung, rời rạc (Ví dụ: ❌ *"Kiến trúc hệ thống"*, ❌ *"Kết quả kiểm thử"*).
- **BẮT BUỘC**: Tiêu đề là **Action Title** — câu khẳng định ngắn gọn chứa kết luận/thông điệp cốt lõi (*Key Takeaway*) giúp người nghe nắm bắt ngay trong 3 giây.
  - *Ví dụ*: ✅ *"Kiến Trúc 4 Tầng Tối Ưu: Express Gateway → Prisma ORM → PostgreSQL 16"*
  - *Ví dụ*: ✅ *"108/108 Test Specs Vượt Qua Tuyệt Đối — Sẵn Sàng 95% Cho Mốc Go-Live"*

### 2. Khống chế Mật Độ Chữ (Density Cap)
- Giới hạn: **40–50 từ** trên một slide nội dung.
- **CẤM**: Đoạn văn xuôi dài dòng (No walls of text).
- **BẮT BUỘC**: Dùng **Khối thẻ (Card Grid)**, **Chỉ số đo lường lớn (Big KPI Numbers)**, và các gạch đầu dòng súc tích (**6–8 từ/ý**).

### 3. Cân Bằng Khoảng Trắng & Bố Cục Tỷ Lệ (Negative Space & Proportional Layout)
- **Triệt tiêu khoảng trống thừa (Anti-Void Rule)**: Tránh dồn toàn bộ nội dung lên nửa trên rồi để nửa dưới là các hộp rỗng.
- **Bố cục Cover Slide dạng Asymmetric Hero (60/40)**:
  - Cột trái (60%): Badge trạng thái, Tiêu đề dự án lớn (44pt+ bold), Action Subtitle, đoạn giá trị cốt lõi, Thông tin người thuyết trình.
  - Cột phải (40%): Khung kính nổi bật (*Executive Highlight Card*) tổng hợp các chỉ số trọng tâm (Sprint, Specs, Mốc Go-Live, Tech Stack) tạo sự cân đối thị giác hoàn hảo.
- **Tính toán chiều cao Card linh hoạt**: Cỡ chữ tiêu đề thẻ 14–16pt, chữ nội dung 12–13pt kèm padding hợp lý, không để thẻ to đùng nhưng chữ lọt thỏm.

### 4. Hệ Thống Nhận Diện Trực Quan Cao Cấp (Anti-Slop Design System)
- **100% Theme Uniformity**: Giữ nguyên một hệ màu nền duy nhất từ slide 1 đến slide cuối (Executive Dark Slate `#0B132B` hoặc Enterprise Clean Light `#F8FAFC`). CẤM TUYỆT ĐỐI pha trộn slide đen trắng lộn xộn.
- **Typography Hiện Đại**: Sử dụng `Segoe UI` (trên Windows/Office) tạo cảm giác thanh thoát, sắc nét và chuyên nghiệp hơn font Arial mặc định.
- **Hoa văn & Họa tiết**:
  - Dải màu thương hiệu ở mép đỉnh slide (Top gradient accent bar: `#00C9FF` → `#10B981`).
  - Status Pill Badges bo góc ở đầu trang (`[SPRINT 2 ACTIVE]`, `[CORE COMPLETE]`).
  - Elevated Cards bo góc viền mảnh tương phản (`#3A506B`) và đổ bóng nhẹ.
  - Icon Badges trực quan (`⚡`, `🚀`, `🛡️`, `🎯`, `💾`, `🐳`, `🔐`, `✓`).
  - Footer Breadcrumbs đồng bộ trên 100% slide: Tên dự án | Chuyên đề | `Trang X / N` | Ngày tháng.
- **Nhúng Hiện Vật Thực Tế**: Bắt buộc nhúng ảnh chụp màn hình UI thật từ bộ test (`screenshots/`) theo bố cục Split-Pane 60/40.

---

## 2 Chế Độ Triển Khai (Execution Modes)

1. **Mode A — Template-First (Khi có sẵn mẫu `.potx` / `.pptx`)**:
   - Nếu có template PowerPoint chuẩn nhận diện thương hiệu của công ty hoặc khách hàng, nạp template và đổ dữ liệu vào các layout placeholder sẵn có.
2. **Mode B — Deck-as-Code Engine (Tự động sinh toàn diện)**:
   - Dựng script Python (`python-pptx`) hoặc PptxGenJS áp dụng đầy đủ quy tắc tính toán tọa độ, typography `Segoe UI`, bảng màu và icon badges.
   - Song hành xuất file HTML tương tác chạy trực tiếp trên trình duyệt.

---

## Cấu Trúc Khung Bộ Slide 10 Trang Chuẩn Mực

- **Slide 1 — Cover Asymmetric Hero**: Action Title, Pill Badge, Cột trái giới thiệu, Cột phải thẻ Executive Highlights.
- **Slide 2 — Tầm Nhìn & 3 Trụ Cột**: 3 Thẻ giải pháp song song kèm số thứ tự nổi bật (01, 02, 03).
- **Slide 3 — Chỉ Số Hoạt Động (KPI Matrix)**: 4 Khối số lớn (36-44pt) kèm Callout đánh giá chất lượng.
- **Slide 4 — Kiến Trúc Hệ Thống**: 4 Tầng phân lập (Presentation, Gateway, Security, Persistence) có viền màu nhận diện.
- **Slide 5–6 — Feature Showcase (Split-Pane)**: Ảnh chụp màn hình thật viền dạ quang + 3 thẻ phân tích giá trị kỹ thuật.
- **Slide 7 — Tiến Độ & Lộ Trình Scrum**: 3 Cột Sprint (Sprint 1 Hoàn thành, Sprint 2 Đang làm, Sprint 3 Go-Live).
- **Slide 8 — Bảo Mật Đa Lớp**: 3 Trụ cột an toàn (Master Auth, API Defense, Network Isolation).
- **Slide 9 — Vận Hành DevOps**: Docker Compose 1-lệnh, Health Probes giám sát, Tự động sao lưu dự phòng.
- **Slide 10 — Nghiệm Thu & Q&A**: Checklist UAT 5 mục hoàn thành + Định hướng mở rộng & thảo luận.

---

## 🔗 Workflow Integration

**Nguồn sự thật pipeline: `<skills_dir>/a1-project-init/references/pipeline.md`** — KHÔNG vẽ lại pipeline trong response; nếu nơi khác mô tả thứ tự lệch, pipeline.md thắng.

- **Bước hiện tại:** X7 — Presentation Deck (Tạo slide thuyết trình chuyên nghiệp)
- **Input từ:** Bất kỳ tài liệu nào trong pipeline cần trình chiếu (A2, A6, B0, B1, C6, X2...)
- **Output cho:** Khách hàng, ban lãnh đạo, toàn thể team dự án
- **Bước kế tiếp:** Trình chiếu trực tiếp trong buổi họp hoặc đính kèm báo cáo

**Kết thúc response:** theo quy ước chung trong `pipeline.md` (≤ 6 dòng ✅→▶; skill tạo/sửa file append `activity_log[]` bằng `update_context.py`).

---

## Self-Improvement Loop

Trước khi kết thúc tác vụ, hãy tự đánh giá lại quá trình thực hiện theo 3 câu hỏi:
1. Có bước nào thất bại, gặp lỗi hoặc phải dùng cách xử lý tạm (workaround) không?
2. Người dùng có phải đính chính, chỉnh sửa hoặc từ chối kết quả nào đáng chú ý không?
3. Có phát hiện thêm ngữ cảnh hay quy tắc mới nào giúp các lần chạy sau làm tốt hơn không?
